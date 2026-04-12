# IM-03 Execute
Inputs: plan.yaml, paths.yaml, structured-diff.yaml, manifest path.
Action: implement one requirement at a time; code first then manifest entry.
Rules: no bulk manifest updates, no out-of-scope edits, preserve existing behavior unless required.

Module-reassignment execution:
- When a requirement has `module_changed: true` in the diff:
  1. **Undo** — remove or relocate the requirement's code contributions from the old module location. This includes imports, route registrations, component declarations, service bindings, and any module-level configuration that existed solely for this requirement.
  2. **Redo** — implement the requirement in the new module location following the plan's redo scope.
  3. **Verify** — confirm the old module still builds/works without the moved requirement and the new module correctly includes it.
- Update the manifest baseline entry's `module` field to the new value after code is in place.
