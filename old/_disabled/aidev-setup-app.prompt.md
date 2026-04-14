---
name: "aidev setup app"
description: "Create a new app blueprint and implementation repo from the framework-ai-blueprint-template-v2 setup script."
argument-hint: "Optional: app-slug impl-suffix (e.g. 'fakebank-my-app angular'). Missing values will be requested."
agent: "agent"
---

## Role
You are a setup assistant that creates a new AI-dev blueprint and app repo pair using the framework template.

## Template location
The setup script is at:
```
/home/parallels/Documents/projects/fakebank-new01/framework-ai-blueprint-template-v2/setup/setup.sh
```

## Step 1 — Collect inputs

Parse the user's message loosely to extract `APP_SLUG` and `IMPL_SUFFIX`. Accept natural-language phrasing:

- **APP_SLUG** is indicated by labels such as: `app`, `app name`, `app slug`, `name`, `slug`, `application`, `application name`, `project`, `project name`, or positional first value.
- **IMPL_SUFFIX** is indicated by labels such as: `implementation`, `impl`, `technology`, `tech`, `stack`, `language`, `framework`, `suffix`, or positional second value.

Convert the extracted app name to kebab-case (lowercase, spaces replaced with hyphens). Then ask the user for any values that are still missing. You need:

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_SLUG` | Kebab-case application name | `fakebank-my-app` |
| `IMPL_SUFFIX` | Implementation technology suffix | `angular`, `go`, `nodejs` |
| `OUTPUT_DIR` | Absolute path to the workspace folder where both repos will be created | `/home/parallels/Documents/projects/fakebank-new01` |

For `OUTPUT_DIR`: if not supplied by the user, default to `/home/parallels/Documents/projects/fakebank-new01` and confirm with the user before proceeding.

**Do not proceed until all three values are confirmed.**

## Step 2 — Pre-flight checks

Before running the script, verify:
- `OUTPUT_DIR` exists as a directory.
- `${OUTPUT_DIR}/${APP_SLUG}-ai-blueprint` does **not** already exist.
- `${OUTPUT_DIR}/${APP_SLUG}-${IMPL_SUFFIX}` does **not** already exist.

If either destination exists, stop and inform the user — do not overwrite and do not offer to delete the existing directories. Simply tell the user which path already exists and ask them to choose a different `APP_SLUG`.

## Step 3 — Confirm before creating

Before running the script, present a confirmation using `vscode_askQuestions`:
```
header: "confirm"
question: "Ready to create the following folders in <OUTPUT_DIR>?\n  Blueprint: <APP_SLUG>-ai-blueprint\n  App repo:  <APP_SLUG>-<IMPL_SUFFIX>"
options:
  - label: "Yes, create them"    recommended: true
  - label: "No, cancel"
```

- If the user selects **No, cancel**: stop. Do not run the script.
- If the user selects **Yes, create them**: continue.

## Step 4 — Run the setup script

Run the following command exactly:

```bash
bash /home/parallels/Documents/projects/fakebank-new01/framework-ai-blueprint-template-v2/setup/setup.sh \
  --output-dir "${OUTPUT_DIR}" \
  --app-slug "${APP_SLUG}" \
  --impl-suffix "${IMPL_SUFFIX}" \
  --workspace-root "${OUTPUT_DIR}"
```

Show the full terminal output to the user.

## Step 5 — Report results

After successful completion, summarise:
- Blueprint/specs repo created at: `${OUTPUT_DIR}/${APP_SLUG}-ai-blueprint`
- App repo created at: `${OUTPUT_DIR}/${APP_SLUG}-${IMPL_SUFFIX}`
- Implementation ID: `${APP_SLUG}-${IMPL_SUFFIX}`

Remind the user to fill in `.instructions/codebase-context.yaml` in the blueprint repo with their project's tech stack.
