#!/usr/bin/env python3
import os
import shutil

from common import (
    app_manifest_path,
    build_parser,
    implementation_delta_history_dir,
    implementation_delta_path,
    implementation_manifest_path,
    now_iso,
    read_yaml,
    resolve_target_implementations,
    validate_target_for_app,
    write_yaml,
)


def _baseline_map(app_manifest: dict) -> dict:
    out = {}
    for e in app_manifest.get("requirement_baseline", []) or []:
        if isinstance(e, dict) and e.get("requirement_id"):
            rid = str(e.get("requirement_id"))
            out[rid] = {
                "requirement_id": rid,
                "pinned_version": str(e.get("pinned_version") or ""),
            }
    return out


def main() -> None:
    parser = build_parser("Apply implementation delta to app requirements manifest")
    args = parser.parse_args()
    targets = resolve_target_implementations(
        args.requirements_path, args.app_path, args.implementation_id, args.all_implementations
    )

    for t in targets:
        validate_target_for_app(t, args.requirements_path)
        impl_id = str(t.get("implementation_id"))
        app_path = str(t.get("app_path"))
        delta_file = implementation_delta_path(args.requirements_path, impl_id, create_dirs=True)
        delta = read_yaml(delta_file)
        if not delta:
            print(f"[{impl_id}] No delta file found: {delta_file}")
            continue

        app_manifest_file = app_manifest_path(app_path)
        app_manifest = read_yaml(app_manifest_file)

        baseline_map = _baseline_map(app_manifest)
        existing_ids = set(baseline_map.keys())
        added_items = (
            delta.get("delta", {}).get("added", [])
            if isinstance(delta.get("delta", {}).get("added", []), list)
            else []
        )
        updated_items = (
            delta.get("delta", {}).get("updated", [])
            if isinstance(delta.get("delta", {}).get("updated", []), list)
            else []
        )
        # Conservative default: only IDs explicitly verified as implemented
        # are allowed to move into versioned requirement_baseline entries.
        added_ids = {
            str(x.get("requirement_id"))
            for x in added_items
            if x.get("requirement_id") and x.get("implementation_verified") is True
        }
        updated_ids = {
            str(x.get("requirement_id"))
            for x in updated_items
            if x.get("requirement_id") and x.get("implementation_verified") is True
        }
        unverified_added = {
            str(x.get("requirement_id"))
            for x in added_items
            if x.get("requirement_id") and x.get("implementation_verified") is not True
        }
        unverified_updated = {
            str(x.get("requirement_id"))
            for x in updated_items
            if x.get("requirement_id") and x.get("implementation_verified") is not True
        }
        removed_ids = {str(x.get("requirement_id")) for x in (delta.get("delta", {}).get("removed", []) if isinstance(delta.get("delta", {}).get("removed", []), list) else []) if x.get("requirement_id")}

        next_ids = (existing_ids | added_ids | updated_ids) - removed_ids
        for rid in list(removed_ids):
            baseline_map.pop(rid, None)
        for item in added_items + updated_items:
            rid = item.get("requirement_id")
            if not rid:
                continue
            rid = str(rid)
            if rid not in next_ids:
                continue
            req = item.get("new_requirement") if isinstance(item.get("new_requirement"), dict) else {}
            if not isinstance(req, dict):
                req = {}
            versioning = req.get("versioning") if isinstance(req.get("versioning"), dict) else {}
            pinned = (
                str(versioning.get("updated_on_version") or versioning.get("created_on_version") or "")
                or str(delta.get("requirements_version_target") or "0.0.0")
            )
            baseline_map[rid] = {
                "requirement_id": rid,
                "pinned_version": pinned,
            }
        app_manifest["requirement_baseline"] = [baseline_map[rid] for rid in sorted(baseline_map.keys())]
        app_manifest.pop("implemented_requirement_ids", None)
        target_version = str(delta.get("requirements_version_target") or "")
        if target_version:
            app_manifest["requirements_version_implemented"] = target_version
        if delta.get("iteration_id") is not None:
            app_manifest["iteration_id"] = delta.get("iteration_id")

        write_yaml(app_manifest_file, app_manifest)

        history_dir = implementation_delta_history_dir(args.requirements_path, impl_id, create_dirs=True)
        stamp = now_iso().replace(":", "").replace("-", "")
        shutil.copy2(delta_file, os.path.join(history_dir, f"{stamp}-01-delta-current.yaml"))

        impl_manifest_file = implementation_manifest_path(args.requirements_path, impl_id, create_dirs=True)
        impl_manifest = read_yaml(impl_manifest_file)
        impl_manifest["last_applied_at"] = now_iso()
        impl_manifest["requirements_version_implemented"] = app_manifest.get("requirements_version_implemented")
        impl_manifest["baseline_requirement_ids_count"] = len(next_ids)
        write_yaml(impl_manifest_file, impl_manifest)

        print(
            f"[{impl_id}] Applied delta to {app_manifest_file} "
            f"(baseline_ids={len(next_ids)}, version_implemented={app_manifest.get('requirements_version_implemented')})"
        )
        if unverified_added or unverified_updated:
            print(
                f"[{impl_id}] Skipped unverified requirement IDs "
                f"(added={len(unverified_added)}, updated={len(unverified_updated)}). "
                "Set implementation_verified=true per delta item to include."
            )


if __name__ == "__main__":
    main()
