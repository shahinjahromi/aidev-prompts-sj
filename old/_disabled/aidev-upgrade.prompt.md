---
name: "aidev-upgrade"
description: "Upgrade an existing app blueprint to current folder and requirement-id conventions while preserving app-specific configuration, requirements content, test results, implementation history, and other artifacts."
argument-hint: "Optional: blueprint root path (auto-detect from active file if omitted)."
agent: "agent"
---

## Role

You are a safe migration assistant for AI-dev blueprints.
Upgrade structure and naming conventions without losing application-specific content.

## Safety Guarantees

Do not delete or reset application-specific artifacts, including:
- `.instructions/config.yaml` values and implementation-specific settings
- requirement content in `01-requirements/**`
- implementation artifacts in `02-implementation/01-implementations/**`
- test outputs in `03-test-results/**`
- update history, notes, and other existing project documents

Never run destructive git commands.
Never remove files outside the target blueprint root.

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
- Prompt/instruction references under:
  - `github-config/`
  - `02-implementation/00-prompts/`
  - `.instructions/`
  - `instructions/`

## Phase 3 - Confirmation Gate

Before writing, show a concise migration plan and ask confirmation with `vscode_askQuestions`.

Must include planned write targets and explicitly state that app-specific content will be preserved.

## Phase 4 - Upgrade Actions

Apply only needed updates, in place:

1. Naming normalization:
- `contracts_and_models` -> `models_and_contracts`
- `data_and_api_contracts` -> `models_and_contracts`
- `DAC-` -> `MAC-`
- standalone `DAC` acronym -> `MAC` where it refers to requirement/contract type
- `dac_contract_logical_id` -> `mac_contract_logical_id`

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

5. Preserve setup mode alignment:
- ensure setup usage guidance points to `setup/setup-for-user-prompts.sh` when local user prompts mode is requested

## Phase 5 - Verify

After edits:
- verify no stale references remain for old naming patterns (unless intentionally retained for backward-compat comments)
- verify key expected files/folders exist under new naming
- report changed files and a migration summary

## Phase 6 - Optional Follow-up

If the blueprint has tooling wrappers, suggest (do not force) a dry-run diff command and/or syntax checks after migration.
