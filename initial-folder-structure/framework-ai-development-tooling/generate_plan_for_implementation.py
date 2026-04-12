#!/usr/bin/env python3
import os
import shutil

from common import (
    build_parser,
    implementation_delta_path,
    implementation_manifest_path,
    implementation_plan_current_dir,
    implementation_plan_dir,
    implementation_plan_history_dir,
    now_iso,
    read_yaml,
    resolve_target_implementations,
    validate_target_for_app,
    write_yaml,
)


def write_plan(requirements_path: str, implementation_id: str) -> None:
    delta = read_yaml(implementation_delta_path(requirements_path, implementation_id, create_dirs=True))
    manifest = read_yaml(implementation_manifest_path(requirements_path, implementation_id, create_dirs=True))
    generated_at = delta.get("generated_at") or now_iso()
    summary = delta.get("summary") or {}

    history_dir = implementation_plan_history_dir(requirements_path, implementation_id, create_dirs=True)
    current_dir = implementation_plan_current_dir(requirements_path, implementation_id, create_dirs=True)
    generic_dir = implementation_plan_dir(requirements_path, implementation_id, create_dirs=True)
    current_plan_path = os.path.join(current_dir, "current-plan.md")
    if os.path.exists(current_plan_path):
        stamp = now_iso().replace(":", "").replace("-", "")
        shutil.copy2(current_plan_path, os.path.join(history_dir, f"{stamp}-current-plan.md"))

    plan_md = "\n".join(
        [
            f"# Current Plan: {implementation_id}",
            "",
            f"- Generated at: {generated_at}",
            f"- Iteration: {manifest.get('iteration_id')}",
            f"- Requirements target version: {manifest.get('requirements_version_target')}",
            f"- Requirements implemented version: {manifest.get('requirements_version_implemented')}",
            "",
            "## Delta Summary",
            f"- Added: {summary.get('added', 0)}",
            f"- Updated: {summary.get('updated', 0)}",
            f"- Removed: {summary.get('removed', 0)}",
            "",
            "## Execution",
            "1. Implement each requirement in delta.added.",
            "2. Update behavior for each requirement in delta.updated based on replacement details.",
            "3. Remove/deprecate items in delta.removed if still present in code.",
            "4. Validate tests and contracts for impacted artifacts.",
            "5. Run apply command to update app manifest state after implementation.",
        ]
    )
    with open(current_plan_path, "w", encoding="utf-8") as f:
        f.write(plan_md + "\n")
    with open(os.path.join(generic_dir, "plan.md"), "w", encoding="utf-8") as f:
        f.write(plan_md + "\n")

    plan_manifest = {
        "generated_at": generated_at,
        "implementation_id": implementation_id,
        "iteration_id": manifest.get("iteration_id"),
        "requirements_version_target": manifest.get("requirements_version_target"),
        "requirements_version_implemented": manifest.get("requirements_version_implemented"),
        "delta_file": "02-delta-history/01-delta-current.yaml",
        "current_plan_file": "03-ai-plan-current/current-plan.md",
    }
    write_yaml(os.path.join(current_dir, "requirements-version-manifest.yaml"), plan_manifest)


def main() -> None:
    parser = build_parser("Generate implementation plan files from current delta")
    args = parser.parse_args()
    targets = resolve_target_implementations(
        args.requirements_path, args.app_path, args.implementation_id, args.all_implementations
    )
    for t in targets:
        validate_target_for_app(t, args.requirements_path)
        impl_id = str(t.get("implementation_id"))
        write_plan(args.requirements_path, impl_id)
        print(f"[{impl_id}] Plan files generated")


if __name__ == "__main__":
    main()
