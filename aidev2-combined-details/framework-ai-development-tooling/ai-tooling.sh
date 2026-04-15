#!/usr/bin/env bash
set -euo pipefail

# Resolve tooling root from this script location by default.
# Allow override for advanced environments.
ROOT="${AI_TOOLING_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

print_usage() {
  cat <<EOF
Usage: ai-tooling.sh <action> [args]
Actions: bootstrap delta plan apply merge update-merged refresh-merged diff promote sync-diff summarize-diff verify repair-yaml all
EOF
}

if [ $# -lt 1 ]; then
  print_usage
  exit 1
fi

action="$1"
shift

case "$action" in
  -h|--help|help)
    print_usage
    ;;
  bootstrap)
    python3 "$ROOT/bootstrap.py" "$@"
    ;;
  merge|update-merged|refresh-merged)
    python3 "$ROOT/merge_requirements.py" "$@"
    ;;
  delta|pending)
    python3 "$ROOT/generate_pending_for_implementation.py" "$@"
    ;;
  plan)
    python3 "$ROOT/generate_plan_for_implementation.py" "$@"
    ;;
  apply)
    python3 "$ROOT/apply_delta_to_app.py" "$@"
    ;;
  diff)
    python3 "$ROOT/generate_structured_diff.py" "$@"
    ;;
  promote)
    python3 "$ROOT/promote_changes.py" "$@"
    ;;
  sync-diff)
    python3 "$ROOT/sync_diff_from_current.py" "$@"
    ;;
  summarize-diff)
    python3 "$ROOT/summarize_diff.py" "$@"
    ;;
  verify)
    python3 "$ROOT/verify_execution_complete.py" "$@"
    ;;
  repair-yaml)
    python3 "$ROOT/repair_yaml.py" "$@"
    ;;
  all)
    # all means delta + plan + merge + diff
    python3 "$ROOT/generate_pending_for_implementation.py" "$@"
    python3 "$ROOT/generate_plan_for_implementation.py" "$@"
    python3 "$ROOT/merge_requirements.py" "$@"
    python3 "$ROOT/generate_structured_diff.py" "$@"
    ;;
  *)
    echo "Unknown action: $action"
    print_usage
    exit 1
    ;;
esac
