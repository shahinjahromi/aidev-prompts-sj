# Generate implementation plan

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml`.
2. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.
3. Pre-read (BEFORE inspecting source):
   - `02-implementation/01-implementations/<IMPLEMENTATION_ID>/ai-app-hints.yaml` (if it exists)

## Inputs (read-only, do not regenerate)
- **Structured diff:** `02-implementation/01-implementations/<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`
- **Contracts & models:** `01-requirements/03-current/models_and_contracts.yaml`
- **Technology selection:** from structured diff `technology_selection`
- **Manifest:** resolve from `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`
- **Timezone:** `config.yaml → variables.timezone`

## Role
Generate an actionable plan from the structured diff. Every change must specify exactly what will be done and which files are in scope.

## NFR-COD-* handling
1. Read all NFRs from `01-requirements/03-current/nfr_and_global_cr.yaml`.
2. Check the diff for NFR-COD items in `created`/`updated`/`removed`.
3. Include every NFR whose version ≤ manifest's `requirements_version_target`.

Rules:
- **New NFR-COD in diff (`created`):** plan a change entry; apply to all code written/modified; manifest after implementation.
- **No new NFR-COD in diff:** existing NFRs already manifested — apply only to new/changed code.
- **NFRs are mandatory.** Violating code is not acceptable.
- Add `standing_nfr_and_global_cr_constraints` in `plan_metadata` listing all applicable NFR IDs + summaries.
- Each change's `implementation_steps` must note which NFRs apply.

## Preserve existing behavior (CRITICAL)
Only plan changes the diff requires. Do NOT alter existing methods, classes, or logic unless the diff + code necessarily imply that change.

## Database contract alignment (CRITICAL)
If structured diff contains DB schema MAC updates (resolve the contract logical ID from config.yaml → implementations.<ID>.database_contract_alignment.mac_contract_logical_id, or `physical_database_schema`):
- Add explicit plan steps for runtime DB alignment (migration/DDL artifacts + data access layer updates).
- Include impacted schema contract file(s) from current MAC metadata.
- Include a validation step that verifies runtime schema matches promoted SQL contract.
- Do NOT allow plan completion with contract-file-only changes.

## Outputs
Write to the **implementation subfolder**:
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.yaml`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.md`
- `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml`

## Per-change fields (every change from the diff)

| Field | Description |
|-------|-------------|
| change_id | requirement_id from diff |
| requirement_delta | created / modified / removed |
| business_intent | short theme |
| what_will_be_changed | detailed description |
| acceptance_criteria | nested ACs/ATs from the requirement |
| scope_for_this_change | files/folders for this change only |
| impacted_files | concrete paths from code analysis |
| impacted_symbols | classes, functions, components, routes, schemas |
| type_of_change | add / modify / remove / refactor |
| implementation_steps | concrete steps; note which NFRs apply |
| expected_behavior_after_change | acceptance outcome |
| dependencies_and_side_effects | impact on other features |
| risk_level | low / medium / high |
| validation | tests, linters, manual_checks |
| open_questions_or_assumptions | list or "None" |

## Manifest rule
Do NOT add requirement_ids to the manifest during planning. Code must exist first.

After generating the plan, run /summarize.
