#!/usr/bin/env python3
"""Rebuild 02-diff files from 03-current artifacts and regenerate merged_requirements.yaml.

Use this when 02-diff files are stale (e.g. after tooling fixes that change
which fields are emitted during normalize_item / extract_requirements_from_yaml).
Equivalent to the rebuild step that promote runs internally, but safe to run
without needing pending items.
"""
import sys
from common import (
    build_parser,
    generate_merged,
    merged_path,
    resolve_target_implementations,
    safe_main,
    validate_target_for_app,
    write_split_merged,
    write_yaml,
)
from promote_changes import rebuild_requirement_diffs


def main() -> None:
    parser = build_parser("Rebuild 02-diff files from 03-current and regenerate merged requirements")
    args = parser.parse_args()
    targets = resolve_target_implementations(
        args.requirements_path, args.app_path, args.implementation_id, args.all_implementations
    )
    req_set = None
    for t in targets:
        req_set, _ = validate_target_for_app(t, args.requirements_path)

    rebuild_requirement_diffs(args.requirements_path)
    merged = generate_merged(args.requirements_path, req_set)
    write_yaml(merged_path(args.requirements_path), merged)
    write_split_merged(args.requirements_path)
    print("Rebuilt 02-diff files and regenerated merged requirements")


if __name__ == "__main__":
    safe_main(main, "rebuild_diffs")
