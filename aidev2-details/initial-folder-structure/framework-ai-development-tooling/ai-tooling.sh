#!/usr/bin/env bash
set -euo pipefail

ROOT="/media/psf/z-work-ai-enablement/projects/ai-development-tooling"

if [ $# -lt 1 ]; then
  echo "Usage: ai-tooling.sh <action> [args]"
  echo "Actions: bootstrap delta plan apply merge update-merged refresh-merged diff promote sync-diff all"
  exit 1
fi

action="$1"
shift

case "$action" in
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
  all)
    # all means delta + plan + merge + diff
    python3 "$ROOT/generate_pending_for_implementation.py" "$@"
    python3 "$ROOT/generate_plan_for_implementation.py" "$@"
    python3 "$ROOT/merge_requirements.py" "$@"
    python3 "$ROOT/generate_structured_diff.py" "$@"
    ;;
  *)
    echo "Unknown action: $action"
    exit 1
    ;;
esac
