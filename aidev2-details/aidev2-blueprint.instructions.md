---
description: "Embedded AI-dev v2 blueprint policy for aidev2 prompts. Covers folder-layout detection, config.yaml resolution, path inference, tooling discovery, and app-root heuristics."
---

# Aidev2 Blueprint Policy

This file is the generic source of truth for aidev2 prompts.

Hard rules:
- Read `BLUEPRINT_ROOT/.instructions/config.yaml` to resolve `IMPLEMENTATION_ID`, `APP_ROOT`, implementation paths, tooling root, startup hints, timezone, and variable defaults. See **Config Resolution** section below.
- Read `BLUEPRINT_ROOT/.instructions/codebase-context.yaml` when it exists and is populated — use it to supplement tech stack detection, known ports, env vars, npm scripts, and app layout paths. Do not rely solely on it; always verify against the actual app repo files. See **Codebase Context Resolution** section below.
- Do not read any other file under `BLUEPRINT_ROOT/.instructions/` (e.g. `implementation.md`).
- Do not read blueprint-local schema files. Use the local user-level schema bundle at `/home/parallels/.config/Code/User/prompts/aidev2-schemas`, which includes `requirements_manifest.json` for blueprint manifest validation and `in-application/requirements-state-schema.json` for app-side requirements state.
- Use the blueprint repo only for storage layout, requirement files, implementation state, manifests, tests, and generated artifacts.
- Use the local user-level schema bundle at `/home/parallels/.config/Code/User/prompts/aidev2-schemas` for schema truth, including `in-application/requirements-state-schema.json` for the app requirements state file.

## Detect BLUEPRINT_ROOT

Walk up from `${file}`. The first ancestor directory containing all of these paths is `BLUEPRINT_ROOT`:
- `01-requirements`
- `02-implementation`
- `03-test-results`

Template guard:
- If the detected directory contains `setup/setup.sh` and does not contain `02-implementation/01-implementations`, treat it as the framework template, not an app blueprint. Stop and ask the user to open a file inside an app-specific blueprint repo.

## Fixed Layout

All paths below are relative to `BLUEPRINT_ROOT`.

- `REQ_PATH` = `01-requirements`
- `PENDING` = `01-requirements/01-pending-promotion`
- `PENDING_CONTRACTS` = `01-requirements/01-pending-promotion/models_and_contracts`
- `PENDING_TECH_SELECTIONS_DIR` = `01-requirements/01-pending-promotion/technology_selection`
- `CURRENT` = `01-requirements/03-current`
- `CURRENT_CONTRACTS` = `01-requirements/03-current/models_and_contracts`
- `CURRENT_TECH_SELECTIONS_DIR` = `01-requirements/03-current/technology_selection`
- `CURRENT_MERGED` = `01-requirements/03-current/merged/merged_requirements.yaml`
- `DIFF_ROOT` = `01-requirements/02-diff`
- `IMPLEMENTATIONS_ROOT` = `02-implementation/01-implementations`
- `IMPLEMENTATION_MAPPINGS` = `02-implementation/02-implementation-mapping`
- `LOCAL_USER_PROMPTS_DIR` = `/home/parallels/.config/Code/User/prompts`
- `TEST_RESULTS_ROOT` = `03-test-results`

## Config Resolution

Read `BLUEPRINT_ROOT/.instructions/config.yaml` early in every run before inferring any implementation path.

Key fields to extract:

```yaml
identity:
  requirement_set_id:   # -> REQ_SET_ID
  app_identifier:       # -> APP_IDENTIFIER override (use in preference to derived name)

tooling_root:           # -> path relative to BLUEPRINT_ROOT; resolve to TOOLING_CMD = tooling_root/ai-tooling.sh

implementations:
  <IMPLEMENTATION_ID>:
    application_root:        # -> APP_ROOT (path relative to BLUEPRINT_ROOT)
    startup_script:          # -> STARTUP_HINT override (path relative to BLUEPRINT_ROOT)
    app_test_startup_script: # -> APP_TEST_STARTUP_HINT override
    manifest_path:           # -> MANIFEST override
    database_contract_alignment:
      enabled:               # -> if true, DB gate is mandatory
      mac_contract_logical_id: # -> DB MAC ID for contract alignment checks
```

