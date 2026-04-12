#!/usr/bin/env bash
set -euo pipefail

# Ensures that required agent configuration files exist in this specs repo.
# Run this after cloning or after adding a new implementation_id.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="${ROOT_DIR}/02-implementation"
CURSOR_DIR="${ROOT_DIR}/.cursor"
RULES_DIR="${CURSOR_DIR}/rules"

mkdir -p "${RULES_DIR}" "${STATE_DIR}"

if [[ ! -f "${CURSOR_DIR}/agent-config.yaml" ]]; then
  echo "WARN: .cursor/agent-config.yaml is missing. Copy from template."
else
  echo "OK: .cursor/agent-config.yaml exists"
fi

if [[ ! -f "${RULES_DIR}/000-planning-memory-history.mdc" ]]; then
  echo "WARN: .cursor/rules/000-planning-memory-history.mdc is missing. Copy from template."
else
  echo "OK: .cursor/rules/000-planning-memory-history.mdc exists"
fi

echo ""
echo "Checking implementation directories..."

IMPL_DIR="${STATE_DIR}/01-implementations"
if [[ -d "${IMPL_DIR}" ]]; then
  for impl_path in "${IMPL_DIR}"/*/; do
    impl_id=$(basename "$impl_path")
    [[ "$impl_id" == "__IMPL_ID__" ]] && continue
    echo "  Implementation: ${impl_id}"
    for subdir in 01-delta-current 02-plan-current 03-plan-execution 04-extract-library-interfaces 05-fix 06-e2e-tests 50-delta-history 51-plan-history 52-plan-execution-history 53-update-history; do
      mkdir -p "${impl_path}/${subdir}"
    done
    echo "    Subdirectories: OK"
  done
else
  echo "  No implementations found yet."
fi

echo ""
echo "Done."
