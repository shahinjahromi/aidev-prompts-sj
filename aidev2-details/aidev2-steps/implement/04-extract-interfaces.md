# IM-04 Extract Interfaces
Inputs: APP_ROOT, AI_TOOLING, TECH_STACK_SUMMARY.
Action: write ref-library-methods.yaml under IMPL_ROOT/04-extract-library-interfaces.
Prefer stack-aware extractor from AI_TOOLING/interface-extractors.

Skip optimisation: if `ref-library-methods.yaml` already exists and no new dependencies were added during IM-03 Execute (check plan.yaml for dependency changes), skip extraction and reuse the existing file. Log: "Interface extraction skipped — no dependency changes."
