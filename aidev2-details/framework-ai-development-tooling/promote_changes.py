#!/usr/bin/env python3
import glob
import os
import shutil
from copy import deepcopy
from typing import Any, Dict, List

from bootstrap import extract_requirements_from_yaml, pick_bucket
from common import (
    CURRENT_DIR,
    DEFAULT_ITERATION_ID,
    DIFF_DIR,
    PENDING_PROMOTION_DIR,
    apply_diff_sequence,
    build_parser,
    bump_patch,
    changes_path,
    compare_versions,
    DIFF_BUCKETS_BY_ARTIFACT_TYPE,
    generate_merged,
    get_app_manifest,
    get_artifact_doc_path,
    get_diff_files,
    grouped_current_doc_path,
    is_grouped_requirement_type,
    iter_pending_promotion_doc_paths,
    merged_path,
    now_iso,
    normalize_iteration_id,
    read_yaml,
    REQUIREMENT_TYPE_TO_ARTIFACT,
    requirements_manifest_path,
    resolve_target_implementations,
    sync_technology_selection_mirrors,
    validate_target_for_app,
    write_split_merged,
    write_yaml,
)


def find_diff_file(requirements_path: str, requirement_id: str):
    for fp in get_diff_files(requirements_path):
        if read_yaml(fp).get('requirement_id') == requirement_id:
            return fp
    return None


def create_diff_file(requirements_path: str, req: dict):
    bucket = 'functional' if req.get('type') == 'functional' else 'non_functional'
    rid = req.get('requirement_id')
    fp = os.path.join(requirements_path, DIFF_DIR, bucket, f'{rid}.yaml')
    write_yaml(fp, {'requirement_id': rid, 'diffs': [{'seq': 1, 'op': 'create', 'at': now_iso(), 'requirement': req}]})


def append_op(fp: str, payload: dict):
    raw = read_yaml(fp)
    diffs = raw.get('diffs', [])
    payload['seq'] = max([d.get('seq', 0) for d in diffs] or [0]) + 1
    payload['at'] = now_iso()
    diffs.append(payload)
    raw['diffs'] = diffs
    write_yaml(fp, raw)


def write_update_event_file(requirements_path: str, requirement_id: str, from_version: str, to_version: str, prior_snapshot: dict, current_snapshot: dict, changes: list):
    stamp = now_iso().replace(':', '').replace('-', '')
    out_dir = os.path.join(requirements_path, DIFF_DIR, 'history', requirement_id)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'{stamp}.yaml')
    write_yaml(out, {
        'requirement_id': requirement_id,
        'from_version': from_version,
        'to_version': to_version,
        'generated_at': now_iso(),
        'prior': prior_snapshot,
        'current': current_snapshot,
        'changes': changes,
    })


def enrich_requirement_versions(req: dict, created_on: str, updated_on: str, iteration_id: int) -> dict:
    out = deepcopy(req or {})
    out.setdefault("iteration_id", iteration_id or DEFAULT_ITERATION_ID)
    versioning = out.get("versioning")
    if not isinstance(versioning, dict):
        versioning = {}
    versioning.setdefault("created_on_version", created_on)
    versioning["updated_on_version"] = updated_on
    out["versioning"] = versioning
    return out


def ensure_updated_version_change(changes: list, to_version: str) -> list:
    out = list(changes or [])
    replaced = False
    for ch in out:
        if ch.get("field") == "versioning.updated_on_version":
            ch["new"] = to_version
            replaced = True
            break
    if not replaced:
        out.append(
            {
                "field": "versioning.updated_on_version",
                "old": "",
                "new": to_version,
            }
        )
    return out


def apply_requirement_changes(requirements_path: str, change_doc: Dict[str, Any], to_version: str, from_version: str) -> Dict[str, List[str]]:
    """Process requirement_change items: apply update/delete actions to the target artifact files.
    Returns a dict mapping artifact_type to lists of affected IDs."""
    affected: Dict[str, List[str]] = {}
    for change_item in change_doc.get("items", []) or []:
        action = change_item.get("action")
        original = change_item.get("original") or {}
        original_id = original.get("id")
        req_type = original.get("type")
        if not original_id or not req_type:
            continue
        artifact_type = REQUIREMENT_TYPE_TO_ARTIFACT.get(req_type, req_type)
        target_fp = get_artifact_doc_path(requirements_path, artifact_type, create_dirs=True)
        if not os.path.exists(target_fp):
            continue
        target_doc = read_yaml(target_fp)
        items_key = "items" if "items" in target_doc else "entries"
        target_items = target_doc.get(items_key, []) or []
        by_id: Dict[str, Dict[str, Any]] = {}
        for it in target_items:
            rid = it.get("id")
            if rid:
                by_id[str(rid)] = it

        if action == "delete":
            if str(original_id) in by_id:
                del by_id[str(original_id)]
                affected.setdefault(artifact_type, []).append(str(original_id))

        elif action == "update":
            new_req = change_item.get("new") or {}
            new_id = new_req.get("id")
            if not new_id:
                continue
            new_entry = deepcopy(new_req)
            new_entry["replaces_id"] = str(original_id)
            new_entry["created_version"] = to_version
            new_entry["updated_version"] = to_version
            by_id[str(new_id)] = new_entry
            if str(original_id) in by_id and str(original_id) != str(new_id):
                existing = by_id[str(original_id)]
                existing["superseded_by"] = str(new_id)
                existing["updated_version"] = to_version
            affected.setdefault(artifact_type, []).append(str(new_id))

        target_doc[items_key] = sorted(by_id.values(), key=lambda x: str(x.get("id", "")))
        write_yaml(target_fp, target_doc)
    return affected


