# IM-01 Diff
Inputs: IMPLEMENTATION_ID, TOOLING_CMD, REQ_PATH.
Action: run "$TOOLING_CMD" diff -r "$REQ_PATH" --implementation-id "$IMPLEMENTATION_ID".
Output: IMPL_ROOT/01-delta-current/structured-diff.yaml.
Report: created/updated/removed/technology_selection counts and IDs.
