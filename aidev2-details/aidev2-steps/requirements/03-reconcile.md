# RQ-03 Reconcile
Inputs: app codebase, current technology_selection, MANIFEST.
Action: backfill implemented TS entries and sync diff.
Rules: only for already-implemented tech choices.

After reconcile writes:
- refresh `01-requirements/03-current/technology-selection/technology_selections_<IMPLEMENTATION_ID>.yaml`
- keep the current mirror aligned with `01-requirements/03-current/technology_selection.yaml`

## Narration
- On entry: `[RQ-03] Reconcile started at <timestamp>`
- On sync: `[RQ-03] Syncing <N> technology selection entries`
- Before script: `[RQ-03] Script start: <command-summary>`
- After script: `[RQ-03] Script end: <command-summary> (exit: <code>, elapsed: <N>s)`
- On error: `[RQ-03] ERROR: Reconcile failed — <details>`
- On unexpected: `[RQ-03] **UNEXPECTED: <details>**`
- On exit: `[RQ-03] Reconcile completed at <timestamp> (elapsed: <N>s)`
