---
name: "aidev2-upgrade"
description: "Upgrade an existing app blueprint to current folder and requirement-id conventions while preserving app-specific configuration, requirements content, test results, implementation history, and other artifacts."
argument-hint: "Optional: blueprint root path (auto-detect from active file if omitted)."
agent: "agent"
---

## Role

You are a safe migration assistant for AI-dev blueprints.
Upgrade structure and naming conventions without losing application-specific content.

Scope expectation:
- transform existing pending/current requirement artifacts to current naming conventions in place
- include contracts catalogs, contract spec folders, and UI contract references where present
- preserve semantic requirement content while normalizing identifiers and field names
- enforce ID formatting for requirement/contract artifacts as `<TYPE>-<7-digit-sequence>-<short-title>`

## Safety Guarantees

Do not delete or reset application-specific artifacts, including:
- `.instructions/config.yaml` values and implementation-specific settings
- requirement content in `01-requirements/**`
- implementation artifacts in `02-implementation/01-implementations/**`
- test outputs in `03-test-results/**`
- update history, notes, and other existing project documents

Never run destructive git commands.
Never remove files outside the target blueprint root.
Never delete obsolete v1 prompt/instruction files — only notify the user to review and remove them.

## Phase 1 - Detect and Validate Blueprint Root

Detect `BLUEPRINT_ROOT` from active file by walking up to the first folder containing:
- `01-requirements`
- `02-implementation`
- `03-test-results`

If not found, ask user for absolute blueprint path.

## Phase 2 - Baseline Inventory (Read-only)

Inspect and summarize:
- Existing requirement type files in pending/current
- Contract catalog filename and contract-spec folder names
- Presence of old/new naming conventions:
  - `contracts_and_models` vs `models_and_contracts`
  - `data_and_api_contracts` vs `models_and_contracts`
  - `DAC-` vs `MAC-`
  - `dac_contract_logical_id` vs `mac_contract_logical_id`
- ID format compliance and outliers for:
  - requirement IDs (`FR-*`, `NFR-*`)
  - technology IDs (`TS-*`)
  - models/contracts IDs (`MAC-*`)
  - UI contract IDs (`UIC-*`)
  - acceptance IDs (`AC-*`, `AT-*`)
  - contract logical IDs (`CONTRACT-*`)
- Prompt/instruction references under:
  - `github-config/`
  - `02-implementation/00-prompts/`
  - `.instructions/`
  - `instructions/`
