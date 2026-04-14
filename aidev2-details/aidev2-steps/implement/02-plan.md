# IM-02 Plan
Inputs: structured diff, CURRENT requirements, MANIFEST, TECH_STACK_SUMMARY.
Action: produce plan.yaml + plan.md + paths.yaml in IMPL_ROOT.
Rules: include standing nfr-and-global-cr constraints, scoped impacted files/symbols, validation and risks.

Read efficiency: batch-read `structured-diff.yaml`, current requirements, manifest, and any existing plan/paths/results files in a single parallel read at the start of this step. Do not re-read files already cached from IM-00.

Pre-computed maps (include in plan.yaml):
- `codebase_map` — key source files, their purpose, and relevant symbols for the planned changes. Reduces file-discovery reads during execute.
- `test_coverage_mapping` — maps each requirement to test type (ui/api/none) and AC/AT IDs. Consumed by test creation to avoid re-reading requirements.

Module-reassignment planning:
- For each requirement flagged `module_changed`, the plan must include:
  1. **Undo scope** — identify code, routes, components, or configuration contributed by the requirement under the OLD module and determine what must be removed or relocated.
  2. **Redo scope** — describe the implementation of the requirement under the NEW module, including new file locations, import changes, and module registration.
- If the old module would become empty after removing the requirement's contributions, note it for potential cleanup.
- Module reassignment steps appear before normal update steps for the same requirement.
