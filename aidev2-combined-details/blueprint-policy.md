# Blueprint Policy

Source of truth for path resolution, config extraction, infrastructure discovery, and shared output rules.

## YAML Output Rules

All YAML written by this prompt must follow:
- 2-space indent. Never tabs.
- Block style only (`|`/`>`). No inline `{key: value}` or `[a, b]`.
- Quote strings containing `{}[]:#&*!|>'"` backtick `%@`.
- No trailing whitespace. Single newline at EOF.

## Blueprint Root Detection

Walk up from `${file}`. First ancestor containing ALL of `01-requirements`, `02-implementation`, `03-test-results` → `BLUEPRINT_ROOT`.

Template guard: if directory contains `setup/setup.sh` without `02-implementation/01-implementations`, it's the framework template — stop and ask user to open an app blueprint file.

## Config Resolution

Read `BLUEPRINT_ROOT/.instructions/config.yaml` early in every run.

| Config path | Variable |
|---|---|
| `identity.requirement_set_id` | `REQ_SET_ID` |
| `identity.app_identifier` | `APP_IDENTIFIER` (overrides derived name) |
| `tooling_root` | → `TOOLING_CMD = <tooling_root>/ai-tooling.sh` (relative to BLUEPRINT_ROOT) |
| `implementations.<ID>.implementation_id` | `IMPLEMENTATION_ID` |
| `implementations.<ID>.application_root` | `APP_ROOT` (relative to BLUEPRINT_ROOT) |
| `implementations.<ID>.startup_script` | `STARTUP_HINT` |
| `implementations.<ID>.app_test_startup_script` | `APP_TEST_STARTUP_HINT` |
| `implementations.<ID>.manifest_path` | `MANIFEST` override |
| `implementations.<ID>.database_contract_alignment.enabled` | DB gate flag |
| `implementations.<ID>.database_contract_alignment.mac_contract_logical_id` | DB MAC ID |
| `variables.timezone` | Manifest date timezone (default UTC) |
| `variables.email_fixed` | Fixed test email |
| `variables.email_random_domain` | Random email domain |

Do NOT read other `.instructions/` files. Do NOT read `.schemas/`.

## Codebase Context Resolution

Read `BLUEPRINT_ROOT/.instructions/codebase-context.yaml` when populated (non-placeholder).

Extract under `implementations.<ID>`: `project.*`, `tech_stack.*`, `ports.*`, `env_vars.*`, `npm_scripts.*`, `client_layout`, `server_layout`, `database`, `e2e_tests`.

Usage: prefer populated fields over file-sniffing but verify against actual files. Use `ports` for startup/E2E base URLs. Use `npm_scripts.root.dev` as startup override. Template placeholders count as unpopulated.

## Fixed Layout

All relative to `BLUEPRINT_ROOT`:

| Variable | Path |
|---|---|
| `REQ_PATH` | `01-requirements` |
| `PENDING` | `01-requirements/01-pending-promotion` |
| `PENDING_CONTRACTS` | `01-requirements/01-pending-promotion/models_and_contracts` |
| `PENDING_TECH_DIR` | `01-requirements/01-pending-promotion/technology-selection` |
| `CURRENT` | `01-requirements/03-current` |
| `CURRENT_CONTRACTS` | `01-requirements/03-current/models_and_contracts` |
| `CURRENT_TECH_DIR` | `01-requirements/03-current/technology-selection` |
| `CURRENT_MERGED` | `01-requirements/03-current/merged/merged_requirements.yaml` |
| `DIFF_ROOT` | `01-requirements/02-diff` |
| `IMPL_ROOT` | `02-implementation/01-implementations/<IMPLEMENTATION_ID>` |
| `TEST_RESULTS` | `03-test-results/<IMPLEMENTATION_ID>` |

App-relative:

| Variable | Path |
|---|---|
| `MANIFEST` | `APP_ROOT/.aidev/requirements/requirements-state.yaml` |

Shared assets (infrastructure data files):

| Variable | Path |
|---|---|
| `SCHEMAS_ROOT` | `<USER_PROMPTS>/aidev2-details/aidev2-schemas` |
| `E2E_TEMPLATES` | `<USER_PROMPTS>/aidev2-details/e2e-playwright-templates` |

