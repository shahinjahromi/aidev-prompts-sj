# IM-01 Diff
Inputs: IMPLEMENTATION_ID, TOOLING_CMD, REQ_PATH.
Action: run "$TOOLING_CMD" diff -r "$REQ_PATH" --implementation-id "$IMPLEMENTATION_ID".
Output: IMPL_ROOT/01-delta-current/structured-diff.yaml.
Report: created/updated/removed/technology_selection counts and IDs.

## Script-First Execution (REQ-042)
This step is **mechanical**. The agent SHALL:
1. Run `ai-tooling.sh diff` via terminal — the Python script handles all YAML comparison logic.
2. Run `ai-tooling.sh summarize-diff` via terminal — produces a plain-text summary with counts, IDs, and module_changed flags.
3. Read the **text summary from stdout only** — do NOT open or parse `structured-diff.yaml`, `merged_requirements.yaml`, or any current-requirements YAML files.
4. Use the summary counts and IDs for the handoff payload and narration.
5. The only case where the agent may read `structured-diff.yaml` directly is when constructing a plan (IM-02) and needs the full requirement snapshots.

Module-change detection:
- The `summarize-diff` script automatically detects module changes and flags them as `module_changed: old -> new` in the summary output.
- The agent reports these flags from the summary; it does NOT compare YAML fields itself.

## Narration
- On entry: `[IM-01] Diff started at <timestamp>`
- Before script: `[IM-01] Script start: ai-tooling.sh diff`
- After script: `[IM-01] Script end: ai-tooling.sh diff (exit: <code>, elapsed: <N>s)`
- On error: `[IM-01] ERROR: Diff script failed — <details>`
- On unexpected: `[IM-01] **UNEXPECTED: <details>**`
- On exit: `[IM-01] Diff completed at <timestamp> (elapsed: <N>s) — created: N, updated: N, removed: N`
