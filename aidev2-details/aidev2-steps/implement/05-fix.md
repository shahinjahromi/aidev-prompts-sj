# IM-05 Fix
Inputs: startup hint(s), terminal errors, extracted interfaces.
Action: iterate startup/build diagnosis and root-cause fixes.
Rules: limit changes to failures; add dependencies only when required.

## Narration
- On entry: `[IM-07] Fix started at <timestamp>`
- Per fix attempt: `[IM-07] Fixing: <short description of issue>`
- Before script: `[IM-07] Script start: <command-summary>`
- After script: `[IM-07] Script end: <command-summary> (exit: <code>, elapsed: <N>s)`
- On error: `[IM-07] ERROR: Fix attempt failed — <details>`
- On unexpected: `[IM-07] **UNEXPECTED: <details>**`
- On exit: `[IM-07] Fix completed at <timestamp> (elapsed: <N>s) — <outcome>`
