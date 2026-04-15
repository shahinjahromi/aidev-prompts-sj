# IM-04 Extract Interfaces
Inputs: APP_ROOT, AI_TOOLING, TECH_STACK_SUMMARY.
Action: write ref-library-methods.yaml under IMPL_ROOT/04-extract-library-interfaces.
Prefer stack-aware extractor from AI_TOOLING/interface-extractors.

Skip optimisation: if `ref-library-methods.yaml` already exists and no new dependencies were added during IM-03 Execute (check plan.yaml for dependency changes), skip extraction and reuse the existing file. Log: "Interface extraction skipped — no dependency changes."

## Narration
- On entry: `[IM-05] Extract interfaces started at <timestamp>`
- On skip: `[IM-05] Skipped: no dependency changes`
- Before script: `[IM-05] Script start: <extractor-command>`
- After script: `[IM-05] Script end: <extractor-command> (exit: <code>, elapsed: <N>s)`
- On error: `[IM-05] ERROR: Interface extraction failed — <details>`
- On unexpected: `[IM-05] **UNEXPECTED: <details>**`
- On exit: `[IM-05] Extract interfaces completed at <timestamp> (elapsed: <N>s)`
