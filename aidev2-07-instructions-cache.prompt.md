---
name: "aidev2-instructions-cache"
description: "Load or refresh the session-memory cache for an aidev2 blueprint using folder layout only. Detects the blueprint from the active file, infers implementation/app paths, tooling path, and startup hints, and never reads blueprint-local .instructions or .schemas."
argument-hint: "[refresh]"
agent: "agent"
---

## Role

You are a cache-warming utility for aidev2 prompts.
Your job is to infer blueprint runtime values from folder layout and nearby repositories, then write them into session memory.

Path semantics:
- Unless explicitly marked absolute, all blueprint paths are relative to `BLUEPRINT_ROOT`.
- App repo paths are absolute values inferred from repository neighbors.

Always use the policy and rules from:
[Blueprint Policy](./aidev2-details/aidev2-blueprint-instructions.md)
[Schema Instructions](./aidev2-details/aidev2-schemas-instructions.md)

Do not read `BLUEPRINT_ROOT/.instructions/*`.
Do not read blueprint-local `.schemas`.

## Step 1 — Parse Argument

Only accepted argument: `refresh`.

- `FORCE_REFRESH = true` if argument is `refresh`
- any other non-empty argument -> stop with an unknown argument message

## Step 2 — Detect and Validate BLUEPRINT_ROOT

Walk up from `${file}` using the rules from `aidev2-blueprint-instructions.md`.

Hard stops:
- active file is not inside a blueprint-layout repo
- detected root is the framework template, not an app blueprint
- active file is outside the detected root

## Step 3 — Check Current Cache

Cache file: `/memories/session/aidev2-config-cache.md`

Section header format:
- `## <absolute BLUEPRINT_ROOT>`

Isolation rule:
- only use the exact matching section for the detected blueprint root

If exact section exists and `FORCE_REFRESH = false`, report that the cache already exists and stop.

## Step 4 — Derive Runtime Values

Derive:
- `app_identifier`
- `tooling_cmd`
- `ai_tooling`
- `pending_req_path`
- `current_req_path_by_type`
- `schemas_root` = `{{VSCODE_USER_PROMPTS_FOLDER}}/prompts/aidev2-schemas` (absolute)
- implementation list from `02-implementation/01-implementations`

Blueprint-relative expectations:
- pending requirements root: `01-requirements/01-pending-promotion`
- current requirements root: `01-requirements/03-current`
- implementations root: `02-implementation/01-implementations`
- test results root: `03-test-results`

For each implementation:
- infer `application_root`
- derive `manifest_path`
- infer `startup_hint`
- infer `app_test_startup_hint`
- infer `tech_stack_summary`

If only one implementation exists, note that it is auto-selectable.

## Step 5 — Write Cache Entry

Write a new section to `/memories/session/aidev2-config-cache.md`:

```markdown
## <BLUEPRINT_ROOT>

- app_identifier: <value>
- tooling_cmd: <value>
- ai_tooling: <value>
- schemas_root: <value>
- pending_req_path: <value>
- current_req_path_by_type: <value>

### Implementations

#### <IMPLEMENTATION_ID>
- application_root: <value>
- manifest_path: <value>
- startup_hint: <value>
- app_test_startup_hint: <value>
- tech_stack_summary: <value>
```

Report: "Cache written for `<BLUEPRINT_ROOT>`."
