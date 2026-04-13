#!/usr/bin/env python3
from typing import Any, Dict, List, Optional

from common import (
    CANONICAL_ARTIFACT_REL_PATHS,
    DEFAULT_ITERATION_ID,
    app_manifest_path,
    apply_diff_sequence,
    build_parser,
    compare_versions,
    get_app_baseline_requirement_ids,
    get_app_iteration_id,
    get_app_manifest,
    get_artifact_doc_path,
    get_diff_files,
    get_technology_selection,
    implementation_structured_diff_path,
    merged_path,
    normalize_iteration_id,
    now_iso,
    read_yaml,
    resolve_target_implementations,
    validate_target_for_app,
    write_yaml,
)


def load_current_requirements(requirements_path: str) -> Dict[str, Dict[str, Any]]:
    merged = read_yaml(merged_path(requirements_path))
    out: Dict[str, Dict[str, Any]] = {}
    for req in merged.get("requirements", []) or []:
        rid = req.get("requirement_id")
        if rid:
            out[str(rid)] = req
    return out


def build_previous_snapshot_map(requirements_path: str, implemented_version: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for fp in get_diff_files(requirements_path):
        raw = read_yaml(fp)
        rid = str(raw.get("requirement_id") or "")
        if not rid:
            continue
        staged = {"requirement_id": rid, "diffs": []}
        for d in raw.get("diffs", []) or []:
            v = str(d.get("version") or d.get("at_version") or implemented_version)
            if compare_versions(v, implemented_version) <= 0:
                staged["diffs"].append(d)
        cur = apply_diff_sequence(staged)
        if cur:
            out[rid] = cur
    return out


def extract_baseline_entry(app_manifest: Dict[str, Any], requirement_id: str) -> Optional[Dict[str, Any]]:
    for entry in app_manifest.get("requirement_baseline", []) or []:
        if str(entry.get("requirement_id")) == requirement_id:
            return entry
    return None


def load_models_and_contracts_items(requirements_path: str) -> Dict[str, Dict[str, Any]]:
    """Load MAC items from the promoted models_and_contracts.yaml (or legacy contracts_and_models.yaml)."""
    import os
    for key in ("models_and_contracts", "data_and_api_contracts", "contracts_and_models"):
        rel = CANONICAL_ARTIFACT_REL_PATHS.get(key)
        if not rel:
            continue
        fp = os.path.join(requirements_path, rel)
        if os.path.isfile(fp):
            doc = read_yaml(fp)
            out: Dict[str, Dict[str, Any]] = {}
            for it in doc.get("items", []) or []:
                rid = it.get("id")
                if rid:
                    out[str(rid)] = it
            return out
    return {}


def build_mac_diff(
    mac_items: Dict[str, Dict[str, Any]],
    implemented_ids: set,
    effective_implemented_version: str,
) -> Dict[str, List[Dict[str, Any]]]:
    """Build created/updated/removed lists for models_and_contracts items."""
    created: List[Dict[str, Any]] = []
    updated: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []

    mac_ids = set(mac_items.keys())

    for mid, item in sorted(mac_items.items()):
        replaces_id = item.get("replaces_id")
        if mid in implemented_ids:
            # Check if it was updated since implementation.
            updated_v = str(item.get("updated_version") or "0.0.0")
            if compare_versions(updated_v, effective_implemented_version) > 0:
                updated.append({
                    "mac_id": mid,
                    "item": item,
                })
            continue
        if replaces_id and str(replaces_id) in implemented_ids:
            updated.append({
                "mac_id": mid,
                "replaces_id": str(replaces_id),
                "item": item,
            })
            continue
        created.append({
            "mac_id": mid,
            "item": item,
        })

    # MAC items in baseline but no longer in current → removed.
    for mid in sorted(implemented_ids):
        if str(mid).startswith("MAC-") and str(mid) not in mac_ids:
            # Check if superseded.
            superseded_by = None
            for cid, citem in mac_items.items():
                if str(citem.get("replaces_id")) == str(mid):
                    superseded_by = cid
                    break
            entry: Dict[str, Any] = {"mac_id": str(mid)}
            if superseded_by:
                entry["superseded_by"] = superseded_by
            removed.append(entry)

    return {"created": created, "updated": updated, "removed": removed}


def main() -> None:
    parser = build_parser("Generate structured diff from app manifest vs current promoted requirements")
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    targets = resolve_target_implementations(args.requirements_path, args.app_path, args.implementation_id, args.all_implementations)
    if args.output and len(targets) > 1:
        raise ValueError("--output can only be used with a single implementation target")

    current_map = load_current_requirements(args.requirements_path)
    merged = read_yaml(merged_path(args.requirements_path))
    merged_version = str(merged.get("requirements_version") or "0.0.0")

    for t in targets:
        req_set, _ = validate_target_for_app(t, args.requirements_path)
        implementation_id = str(t.get("implementation_id"))
        app_path = t.get("app_path")
        app_manifest = get_app_manifest(app_path) if app_path else {}
        # Target version comes from the requirements repo (merged/control), not the app manifest.
        target_version = str(merged_version or "0.0.0")
        # App manifest requirement_baseline is the source of truth for "already implemented".
        implemented_ids = set(get_app_baseline_requirement_ids(app_path)) if app_path else set()
        current_iteration = get_app_iteration_id(app_path) if app_path else DEFAULT_ITERATION_ID
        implemented_version = str(app_manifest.get("requirements_version_implemented") or "0.0.0")
        previous_snapshot_map = build_previous_snapshot_map(args.requirements_path, implemented_version)

        explicit_targets = app_manifest.get("app_requirement_ids")
        explicit_target_ids = set(str(x) for x in explicit_targets) if isinstance(explicit_targets, list) else set()
        tracked_requirement_ids = set(current_map.keys()) | set(previous_snapshot_map.keys())
        # Only for "updated" do we need repo version: implemented and present in requirements repo.
        comparable_implemented_ids = implemented_ids & tracked_requirement_ids
        if explicit_target_ids:
            comparable_implemented_ids &= explicit_target_ids

        eligible_current_map: Dict[str, Dict[str, Any]] = {}
        for rid, req in current_map.items():
            req_iteration = normalize_iteration_id(req.get("iteration_id"), DEFAULT_ITERATION_ID)
            if req_iteration > current_iteration:
                continue
            if explicit_target_ids and rid not in explicit_target_ids:
                continue
            eligible_current_map[rid] = req

        eligible_ids = set(eligible_current_map.keys())

        created: List[Dict[str, Any]] = []
        updated: List[Dict[str, Any]] = []
        removed: List[Dict[str, Any]] = []

        replaces_id_map = {}
        for rid, req in eligible_current_map.items():
            rep = req.get("replaces_id")
            if rep:
                replaces_id_map[str(rep)] = rid

        baseline_implemented_versions: List[str] = []
        for entry in app_manifest.get("requirement_baseline", []) or []:
            if isinstance(entry, dict) and entry.get("implemented_at"):
                rid_b = str(entry.get("requirement_id", ""))
                req_b = eligible_current_map.get(rid_b)
                if req_b:
                    v = str((req_b.get("versioning") or {}).get("updated_on_version") or "0.0.0")
                    baseline_implemented_versions.append(v)
        effective_implemented_version = implemented_version
        for v in baseline_implemented_versions:
            if compare_versions(v, effective_implemented_version) > 0:
                effective_implemented_version = v

        for rid, req in sorted(eligible_current_map.items()):
            replaces_id = req.get("replaces_id")
            if rid in implemented_ids:
                if rid not in comparable_implemented_ids:
                    continue
                updated_on_version = str(
                    (req.get("versioning") or {}).get("updated_on_version") or "0.0.0"
                )
                if compare_versions(updated_on_version, effective_implemented_version) > 0:
                    entry = {
                        "requirement_id": rid,
                        "original_requirement": previous_snapshot_map.get(rid)
                        or extract_baseline_entry(app_manifest, rid),
                        "new_requirement": req,
                    }
                    if replaces_id:
                        entry["replaces_id"] = str(replaces_id)
                    updated.append(entry)
                continue
            if replaces_id and str(replaces_id) in implemented_ids:
                entry = {
                    "requirement_id": rid,
                    "replaces_id": str(replaces_id),
                    "original_requirement": previous_snapshot_map.get(str(replaces_id))
                    or extract_baseline_entry(app_manifest, str(replaces_id)),
                    "new_requirement": req,
                }
                updated.append(entry)
                continue
            entry = {
                "requirement_id": rid,
                "new_requirement": req,
            }
            if replaces_id:
                entry["replaces_id"] = str(replaces_id)
            created.append(entry)

        for rid in sorted(comparable_implemented_ids - eligible_ids):
            superseded_by = replaces_id_map.get(rid)
            entry = {
                "requirement_id": rid,
                "original_requirement": previous_snapshot_map.get(rid)
                or extract_baseline_entry(app_manifest, rid),
            }
            if superseded_by:
                entry["superseded_by"] = superseded_by
            removed.append(entry)

        technology_selection_doc = get_technology_selection(args.requirements_path, implementation_id)
        ts_entries = technology_selection_doc.get("entries") or []
        technology_selection_doc["entries"] = [
            e for e in ts_entries
            if isinstance(e, dict) and str(e.get("id", "")) not in implemented_ids
        ]

        # Build models_and_contracts diff.
        mac_items = load_models_and_contracts_items(args.requirements_path)
        mac_diff = build_mac_diff(mac_items, implemented_ids, effective_implemented_version)

        out_doc = {
            'diff_metadata': {
                'requirement_set_id': req_set,
                'implementation_id': implementation_id,
                'base_version': implemented_version,
                'target_version': target_version,
                'generated_at': now_iso(),
                'compare_source': {
                    'app_manifest_path': app_manifest_path(app_path) if app_path else "",
                    'requirements_version_implemented': app_manifest.get('requirements_version_implemented'),
                    'effective_implemented_version': effective_implemented_version,
                    'baseline_requirement_ids_count': len(implemented_ids),
                    'comparable_implemented_ids_count': len(comparable_implemented_ids),
                    'current_requirements_eligible_count': len(eligible_ids),
                },
            },
            'technology_selection': technology_selection_doc,
            'requirements_diff': {'created': created, 'updated': updated, 'removed': removed},
            'models_and_contracts_diff': mac_diff,
        }
        out = args.output or implementation_structured_diff_path(
            args.requirements_path, implementation_id, create_dirs=True
        )
        write_yaml(out, out_doc)
        print(f'[{implementation_id}] Structured diff written to {out}')


if __name__ == '__main__':
    main()
