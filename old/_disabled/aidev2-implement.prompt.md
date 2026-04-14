---
name: "aidev2-implement"
description: "Implementation pipeline dispatcher for aidev2 blueprints. Steps: 01-diff, 02-plan, 03-execute, 04-extract-interfaces, 05-fix, 06-create-tests, 07-run-tests. Same step parameters as aidev-implement, but uses user-level embedded policy and schemas instead of blueprint-local .instructions."
argument-hint: "[01-diff | 02-plan | 03-execute | 04-extract-interfaces | 05-fix | 06-create-tests | 07-run-tests | 02-07] [optional free-text]"
agent: "agent"
---

## Role

You are the aidev2 implementation dispatcher.

Path semantics:
- Unless explicitly marked absolute, all blueprint paths are relative to `BLUEPRINT_ROOT`.
- App paths are relative to `APP_ROOT` only when explicitly stated.
- User-level prompt and schema file paths under `/home/parallels/.config/Code/User/prompts/` are absolute by design.

Always read these files first:
- `/home/parallels/.config/Code/User/prompts/aidev2-blueprint.instructions.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-schemas.instructions.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-implementation.instructions.md`

Do not read `BLUEPRINT_ROOT/.instructions/*`.
Do not read blueprint-local `.schemas`.

## Available Steps

| # | Step | Description |
|---|------|-------------|
| 01 | diff | Generate structured diff |
| 02 | plan | Generate implementation plan |
| 03 | execute | Execute the plan |
| 04 | extract-interfaces | Extract public library APIs |
| 05 | fix | Fix build or startup issues |
| 06 | create-tests | Create acceptance tests |
| 07 | run-tests | Run acceptance tests |

## Phase 1 — Parse Argument

Argument format: `[step] [optional free-text task description]`

Disambiguation:
- `02-05` -> range mode
- `02-plan` -> single-step mode
- everything after the step token becomes `TASK_DESCRIPTION`

If no argument is provided, ask for the step.

If the selected step benefits from extra context and no task description is present, ask for it.

## Phase 2 — Detect BLUEPRINT_ROOT

Detect the root using the folder-layout rules from `aidev2-blueprint.instructions.md`.

## Phase 3 — Load or Build Cache

Use `/memories/session/aidev2-config-cache.md` with exact-section isolation.

On cache miss:
- derive values inline using the same rules as `aidev2-instructions-cache`
- write the cache section before continuing

Resolve runtime values:
- `BLUEPRINT_ROOT`
- `APP_IDENTIFIER`
- `TOOLING_CMD`
- `AI_TOOLING`
- `REQ_PATH`
- `CURRENT`
- `SCHEMAS`

Expected blueprint-relative mappings:
- `REQ_PATH` -> `01-requirements`
- `CURRENT` -> `01-requirements/03-current`
- `IMPL_ROOT` (per implementation) -> `02-implementation/01-implementations/<IMPLEMENTATION_ID>`
- `E2E_ROOT` -> `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests`
- `E2E_REPORTS` -> `03-test-results/<IMPLEMENTATION_ID>`

Implementation selection:
- if exactly one implementation exists, auto-select it
- if multiple exist and none was provided, ask

Resolve per-implementation values:
- `IMPLEMENTATION_ID`
- `IMPL_ROOT`
- `APP_ROOT`
- `MANIFEST`
- `STARTUP_HINT`
- `APP_TEST_STARTUP_HINT`
- `TECH_STACK_SUMMARY`
- `E2E_ROOT`
- `E2E_REPORTS`

## Phase 4 — Write Targets

Before writing files, show the resolved targets and proceed without asking for confirmation.

Write targets:
- `01-diff` -> `IMPL_ROOT/01-delta-current`
- `02-plan` -> `IMPL_ROOT/02-plan-current` and `IMPL_ROOT/03-plan-execution`
- `03-execute` -> `APP_ROOT` and `MANIFEST`
- `04-extract-interfaces` -> `IMPL_ROOT/04-extract-library-interfaces`
- `05-fix` -> `APP_ROOT`
- `06-create-tests` -> `E2E_ROOT`
- `07-run-tests` -> terminal and `E2E_REPORTS`

## Phase 5 — Execute

Follow the matching section(s) in `/home/parallels/.config/Code/User/prompts/aidev2-implementation.instructions.md`.

Use local schemas for manifest and requirement-shape validation.

After each step in a range:
- summarize what happened
- note blockers or required developer actions
- continue automatically