def merge_pending_doc_into_target(target_doc: Dict[str, Any], pending_doc: Dict[str, Any], to_version: str, from_version: str) -> Dict[str, Any]:
    out = deepcopy(target_doc or {})
    out.pop("source_path", None)
    items_key = "entries" if "entries" in out else "items"
    pending_items_key = "entries" if "entries" in pending_doc else "items"
    pending_items = pending_doc.get(pending_items_key, []) or []
    target_items = out.get(items_key, []) or []
    by_id: Dict[str, Dict[str, Any]] = {}
    for it in target_items:
        rid = it.get("id")
        if rid:
            by_id[str(rid)] = it

    for pit in pending_items:
        rid = pit.get("id")
        if not rid:
            continue
        rid = str(rid)
        existing = by_id.get(rid)
        incoming = deepcopy(pit)
        incoming.pop("app_identifier", None)
        incoming.pop("implementation_id", None)
        incoming.pop("implementation_ids", None)
        if existing:
            created_v = str(existing.get("created_version") or from_version)
            incoming["created_version"] = created_v
            incoming["updated_version"] = to_version
            by_id[rid] = incoming
        else:
            incoming["created_version"] = to_version
            incoming["updated_version"] = to_version
            by_id[rid] = incoming

    out[items_key] = sorted(by_id.values(), key=lambda x: str(x.get("id", "")))
    if "paragraphs" in out and "paragraphs" in pending_doc:
        out["paragraphs"] = pending_doc.get("paragraphs", [])
    return out


def rebuild_requirement_diffs(requirements_path: str) -> None:
    for bucket in sorted(set(DIFF_BUCKETS_BY_ARTIFACT_TYPE.values())):
        p = os.path.join(requirements_path, DIFF_DIR, bucket)
        if os.path.isdir(p):
            for fp in glob.glob(os.path.join(p, "*.yaml")):
                os.remove(fp)
        else:
            os.makedirs(p, exist_ok=True)

    for req_type, bucket in DIFF_BUCKETS_BY_ARTIFACT_TYPE.items():
        sources: List[str] = []
        if is_grouped_requirement_type(req_type):
            from common import GROUPED_REQUIREMENT_REL_DIRS
            grouped_dir = os.path.join(
                requirements_path, CURRENT_DIR,
                GROUPED_REQUIREMENT_REL_DIRS[req_type],
            )
            if os.path.isdir(grouped_dir):
                sources = sorted(glob.glob(os.path.join(grouped_dir, "*.yaml")))
        else:
            flat = get_artifact_doc_path(requirements_path, req_type, create_dirs=False)
            if os.path.exists(flat):
                sources = [flat]
        for src in sources:
            for req in extract_requirements_from_yaml(src):
            effective_bucket = bucket or pick_bucket(req.get("type", "functional"))
            rid = req["requirement_id"]
            out = os.path.join(requirements_path, DIFF_DIR, effective_bucket, f"{rid}.yaml")
            write_yaml(
                out,
                {
                    "requirement_id": rid,
                    "diffs": [
                        {
                            "seq": 1,
                            "op": "create",
                            "version": (req.get("versioning") or {}).get("updated_on_version"),
                            "at": now_iso(),
                            "requirement": req,
                        }
                    ],
                },
            )


def promote_contract_spec_files(requirements_path: str) -> int:
    """Copy contract/model spec files from pending models_and_contracts/ to current models_and_contracts/.
    Returns the number of files promoted."""
    pending_specs = os.path.join(requirements_path, PENDING_PROMOTION_DIR, "models_and_contracts")
    # Also check legacy folder name for backward compatibility.
    if not os.path.isdir(pending_specs):
        pending_specs = os.path.join(requirements_path, PENDING_PROMOTION_DIR, "contracts_and_models")
    if not os.path.isdir(pending_specs):
        return 0
    current_specs = os.path.join(requirements_path, CURRENT_DIR, "models_and_contracts")
    os.makedirs(current_specs, exist_ok=True)
    count = 0
    for entry in sorted(os.listdir(pending_specs)):
        src = os.path.join(pending_specs, entry)
        if os.path.isfile(src) and entry.endswith((".yaml", ".yml", ".json")):
            dst = os.path.join(current_specs, entry)
            shutil.copy2(src, dst)
            count += 1
    return count


