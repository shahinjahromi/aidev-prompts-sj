---
name: "aidev-requirements"
description: "Requirements pipeline dispatcher for AI-dev blueprints. Steps: 01-author, 02-promote, 03-reconcile. Pass a step name, a numeric range (e.g. 01-02), and optional free-text task description. Use: /aidev-requirements 01-author add login FR"
argument-hint: "[01-author | 02-promote | 03-reconcile | 01-02] [optional free-text task description]"
agent: "agent"
---

## Available Steps

| # | Step | Description |
|---|------|-------------|
| 01 | author | Author FR / NFR / MAC / UIC / TS into pending |
| 02 | promote | Promote pending artifacts to current, advance version |
| 03 | reconcile | Backfill implemented technology selections (optional) |

---

## Phase 1 — Parse Argument

Argument format: `[step] [optional free-text task description]`

**Disambiguation:**
- Both halves purely numeric (e.g. `01-02`) → **range mode**: run steps N through M inclusive.
- Second half has letters (e.g. `01-author`) → **single-step mode**.
- Everything after the step identifier is `TASK_DESCRIPTION`.

**No argument:** use `vscode_askQuestions`:
```
header: "step"
question: "Which requirements step do you want to run?"
options:
  - label: "01-author"    recommended: true
    description: "Author a new or updated requirement into pending"
  - label: "02-promote"
    description: "Promote pending requirements to current"
  - label: "03-reconcile"
    description: "Backfill implemented technology selections (optional)"
  - label: "01-02"
    description: "Author then promote in sequence"
```

If step selected is `01-author` (or a range starting with 01) and `TASK_DESCRIPTION` is still empty, ask:
> "What requirement do you want to author? Describe the feature, behaviour, or contract to capture."

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
- `TOOLING_CMD` = `BLUEPRINT_ROOT` / `tooling_root` + `/ai-tooling.sh`
- `REQ_PATH`    = `BLUEPRINT_ROOT` / parent dir of `current_req_path_by_type` (i.e. `01-requirements`)
- `PENDING`     = `BLUEPRINT_ROOT` / `pending_req_path`
- `CURRENT`     = `BLUEPRINT_ROOT` / `current_req_path_by_type`
- `TZ`          = `timezone`

Read `BLUEPRINT_ROOT/github-config/aidev-framework.instructions.md` — treat its contents as active policy for this session.

---

## Phase 4 — Confirmation Gate

Before writing any files, present a summary of what will be written and ask the user to confirm.

Build the confirmation table based on the step(s) in the run list:

| Step | Files written to |
|------|------------------|
| 01-author | `PENDING` (`01-requirements/01-pending-promotion/`) |
| 02-promote | `CURRENT` (`01-requirements/03-current/`) — promoted from pending |
| 03-reconcile | `CURRENT` (`01-requirements/03-current/`) — technology selections backfilled |

Use `vscode_askQuestions` with:
```
header: "confirm"
question: "Ready to write files for step(s) <STEP_LIST> in <BLUEPRINT_ROOT>?"
options:
  - label: "Yes, proceed"    recommended: true
  - label: "No, cancel"
```
Also show the resolved write folder(s) in the question text.

- If the user selects **No, cancel**: stop immediately. Do not execute any steps.
- If the user selects **Yes, proceed**: continue to Phase 5.

---

## Phase 5 — Execute Steps

Before reading each instruction source, output the following resolved context block exactly as shown (substitute resolved values):

```
BLUEPRINT_ROOT:  <absolute resolved path>
APP_IDENTIFIER:  <value>
PENDING:         <absolute path>
CURRENT:         <absolute path>
SCHEMAS:         <absolute path>
TZ:              <timezone>
Framework policy: <BLUEPRINT_ROOT>/github-config/aidev-framework.instructions.md — loaded.
```

For each step in the run list, read the corresponding instruction source and follow it. Pass `TASK_DESCRIPTION` as context into each reading.

| Step | Instruction source | Section(s) to follow |
|------|--------------------|----------------------|
| 01-author | `BLUEPRINT_ROOT/.instructions/requirements-management.md` | RQ-1 and all Authoring Rules / Procedures sections |
| 02-promote | `BLUEPRINT_ROOT/.instructions/requirements-management.md` | RQ-2 |
| 03-reconcile | `BLUEPRINT_ROOT/.instructions/requirements-management.md` | RQ-3 |

**Do not re-read config or framework files** — they are already resolved in Phase 3.

After each step in a range: summarise the outcome, state any required developer actions, then proceed to the next step automatically.
