#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

import yaml

from common import implementation_structured_diff_path, read_yaml


TOOLING_DIR = Path(__file__).resolve().parent
UTAH_TZ = "America/Denver"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate structured diff and fail if any requirements remain unimplemented."
    )
    parser.add_argument("-r", "--requirements-path", required=True)
    parser.add_argument("-a", "--app-path", required=True)
    parser.add_argument("--implementation-id", required=True)
    parser.add_argument("--results-path", default=None)
    return parser.parse_args()


def requirement_ids(items: List[Dict[str, Any]]) -> List[str]:
    return [str(item.get("requirement_id")) for item in items if item.get("requirement_id")]


def technology_selection_ids(items: List[Dict[str, Any]]) -> List[str]:
    return [str(item.get("id")) for item in items if item.get("id")]


def utah_now_str() -> str:
    return datetime.now(ZoneInfo(UTAH_TZ)).isoformat() + f" {UTAH_TZ}"


def load_results(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_results(
    path: Path,
    start_datetime: str,
    end_datetime: str,
    total_diffs: int,
    implemented_diffs: int,
    remaining_diffs: int,
    status: str,
    blockers: List[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "total_diffs": total_diffs,
        "implemented_diffs": implemented_diffs,
        "remaining_diffs": remaining_diffs,
        "status": status,
        "blockers": blockers,
    }
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def main() -> int:
    args = parse_args()

    cmd = [
        sys.executable,
        str(TOOLING_DIR / "generate_structured_diff.py"),
        "-r",
        args.requirements_path,
        "-a",
        args.app_path,
        "--implementation-id",
        args.implementation_id,
    ]
    result = subprocess.run(cmd, cwd=str(TOOLING_DIR))
    if result.returncode != 0:
        return result.returncode

    diff_path = implementation_structured_diff_path(
        args.requirements_path, args.implementation_id, create_dirs=False
    )
    doc = read_yaml(diff_path)
    req_diff = doc.get("requirements_diff") or {}
    created = req_diff.get("created") or []
    updated = req_diff.get("updated") or []
    removed = req_diff.get("removed") or []
    technology_selection_entries = (doc.get("technology_selection") or {}).get("entries") or []
    remaining = len(created) + len(updated) + len(removed) + len(technology_selection_entries)

    results_path = Path(args.results_path) if args.results_path else None
    now = utah_now_str()
    if results_path:
        previous = load_results(results_path)
        starting_total = int(previous.get("total_diffs", remaining) or remaining)
        start_datetime = str(previous.get("start_datetime") or now)
        implemented = max(starting_total - remaining, 0)
        blockers: List[str] = []
        if created or updated or removed or technology_selection_entries:
            blockers.append("Execution has not yet implemented all remaining diff items.")
            blockers.append("Verification still reports remaining requirements in structured-diff.yaml.")
            if technology_selection_entries:
                blockers.append(
                    "Verification still reports remaining technology_selection entries in structured-diff.yaml."
                )
        write_results(
            results_path,
            start_datetime=start_datetime,
            end_datetime=now,
            total_diffs=starting_total,
            implemented_diffs=implemented,
            remaining_diffs=remaining,
            status="complete" if remaining == 0 else "incomplete",
            blockers=blockers,
        )

    if not created and not updated and not removed and not technology_selection_entries:
        print(
            "Execution complete: no remaining created, updated, removed, or technology_selection diff items."
        )
        return 0

    print("Execution incomplete: remaining requirements still exist in structured diff.")
    if created:
        print(f"created ({len(created)}): {', '.join(requirement_ids(created))}")
    if updated:
        print(f"updated ({len(updated)}): {', '.join(requirement_ids(updated))}")
    if removed:
        print(f"removed ({len(removed)}): {', '.join(requirement_ids(removed))}")
    if technology_selection_entries:
        print(
            f"technology_selection ({len(technology_selection_entries)}): "
            f"{', '.join(technology_selection_ids(technology_selection_entries))}"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
