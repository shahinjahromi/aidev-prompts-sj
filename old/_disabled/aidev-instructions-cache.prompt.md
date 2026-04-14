---
name: "aidev-instructions-cache"
description: "Load or refresh the session-memory config cache for the AI-dev blueprint containing the currently active file. Detects BLUEPRINT_ROOT by walking up from the active file — no argument needed. Accepts only the optional word 'refresh' to force re-read. Fails if the active file is not inside an app-specific blueprint."
argument-hint: "[refresh]"
agent: "agent"
---

## Role
You are a cache-warming utility. Your only job is to read blueprint config files for the **currently active app** and write a structured cache entry into session memory. You derive the target app entirely from the active file — you never ask the user which app to load and you never use or mix data from a different app's cache section.

---

## Step 1 — Parse Argument

The only accepted argument is the optional word `refresh` (case-insensitive).

- `FORCE_REFRESH = true` if the argument is `refresh`, otherwise `false`.
- Any other non-empty argument: stop with ❌ *Unknown argument `<arg>`. The only accepted argument is `refresh`. Usage: `/aidev-instructions-cache [refresh]`*

---

## Step 2 — Detect and Validate BLUEPRINT_ROOT

Walk **up** from `${file}`'s directory. The first ancestor directory that contains a `.instructions/config.yaml` file is `BLUEPRINT_ROOT`.

**Hard stops — do not ask, do not guess:**

1. **Not in a blueprint:** if no `.instructions/config.yaml` is found anywhere up the tree:
   > ❌ The active file is not inside any AI-dev blueprint. Open a file inside an app-specific blueprint folder and run again.

2. **Template detected:** if `BLUEPRINT_ROOT/setup/` exists:
   > ❌ The active file is inside `<BLUEPRINT_ROOT>`, which is the blueprint **template** (it contains `setup/`). Open a file inside an app-specific blueprint and run again.

3. **Scope check:** if `${file}` is not a descendant of `BLUEPRINT_ROOT`:
   > ❌ Active file is outside the detected blueprint root `<BLUEPRINT_ROOT>`. Open a file inside the target blueprint and run again.

---

## Step 3 — Check Current Cache

Read `/memories/session/blueprint-config-cache.md`.

Look for a section header `## <BLUEPRINT_ROOT>` (exact absolute path match).

**⚠️ Isolation rule:** Only the section whose header exactly matches `## <BLUEPRINT_ROOT>` is relevant. All other sections belong to different apps. Never read, merge, or borrow values from another app's section.

- **Section found and `FORCE_REFRESH = false`:**
  Report:
  > Cache already loaded for `<APP_IDENTIFIER>` (`<BLUEPRINT_ROOT>`).
  > Run `/aidev-instructions-cache refresh` to force re-read after config changes.

  Stop — do not re-read or overwrite.

- **Section not found or `FORCE_REFRESH = true`:** proceed to Step 4.

---

## Step 4 — Read Source Files

Read the following files completely. Do not skip fields.

### 4a. `BLUEPRINT_ROOT/.instructions/config.yaml`

Extract:
| Key | Config path |
|-----|-------------|
| `app_identifier` | `identity.app_identifier` |
| `tooling_root` | `tooling_root` |
| `timezone` | `variables.timezone` |
| `pending_req_path` | `requirements.pending_req_path` — fall back to top-level `pending_req_path` if absent |
| `current_req_path_by_type` | `requirements.current_req_path_by_type` — fall back to top-level if absent |
| `schemas_root` | `requirements.schemas_root` — fall back to top-level if absent |
| `secrets_instructions_path` | `secrets_instructions_path` (optional — omit from cache if absent) |
| `implementations` | all keys under `implementations:` |

For each implementation key, extract:
- `application_root`
- `manifest_path`
- `startup_script`
- `app_test_startup_script`
- `database_contract_alignment.enabled` (default `false` if absent)

### 4b. `BLUEPRINT_ROOT/.instructions/codebase-context.yaml`

For each implementation key found in Step 4a, produce a one-line `tech_stack_summary`:
- Format: `<package_manager> | <server.runtime>/<server.framework> | <client.framework>/<client.language> | ports: <server>/<client>`
- Omit segments that are empty/commented-out. If the entire stack is empty, write `(not yet configured)`.

### 4c. `BLUEPRINT_ROOT/github-config/aidev-framework.instructions.md`

Confirm the file is readable. Do not cache its content — just record its path. If missing, note a warning.

---

## Step 5 — Write Cache Entry

Open `/memories/session/blueprint-config-cache.md` using the `memory` tool.

- If the file does not exist: create it with this header, then append the entry:
```
# Blueprint Config Cache
# Managed automatically by aidev-* prompts. Do not edit manually.
# Run `/aidev-instructions-cache refresh` (active file inside the target blueprint) to force re-read.
# Delete this file to clear all cached entries.
# ISOLATION: each ## section belongs to exactly one BLUEPRINT_ROOT. Never merge sections.
```

- If `FORCE_REFRESH = true` and the section already exists: replace only the `## <BLUEPRINT_ROOT>` section. Do not modify other sections.

**Cache entry format:**
```
## /absolute/path/to/BLUEPRINT_ROOT
app_identifier: <value>
tooling_root: <value>
pending_req_path: <value>
current_req_path_by_type: <value>
schemas_root: <value>
timezone: <value>
framework_instructions: <BLUEPRINT_ROOT>/github-config/aidev-framework.instructions.md
implementations: <comma-separated list of implementation_ids>
implementations_detail:
  <IMPLEMENTATION_ID_1>:
    application_root: <value>
    manifest_path: <value>
    startup_script: <value>
    app_test_startup_script: <value>
    db_contract_enabled: <true|false>
    tech_stack_summary: <one-line summary>
  <IMPLEMENTATION_ID_2>:
    ...
```

---

## Step 6 — Report

Print a concise summary:

```
Cache [created | refreshed] for: <APP_IDENTIFIER>
Blueprint root:    <BLUEPRINT_ROOT>
Implementations:   <comma-separated list>
Timezone:          <value>
Framework policy:  <path to aidev-framework.instructions.md> [OK | MISSING ⚠️]
```

List any warnings (missing optional fields, placeholder values still present in config.yaml, missing codebase-context tech stack).

> **App isolation reminder:** this cache entry is valid only while working in `<BLUEPRINT_ROOT>`. Other aidev-* prompts will detect their own `BLUEPRINT_ROOT` from `${file}` and will only ever read the matching section from this file.