def main() -> None:
    parser = build_parser('Promote pending changes to diff files and advance version')
    parser.add_argument('--change-file', default=None)
    args = parser.parse_args()

    targets = resolve_target_implementations(args.requirements_path, args.app_path, args.implementation_id, args.all_implementations)
    req_set = None
    for t in targets:
        req_set, _ = validate_target_for_app(t, args.requirements_path)

    cp = args.change_file or changes_path(args.requirements_path)
    control = read_yaml(cp)
    from_v = str(control.get('current_version', '1.0.0'))
    # Requirements version is driven solely by control.yaml — never by the app manifest.
    to_v = str(control.get('next_version') or bump_patch(from_v))
    if compare_versions(to_v, from_v) <= 0:
        to_v = bump_patch(from_v)
    iteration_id = normalize_iteration_id(control.get("iteration_id"), DEFAULT_ITERATION_ID)
    promoted_counts: Dict[str, int] = {}
    promoted_ids: List[str] = []

    for pfp in iter_pending_promotion_doc_paths(args.requirements_path):
        base = os.path.basename(pfp)
        pending_doc = read_yaml(pfp)
        req_type = str(pending_doc.get("type") or os.path.splitext(base)[0])

        if req_type == "requirement_change":
            change_affected = apply_requirement_changes(args.requirements_path, pending_doc, to_v, from_v)
            for atype, ids in change_affected.items():
                promoted_counts[atype] = promoted_counts.get(atype, 0) + len(ids)
                promoted_ids.extend(ids)
            pending_doc["items"] = []
            write_yaml(pfp, pending_doc)
            continue

        # Grouped requirement types (nfr_and_global_cr, technology_selection) use
        # per-implementation-id files inside a subfolder rather than a single flat artifact.
        if is_grouped_requirement_type(req_type):
            target_fp = grouped_current_doc_path(
                args.requirements_path, req_type, base, create_dirs=True
            )
            write_yaml(target_fp, pending_doc)
            promoted_counts[req_type] = promoted_counts.get(req_type, 0) + 1
            for it in pending_doc.get("items", []) or pending_doc.get("requirements", []) or []:
                rid = it.get("id") or it.get("requirement_id")
                if rid:
                    promoted_ids.append(str(rid))
            continue

        target_fp = get_artifact_doc_path(args.requirements_path, req_type, create_dirs=True)
        if not os.path.exists(target_fp):
            continue
        target_doc = read_yaml(target_fp)
        merged_doc = merge_pending_doc_into_target(target_doc, pending_doc, to_v, from_v)
        write_yaml(target_fp, merged_doc)
        promoted_counts[req_type] = promoted_counts.get(req_type, 0) + len(pending_doc.get("items", []) or [])
        for it in pending_doc.get("items", []) or []:
            rid = it.get("id")
            if rid:
                promoted_ids.append(str(rid))
        # clear pending collection after promote
        pending_doc["items"] = []
        if "paragraphs" in pending_doc:
            pending_doc["paragraphs"] = []
        write_yaml(pfp, pending_doc)

    control['current_version'] = to_v
    control['next_version'] = bump_patch(to_v)
    control['iteration_id'] = iteration_id
    control['requirement_set_id'] = req_set
    write_yaml(cp, control)
    req_manifest_file = requirements_manifest_path(args.requirements_path)
    req_manifest = read_yaml(req_manifest_file)
    req_manifest["requirement_set_id"] = req_set
    req_manifest["iteration_id"] = iteration_id
    req_manifest["current_version"] = control["current_version"]
    req_manifest["next_version"] = control["next_version"]
    write_yaml(req_manifest_file, req_manifest)

    # Promote contract/model spec definition files to current.
    spec_count = promote_contract_spec_files(args.requirements_path)
    if spec_count:
        promoted_counts["models_and_contracts_specs"] = spec_count

    rebuild_requirement_diffs(args.requirements_path)

    merged = generate_merged(args.requirements_path, req_set)
    write_yaml(merged_path(args.requirements_path), merged)
    write_split_merged(args.requirements_path)
    implementation_ids = [str(t.get("implementation_id")) for t in targets if t.get("implementation_id")]
    if implementation_ids:
        sync_technology_selection_mirrors(args.requirements_path, PENDING_PROMOTION_DIR, implementation_ids)
        sync_technology_selection_mirrors(args.requirements_path, CURRENT_DIR, implementation_ids)
    print('Promoted pending changes and regenerated merged requirements')


if __name__ == '__main__':
    main()
