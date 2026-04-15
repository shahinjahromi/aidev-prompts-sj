#!/usr/bin/env bash
set -euo pipefail

# Restore VS Code user prompts (Linux) from this template's github-config/backup-prompts.
# Safe behavior:
# - Copies backup prompts INTO the VS Code user prompts folder (additive/merge only)
# - Does NOT delete any prompts that already exist in the VS Code user prompts folder
# - Existing files with the same name will be overwritten with the backed-up version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../user-prompts-content"
TARGET_DIR="${HOME}/.config/Code/User/prompts"

# Normalize source path
SOURCE_DIR="$(cd "${SOURCE_DIR}" && pwd)"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "ERROR: Backup prompts directory does not exist: ${SOURCE_DIR}"
  exit 1
fi

# Guard against restoring from unexpected source path
if [[ "${SOURCE_DIR}" != */framework-ai-blueprint-template-v2/user-prompts-content ]]; then
  echo "ERROR: Refusing to restore from unexpected source path: ${SOURCE_DIR}"
  exit 1
fi

# Create VS Code prompts folder if it does not exist
if [[ ! -d "${TARGET_DIR}" ]]; then
  echo "Creating VS Code prompts directory: ${TARGET_DIR}"
  mkdir -p "${TARGET_DIR}"
fi

echo "Source (backup): ${SOURCE_DIR}"
echo "Target (VS Code prompts): ${TARGET_DIR}"
echo "Restoring prompts (merge - no deletions)..."

# Copy all files from backup into VS Code prompts folder.
# Existing files in the target that are NOT in the backup are left untouched.
while IFS= read -r -d '' src_file; do
  relative="${src_file#${SOURCE_DIR}/}"
  dest_file="${TARGET_DIR}/${relative}"
  dest_dir="$(dirname "${dest_file}")"

  if [[ ! -d "${dest_dir}" ]]; then
    mkdir -p "${dest_dir}"
  fi

  cp -f -- "${src_file}" "${dest_file}"
  echo "  Restored: ${relative}"
done < <(find "${SOURCE_DIR}" -type f -print0)

source_count="$(find "${SOURCE_DIR}" -type f | wc -l | tr -d ' ')"
target_count="$(find "${TARGET_DIR}" -type f | wc -l | tr -d ' ')"

echo "Done."
echo "Files restored from backup: ${source_count}"
echo "Total files now in VS Code prompts: ${target_count}"
echo "Restore location: ${TARGET_DIR}"
