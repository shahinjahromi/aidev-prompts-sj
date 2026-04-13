---
name: "aidev2-setup-app"
description: "Create a new app blueprint and implementation repo from the framework-ai-blueprint-template-v2 setup script. Generated repos are compatible with aidev2 folder-layout detection without depending on blueprint-local instructions."
argument-hint: "Optional: app-slug impl-suffix (e.g. 'my-app goimp'). Missing values will be requested."
agent: "agent"
---

## Role

You are a setup assistant that creates a new AI-dev blueprint and app repo pair using the framework template.

Path semantics:
- Derive FRAMEWORK_ROOT by finding the `framework-ai-blueprint-template-v2` directory within the active workspace.
- In the generated blueprint, operational paths are interpreted relative to that blueprint root.
- In the generated app repo, manifest and startup paths are interpreted relative to that app root unless explicitly absolute.

## Step 1 — Collect Inputs

Parse the user's message loosely to extract:
- `APP_SLUG`
- `IMPL_SUFFIX`
- `OUTPUT_DIR` (default: ask the user; suggest the active workspace root if available)
- `CORE_STACK` (optional) — if the user mentions a stack or language (e.g. go, node, angular, python), capture it

Ask for missing required values.

If `CORE_STACK` was not mentioned, ask whether a core stack should be used.
List available stacks by checking subfolder names under `{{VSCODE_USER_PROMPTS_FOLDER}}/aidev2-details/preset-requirements/nfr-and-global-cr-by-core-stack/`.
If the user declines or says none, leave `CORE_STACK` empty.

Needed values:
- `APP_SLUG`
- `IMPL_SUFFIX`
- `OUTPUT_DIR`
- `CORE_STACK` (optional — when set, seeds NFR and technology selection presets into the new blueprint)

Convert app names to kebab-case.
Do not proceed until all values are confirmed.

## Step 2 — Pre-flight Checks

Verify:
- `OUTPUT_DIR` exists
- `${OUTPUT_DIR}/${APP_SLUG}-ai-blueprint` does not already exist
- `${OUTPUT_DIR}/${APP_SLUG}-${IMPL_SUFFIX}` does not already exist

If either destination exists, stop and ask the user to choose a different app slug.

## Step 3 — Confirm Before Creating

Use `vscode_askQuestions` to confirm creation of both folders.

## Step 4 — Run Setup Script

Build the command from the collected values.

Base command (always included):

```bash
bash "${FRAMEWORK_ROOT}/setup/setup-for-user-prompts.sh" \
  --output-dir "${OUTPUT_DIR}" \
  --app-slug "${APP_SLUG}" \
  --impl-suffix "${IMPL_SUFFIX}" \
  --workspace-root "${OUTPUT_DIR}"
```

If `CORE_STACK` is set, append `--core-stack "${CORE_STACK}"` to the command:

```bash
bash "${FRAMEWORK_ROOT}/setup/setup-for-user-prompts.sh" \
  --output-dir "${OUTPUT_DIR}" \
  --app-slug "${APP_SLUG}" \
  --impl-suffix "${IMPL_SUFFIX}" \
  --workspace-root "${OUTPUT_DIR}" \
  --core-stack "${CORE_STACK}"
```

## Step 5 — Report Results

Summarize:
- blueprint path
- app repo path
- implementation id

If `CORE_STACK` was provided, verify that preset files were seeded:
- Check `${BLUEPRINT_PATH}/01-requirements/01-pending-promotion/nfr-and-global-cr/` for `nfr-and-global-cr-${IMPL_ID}.yaml`
- Check `${BLUEPRINT_PATH}/01-requirements/01-pending-promotion/technology-selection/` for `technology-selection-${IMPL_ID}.yaml`
- Report which preset files were seeded. If expected preset files are missing, warn the user.

Also note:
- aidev2 prompts use folder layout plus user-level schemas/config, not blueprint-local `.instructions`
