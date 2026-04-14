#!/usr/bin/env python3
import os
import shutil
from typing import Any, Dict, List, Optional

from common import (
    DEFAULT_ITERATION_ID,
    app_manifest_path,
    apply_diff_sequence,
    build_parser,
    compare_versions,
    get_app_baseline_requirement_ids,
    get_app_iteration_id,
    get_app_manifest,
    get_diff_files,
    implementation_delta_history_dir,
    implementation_delta_path,
    implementation_dir,
    implementation_manifest_path,
    merge_scopes,
    merged_path,
    normalize_iteration_id,
    now_iso,
    read_yaml,
    resolve_scope_for_requirement,
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


def main() -> None:
    parser = build_parser("Generate per-implementation delta state")
    args = parser.parse_args()

    targets = resolve_target_implementations(
        args.requirements_path, args.app_path, args.implementation_id, args.all_implementations
    )
    current_map = load_current_requirements(args.requirements_path)
    merged = read_yaml(merged_path(args.requirements_path))
    merged_version = str(merged.get("requirements_version") or "0.0.0")

    for t in targets:
        app_path = t["app_path"]
        validate_target_for_app(t, args.requirements_path)
        implementation_id = str(t.get("implementation_id"))
        manifest = get_app_manifest(app_path)
        # Requirements version comes from the requirements repo (merged/control), not the app manifest.
        latest_version = str(merged_version or "0.0.0")
        baseline_ids = set(get_app_baseline_requirement_ids(app_path))
        # Delta compares current requirements against versioned baseline requirements.
        effective_implemented_ids = baseline_ids
        current_iteration = get_app_iteration_id(app_path)
        implemented_version = str(manifest.get("requirements_version_implemented") or "0.0.0")
        explicit_targets = manifest.get("app_requirement_ids")
        explicit_target_ids = set(str(x) for x in explicit_targets) if isinstance(explicit_targets, list) else set()
        previous_snapshot_map = build_previous_snapshot_map(args.requirements_path, implemented_version)
        tracked_requirement_ids = set(current_map.keys()) | set(previous_snapshot_map.keys())
        comparable_implemented_ids = effective_implemented_ids & tracked_requirement_ids
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
        current_ids = set(eligible_current_map.keys())
        # Delta should represent all differences against already-implemented state.
        # Compare only within tooling-tracked requirement IDs to avoid false removals
        # for legacy/non-tracked artifact IDs in app manifests.
        removed_ids = sorted(comparable_implemented_ids - current_ids)

        added: List[Dict[str, Any]] = []
        updated: List[Dict[str, Any]] = []
        unchanged: List[str] = []
        considered = 0

        replaces_id_map: Dict[str, str] = {}
        for rid, req in eligible_current_map.items():
            rep = req.get("replaces_id")
            if rep:
                replaces_id_map[str(rep)] = rid

        for rid, req in sorted(eligible_current_map.items()):
            considered += 1
            updated_on_version = str(
                (req.get("versioning") or {}).get("updated_on_version") or latest_version
            )
            replaces_id = req.get("replaces_id")
            if rid not in comparable_implemented_ids:
                if replaces_id and str(replaces_id) in comparable_implemented_ids:
                    entry = {
                        "requirement_id": rid,
                        "replaces_id": str(replaces_id),
                        "artifact_type": req.get("artifact_type"),
                        "implementation_verified": False,
                        "scope": resolve_scope_for_requirement(
                            args.requirements_path, implementation_id, req.get("traceability")
                        ),
                        "original_requirement": previous_snapshot_map.get(str(replaces_id))
                        or extract_baseline_entry(manifest, str(replaces_id)),
                        "new_requirement": req,
                        "replaces": {
                            "previous_requirement": previous_snapshot_map.get(str(replaces_id)),
                            "baseline": extract_baseline_entry(manifest, str(replaces_id)),
                            "implemented_version": implemented_version,
                        },
                    }
                    updated.append(entry)
                else:
                    entry = {
                        "requirement_id": rid,
                        "artifact_type": req.get("artifact_type"),
                        "implementation_verified": False,
                        "scope": resolve_scope_for_requirement(
                            args.requirements_path, implementation_id, req.get("traceability")
                        ),
                        "new_requirement": req,
                    }
                    if replaces_id:
                        entry["replaces_id"] = str(replaces_id)
                    added.append(entry)
            elif compare_versions(updated_on_version, implemented_version) > 0:
                entry = {
                    "requirement_id": rid,
                    "artifact_type": req.get("artifact_type"),
                    "implementation_verified": False,
                    "scope": resolve_scope_for_requirement(
                        args.requirements_path, implementation_id, req.get("traceability")
                    ),
                    "original_requirement": previous_snapshot_map.get(rid)
                    or extract_baseline_entry(manifest, rid),
                    "new_requirement": req,
                    "replaces": {
                        "previous_requirement": previous_snapshot_map.get(rid),
                        "baseline": extract_baseline_entry(manifest, rid),
                        "implemented_version": implemented_version,
                    },
                }
                if replaces_id:
                    entry["replaces_id"] = str(replaces_id)
                updated.append(entry)
            else:
                unchanged.append(rid)

        removed_payload: List[Dict[str, Any]] = []
        for rid in removed_ids:
            superseded_by = replaces_id_map.get(rid)
            entry = {
                "requirement_id": rid,
                "scope": resolve_scope_for_requirement(
                    args.requirements_path,
                    implementation_id,
                    (previous_snapshot_map.get(rid) or {}).get("traceability"),
                ),
                "replaces": {
                    "previous_requirement": previous_snapshot_map.get(rid),
                    "baseline": extract_baseline_entry(manifest, rid),
                    "implemented_version": implemented_version,
                },
            }
            if superseded_by:
                entry["superseded_by"] = superseded_by
            removed_payload.append(entry)

        # Enforce scope presence on every delta item.
        # If a future code path forgets scope, fall back to implementation global scope.
        for item in added:
            scope = item.get("scope")
            if not isinstance(scope, dict):
                item["scope"] = resolve_scope_for_requirement(
                    args.requirements_path, implementation_id, (item.get("new_requirement") or {}).get("traceability")
                )
        for item in updated:
            scope = item.get("scope")
            if not isinstance(scope, dict):
                item["scope"] = resolve_scope_for_requirement(
                    args.requirements_path, implementation_id, (item.get("new_requirement") or {}).get("traceability")
                )
        for item in removed_payload:
            scope = item.get("scope")
            if not isinstance(scope, dict):
                fallback_prev = ((item.get("replaces") or {}).get("previous_requirement") or {})
                item["scope"] = resolve_scope_for_requirement(
                    args.requirements_path, implementation_id, fallback_prev.get("traceability")
                )

        delta_doc = {
            "generated_at": now_iso(),
            "app_manifest_state": {
                "requirement_set_id": manifest.get("requirement_set_id"),
                "implementation_id": implementation_id,
                "iteration_id": current_iteration,
                "requirements_version_implemented": implemented_version,
                "baseline_requirement_ids_count": len(baseline_ids),
                "implemented_baseline_ids_count": len(effective_implemented_ids),
                "comparable_implemented_ids_count": len(comparable_implemented_ids),
            },
            "requirement_set_id": manifest.get("requirement_set_id"),
            "implementation_id": implementation_id,
            "app_manifest_path": app_manifest_path(app_path),
            "iteration_id": current_iteration,
            "requirements_version_implemented": implemented_version,
            "requirements_version_target": latest_version,
            "requirements_version_latest": latest_version,
            "summary": {
                "considered": considered,
                "added": len(added),
                "updated": len(updated),
                "removed": len(removed_payload),
                "unchanged": len(unchanged),
            },
            "scope": merge_scopes(
                [x.get("scope") for x in added] + [x.get("scope") for x in updated] + [x.get("scope") for x in removed_payload]
            ),
            "delta": {
                "added": added,
                "updated": updated,
                "removed": removed_payload,
            },
        }

        implementation_dir(args.requirements_path, implementation_id, create_dirs=True)
        delta_out = implementation_delta_path(args.requirements_path, implementation_id, create_dirs=True)
        if os.path.exists(delta_out):
            history_dir = implementation_delta_history_dir(
                args.requirements_path, implementation_id, create_dirs=True
            )
            stamp = now_iso().replace(":", "").replace("-", "")
            shutil.copy2(delta_out, os.path.join(history_dir, f"{stamp}-01-delta-current.yaml"))
        write_yaml(delta_out, delta_doc)

        write_yaml(
            implementation_manifest_path(args.requirements_path, implementation_id, create_dirs=True),
            {
                "implementation_id": implementation_id,
                "app_identifier": manifest.get("app_identifier"),
                "app_path": app_path,
                "app_manifest_path": app_manifest_path(app_path),
                "last_generated_at": delta_doc["generated_at"],
                "requirement_set_id": manifest.get("requirement_set_id"),
                "iteration_id": current_iteration,
                "requirements_version_target": latest_version,
                "requirements_version_implemented": implemented_version,
                "baseline_requirement_ids_count": len(effective_implemented_ids),
                "comparable_implemented_ids_count": len(comparable_implemented_ids),
                "delta_file": "02-delta-history/01-delta-current.yaml",
                "delta_history_dir": "02-delta-history",
                "plan_current_dir": "03-ai-plan-current",
                "plan_history_dir": "04-ai-plan-history",
                "plan_dir": "05-ai-plan",
            },
        )

        print(
            f"[{implementation_id}] Generated delta in "
            f"{implementation_dir(args.requirements_path, implementation_id)} "
            f"(added={len(added)}, updated={len(updated)}, removed={len(removed_payload)})"
        )


if __name__ == "__main__":
    main()

