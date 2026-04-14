#!/usr/bin/env python3
"""Summarize a structured-diff.yaml into concise plain-text output.

Usage:
    python3 summarize_diff.py -r <requirements-path> --implementation-id <id>
    python3 summarize_diff.py --input <path-to-structured-diff.yaml>

Outputs a plain-text summary suitable for agent consumption, including:
  - diff metadata (implementation_id, base_version, target_version)
  - counts for created/updated/removed requirements and MAC items
  - technology selection entry count
  - list of affected requirement IDs with module_changed flags
"""
from typing import Any, Dict, List

from common import (
    build_parser,
    implementation_structured_diff_path,
    read_yaml,
    resolve_target_implementations,
)


def summarize(diff_doc: Dict[str, Any]) -> str:
    lines: List[str] = []

    meta = diff_doc.get("diff_metadata") or {}
    lines.append("=== Diff Summary ===")
    lines.append(f"implementation_id: {meta.get('implementation_id', 'unknown')}")
    lines.append(f"base_version:      {meta.get('base_version', '?')}")
    lines.append(f"target_version:    {meta.get('target_version', '?')}")
    lines.append(f"generated_at:      {meta.get('generated_at', '?')}")
    lines.append("")

    req_diff = diff_doc.get("requirements_diff") or {}
    created = req_diff.get("created") or []
    updated = req_diff.get("updated") or []
    removed = req_diff.get("removed") or []

    lines.append("--- Requirements ---")
    lines.append(f"created: {len(created)}")
    lines.append(f"updated: {len(updated)}")
    lines.append(f"removed: {len(removed)}")
    lines.append("")

    if created:
        lines.append("created_ids:")
        for e in created:
            rid = e.get("requirement_id", "?")
            mod = (e.get("new_requirement") or {}).get("module", "")
            suffix = f"  [module={mod}]" if mod else ""
            lines.append(f"  - {rid}{suffix}")
        lines.append("")

    if updated:
        lines.append("updated_ids:")
        for e in updated:
            rid = e.get("requirement_id", "?")
            old_mod = (e.get("original_requirement") or {}).get("module", "")
            new_mod = (e.get("new_requirement") or {}).get("module", "")
            flags: List[str] = []
            if old_mod and new_mod and old_mod != new_mod:
                flags.append(f"module_changed: {old_mod} -> {new_mod}")
            elif new_mod:
                flags.append(f"module={new_mod}")
            replaces = e.get("replaces_id")
            if replaces:
                flags.append(f"replaces={replaces}")
            suffix = f"  [{', '.join(flags)}]" if flags else ""
            lines.append(f"  - {rid}{suffix}")
        lines.append("")

    if removed:
        lines.append("removed_ids:")
        for e in removed:
            rid = e.get("requirement_id", "?")
            sup = e.get("superseded_by")
            suffix = f"  [superseded_by={sup}]" if sup else ""
            lines.append(f"  - {rid}{suffix}")
        lines.append("")

    mac_diff = diff_doc.get("models_and_contracts_diff") or {}
    mac_created = mac_diff.get("created") or []
    mac_updated = mac_diff.get("updated") or []
    mac_removed = mac_diff.get("removed") or []

    lines.append("--- Models & Contracts ---")
    lines.append(f"created: {len(mac_created)}")
    lines.append(f"updated: {len(mac_updated)}")
    lines.append(f"removed: {len(mac_removed)}")
    lines.append("")

    if mac_created:
        lines.append("mac_created_ids:")
        for e in mac_created:
            lines.append(f"  - {e.get('mac_id', '?')}")
        lines.append("")

    if mac_updated:
        lines.append("mac_updated_ids:")
        for e in mac_updated:
            mid = e.get("mac_id", "?")
            rep = e.get("replaces_id")
            suffix = f"  [replaces={rep}]" if rep else ""
            lines.append(f"  - {mid}{suffix}")
        lines.append("")

    if mac_removed:
        lines.append("mac_removed_ids:")
        for e in mac_removed:
            mid = e.get("mac_id", "?")
            sup = e.get("superseded_by")
            suffix = f"  [superseded_by={sup}]" if sup else ""
            lines.append(f"  - {mid}{suffix}")
        lines.append("")

    ts = diff_doc.get("technology_selection") or {}
    ts_entries = ts.get("entries") or []
    lines.append("--- Technology Selection ---")
    lines.append(f"entries: {len(ts_entries)}")
    if ts_entries:
        lines.append("ts_ids:")
        for e in ts_entries:
            lines.append(f"  - {e.get('id', '?')}")
    lines.append("")

    total = len(created) + len(updated) + len(removed) + len(mac_created) + len(mac_updated) + len(mac_removed) + len(ts_entries)
    lines.append(f"total_diff_items: {total}")

    return "\n".join(lines)


def main() -> None:
    parser = build_parser("Summarize a structured-diff.yaml into plain text")
    parser.add_argument("--input", default=None, help="Direct path to structured-diff.yaml (overrides auto-discovery)")
    args = parser.parse_args()

    if args.input:
        doc = read_yaml(args.input)
        print(summarize(doc))
        return

    targets = resolve_target_implementations(
        args.requirements_path, args.app_path, args.implementation_id, args.all_implementations
    )
    for t in targets:
        imp_id = str(t.get("implementation_id"))
        diff_path = implementation_structured_diff_path(args.requirements_path, imp_id)
        doc = read_yaml(diff_path)
        print(summarize(doc))


if __name__ == "__main__":
    main()
