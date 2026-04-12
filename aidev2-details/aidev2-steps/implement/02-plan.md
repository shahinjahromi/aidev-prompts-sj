# IM-02 Plan
Inputs: structured diff, CURRENT requirements, MANIFEST, TECH_STACK_SUMMARY.
Action: produce plan.yaml + plan.md + paths.yaml in IMPL_ROOT.
Rules: include standing nfr-and-global-cr constraints, scoped impacted files/symbols, validation and risks.

Module-reassignment planning:
- For each requirement flagged `module_changed`, the plan must include:
  1. **Undo scope** — identify code, routes, components, or configuration contributed by the requirement under the OLD module and determine what must be removed or relocated.
  2. **Redo scope** — describe the implementation of the requirement under the NEW module, including new file locations, import changes, and module registration.
- If the old module would become empty after removing the requirement's contributions, note it for potential cleanup.
- Module reassignment steps appear before normal update steps for the same requirement.
