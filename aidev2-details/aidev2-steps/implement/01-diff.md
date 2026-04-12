# IM-01 Diff
Inputs: IMPLEMENTATION_ID, TOOLING_CMD, REQ_PATH.
Action: run "$TOOLING_CMD" diff -r "$REQ_PATH" --implementation-id "$IMPLEMENTATION_ID".
Output: IMPL_ROOT/01-delta-current/structured-diff.yaml.
Report: created/updated/removed/technology_selection counts and IDs.

Module-change detection:
- For each `updated` entry, compare the `module` field between current and manifest baseline.
- If a requirement's `module` value changed (including from absent to present, present to absent, or value A to value B), flag it as `module_changed: true` in the diff report.
- Include a summary line: "Module reassignments: N" with the affected requirement IDs.
