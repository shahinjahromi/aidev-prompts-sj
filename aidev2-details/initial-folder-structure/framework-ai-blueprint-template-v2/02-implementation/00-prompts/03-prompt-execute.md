# Execute implementation plan

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml`.
2. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.
3. Pre-read (BEFORE inspecting source):
   - `02-implementation/01-implementations/<IMPLEMENTATION_ID>/ai-app-hints.yaml` (if it exists)

## Inputs (read-only)
- **Plan:** `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.yaml`
- **Structured diff:** `02-implementation/01-implementations/<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`
- **paths.yaml:** `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml`
- **Contracts & models:** `01-requirements/03-current/models_and_contracts.yaml`
- **Timezone:** `config.yaml → variables.timezone`

## Role
Implement the changes in the plan. Only modify files/folders within the plan's scope.

## Execution order
1. Init `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/results.yaml` with `start_datetime`, `total_diffs`, `implemented_diffs: 0`.
2. Read `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml` — source of truth for roots.
3. Read `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.yaml` — note steps per change.
4. For each requirement in the plan:
   a. Implement code within scope.
   b. If requirement includes DB-schema MAC work, complete runtime DB alignment + schema verification first.
   c. Update the app manifest (path from `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`): append requirement_baseline entry.
   d. Re-run diff verification.
   e. Increment implemented_diffs.
   f. Continue to next requirement.
5. Continue until `remaining_diffs: 0` or blockers recorded.

## Critical rules
1. Code first, then manifest. Never add a requirement_id before its code exists.
2. One at a time. Add each requirement_id to manifest only after that requirement's code is implemented.
3. No bulk manifest updates. No speculative entries.
4. Execution incomplete while diff has remaining items.
5. For DB-schema MAC items, do NOT mark implemented until schema verification evidence exists.
6. Record DB verification in `results.yaml` when DB gate is required:
   - `db_schema_verification.verified: true`
   - `db_schema_verification.evidence`: command output references (array/string)
7. Never write resolved secret values to blueprint artifacts, prompts, plan files,
   manifest files, requirement files, or logs.

## After implementation
- Finalize `results.yaml`.
- Confirm touched runtimes start/compile cleanly.
- Archive plan to history.
