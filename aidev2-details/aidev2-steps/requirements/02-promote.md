# RQ-02 Promote
Inputs: TOOLING_CMD, REQ_PATH, IMPLEMENTATION_ID, APP_ROOT.
Action: run promote command; summarize promoted counts.
Reminder: developer updates app manifest iteration_id manually afterward.

## Narration
- On entry: `[RQ-02] Promote started at <timestamp>`
- Before script: `[RQ-02] Script start: ai-tooling.sh promote`
- After script: `[RQ-02] Script end: ai-tooling.sh promote (exit: <code>, elapsed: <N>s)`
- On results: `[RQ-02] Promoted <N> items`
- On error: `[RQ-02] ERROR: Promote failed — <details>`
- On unexpected: `[RQ-02] **UNEXPECTED: <details>**`
- On exit: `[RQ-02] Promote completed at <timestamp> (elapsed: <N>s)`
