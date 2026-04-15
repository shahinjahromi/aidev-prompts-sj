#!/usr/bin/env bash
set -euo pipefail

# Backup VS Code user prompts (Linux) into this template's github-config directory.
# Safe behavior:
# - Resolves paths from this script location (independent of current working directory)
# - Uses explicit absolute target path for deletion (no "cd ... && rm ...")
# - Deletes only contents of target directory, not the directory itself

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${SCRIPT_DIR}/../user-prompts-content"
SOURCE_DIR="${HOME}/.config/Code/User/prompts"

# Normalize paths for strict comparisons
mkdir -p "${TARGET_DIR}"
TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"
SOURCE_DIR="$(cd "${SOURCE_DIR}" && pwd)"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "ERROR: Source prompts directory does not exist: ${SOURCE_DIR}"
  exit 1
fi

if [[ "${SOURCE_DIR}" == "${TARGET_DIR}" ]]; then
  echo "ERROR: Source and target directories are the same path. Aborting."
  exit 1
fi

# Additional guard to avoid accidental broad deletions.
if [[ "${TARGET_DIR}" != */framework-ai-blueprint-template-v2/user-prompts-content ]]; then
  echo "ERROR: Refusing to operate on unexpected target path: ${TARGET_DIR}"
  exit 1
fi

echo "Source: ${SOURCE_DIR}"
echo "Target: ${TARGET_DIR}"

echo "Clearing target contents..."
find "${TARGET_DIR}" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +

echo "Copying prompts folder into target..."
# Copies full source contents directly into ${TARGET_DIR}.
cp -a "${SOURCE_DIR}/." "${TARGET_DIR}/"

source_count="$(find "${SOURCE_DIR}" -type f | wc -l | tr -d ' ')"
target_count="$(find "${TARGET_DIR}" -type f | wc -l | tr -d ' ')"

echo "Done."
echo "Source files: ${source_count}"
echo "Target files: ${target_count}"

echo "Backup location: ${TARGET_DIR}"
