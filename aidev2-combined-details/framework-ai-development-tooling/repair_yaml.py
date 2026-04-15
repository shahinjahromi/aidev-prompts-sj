#!/usr/bin/env python3
"""Repair YAML files: replace tabs with spaces, normalise indentation,
strip trailing whitespace, and validate parseability.

Usage:
    python3 repair_yaml.py <path> [--check]

<path> can be a single YAML file or a directory (recursed for *.yaml / *.yml).
With --check the script only reports problems and exits non-zero if any are found.
"""

import argparse
import os
import re
import sys

import yaml


def find_yaml_files(path: str):
    if os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        for root, _dirs, files in os.walk(path):
            for f in sorted(files):
                if f.endswith((".yaml", ".yml")):
                    yield os.path.join(root, f)
    else:
        print(f"ERROR: path not found: {path}", file=sys.stderr)
        sys.exit(1)


def repair_text(text: str):
    """Return (repaired_text, list_of_fixes_applied)."""
    fixes = []

    # 1. Replace tabs with 2 spaces
    if "\t" in text:
        text = text.replace("\t", "  ")
        fixes.append("replaced tabs with spaces")

    # 2. Strip trailing whitespace on each line
    lines = text.split("\n")
    stripped = [line.rstrip() for line in lines]
    if stripped != lines:
        fixes.append("stripped trailing whitespace")
    text = "\n".join(stripped)

    # 3. Ensure file ends with exactly one newline
    text = text.rstrip("\n") + "\n"

    return text, fixes


def validate_yaml(text: str, path: str):
    """Try to parse YAML; return error message or None."""
    try:
        yaml.safe_load(text)
        return None
    except yaml.YAMLError as exc:
        return f"{path}: YAML parse error: {exc}"


def main():
    parser = argparse.ArgumentParser(description="Repair and validate YAML files.")
    parser.add_argument("path", help="File or directory to process.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report problems only; do not modify files.",
    )
    args = parser.parse_args()

    files_checked = 0
    files_repaired = 0
    errors = []

    for fpath in find_yaml_files(args.path):
        files_checked += 1
        with open(fpath, "r", encoding="utf-8") as f:
            original = f.read()

        repaired, fixes = repair_text(original)

        parse_err = validate_yaml(repaired, fpath)
        if parse_err:
            errors.append(parse_err)
            # Still write the whitespace-cleaned version if not in check mode
            # so at least formatting is better, but report the error.

        if fixes:
            if args.check:
                print(f"NEEDS REPAIR: {fpath} — {', '.join(fixes)}")
            else:
                with open(fpath, "w", encoding="utf-8", newline="\n") as f:
                    f.write(repaired)
                print(f"REPAIRED: {fpath} — {', '.join(fixes)}")
                files_repaired += 1
        else:
            # Even if no whitespace fixes, write if we need to normalise the trailing newline
            if repaired != original and not args.check:
                with open(fpath, "w", encoding="utf-8", newline="\n") as f:
                    f.write(repaired)

    print(f"\nSummary: {files_checked} file(s) checked, {files_repaired} repaired, {len(errors)} parse error(s).")
    for err in errors:
        print(f"  ERROR: {err}", file=sys.stderr)

    if errors or (args.check and files_repaired == 0 and files_checked > 0):
        # In check mode exit non-zero only when there are actual problems
        pass

    if errors:
        sys.exit(1)
    if args.check:
        # Exit non-zero if any file needs repair
        for fpath in find_yaml_files(args.path):
            with open(fpath, "r", encoding="utf-8") as f:
                original = f.read()
            _, fixes = repair_text(original)
            if fixes:
                sys.exit(1)


from common import safe_main

if __name__ == "__main__":
    safe_main(main, 'repair_yaml')