Resolution order when a field is present in config.yaml:
- `app_identifier` from config overrides the derived `APP_IDENTIFIER`
- `application_root` from config overrides the sibling-directory inference for `APP_ROOT`
- `startup_script` and `app_test_startup_script` from config override the startup heuristics
- `manifest_path` from config overrides the default `APP_ROOT/.aidev/requirements/requirements-state.yaml`
- `tooling_root` from config overrides the tooling-discovery walk
- `variables.timezone` is used for date-time fields in the manifest (e.g. `implementation_initial_date`, `implementation_last_date`) — default `UTC` if absent
- `variables.email_fixed` and `variables.email_random_domain` are the only sources for email values in tests

If `.instructions/config.yaml` does not exist, fall back to the inference heuristics in the sections below.

## Codebase Context Resolution

Read `BLUEPRINT_ROOT/.instructions/codebase-context.yaml` when it exists and contains populated fields.

Key fields to extract (keyed under `implementations.<IMPLEMENTATION_ID>`):

```yaml
project:
  name:            # -> display name for the project
  monorepo:        # -> true/false
  package_manager: # -> npm / yarn / pnpm / go / maven etc.

tech_stack:
  client:
    framework:     # -> front-end framework name (see codebase-context)
    language:      # -> primary language name
    styling:       # -> e.g. sass, tailwind
  testing:
    e2e:           # -> e.g. playwright
    unit:          # -> e.g. jest, karma

ports:
  server:          # -> port number
  client:          # -> port number

env_vars:
  required: []     # -> env vars the app requires at startup
  env_file:        # -> path to .env template relative to APP_ROOT

npm_scripts:
  root:
    dev:           # -> preferred dev command override

client_layout:     # -> paths relative to APP_ROOT
server_layout:     # -> paths relative to APP_ROOT
```

Usage rules:
- If `tech_stack` fields are populated, prefer them over file-sniffing heuristics but still verify against `package.json` / framework-specific config files.
- If `ports` are populated, use them in startup hints and E2E base URL configuration.
- If `env_vars.required` is populated, include those in startup pre-checks.
- If `npm_scripts.root.dev` is set, override the startup heuristic with that command.
- If `codebase-context.yaml` contains template placeholders (`<IMPLEMENTATION_ID>`, `<PROJECT_NAME>` etc.) treat the file as unpopulated for those fields and fall back to inference.

## Blueprint Structure Awareness

Treat the app blueprint as a complete system with known folders, file roles, and relative paths.
Use this awareness for navigation, validation, and safe write targeting.

Top-level folders relative to `BLUEPRINT_ROOT`:
- `.instructions/` -> blueprint-local policy/config/context files; aidev2 reads `.instructions/config.yaml` (always) and `.instructions/codebase-context.yaml` (supplemental, when populated)
- `.schemas/` -> blueprint-local schema files (aware of location; aidev2 should use user-level schemas instead)
- `01-requirements/` -> requirements lifecycle root
- `02-implementation/` -> implementation state, prompts, mappings, history
- `03-test-results/` -> per-implementation test reports and artifacts
- `github-config/` -> prompt/instruction files used by non-aidev2 workflows
- `scripts/` -> utility scripts for setup/maintenance
- `setup/` -> template/bootstrap scripts and guidance
- `notes/`, `update-history/`, `README.md`, `readme-files.yaml` -> documentation and change logs

Important requirement paths relative to `BLUEPRINT_ROOT`:
- `01-requirements/control.yaml` -> requirements version state
- `01-requirements/01-pending-promotion/functional_requirements.yaml`
- `01-requirements/01-pending-promotion/nfr-and-global-cr/nfr_and_global_cr_<IMPLEMENTATION_ID>.yaml` -> per-implementation pending NFR file
- `01-requirements/01-pending-promotion/technology-selection/technology_selections_<IMPLEMENTATION_ID>.yaml` -> per-implementation pending technology-selection mirror
- `01-requirements/01-pending-promotion/models_and_contracts.yaml`
- `01-requirements/01-pending-promotion/models_and_contracts/` -> pending contract spec files
- `01-requirements/01-pending-promotion/structured-diff.yaml` -> diff summary for planning/execution
- `01-requirements/02-diff/functional/<ID>.yaml`
- `01-requirements/02-diff/nfr-and-global-cr/<ID>.yaml`
- `01-requirements/02-diff/technology-selection/<ID>.yaml`
- `01-requirements/02-diff/contracts/<ID>.yaml`
- `01-requirements/02-diff/ui_contracts/<ID>.yaml`
- `01-requirements/03-current/*.yaml` -> canonical promoted artifacts
- `01-requirements/03-current/technology-selection/technology_selections_<IMPLEMENTATION_ID>.yaml` -> per-implementation current technology-selection mirror
- `01-requirements/03-current/models_and_contracts/` -> promoted contract specs
- `01-requirements/03-current/merged/merged_requirements.yaml` -> merged requirement view

