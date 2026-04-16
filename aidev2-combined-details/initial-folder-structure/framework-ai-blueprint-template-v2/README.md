# AI Blueprint Template v2

Generic, reusable template for creating a new application's **specs repository** -- the requirements-to-code pipeline powered by the shared `ai-development-tooling`.

**Using an AI assistant with this repo:** see [instructions/README.md](instructions/README.md) for copy-paste prompts (e.g. “learn from `instructions`”) and for running `setup/setup.sh` to create a new blueprint instance.

## Quick Start

### Option A: Automated setup (recommended)

```bash
./setup/setup.sh \
  --output-dir /path/to/workspace \
  --app-slug "my-app" \
  --impl-suffix "nodejs"
```

Any omitted optional arguments will be prompted interactively or defaulted.

### Option B: Manual setup

1. Copy this entire directory to your target location
2. Search-and-replace all `<<PLACEHOLDER>>` tokens (see table below)
3. Rename `02-implementation/01-implementations/__IMPL_ID__/` to your actual implementation ID
4. Copy `manifest-template.yaml` to your app repo at `.aidev/requirements/requirements-state.yaml`
5. Fill in `instructions/codebase-context.yaml` with your project's structure

## Placeholders

All app-specific configuration files use `<<PLACEHOLDER>>` tokens that must be replaced.

| Placeholder | Example | Description |
|---|---|---|
| `<<APP_SLUG>>` | `my-app` | Kebab-case slug, used as `requirement_set_id` and `app_identifier` |
| `<<APP_REPO_DIR>>` | `my-app` | Application repo directory name |
| `<<SPECS_REPO_DIR>>` | `my-app-ai-blueprint` | This specs repo directory name |
| `<<IMPLEMENTATION_ID>>` | `MYAPP_NODEJS_01` | Implementation ID (PROJECT_STACK_SEQ) |
| `<<WORKSPACE_ROOT>>` | `/path/to/projects` | Absolute workspace root path |
| `<<APP_STARTUP_SCRIPT>>` | `scripts/local-dev.sh` | App startup script relative to app repo |
| `<<E2E_REPORTS_DIR>>` | `my-app-test-results` | E2E reports dir relative to workspace |
| `<<DB_CONTRACT_LOGICAL_ID>>` | `CONTRACT-APP-DB-SCHEMA` | DB contract family ID |
| `<<DB_CONTRACT_ENABLED>>` | `true` or `false` | Enable DB contract alignment |
| `<<SECRETS_INSTRUCTIONS_PATH>>` | `/path/to/secrets-instructions.txt` | Secrets file path |
| `<<TIMEZONE>>` | `America/Denver` | Timezone for timestamps |
| `<<EMAIL_FIXED>>` | `test@example.com` | Fixed test email |
| `<<EMAIL_RANDOM_DOMAIN>>` | `example.com` | Random email domain |
| `<<DATE>>` | `2026-04-03` | Current date (auto-filled by setup.sh) |

## Requirement Types

This template supports the following requirement types, organized by role:

### Core implementable types (flow through the full pipeline)
| Type | ID Pattern | Schema | Description |
|------|-----------|--------|-------------|
| `functional_requirements` | FR-NNNNNN | `.schemas/functional_requirements.json` | Features, behavior, business logic (AC/AT embedded inline) |
| `nfr_and_global_cr` | NFR-NNNNNN | `.schemas/nfr_and_global_cr.json` | Quality, constraints, coding standards (AC/AT embedded inline) |
| `technology_selection` | TS-NNNNNN | `.schemas/technology_selection.json` | Tech decisions as implementable requirements |
| `data_and_api_contracts` | DAC-NNNNNN | `.schemas/contracts/models_and_contracts.json` | Contract metadata (OpenAPI, DB schema, etc.) |
| `ui_contracts` | UIC-NNNNNN | `.schemas/contracts/ui_contracts.json` | Screen-only model files under `models_and_contracts/` |

### Contract spec formats (referenced by DAC entries)
| Format | Schema | Description |
|--------|--------|-------------|
| `openapi_yaml` | `.schemas/contracts/openapi_yaml.json` | OpenAPI contract files (.yaml) |
| `graphql_sdl_yaml` | `.schemas/contracts/graphql_sdl_yaml.json` | GraphQL SDL in YAML format |
| `logical_database_schema` | `.schemas/contracts/logical_database_schema.json` | DB-agnostic data model |
| `physical_database_schema` | `.schemas/contracts/physical_database_schema.json` | DB-specific DDL/schema |
| `domain_model` | `.schemas/contracts/domain_model.json` | Domain entities and relationships |

AC and AT are embedded inside FR/NFR items — no standalone artifact files.

## Configuration Design

All project identity and paths are consolidated in **one file**: `instructions/config.yaml`.