- Obsolete v1 prompt/instruction artifacts (superseded by user-level aidev2 prompts):
  - `02-implementation/00-prompts/` — v1 implementation step prompts, replaced by `aidev2-steps/implement/`
  - `github-config/aidev-*.prompt.md` — v1 framework prompts, replaced by `.github/prompts/aidev2-*.prompt.md` wrappers
  - `github-config/aidev-framework.instructions.md` — v1 framework instructions, replaced by user-level `aidev2-*.instructions.md`
  - `instructions/` — v1 documentation folder
  Note: `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are NOT obsolete — aidev2 reads both.
- App manifest compliance: locate via `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`; check whether each `requirement_baseline` entry has `e2e_test_status`, `implementation_initial_date`, `implementation_last_date`

## Phase 3 - Write Targets

Before writing, show a concise migration plan and proceed without asking for confirmation.

Must include planned write targets and explicitly state that app-specific content will be preserved.

## Phase 4 - Upgrade Actions

Apply only needed updates, in place:

1. Naming normalization:
- `contracts_and_models` -> `models_and_contracts`
- `data_and_api_contracts` -> `models_and_contracts`
- `DAC-` -> `MAC-`
- standalone `DAC` acronym -> `MAC` where it refers to requirement/contract type
- `dac_contract_logical_id` -> `mac_contract_logical_id`

ID format normalization:
- convert IDs to the pattern `<TYPE>-<7-digit-sequence>-<short-title>`
- examples: `FR-0000001-credit-platform-ui-placeholder`, `FR-0000001-credit-platform-ui-placeholder-v2`, `NFR-0000002-code-quality`, `TS-0000007-angular-framework`, `MAC-0000001-marqueta-credit-platform`, `UIC-0000001-authenticated-app-shell`, `AC-0000004-placeholder-ui-render`, `AT-0000004-verify-placeholder-navigation`, `CONTRACT-0000001-marqueta-credit-platform`
- short-title format: lowercase kebab-case, concise semantic slug, no spaces/underscores
- preserve meaning while normalizing order and numeric width; move numeric sequence immediately after type code
- update cross-references when an ID changes (e.g., `replaces_id`, `specific_ids`, `contract_refs`, related requirement/UI links)

Reference integrity requirements (mandatory):
- build an old->new ID mapping for every rewritten ID and apply it everywhere in scope
- update reference fields including (as applicable): `requirement_id`, `replaces_id`, `related_requirement_ids`, `related_uic_ids`, `contract_refs`, `specific_ids`, `implements_contract_ids`, `consumes_upstream_contract_ids`, `contract_id`, and manifest/baseline references
- update any string references in merged/current requirement views that embed rewritten IDs
- do not complete migration if any stale old IDs remain in scoped files

Apply these updates across both pending and current requirement artifacts, including:
- `functional_requirements.yaml`
- `non_functional_requirements.yaml`
- `technology_selection.yaml`
- contracts catalog files and contract spec references
- UI contract references and traceability links when they point to renamed contract identifiers

2. File/folder normalization when old names exist:
- `01-requirements/01-pending-promotion/contracts_and_models.yaml` -> `models_and_contracts.yaml`
- `01-requirements/03-current/contracts_and_models.yaml` -> `models_and_contracts.yaml`
- `01-requirements/01-pending-promotion/contracts_and_models/` -> `models_and_contracts/`
- `02-implementation/02-implementation-mapping/contracts_and_models.yaml` -> `models_and_contracts.yaml`
- `.schemas/contracts/contracts_and_models.json` -> `models_and_contracts.json`

3. Structured diff compatibility:
- ensure pending `structured-diff.yaml` includes `models_and_contracts_diff` with `created/updated/removed`

4. Keep content and history:
- do not remove requirement entries
- do not clear diff history files
- do not delete implementation/test history folders

5. Manifest schema upgrade:
- Locate the app manifest from `BLUEPRINT_ROOT/.instructions/config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`.
- For each `requirement_baseline` entry missing `e2e_test_status`, add `e2e_test_status: NOT_TESTED`.
- Do NOT add `implementation_initial_date` or `implementation_last_date` — these are populated by IM-04 Execute.
- Validate the manifest shape against the local schema at `/home/parallels/.config/Code/User/prompts/aidev2-schemas/requirements_manifest.json`.
- Timezone for any existing date fields comes from `config.yaml → variables.timezone`.

6. Preserve setup mode alignment:
- ensure setup usage guidance points to `setup/setup-for-user-prompts.sh` when local user prompts mode is requested

Use hidden detailed step files for execution:
- `/home/parallels/.config/Code/User/prompts/aidev2-steps/upgrade/01-detect-root.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-steps/upgrade/02-inventory.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-steps/upgrade/03-confirm.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-steps/upgrade/04-transform.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-steps/upgrade/05-verify.md`
- `/home/parallels/.config/Code/User/prompts/aidev2-steps/upgrade/06-report.md`

## Phase 5 - Verify

After edits:
- verify no stale references remain for old naming patterns (unless intentionally retained for backward-compat comments)
- verify key expected files/folders exist under new naming
- verify IDs are normalized to `<TYPE>-<7-digit-sequence>-<short-title>` where applicable, with references updated consistently
- verify no dangling references exist (every rewritten ID must resolve to an existing target definition)
- if unresolved references remain, stop and report blockers instead of declaring success
- report changed files and a migration summary

## Phase 6 - Notify Obsolete v1 Artifacts

After verification, scan for v1 prompt/instruction artifacts that are superseded by user-level aidev2 prompts.
Do NOT delete these files. Instead, list them in the migration report and tell the user they can safely remove them.

Obsolete paths to check:
- `BLUEPRINT_ROOT/02-implementation/00-prompts/` — entire directory (replaced by user-level `aidev2-steps/implement/`)
- `BLUEPRINT_ROOT/github-config/aidev-*.prompt.md` — v1 prompt files (replaced by `.github/prompts/aidev2-*.prompt.md`)
- `BLUEPRINT_ROOT/github-config/aidev-framework.instructions.md` — v1 framework instructions
- `BLUEPRINT_ROOT/instructions/` — v1 documentation folder
Note: `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are NOT obsolete — aidev2 reads both.

Only report paths that actually exist. Group them under a clear "Obsolete v1 files — safe to remove" heading.
Also report the manifest upgrade summary: whether `e2e_test_status` was added to any entries, and remind user that date fields are set during IM-04 Execute.

## Phase 7 - Optional Follow-up

If the blueprint has tooling wrappers, suggest (do not force) a dry-run diff command and/or syntax checks after migration.
