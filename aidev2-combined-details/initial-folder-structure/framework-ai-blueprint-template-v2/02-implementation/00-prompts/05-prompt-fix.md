# Fix startup / build errors

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml`.
2. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.
3. Pre-read (BEFORE inspecting source):
   - `02-implementation/01-implementations/<IMPLEMENTATION_ID>/ai-app-hints.yaml` (if it exists)

## Context (read before fixing)
- Plan: `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.yaml`
- Library interfaces: `02-implementation/01-implementations/<IMPLEMENTATION_ID>/04-extract-library-interfaces/ref-library-methods.yaml`
- Execution paths: `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml`

## Fix rules
- Use terminal output to identify the failure.
- Iterate until the startup script (resolve from `config.yaml → implementations.<IMPLEMENTATION_ID>.startup_script`) runs cleanly.
- Missing dependency? Add to workspace dependency manifest first.
- Library usage/typing issue? Consult `ref-library-methods.yaml`.
- DB/migration/schema mismatch error? Fix migration/DDL and data-layer alignment before startup retry.
- Keep fixes consistent with plan scope and intent.
- No unrelated changes beyond what resolves the errors.
