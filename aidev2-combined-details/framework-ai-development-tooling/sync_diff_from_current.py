#!/usr/bin/env python3
"""Sync diff files from current requirements.

Scans 03-current/ for all requirements and creates diff entries in 02-diff/
for any that are missing. This is used after backporting requirements directly
to current (e.g. step 8 technology-selection backfill) to keep the diff
directory consistent without a full rebuild.

Naming convention enforced:
  02-diff/<bucket>/<REQUIREMENT_ID>.yaml

Buckets:
  functional/             → FR-NNNNNN
  non_functional/         → NFR-NNNNNN
  technology_selection/   → TS-*
  models_and_contracts/   → MAC-*

Usage:
  python3 sync_diff_from_current.py -r <requirements_path>
  ai-tooling.sh sync-diff -r <requirements_path>
"""
import os
from typing import Dict, Set

from bootstrap_core import extract_requirements_from_yaml, pick_bucket
from common import (
    build_parser,
    DIFF_BUCKETS_BY_ARTIFACT_TYPE,
    DIFF_DIR,
    get_artifact_doc_path,
    get_diff_files,
    now_iso,
    read_yaml,
    safe_main,
    write_yaml,
)


def collect_existing_diff_ids(requirements_path: str) -> Set[str]:
    """Return the set of requirement IDs that already have a diff file."""
    ids: Set[str] = set()
    for fp in get_diff_files(requirements_path):
        raw = read_yaml(fp)
        rid = raw.get("requirement_id")
        if rid:
            ids.add(str(rid))
    return ids


def collect_current_requirements(requirements_path: str) -> Dict[str, dict]:
    """Return {requirement_id: requirement_dict} for every item in 03-current/."""
    out: Dict[str, dict] = {}
    for req_type in DIFF_BUCKETS_BY_ARTIFACT_TYPE:
        src = get_artifact_doc_path(requirements_path, req_type, create_dirs=False)
        if not os.path.exists(src):
            continue
        for req in extract_requirements_from_yaml(src):
            rid = req.get("requirement_id")
            if rid:
                out[str(rid)] = req
    return out


def create_diff_entry(requirements_path: str, req: dict) -> str:
    """Create a single diff file for a requirement. Returns the output path."""
    req_type = req.get("artifact_type") or req.get("type", "functional")
    bucket = DIFF_BUCKETS_BY_ARTIFACT_TYPE.get(req_type) or pick_bucket(req_type)
    rid = str(req["requirement_id"])
    version = (req.get("versioning") or {}).get("updated_on_version") or (
        req.get("updated_version")
    )
    fp = os.path.join(requirements_path, DIFF_DIR, bucket, f"{rid}.yaml")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    write_yaml(
        fp,
        {
            "requirement_id": rid,
            "diffs": [
                {
                    "seq": 1,
                    "op": "create",
                    "version": version,
                    "at": now_iso(),
                    "requirement": req,
                }
            ],
        },
    )
    return fp


def main() -> None:
    parser = build_parser(
        "Sync diff files: create 02-diff/ entries for requirements in "
        "03-current/ that are missing from the diff directory"
    )
    args = parser.parse_args()
    requirements_path = os.path.join(
        args.requirements_path, "01-requirements"
    ) if not args.requirements_path.rstrip("/\\").endswith("01-requirements") else args.requirements_path

    existing_ids = collect_existing_diff_ids(requirements_path)
    current_reqs = collect_current_requirements(requirements_path)
    missing_ids = set(current_reqs.keys()) - existing_ids
    if not missing_ids:
        print("All current requirements already have diff entries. Nothing to sync.")
        return

    created = []
    for rid in sorted(missing_ids):
        fp = create_diff_entry(requirements_path, current_reqs[rid])
        created.append((rid, fp))
        print(f"  Created diff: {fp}")

    print(f"\nSynced {len(created)} missing diff file(s).")


if __name__ == "__main__":
    safe_main(main, 'sync_diff_from_current')