Important implementation paths relative to `BLUEPRINT_ROOT`:
- `02-implementation/00-prompts/` -> shared prompt files
- `02-implementation/00-templates/e2e-playwright/` -> reusable Playwright reporter templates (canonical source: `aidev2-details/e2e-playwright-templates/` in user prompts)
- `02-implementation/02-implementation-mapping/scope.yaml` -> default execution scope per implementation
- `02-implementation/02-implementation-mapping/<type>.yaml` -> per-type implementation mapping rules
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.yaml`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.md`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/results.yaml`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/04-extract-library-interfaces/ref-library-methods.yaml`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/05-fix/`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests/`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/50-delta-history/`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/51-plan-history/`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/52-plan-execution-history/`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/53-update-history/`
- `03-test-results/<IMPLEMENTATION_ID>/` -> test report artifacts (HTML, JSON, screenshots)

App repo paths (relative to `APP_ROOT`) that are typically required by aidev2:
- `.aidev/requirements/requirements-state.yaml` -> implementation manifest
- `scripts/local-dev.sh` -> preferred startup script
- `scripts/start.sh` -> fallback startup script
- `package.json` / `go.mod` / framework config files -> tech detection and run/test commands

Implementation layout under `02-implementation/01-implementations/<IMPLEMENTATION_ID>/`:
- `01-delta-current`
- `02-plan-current`
- `03-plan-execution`
- `04-extract-library-interfaces`
- `05-fix`
- `06-e2e-tests`
- `50-delta-history`
- `51-plan-history`
- `52-plan-execution-history`
- `53-update-history`

## App Identifier and Implementation Discovery

Derive `APP_IDENTIFIER` from the blueprint folder name:
- Strip a trailing `-ai-blueprint` if present.
- Otherwise strip a trailing `-blueprint` if present.
- Otherwise use the folder basename as-is.

Discover implementations by listing directories directly under `BLUEPRINT_ROOT/02-implementation/01-implementations`.

Implementation selection:
- If exactly one implementation exists, auto-select it.
- If multiple exist and the user did not provide one, ask.
- Never guess when multiple implementations exist.

## Application Root Inference

Infer `APP_ROOT` using this order:
1. Sibling directory of `BLUEPRINT_ROOT` whose basename exactly matches `IMPLEMENTATION_ID`.
2. If no exact match exists, look for a sibling directory whose basename starts with `APP_IDENTIFIER` and ends with the last hyphen-delimited segment of `IMPLEMENTATION_ID`.
3. If multiple candidates remain, ask the user.
4. If no candidate exists, stop and ask for the app repo path.

**Target Folder Validation (REQ-053):** After resolving `APP_ROOT`, verify the directory exists on disk. If it does not exist, this is an **unrecoverable error** — the pipeline must abort. Do not create the app repo directory; only the `.aidev` bootstrap files inside an existing app repo may be auto-created.

Derived paths:
- `APP_ROOT` = inferred application repo root
- `MANIFEST` = `APP_ROOT/.aidev/requirements/requirements-state.yaml`
- `IMPL_ROOT` = `BLUEPRINT_ROOT/02-implementation/01-implementations/IMPLEMENTATION_ID`
- `E2E_ROOT` = `IMPL_ROOT/06-e2e-tests`
- `E2E_REPORTS` = `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID`

## Bootstrap `.aidev` Files (REQ-054)

When `APP_ROOT` exists but the required `.aidev` bootstrap structure is missing, create it automatically before proceeding with any pipeline stage.

