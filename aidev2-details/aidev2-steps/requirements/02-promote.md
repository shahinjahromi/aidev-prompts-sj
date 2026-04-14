# RQ-02 Promote
Inputs: TOOLING_CMD, REQ_PATH, IMPLEMENTATION_ID, APP_ROOT.
Action: run `"$TOOLING_CMD" promote -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"`.
Output: promoted items merged into `03-current/`, control.yaml version bumped, diffs rebuilt, merged regenerated.
Reminder: developer updates app manifest iteration_id manually afterward.

## Script-First Execution (REQ-042)
This step is **mechanical**. The agent SHALL:
1. Run `ai-tooling.sh promote` via terminal — the Python script handles all YAML merging, version bumping, diff rebuilding, and TS mirror syncing.
2. Read only the **script stdout/stderr and exit code** for narration and handoff.
3. Do NOT read pending-promotion YAML files, current YAML files, or control.yaml to replicate promote logic.
4. Do NOT open or parse any YAML inputs that the promote script already processes.
5. After promote completes, if the next step needs current state, rely on the script having updated `03-current/` — do not re-read inputs.

## Narration
- On entry: `[RQ-02] Promote started at <timestamp>`
- Before script: `[RQ-02] Script start: ai-tooling.sh promote`
- After script: `[RQ-02] Script end: ai-tooling.sh promote (exit: <code>, elapsed: <N>s)`
- On results: `[RQ-02] Promoted <N> items`
- On error: `[RQ-02] ERROR: Promote failed — <details>`
- On unexpected: `[RQ-02] **UNEXPECTED: <details>**`
- On exit: `[RQ-02] Promote completed at <timestamp> (elapsed: <N>s)`
