# IM-10 Update App Manifest

After all requirements are implemented, the diff is clear, and tests pass:

1. Read `APP_ROOT/.aidev/requirements/requirements-state.yaml`.
2. For **every** requirement ID that was implemented in this run (from the structured diff's `created`, `updated`, and `models_and_contracts_diff.created`/`updated` lists):
   - Add or update an entry in `requirement_baseline`:
     ```yaml
     - requirement_id: <REQ_ID>
       pinned_version: <requirements_version_target>
     ```
   - If the entry already exists (update case), update its `pinned_version` to the current `requirements_version_target`.
3. For any requirement ID in the diff's `removed` list: remove it from `requirement_baseline`.
4. Set `requirements_version_implemented` to the value of `requirements_version_target`.
5. Write the updated manifest back to `APP_ROOT/.aidev/requirements/requirements-state.yaml`.

**Alternative** — use the tooling command if the delta file was generated:
```bash
"$TOOLING_CMD" apply -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"
```

This step is **mandatory**. The pipeline is not complete if `requirements_version_implemented` still equals `0.0.0` or differs from `requirements_version_target` after a successful implementation run.

## Narration
- On entry: `[IM-10] Update manifest started at <timestamp>`
- Before script (if using tooling): `[IM-10] Script start: ai-tooling.sh apply`
- After script: `[IM-10] Script end: ai-tooling.sh apply (exit: <code>, elapsed: <N>s)`
- On write: `[IM-10] Updated manifest — <N> entries written, version: <version>`
- On error: `[IM-10] ERROR: Manifest update failed — <details>`
- On unexpected: `[IM-10] **UNEXPECTED: <details>**`
- On exit: `[IM-10] Update manifest completed at <timestamp> (elapsed: <N>s)`