Required bootstrap structure:
```
APP_ROOT/
  .aidev/
    requirements/
      requirements-state.yaml
```

**Bootstrap rules:**
1. Check whether `APP_ROOT/.aidev/requirements/requirements-state.yaml` exists.
2. If the file is missing, create the directory structure and file:
   - `APP_ROOT/.aidev/` (directory)
   - `APP_ROOT/.aidev/requirements/` (directory)
   - `APP_ROOT/.aidev/requirements/requirements-state.yaml` with default content:
     ```yaml
     manifest_version: '1.0'
     requirement_set_id: <REQ_SET_ID>
     app_identifier: <APP_IDENTIFIER>
     implementation_id: <IMPLEMENTATION_ID>
     iteration_id: 1
     requirements_version_target: 1.0.0
     requirements_version_implemented: 0.0.0
     requirement_baseline: []
     ```
   - `<REQ_SET_ID>` comes from `config.yaml` → `identity.requirement_set_id`, or derived from `APP_IDENTIFIER`.
   - `<APP_IDENTIFIER>` comes from `config.yaml` → `identity.app_identifier`, or derived from the blueprint folder name (strip `-ai-blueprint` suffix).
   - `<IMPLEMENTATION_ID>` comes from `config.yaml` or the implementation directory name.
3. If only the directory is missing but partial files exist, create only the missing parts.
4. Log the bootstrap creation in the pipeline activity log.
5. Never overwrite an existing `requirements-state.yaml` — only create when absent.

## Tooling Discovery

Resolve `TOOLING_CMD` by searching for `framework-ai-development-tooling/ai-tooling.sh` in this order:

1. **Workspace root folders** — check every root folder loaded in the current VS Code workspace (i.e. the top-level directories visible in the Explorer sidebar). If any workspace root contains `framework-ai-development-tooling/ai-tooling.sh`, use it. This is the preferred resolution path.
2. **Blueprint sibling** — `BLUEPRINT_ROOT/../framework-ai-development-tooling/ai-tooling.sh`
3. **Ancestor walk** — walk up ancestor directories of `BLUEPRINT_ROOT`; at each level check for a sibling `framework-ai-development-tooling/ai-tooling.sh`
4. If still missing, stop and ask the user for the tooling repo path.

Important: the tooling folder must exist as a directory loaded in the IDE workspace. Do **not** use a path derived from the `ai-tooling.sh` internal `ROOT` variable — that variable may point to a stale or non-local path. Always invoke scripts directly from the discovered `AI_TOOLING` directory (e.g. `"$AI_TOOLING/promote_changes.py" ...`) rather than delegating to `ai-tooling.sh` unless you have verified its `ROOT` resolves correctly on the current machine.

Set:
- `AI_TOOLING` = parent directory of the resolved `ai-tooling.sh` (i.e. the `framework-ai-development-tooling` folder)
- `TOOLING_CMD` = `$AI_TOOLING/ai-tooling.sh` (for reference; invoke scripts directly if ROOT is stale)

## Startup Heuristics

Infer `STARTUP_HINT` and `APP_TEST_STARTUP_HINT` using this order:
1. `APP_ROOT/scripts/local-dev.sh`
2. `APP_ROOT/scripts/start.sh`
3. `APP_ROOT/scripts/dev.sh`
4. If `APP_ROOT/package.json` exists, inspect scripts and prefer `npm run dev`, then `npm run start`, then `npm run serve`
5. If no clear startup command exists, leave blank and ask only when a startup-dependent step is run

Treat startup hints as commands, not necessarily file paths.

## Tech Stack Summary Heuristics

Infer a one-line `TECH_STACK_SUMMARY` from the app repo:
- Framework-specific config + `package.json` present -> `npm | client: <framework> application`
- `package.json` only -> `npm | node application`
- `go.mod` -> `go application`
- `pom.xml` -> `JVM/maven application`
- `Cargo.toml` -> `compiled binary application`
- Add port information only if clearly discoverable from config files or scripts
- If uncertain, use `(not yet inferred)`

## Session Cache Contract

Session cache file: `/memories/session/aidev2-config-cache.md`

Each section is isolated by exact header:
- `## <absolute BLUEPRINT_ROOT>`

Only the exact section for the current blueprint may be used.
Never read, merge, or borrow values from another section.
