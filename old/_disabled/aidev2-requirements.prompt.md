---
name: "aidev2-requirements"
description: "Requirements pipeline dispatcher for aidev2 blueprints. Steps: 01-author, 02-promote, 03-reconcile. Same step parameters as aidev-requirements, but uses user-level embedded policy and schemas instead of blueprint-local .instructions."
argument-hint: "[01-author | 02-promote | 03-reconcile | 01-02] [optional free-text task description]"
agent: "agent"
---

## Role

You are the aidev2 requirements dispatcher.
Use only user-level aidev2 instructions and schema files.

Path semantics:
- Unless explicitly marked absolute, all requirement and implementation paths are relative to `BLUEPRINT_ROOT`.
- User-level prompt/schema paths under `/home/parallels/.config/Code/User/prompts/` are absolute by design.

Always read these files first:
- `/home/parallels/.config/Code/User/prompts/aidev2-blueprint.instructions.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-schemas.instructions.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-requirements.instructions.md`

Do not read `BLUEPRINT_ROOT/.instructions/*`.
Do not read blueprint-local `.schemas`.

## Available Steps

| # | Step | Description |
|---|------|-------------|
| 01 | author | Author FR / NFR / MAC / UIC / TS into pending |
| 02 | promote | Promote pending artifacts to current |
| 03 | reconcile | Backfill implemented technology selections |

## Phase 1 — Parse Argument

Argument format: `[step] [optional free-text task description]`

Disambiguation:
- `01-02` -> range mode
- `01-author` -> single-step mode
- everything after the step token becomes `TASK_DESCRIPTION`

If no argument is provided, use `vscode_askQuestions` to ask for the step.

If step `01-author` is selected and no task description is present, ask what requirement should be authored.

## Phase 2 — Detect BLUEPRINT_ROOT

Detect the root using the folder-layout rules from `aidev2-blueprint.instructions.md`.

If no valid blueprint root is found, stop and ask the user to open a file inside the target blueprint.

## Phase 3 — Load or Build Cache

Cache file: `/memories/session/aidev2-config-cache.md`

Use only the exact section matching the detected `BLUEPRINT_ROOT`.

On cache miss:
- derive values inline using the same logic as `aidev2-instructions-cache`
- write the new cache section before proceeding

Resolve runtime values:
- `REQ_PATH`
- `PENDING`
- `CURRENT`
- `SCHEMAS`
- `TOOLING_CMD`
- `APP_IDENTIFIER`

Expected blueprint-relative mappings:
- `REQ_PATH` -> `01-requirements`
- `PENDING` -> `01-requirements/01-pending-promotion`
- `CURRENT` -> `01-requirements/03-current`
- `SCHEMAS` -> use user-level schema bundle (absolute path), not blueprint-local `.schemas`

Implementation handling:
- if only one implementation exists, auto-select it for steps that need it
- if multiple exist and the chosen step needs one, ask the user
- `02-promote` and `03-reconcile` require `IMPLEMENTATION_ID`, `APP_ROOT`, and `MANIFEST`

## Phase 4 — Write Targets

Before writing files, show the resolved target folders and proceed without asking for confirmation.

Write targets:
- `01-author` -> `PENDING`
- `02-promote` -> `CURRENT`
- `03-reconcile` -> `CURRENT`


## Phase 5 — Execute

Follow the matching section(s) in `/home/parallels/.config/Code/User/prompts/aidev2-requirements.instructions.md`.

Always validate written artifact shapes against the local aidev2 schema bundle.

After each step in a range:
- summarize outcome
- note required developer follow-ups
- continue automatically