- `config.yaml -> identity` -- `requirement_set_id`, `app_identifier`, `app_name`
- `config.yaml -> paths` -- workspace, specs root, implementations root, mappings root
- `config.yaml -> implementations` -- per-implementation app repo linkage
- `control.yaml` -- only version management (`current_version`, `next_version`, `iteration_id`)
- App manifest `iteration_id` -- developer-controlled; must be manually updated to include an iteration's requirements in the pipeline

Generic framework conventions (fixed tooling paths, requirements directory layout, secrets policy) live in `ai-tooling-hints.yaml`.

## Directory Structure

```
<specs-repo>/
├── instructions/                        -- Configuration and AI context
│   ├── config.yaml                      -- Identity, paths, implementations (app-specific)
│   ├── instructions.txt                 -- Command reference (env vars + pipeline steps)
│   ├── explanation.txt                  -- How the pipeline works
│   ├── codebase-context.yaml            -- Per-implementation project structure for AI
│   ├── ai-tooling-hints.yaml            -- Layout conventions, gotchas, patterns (generic)
│   └── add-or-update-pending-requirement-prompt.txt
├── 01-requirements/
│   ├── .instructions/                   -- Requirement-authoring onboarding pack
│   │   ├── README.md
│   │   ├── config.yaml
│   │   ├── codebase-context.yaml
│   │   ├── ai-tooling-hints.yaml
│   │   ├── explanation.txt
│   │   ├── instructions.txt
│   │   └── add-or-update-pending-requirement-prompt.txt
│   ├── .schemas/                        -- JSON schemas validating requirement YAML
│   │   ├── functional_requirements.json
│   │   ├── nfr_and_global_cr.json
│   │   ├── technology_selection.json
│   │   ├── _ac_definition.json
│   │   ├── _at_definition.json
│   │   └── contracts/
│   │       ├── models_and_contracts.json
│   │       ├── domain_model.json
│   │       ├── logical_database_schema.json
│   │       ├── openapi_yaml.json
│   │       ├── graphql_sdl_yaml.json
│   │       ├── physical_database_schema.json
│   │       └── ui_contracts.json
│   ├── control.yaml                     -- Version management
│   ├── 01-pending-promotion/            -- Staging area (empty YAML templates)
│   │   ├── technology_selection/        -- Per-implementation pending TS mirrors
│   │   ├── models_and_contracts/        -- Pending contract spec files
│   │   └── *.yaml                       -- Per-type pending files
│   ├── 02-diff/                         -- Version-stamped diffs from promotion
│   └── 03-current/                      -- Canonical requirements (populated by promote)
│       ├── *.yaml                       -- Grouped requirement files
│       ├── technology_selection/        -- Per-implementation current TS mirrors
│       ├── models_and_contracts/        -- Promoted contract spec files
│       └── merged/merged_requirements.yaml
├── 02-implementation/
│   ├── 00-prompts/                      -- Shared prompts (implementation-agnostic)
│   │   ├── 01-prompt-diff.txt           -- through 07-prompt-run-tests.txt
│   ├── 00-templates/
│   │   └── e2e-playwright/              -- Reusable Playwright reporter templates
│   ├── 01-implementations/__IMPL_ID__/  -- Per-implementation artifacts
│   │   ├── 01-delta-current/            -- structured-diff.yaml
│   │   ├── 02-plan-current/             -- plan.yaml, plan.md
│   │   ├── 03-plan-execution/           -- paths.yaml, results.yaml
│   │   ├── 05-fix/
│   │   ├── 06-e2e-tests/               -- Playwright tests
│   │   └── 50-53-*-history/            -- Historical archives
│   └── 02-implementation-mapping/       -- Per-type implementation scoping
├── scripts/
│   └── ensure-specs-agent-config.sh
├── manifest-template.yaml               -- Template for app manifest
├── readme-command-sequence.txt
├── readme-files.yaml
├── setup/
│   ├── setup.sh                         -- This setup script
│   └── .instructions/                   -- AI usage instructions for setup
└── README.md
```

## Pipeline Overview

1. **Add Requirement** -- Describe a feature; AI writes structured YAML
2. **Promote** -- Tooling validates and moves to canonical set
3. **Diff** -- Compare current requirements vs app manifest
4. **Plan** -- AI reads diff + code, produces implementation plan
5. **Execute** -- AI implements code, updates manifest
6. **Fix** -- AI fixes any startup errors (if needed)
7. **Verify** -- E2E tests confirm acceptance criteria

See `instructions/explanation.txt` for the full detailed guide.

## Tooling

All commands use the shared tooling. Resolve the path from `config.yaml → tooling_root`:

```
<config.yaml → tooling_root>/ai-tooling.sh
```

This tooling is application-agnostic. The specs repo provides the application-specific context while the tooling provides the pipeline logic.
