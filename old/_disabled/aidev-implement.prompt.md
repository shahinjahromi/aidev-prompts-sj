---
name: "aidev-implement"
description: "Implementation pipeline dispatcher for AI-dev blueprints. Steps: 01-diff, 02-plan, 03-execute, 04-extract-interfaces, 05-fix, 06-create-tests, 07-run-tests. Pass a step name, a range (e.g. 02-05), and optional free-text task description."
argument-hint: "[01-diff | 02-plan | 03-execute | 04-extract-interfaces | 05-fix | 06-create-tests | 07-run-tests | 02-07] [optional free-text]"
agent: "agent"
---

## Available Steps

| # | Step | Description |
|---|------|-------------|
| 01 | diff | Generate structured diff of requirements vs app manifest |
| 02 | plan | Generate implementation plan from the structured diff |
| 03 | execute | Execute the plan — write code, update manifest per requirement |
| 04 | extract-interfaces | Extract public library API signatures |
| 05 | fix | Fix build or startup errors iteratively |
| 06 | create-tests | Generate Playwright acceptance tests |
| 07 | run-tests | Run Playwright tests and report results |

---

## Phase 1 — Parse Argument

Argument format: `[step] [optional free-text task description]`

**Disambiguation:**
- Both halves purely numeric (e.g. `02-05`) → **range mode**: run steps N through M inclusive.
- Second half has letters (e.g. `02-plan`) → **single-step mode**.
- Everything after the step identifier is `TASK_DESCRIPTION`.

**No argument:** use `vscode_askQuestions`:
```
header: "step"
question: "Which implementation step do you want to run?"
options:
  - label: "01-diff"
    description: "Generate structured diff of requirements vs app manifest"
  - label: "02-plan"    recommended: true
    description: "Generate an implementation plan from the diff"
  - label: "03-execute"
    description: "Execute the plan — write code, update manifest per requirement"
  - label: "04-extract-interfaces"
    description: "Extract public library API signatures (run before fix if needed)"
  - label: "05-fix"
    description: "Fix build or startup errors iteratively"
  - label: "06-create-tests"
    description: "Generate Playwright acceptance tests"
  - label: "07-run-tests"
    description: "Run Playwright tests and report pass/fail"
  - label: "02-03"
    description: "Plan then execute in sequence"
  - label: "02-07"
    description: "Full cycle: plan → execute → extract → fix → tests → run"
```

If `TASK_DESCRIPTION` is still empty after step selection, ask a follow-up tailored to the step:

| Step | Follow-up |
|------|-----------|
| 01-diff | *(none — fully automated)* |
| 02-plan | "Any focus, constraints, or sequencing preferences for the plan?" |
| 03-execute | "Any scope or order guidance? e.g. 'implement FR-000012 first'." |
| 04-extract-interfaces | *(none — fully automated)* |
| 05-fix | "Paste the error output or describe what is failing." |
| 06-create-tests | "Any coverage focus? e.g. happy path only, specific AT IDs, auth flows." |
| 07-run-tests | "Run mode? headless (default) / headed / debug / single feature name." |
| range | "Any context to carry across all steps in the range?" |

---

## Phase 2 — Detect and Validate BLUEPRINT_ROOT

Start from `${file}`'s directory and walk **up** the tree. The first directory containing a `.instructions` folder is `BLUEPRINT_ROOT`.

If the user passed an absolute path alongside the step argument, use it directly.

If no `.instructions` folder is found anywhere up the tree, stop and ask the user to provide the blueprint folder path.

**Validation — run immediately after detection:**

1. **Template check:** does `BLUEPRINT_ROOT/setup/` exist?
   - Yes → stop: ❌ *You are in `<BLUEPRINT_ROOT>`, which is a blueprint template (it contains `setup/`). Open a file inside an app blueprint folder and run again.*
2. **Scope check:** is `${file}` inside `BLUEPRINT_ROOT`?
   - No → stop: ⚠️ *Active file is outside the detected blueprint root. Open a file inside the target blueprint and run again.*

---

## Phase 3 — Load Config (auto-cached per blueprint)

**⚠️ Isolation rule (CRITICAL):** Only the cache section whose `##` header exactly matches `BLUEPRINT_ROOT` (absolute path) is used. All other sections in the cache file belong to different apps and must be ignored entirely — never read, merge, or borrow values from them.

Check session memory at `/memories/session/blueprint-config-cache.md` for a section header `## <BLUEPRINT_ROOT>` (exact absolute path match).

**Cache hit** — use the stored values directly. Do not re-read config files.

**Cache miss — auto-load (no prompting):**
Inline-read and cache the config for `BLUEPRINT_ROOT` now:
1. Read `BLUEPRINT_ROOT/.instructions/config.yaml` — extract `app_identifier`, `tooling_root`, `timezone`, `pending_req_path`, `current_req_path_by_type`, `schemas_root`, `secrets_instructions_path` (optional), and all `implementations` keys with their `application_root`, `manifest_path`, `startup_script`, `app_test_startup_script`, `database_contract_alignment.enabled`.
2. Read `BLUEPRINT_ROOT/.instructions/codebase-context.yaml` — produce a one-line `tech_stack_summary` per implementation.
3. Confirm `BLUEPRINT_ROOT/github-config/aidev-framework.instructions.md` is accessible.
4. Write the cache entry to `/memories/session/blueprint-config-cache.md` — append if file is new, otherwise only add the `## <BLUEPRINT_ROOT>` section without modifying any other section.

