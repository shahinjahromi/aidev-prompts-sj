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

Ask for missing values.

Needed values:
- `APP_SLUG`
- `IMPL_SUFFIX`
- `OUTPUT_DIR`

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

Run exactly:

```bash
bash "${FRAMEWORK_ROOT}/setup/setup-for-user-prompts.sh" \
  --output-dir "${OUTPUT_DIR}" \
  --app-slug "${APP_SLUG}" \
  --impl-suffix "${IMPL_SUFFIX}" \
  --workspace-root "${OUTPUT_DIR}"
```

## Step 5 — Report Results

Summarize:
- blueprint path
- app repo path
- implementation id

Also note:
- aidev2 prompts use folder layout plus user-level schemas/config, not blueprint-local `.instructions`