Where `<USER_PROMPTS>` = `/home/parallels/.config/Code/User/prompts`.

Implementation sub-layout under `IMPL_ROOT`:
`01-delta-current`, `02-plan-current`, `03-plan-execution`, `04-extract-library-interfaces`, `05-fix`, `06-e2e-tests`, `50-delta-history`, `51-plan-history`, `52-plan-execution-history`, `53-update-history`.

Requirement file paths (relative to BLUEPRINT_ROOT):
- `01-requirements/control.yaml`
- `PENDING/functional_requirements.yaml`
- `PENDING/nfr-and-global-cr/nfr_and_global_cr_<IMPLEMENTATION_ID>.yaml`
- `PENDING/technology-selection/technology_selection_<IMPLEMENTATION_ID>.yaml`
- `PENDING/models_and_contracts.yaml`
- `PENDING/models_and_contracts/<spec-files>`
- `CURRENT/functional_requirements.yaml`
- `CURRENT/nfr-and-global-cr/nfr_and_global_cr_<IMPLEMENTATION_ID>.yaml`
- `CURRENT/technology-selection/technology_selection_<IMPLEMENTATION_ID>.yaml`
- `CURRENT/models_and_contracts.yaml`
- `CURRENT/models_and_contracts/<spec-files>`
- `CURRENT/merged/merged_requirements.yaml`

## Implementation Discovery

Derive `APP_IDENTIFIER` from blueprint folder name: strip trailing `-ai-blueprint` or `-blueprint`, else use basename.

List directories under `02-implementation/01-implementations`:
- Exactly one → auto-select.
- Multiple and user didn't specify → ask. Never guess.

## App Root Inference

Resolution order:
1. `config.yaml → implementations.<ID>.application_root` (relative to BLUEPRINT_ROOT)
2. Sibling of BLUEPRINT_ROOT matching `IMPLEMENTATION_ID` exactly
3. Sibling starting with `APP_IDENTIFIER` ending with last segment of `IMPLEMENTATION_ID`
4. Multiple candidates → ask. None → ask.

**Validation (REQ-053):** Verify directory exists on disk. Missing → **abort** (never create app repo).

Derived paths after resolution:
- `MANIFEST` = `APP_ROOT/.aidev/requirements/requirements-state.yaml`
- `E2E_ROOT` = `IMPL_ROOT/06-e2e-tests`
- `E2E_REPORTS` = `BLUEPRINT_ROOT/03-test-results/<IMPLEMENTATION_ID>`

## Bootstrap `.aidev` Files (REQ-054)

When `APP_ROOT` exists but `MANIFEST` doesn't:
1. Create `APP_ROOT/.aidev/requirements/` directory.
2. Write `requirements-state.yaml`:
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
3. Never overwrite existing file.

## Tooling Discovery

Search for `framework-ai-development-tooling/ai-tooling.sh`:
1. Workspace root folders (preferred)
2. `BLUEPRINT_ROOT/../framework-ai-development-tooling/ai-tooling.sh`
3. Ancestor walk from BLUEPRINT_ROOT
4. Not found → ask user

Set `AI_TOOLING` = parent directory, `TOOLING_CMD` = `$AI_TOOLING/ai-tooling.sh`.

## Startup Heuristics

Order: (1) `APP_ROOT/scripts/local-dev.sh` (2) `scripts/start.sh` (3) `scripts/dev.sh` (4) `package.json` → `npm run dev`/`start`/`serve` (5) blank — ask when needed.

## Tech Stack Heuristics

- Framework config + `package.json` → `npm | client: <framework> application`
- `package.json` only → `npm | node application`
- `go.mod` → `go application`
- `pom.xml` → `JVM/maven application`
- `Cargo.toml` → `compiled binary application`
- Uncertain → `(not yet inferred)`

## Session Cache

File: `/memories/session/aidev2-config-cache.md`
Section header: `## <absolute BLUEPRINT_ROOT>` — isolated by exact header match.
Contents: all resolved variables, requirement file paths (names only), and directory listings. Does NOT contain YAML content, max sequences, or requirement summaries — those are read fresh by the stages that need them.