> To force a config refresh: run `/aidev-instructions-cache refresh` while a file inside this blueprint is active.

Resolve runtime variables from the cache:
- `TOOLING_CMD`  = `BLUEPRINT_ROOT` / `tooling_root` + `/ai-tooling.sh`
- `REQ_PATH`     = `BLUEPRINT_ROOT` / parent dir of `current_req_path_by_type` (i.e. `01-requirements`)
- `CURRENT`      = `BLUEPRINT_ROOT` / `current_req_path_by_type`
- `TZ`           = `timezone`
- `AI_TOOLING`   = `BLUEPRINT_ROOT` / `tooling_root`

Read `BLUEPRINT_ROOT/github-config/aidev-framework.instructions.md` — treat its contents as active policy for this session.

**Resolve `implementation_id`:** required for all steps. List available IDs from the cached `implementations` value and ask if not already provided.

Resolve per-implementation variables:
- `IMPL_ROOT` = `BLUEPRINT_ROOT/02-implementation/01-implementations/<IMPLEMENTATION_ID>`
- `APP_ROOT`  = absolute path from `implementations_detail.<IMPLEMENTATION_ID>.application_root`
- `MANIFEST`  = absolute path from `implementations_detail.<IMPLEMENTATION_ID>.manifest_path`

Also read `BLUEPRINT_ROOT/.instructions/implementation.md` — this is the implementation pipeline overview. Use it for IM-00 pre-step verification and the DB gate check.

---

## Phase 4 — Confirmation Gate

Before writing any files, present a summary of what will be written and ask the user to confirm.

Build the confirmation table based on the step(s) in the run list:

| Step | Files written to |
|------|------------------|
| 01-diff | `IMPL_ROOT/01-delta-current/` (structured diff output) |
| 02-plan | `IMPL_ROOT/02-plan/` (implementation plan) |
| 03-execute | `APP_ROOT` (application code + manifest) |
| 04-extract-interfaces | `IMPL_ROOT/` (extracted interface files) |
| 05-fix | `APP_ROOT` (fixed application code) |
| 06-create-tests | `APP_ROOT` (e2e test files) |
| 07-run-tests | *(no file writes — terminal only)* |

For steps that write files, show the resolved absolute path. Skip `07-run-tests` from the confirmation table if it is the only step.

Use `vscode_askQuestions` with:
```
header: "confirm"
question: "Ready to write files for step(s) <STEP_LIST> in:\n  Blueprint: <BLUEPRINT_ROOT>\n  App root:  <APP_ROOT>?"
options:
  - label: "Yes, proceed"    recommended: true
  - label: "No, cancel"
```

- If the user selects **No, cancel**: stop immediately. Do not execute any steps.
- If the user selects **Yes, proceed**: continue to Phase 5.

---

## Phase 5 — Execute Steps

Before reading each step file, output the following resolved context block exactly as shown (substitute resolved values). The step file will see this and skip its `## Context` standalone fallback.

```
BLUEPRINT_ROOT:    <absolute resolved path>
APP_IDENTIFIER:    <value>
TOOLING_CMD:       <absolute path to ai-tooling.sh>
PENDING:           <absolute path>
CURRENT:           <absolute path>
SCHEMAS:           <absolute path>
TZ:                <timezone>
IMPLEMENTATION_ID: <value>
IMPL_ROOT:         <absolute path>
APP_ROOT:          <absolute path>
MANIFEST:          <absolute path>
STARTUP:           <absolute startup_script path>
APP_TEST_STARTUP:  <absolute app_test_startup_script path>
AI_TOOLING:        <absolute tooling_root path>
E2E_ROOT:          <IMPL_ROOT>/06-e2e-tests
E2E_REPORTS:       <BLUEPRINT_ROOT>/03-test-results/<IMPLEMENTATION_ID>
TECH_STACK:        <one-line summary from codebase-context.yaml>
Framework policy:  <BLUEPRINT_ROOT>/github-config/aidev-framework.instructions.md — loaded.
```

For each step in the run list, read the corresponding file from `BLUEPRINT_ROOT/github-config/` and follow its instructions. Skip each file's `## Context` standalone fallback — all inputs are already resolved above. Pass `TASK_DESCRIPTION` as context.

| Step | Instruction file |
|------|-----------------|
| 01-diff | `github-config/aidev-02-diff.prompt.md` |
| 02-plan | `github-config/aidev-03-plan.prompt.md` |
| 03-execute | `github-config/aidev-04-execute.prompt.md` |
| 04-extract-interfaces | `github-config/aidev-05-extract-interfaces.prompt.md` |
| 05-fix | `github-config/aidev-06-fix.prompt.md` |
| 06-create-tests | `github-config/aidev-07-create-tests.prompt.md` |
| 07-run-tests | `github-config/aidev-08-run-tests.prompt.md` |

**Do not re-read config or framework files** — they are already resolved in Phase 3.

After each step in a range: summarise the outcome, state any required developer actions, then proceed to the next step automatically.
