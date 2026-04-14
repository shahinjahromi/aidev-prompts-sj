# IM-01 Diff
Inputs: IMPLEMENTATION_ID, TOOLING_CMD, REQ_PATH.
Action: run "$TOOLING_CMD" diff -r "$REQ_PATH" --implementation-id "$IMPLEMENTATION_ID".
Output: IMPL_ROOT/01-delta-current/structured-diff.yaml.
Report: created/updated/removed/technology_selection counts and IDs.

Module-change detection:
- For each `updated` entry, compare the `module` field between current and manifest baseline.
- If a requirement's `module` value changed (including from absent to present, present to absent, or value A to value B), flag it as `module_changed: true` in the diff report.
- Include a summary line: "Module reassignments: N" with the affected requirement IDs.

## Narration
- On entry: `[IM-01] Diff started at <timestamp>`
- Before script: `[IM-01] Script start: ai-tooling.sh diff`
- After script: `[IM-01] Script end: ai-tooling.sh diff (exit: <code>, elapsed: <N>s)`
- On error: `[IM-01] ERROR: Diff script failed — <details>`
- On unexpected: `[IM-01] **UNEXPECTED: <details>**`
- On exit: `[IM-01] Diff completed at <timestamp> (elapsed: <N>s) — created: N, updated: N, removed: N`
