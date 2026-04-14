# AI-Dev Blueprint Instructions

> **Root:** All paths in this file are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../`

> **Rule 1 (Critical):** `config.yaml` is the **only** app-specific file in `.instructions`. This file (`instructions.md`) must remain **generic**. Never store app-specific values (project names, paths, IDs, secrets paths, scripts, emails, or contract IDs) here.
>
> **App-specific values:** `config.yaml`
> **Per-implementation codebase context:** See [Codebase Context Template](#codebase-context-template) at the end of this file.

---

## Overview

Entry point for humans and coding assistants. Read this file first, then follow the routing table below to the appropriate specialized file. Do not guess paths, pipeline steps, or rules — read the files first.

### What Drives Code

Only **FR (functional requirements)** and **NFR (non-functional and global CR)** cause code to be written. Every other artifact type is **reference-only**:

| Artifact | Role |
|----------|------|
| FR / NFR | Drive code. Implementation satisfies their acceptance criteria (AC/AT embedded inline). |
| MAC | Metadata pointer to a contract/model file. Referenced by FR/NFR. |
| UIC | Screen-only model stored under `models_and_contracts/` and cataloged via MAC entry. Referenced by FR/NFR. |
| TS | Constrains technology choice. Applied during implementation but does not trigger new code on its own. |

### App Manifest Schema

The per-application manifest at `implementations.<IMPLEMENTATION_ID>.manifest_path` must conform to `.schemas/in-application/requirements-state-schema.json`.

Each `requirement_baseline` item has: `requirement_id`, `pinned_version`, `functional_test_status` (`status`: `unspecified`/`passed`/`failed`, `first_version`, `current_version`, `tested_version`). See [Manifest Format](implementation.md#manifest-format) in `implementation.md`.

---

## Task Routing

Identify your goal and follow the appropriate file and steps:

| Goal | File | Steps |
|------|------|-------|
| Add or change a **pending** requirement (FR, NFR, MAC, UIC, TS) | [requirements-management.md](requirements-management.md) | RQ-1 |
| **Promote** pending requirements to current | [requirements-management.md](requirements-management.md) | RQ-2 |
| **Backfill** technology selections (reconcile) | [requirements-management.md](requirements-management.md) | RQ-3 |
| **Design-first / contracts** | [requirements-management.md](requirements-management.md) | RQ-1 (with contracts dependency) |
| Run **full pipeline** (promote → diff → plan → execute → test) | RQ-2 in [requirements-management.md](requirements-management.md), then IM-00 → IM-09 in [implementation.md](implementation.md) | — |
| **Diff only** | [implementation.md](implementation.md) | IM-00 → IM-01 |
| **Plan only** | [implementation.md](implementation.md) | IM-00 → IM-03 |
| **Execute / implement only** | [implementation.md](implementation.md) | IM-00 → IM-04 |
| **Fix** startup errors | [implementation.md](implementation.md) | IM-07 |
| **Create tests** | [implementation.md](implementation.md) | IM-08 |
| **Run tests** | [implementation.md](implementation.md) | IM-09 |

---

## Core Rules

1. **Pending first**: all artifacts are created/updated in `01-pending-promotion`. `03-current` is populated only by promote.
2. **FR/NFR drive code**: code satisfies FR/NFR acceptance criteria. Everything else is reference.
3. **Spec before FR**: create/update the contract spec, then write the FR referencing it.
4. **Requirements must declare contract coverage**: if a requirement touches contracts or models, add `contract_refs` entries naming the `contract_type` and either `selection: all` or `selection: specific_ids`.
5. **UIC = screen-only model**: store UI contracts under `models_and_contracts/`, catalog them via MAC entries, keep them free of backend details.
6. **Manifest after code**: never add a requirement to the app manifest before its code exists.
7. **Iteration gate**: app manifest `iteration_id` is developer-controlled; tooling never auto-updates it.
8. **Scope discipline**: do exactly what is requested.
9. **Security**: never store secrets in this repository.
10. **Genericity**: if a command or example needs a concrete value, describe how to resolve it from `config.yaml` instead of embedding it here.
11. **Manifest schema**: the app manifest must conform to `.schemas/in-application/requirements-state-schema.json`.

---

## Resolving Runtime Values

Resolve these app-specific values from `config.yaml`. All blueprint-internal paths are fixed constants — see [Fixed Blueprint Paths](#fixed-blueprint-paths).

| Value | Resolved From |
|-------|--------------|
| Tooling root | `config.yaml → tooling_root` |
| App repo root | `config.yaml → implementations.<IMPLEMENTATION_ID>.application_root` |
| App manifest path | `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path` |
| App startup path | `config.yaml → implementations.<IMPLEMENTATION_ID>.app_test_startup_script` |
| Test output directory | `03-test-results/<IMPLEMENTATION_ID>` (fixed — not in config) |
| Test email strategy | `config.yaml → variables.email_fixed`, `variables.email_random_domain` |

---

## Fixed Blueprint Paths

These paths are identical for every project using this blueprint. They are **hardcoded constants** — do not put them in `config.yaml`. All paths are relative to the blueprint root (`.`).

| Path | Fixed value |
|------|-------------|
| `specs_root` | `.` |
| `schemas_root` | `.schemas` |
| `implementations_root` | `02-implementation/01-implementations` |
| `implementation_mappings` | `02-implementation/02-implementation-mapping` |
| `shared_prompts` | `02-implementation/00-prompts` |
| `requirements_prompts` | `01-requirements/prompts` |
| `pending_req_path` | `01-requirements/01-pending-promotion` |
| `pending_contract_specs_path` | `01-requirements/01-pending-promotion/models_and_contracts` |
| `current_req_path_by_type` | `01-requirements/03-current` |
| `current_contract_specs_path` | `01-requirements/03-current/models_and_contracts` |
| `current_req_path_merged` | `01-requirements/03-current/merged/merged_requirements.yaml` |
| `diff_path` | `01-requirements/02-diff` |
| `e2e_tests_root` (per impl) | `02-implementation/01-implementations/<IMPL_ID>/06-e2e-tests` |
| `mac_artifact_file` | `01-requirements/03-current/models_and_contracts.yaml` |
| `promoted_schema_specs_root` | `01-requirements/03-current/models_and_contracts` |
| `pending_schema_specs_root` | `01-requirements/01-pending-promotion/models_and_contracts` |
| `ai_tooling` | `../framework-ai-development-tooling` (relative to blueprint root; resolved from `config.yaml → tooling_root`) |
| `tooling_command` | `../framework-ai-development-tooling/ai-tooling.sh` |

---

## Secrets Handling Policy

Never store secrets in this repository.

- Never store secret values in blueprint files, prompts, requirements, manifests, plans, or reports.
- Use placeholder variable names when documenting configuration.
- Before starting the application, source the relevant export script(s) from the project secrets file.

---

## Multi-Implementation Design

The specs repo supports multiple implementation IDs. Each has its own subdirectory under `02-implementation/01-implementations/<IMPLEMENTATION_ID>/`. Shared prompts live in `02-implementation/00-prompts/` and are reused by all implementations.

**If no `implementation_id` is provided, stop and ask — do not guess.**

**How to resolve:**
1. Read `config.yaml → implementations` to see all registered implementations.
2. Use `implementations.<IMPLEMENTATION_ID>.application_root` for the implementation repo path.
3. Use `implementations.<IMPLEMENTATION_ID>.manifest_path` for the app manifest.
4. Derive implementation state paths from the fixed subdirectory layout in [implementation.md](implementation.md#implementation-subdirectory-layout).
5. Read the [Codebase Context Template](#codebase-context-template) for the active `implementation_id` tech stack, file maps, and conventions.
6. Tooling may maintain implementation-local AI app guidance at `02-implementation/01-implementations/<IMPLEMENTATION_ID>/ai-app-hints.yaml`.

**implementation_id format:** `{PROJECT}_{STACK}_{SEQ}` (e.g. MYAPP_NODEJS_01, MYAPP_PYTHON_01)

---

## Common Gotchas

| ID | Rule |
|----|------|
| `paths-are-relative` | `paths.yaml` values are relative to `paths.yaml` itself, NOT to the workspace root. Always resolve from the file's location. |
| `never-store-secrets-in-blueprint` | Never store secrets in this blueprint repository (instructions, requirements, prompts, implementation artifacts, or docs). Use secret managers or local untracked environment files. |
| `manifest-after-code` | NEVER add a requirement to the manifest before its code exists. The structured-diff tool uses the manifest as "implemented" — premature entries corrupt the delta. |
| `nfr-and-global-cr-manifestable` | NFR/GLOBAL items are manifestable just like FRs. When an NFR or GLOBAL item appears in the diff as created, implement it by applying it to all code written or modified in this run, then add it to the app manifest. On subsequent runs, apply existing NFRs and Global CRs only to new or changed code. |
| `scope-enforcement` | Only modify files listed in `plan_metadata.scope` and per-change `scope_for_this_change`. Do not touch out-of-scope files. |
| `verify-diff-clear-before-complete` | Execution is complete only when regenerated `structured-diff.yaml` has zero created, updated, removed, and technology_selection entries. |
| `implementation-specific-context` | Always resolve the active `implementation_id` before reading codebase context. The file maps, tech stack, and conventions are per-implementation. |
| `e2e-email-source-of-truth` | Never hardcode literal emails in E2E/API tests. Resolve fixed email from `config.yaml:variables.email_fixed` only when AT/AC explicitly requires it; otherwise generate `<lowercase-guid>@<config.yaml:variables.email_random_domain>`. |
| `tooling-not-in-pending` | Tooling/process changes are NOT application requirements and must not go in `01-pending-promotion`. Exception: database CONTRACT specs (MAC with `physical_database_schema`) ARE requirement artifacts and MUST be staged in pending. |
| `retired-artifact-types` | Retired and no longer having standalone files: decisions, glossary, business_context, change_log, requirements (aggregate), standalone acceptance_criteria, standalone acceptance_tests, standalone ui_contracts.yaml. AC and AT are embedded inline in FR/NFR items. Requirement removals are expressed via `replaces_id` with empty `text`; the original entry stays in `03-current/` for history. Look up prior state in `02-diff/<bucket>/<ID>.yaml`. |
| `identity-in-config-only` | `requirement_set_id` and `app_identifier` live ONLY in `config.yaml → identity`. Do not duplicate them in other files. `control.yaml` holds only version management. |

---

## Agnostic Design

All tooling and predefined prompts are application-agnostic and implementation-agnostic. Prompts live in `02-implementation/00-prompts/` (shared across all implementations). Implementation-specific content is confined to `config.yaml`, the [Codebase Context Template](#codebase-context-template), `02-implementation/02-implementation-mapping/`, and `01-requirements/`.

**NEVER modify** tooling scripts (`../framework-ai-development-tooling/`), prompt files (`00-prompts/01-*.md` through `07-*.md`), or this file unless the user explicitly requests changes to the tooling or prompts themselves.

---

## Codebase Context Template

Adapt this template for the active `implementation_id`. Fill in actual values after resolving `implementation_id` from `config.yaml`. Keep specific implementation notes in `02-implementation/01-implementations/<IMPLEMENTATION_ID>/ai-app-hints.yaml`.

```yaml
implementations:
  <IMPLEMENTATION_ID>:
    project:
      name: "<PROJECT_NAME>"
      monorepo: false
      package_manager: npm
      # workspaces: [client, server]
      # root_package_json: package.json

    tech_stack:
      # server:
      #   runtime: <RUNTIME>
      #   framework: <FRAMEWORK>
      # client:
      #   framework: <UI_FRAMEWORK>
      #   language: <LANGUAGE>
      #   styling: <STYLING_APPROACH>
      # testing:
      #   e2e: <E2E_TOOL>
      #   unit: <UNIT_TEST_TOOL>

    ports:
      # server: <PORT>
      # client: <PORT>

    env_vars:
      # required: [<ENV_VAR>]
      # optional: [<ENV_VAR>]
      # env_file: <PATH>

    npm_scripts: {}
      # root:
      #   dev: "<COMMAND>"

    # All paths below are relative to the implementation's application_root.
    # server_layout:
    #   entry: <PATH>
    #   config: []
    #   routes:
    #     mount_prefix: <PREFIX>
    #     files: []
    #   services: []
    #   middleware: []
    #   utils: []

    # client_layout:
    #   entry: <PATH>
    #   routes: <PATH>
    #   core: []
    #   layout: []
    #   features: []

    database:
      contract_catalog: 01-requirements/03-current/models_and_contracts.yaml
      contract_specs_root: 01-requirements/03-current/models_and_contracts
      pending_contract_specs_root: 01-requirements/01-pending-promotion/models_and_contracts
      physical_schema_contract_logical_id: <DB_CONTRACT_LOGICAL_ID>
      notes: []

    e2e_tests:
      root: 06-e2e-tests
      config: 06-e2e-tests/playwright.config.ts
      helpers: 06-e2e-tests/helpers/
      api_tests: 06-e2e-tests/api/
      ui_tests: 06-e2e-tests/ui/
      # specs: []

    other:
      manifests_dir: .aidev/requirements/
      requirements_manifest: .aidev/requirements/requirements-state.yaml

    conventions: {}
      # server_routes: "<CONVENTION>"
      # server_services: "<CONVENTION>"
      # client_components: "<CONVENTION>"
```
