# aidev2 Pipeline — Process Overview

This file is read automatically by Agentic AI before responding. It is the canonical AI entry-point for the aidev2 AI-assisted software engineering framework.

## What aidev2 Does

aidev2 is a structured pipeline for managing requirements and implementing them into application code using AI agents. It keeps requirements, diffs, implementation plans, and test artifacts versioned under a dedicated blueprint repository per application.

## Pipeline Stages and Prompt Order

| Step | Prompt | Purpose | Key Inputs | Key Outputs |
|------|--------|---------|------------|-------------|
| 01 | `/01-aidev2-setup-app` | Create blueprint + app repo pair from template | `app-slug`, `impl-suffix` | `<slug>-ai-blueprint/`, `<slug>-<impl-suffix>/`, `.instructions/config.yaml`, `.aidev/requirements/requirements-state.yaml` |
| 02 | `/02-aidev2-requirements` | Author, promote, and reconcile requirements | Blueprint root, requirement description | Pending requirements YAML in `01-requirements/01-pending-promotion/`, current requirements in `01-requirements/03-current/`, merged file in `01-requirements/03-current/merged/` |
| 03 | `/03-aidev2-implement` | Diff requirements → plan → execute → test | Blueprint root, implementation id | Diff manifest in `01-requirements/02-diff/`, plan artifact, implemented code in app repo, test results in `03-test-results/` |
| 04 | `/04-aidev2-upgrade` | Migrate existing blueprint to current conventions | Blueprint root | Updated folder structure and naming, no semantic content loss |
| 05 | `/05-aidev2-all-steps` | Full supervised pipeline in one run: requirements → diff → plan → execute → interfaces → fix → tests | Blueprint root, requirements | All artifacts from steps 02–03 |
| 06 | `/06-aidev2-backup-prompts` | Back up user prompts folder to Git | User prompts path | Committed backup in `aidev2-prompts-backup` repo |
| 07 | `/07-aidev2-instructions-cache` | Refresh cached instruction context for faster runs | — | Updated instruction cache |

## Implementation Sub-steps (inside `/03-aidev2-implement`)

`01-diff` → `02-plan` → `03-execute` → `04-extract-interfaces` → `05-fix` → `06-create-tests` → `07-run-tests`

Run ranges like `02-07` to skip diff if it already exists.

## Key Directory Layout (Blueprint Root)

```
01-requirements/
  01-pending-promotion/     ← authored requirements awaiting promotion
  02-diff/                  ← diff manifests
  03-current/               ← promoted requirements + merged YAML
    merged/merged_requirements.yaml
02-implementation/
  01-implementations/<impl-id>/   ← per-implementation artifacts
  02-implementation-mapping/      ← cross-cutting mapping files
03-test-results/<impl-id>/        ← acceptance test outputs
.instructions/
  config.yaml               ← app identity, impl mapping, tooling root, variables
  codebase-context.yaml     ← optional tech/port hints for AI
```

App repo layout (relative to `APP_ROOT`):
```
.aidev/
  requirements/
    requirements-state.yaml   ← implementation manifest (iteration, baseline, version tracking)
```

## How to Navigate

- **Starting a new app** → use `/01-aidev2-setup-app`
- **Adding or updating requirements** → use `/02-aidev2-requirements 01-author` then `02-promote`; authoring is design-first: define models, contracts, and UI contracts before or alongside functional requirements
- **Implementing requirements** → open any file in the blueprint repo, then use `/03-aidev2-implement 01-diff` (or a later step if diff exists)
- **Scope implementation to one module** → pass the module name as a filter argument to `/03-aidev2-implement` so only diff entries with that module property are processed
- **Something broke** → use `/03-aidev2-implement 05-fix`
- **Full fresh run** → use `/05-aidev2-all-steps`

## Preset Requirements (Core-Stack Defaults)

Per-stack NFR and technology selections live in:

```
aidev2-details/preset-requirements/
  nfr-and-global-cr-by-core-stack/<stack>/nfr-and-global-cr-<impl-id>.yaml
  tech_selections_by-core-stack/<stack>/technology-selection-<impl-id>.yaml
```

Copy the placeholder template file for your implementation ID when setting up a new implementation.

## Execution Optimization Strategy

The following rules govern how the framework executes for speed and output quality. These are prescriptive — they describe what the framework does.

- **Agent routing**: The dispatcher agent routes each pipeline stage to its specialist subagent (requirements-specialist, planning-specialist, implementation-specialist, validation-specialist, testing-specialist). Specialist agents do not re-route to each other — they execute their scoped stage and return a single handoff payload to the dispatcher.
- **Subagent communication pattern**: The dispatcher invokes a specialist via `runSubagent`. The specialist executes its full stage and returns exactly one structured `handoff` payload message. The dispatcher reads that payload and either continues to the next stage (on `status: pass`) or stops and reports blockers to the user (on `status: blocked` or `status: fail`). The dispatcher shall not pass full prompt or instruction file contents as input — only `requirement_ids`, `step_tokens`, artifact paths, and key check results.
- **Plan-before-execute gate**: The diff artifact must exist and be non-empty before planning begins. The plan artifact must exist and have been reviewed before execution begins. The dispatcher enforces both gates and stops the pipeline if either is not satisfied.
- **Read efficiency**: Agents shall use targeted file reads and exact-match searches when the file path is already known. Semantic search shall not be used when a path is deterministic. Broad workspace scans are prohibited when a targeted read would suffice.
