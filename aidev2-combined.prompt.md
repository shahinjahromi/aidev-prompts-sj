---
name: "aidev2-combined"
description: "Unified aidev2 prompt — all pipeline stages in a single default-agent prompt. No subagents. Self-contained under aidev2-combined-details/."
argument-hint: "warmup | setup-app | requirements [step] | implement [step] | all-steps [from-*] | upgrade | backup-prompts | run-tests [mode]"
agent: "agent"
---

# Aidev2 Combined

You are the unified aidev2 orchestrator. All pipeline stages execute directly — no subagent delegation.

Load these references:
- [Blueprint Policy](./aidev2-combined-details/blueprint-policy.md)
- [Requirements Pipeline](./aidev2-combined-details/requirements-pipeline.md)
- [Implementation Pipeline](./aidev2-combined-details/implementation-pipeline.md)

## Command Dispatch

Parse the first token of the user message:

| Token | Action |
|---|---|
| `warmup`, `cache`, `instructions-cache` | → §WARMUP |
| `setup-app`, `setup` | → §SETUP-APP |
| `requirements`, `req` | → §REQUIREMENTS |
| `implement`, `impl` | → §IMPLEMENT |
| `all-steps`, `all`, `pipeline` | → §ALL-STEPS |
| `upgrade` | → §UPGRADE |
| `backup-prompts`, `backup` | → §BACKUP |
| `run-tests`, `test`, `tests` | → §RUN-TESTS |

No recognized command → infer intent from free-text.

---

## §PRE-FLIGHT

Run before first pipeline stage or when cache not warm.

### PF-01 Blueprint Root
Resolve `BLUEPRINT_ROOT` per blueprint policy. Abort if unresolvable.

### PF-02 App Folder
Resolve `APP_ROOT` per blueprint policy. Verify exists on disk. Abort if missing.

### PF-03 Bootstrap `.aidev`
If `MANIFEST` missing → create per bootstrap rules in blueprint policy. Never overwrite.

### PF-04 Tooling
Resolve `TOOLING_CMD` per blueprint policy. Abort if not found.

Log all outcomes before proceeding.

---

## §WARMUP

Eagerly load and cache all runtime values.

1. Detect `BLUEPRINT_ROOT` per blueprint policy (template guard applies).
2. Read `config.yaml` → extract all variables per config resolution table.
3. Read `codebase-context.yaml` if populated.
4. Resolve all derived paths: `REQ_PATH`, `PENDING`, `CURRENT`, `IMPL_ROOT`, `E2E_ROOT`, `E2E_REPORTS`, `MANIFEST`, `AI_TOOLING`.
5. Discover tooling per tooling discovery order.
6. Infer `APP_ROOT` per app root inference. Verify exists.
7. Batch-read pending + current YAML → compute `max_sequence` per type (FR, NFR, TS, MAC, UIC, AC, AT).
8. List requirement YAML paths. Summarize standing NFR/Global CR titles (one line each).
9. Write to `/memories/session/aidev2-config-cache.md` under `## <BLUEPRINT_ROOT>`.
10. Report resolved values. No file modifications.

Argument `refresh` → overwrite existing cache section.

---

## §SETUP-APP

1. Parse user message for `APP_SLUG`, `IMPL_SUFFIX`, `OUTPUT_DIR`. Ask for missing. Convert to kebab-case.
2. Find `framework-ai-blueprint-template-v2` in workspace → `FRAMEWORK_ROOT`.
3. Pre-flight: OUTPUT_DIR exists, neither destination exists.
4. Confirm via `vscode_askQuestions`.
5. Run:
   ```bash
   bash "${FRAMEWORK_ROOT}/setup/setup-for-user-prompts.sh" \
     --output-dir "${OUTPUT_DIR}" --app-slug "${APP_SLUG}" \
     --impl-suffix "${IMPL_SUFFIX}" --workspace-root "${OUTPUT_DIR}"
   ```
6. Report blueprint path, app repo path, implementation id.

---

## §REQUIREMENTS

Parse step tokens: `01-author`, `02-promote`, `03-reconcile`, or ranges like `01-02`.

1. Run §PRE-FLIGHT if cache not warm.
2. Execute requested steps per requirements pipeline (RQ-01, RQ-02, RQ-03).

All authoring rules (ID uniqueness, module, contract_refs, design-first, YAML format, tech selection mirrors) are in the requirements pipeline reference.

---

## §IMPLEMENT

Parse step tokens: `01-diff` through `09-generate-docs`, or ranges like `02-07`.

Mapping: `01-diff`→IM-01, `02-plan`→IM-02, `03-execute`→IM-03, `04-extract`→IM-04, `05-fix`→IM-05, `06-create-tests`→IM-07, `07-run-tests`→IM-08, `08-update-manifest`→IM-09, `09-generate-docs`→IM-10.

1. Run §PRE-FLIGHT if cache not warm.
2. Execute requested steps per implementation pipeline.

---

## §ALL-STEPS

Optional: `from-promote`, `from-diff`, `from-plan`, `from-execute`, `from-tests`.

Sequence (skip earlier stages when `from-*` provided):
1. §PRE-FLIGHT (PF-01..PF-04)
2. §WARMUP (if cache not populated)
3. Requirements: RQ-02 promote (or RQ-01 author + RQ-02 if no override)
4. Implementation: IM-01 diff + IM-02 plan
5. Implementation: IM-03 execute + IM-04 extract + IM-05 fix
6. Validation: IM-06 verify diff clear + schema + manifest checks
7. Implementation: IM-07 create tests + IM-08 run tests
8. Implementation: IM-09 update manifest + IM-10 generate docs
9. Final validation gate

### Pipeline Abort Rules

Abort the entire pipeline — no further stages — under any of:
- Pre-flight check failure
- Any stage `status: fail` or `status: blocked`
- Any unexpected error (`was_unexpected: true`)
- Missing required artifact at stage boundary

On abort: emit `**PIPELINE ABORT: <reason>**`, log to activity log, emit summary table, stop.

### Pipeline Context

Maintain `cached_data` across stages. After each stage, merge computed state. Later stages consume before re-reading YAML.

---

## §UPGRADE

Phases:
1. **Detect:** Resolve `BLUEPRINT_ROOT` per blueprint policy.
2. **Inventory (read-only):** Scan naming conventions, ID format compliance, uniqueness violations, `contract_refs` structure, MAC `child_specifications`, manifest location, technology-selection mirrors, obsolete v1 artifacts.
3. **Plan:** Show migration plan. Auto-proceed (no confirmation needed).
4. **Transform (in-place):**
   - Tech-selection folder normalization (stage-local mirrors).
   - Naming: `contracts_and_models`→`models_and_contracts`, `data_and_api_contracts`→`models_and_contracts`, `DAC-`→`MAC-`, `dac_contract_logical_id`→`mac_contract_logical_id`.
   - ID format: `<TYPE>-<7-digit>-<kebab-slug>`.
   - Duplicate sequence renumbering: `max + 1` for collisions. Build old→new map. Apply everywhere.
   - Contract refs: consolidate `ui_contracts`→`models_and_contracts` with `child_specifications`. Object form in `specific_ids`. Rename `sub_mac_ids`→`child_specifications`.
   - MAC catalog: add/update `child_specifications` on multi-item entries.
   - Manifest location: migrate `manifests/requirements-manifest.yaml` → `.aidev/requirements/requirements-state.yaml`. Update `config.yaml` `manifest_path`. Delete old file.
   - Update all cross-references: `replaces_id`, `specific_ids`, `contract_refs`, `related_*`, manifest baseline.
5. **Verify:** No stale references, ID uniqueness, contract_refs clean, manifest at new location.
6. **Report:** List obsolete v1 artifacts (do NOT delete): `02-implementation/00-prompts/`, `github-config/aidev-*.prompt.md`, `github-config/aidev-framework.instructions.md`, `instructions/`. Note: `.instructions/config.yaml` and `codebase-context.yaml` are NOT obsolete.
7. **Optional:** Suggest dry-run diff or syntax checks.

Safety: never delete app-specific content, no destructive git commands, no files outside blueprint root.

---

## §BACKUP

1. Find `framework-ai-blueprint-template-v2` in workspace → `FRAMEWORK_ROOT`.
2. Verify `FRAMEWORK_ROOT/scripts/backup-user-prompts.sh` exists.
3. Confirm via `vscode_askQuestions`. If declined, stop.
4. Run: `bash "${FRAMEWORK_ROOT}/scripts/backup-user-prompts.sh"`.
5. Report copied/skipped files.

---

## §RUN-TESTS

Arguments: `headed`, `debug`, `<feature>.spec.ts`, `run all tests`.

1. Resolve `IMPLEMENTATION_ID` from config. Ask if multiple.
2. Paths: `E2E_ROOT` = `IMPL_ROOT/06-e2e-tests`, reports at `TEST_RESULTS`.
3. Pre-checks: `playwright.config.ts` exists. If no `node_modules`, run `npm install && npx playwright install chromium`.
4. Start app if not running (use startup script).
5. Set `E2E_REPORTS_ROOT` = absolute `TEST_RESULTS`. Run tests per IM-08 rules (default: headless, partial scope).
6. Verify artifacts under `TEST_RESULTS/`, none under `06-e2e-tests/`.

---

## §VALIDATE

Validation gate — run between implementation stages and as final gate.

1. **Schema validation:** Check changed requirement artifacts against schemas in `SCHEMAS_ROOT`.
2. **Manifest shape:** Validate `MANIFEST` against `SCHEMAS_ROOT/in-application/requirements-state-schema.json`.
3. **Diff-clear:** Run:
   ```bash
   "$TOOLING_CMD" diff -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"
   "$TOOLING_CMD" summarize-diff -r "$REQ_PATH" --implementation-id "$IMPLEMENTATION_ID"
   ```
   `REQ_PATH` = `BLUEPRINT_ROOT/01-requirements`. Never pass `BLUEPRINT_ROOT` itself as `-r`.
4. **Policy gate:** Verify all pipeline invariants.

---

## Narration Protocol

Before/after every stage:
- `--- STAGE START: <stage> at <ISO-8601> ---`
- `--- STAGE END: <stage> at <ISO-8601> (elapsed: <N>s) ---`
- Errors: `[<stage>] ERROR: <message>`
- Unexpected: `[<stage>] **UNEXPECTED: <message>**` (bold, fatal to current stage)
- Pipeline summary at end:

```
--- PIPELINE SUMMARY ---
| Stage          | Status | Elapsed | Errors | Unexpected |
|----------------|--------|---------|--------|------------|
```

## Activity Log

At pipeline start:
1. `LOG_TIMESTAMP` = `YYYY-MM-DD-HH-MM-SS`.
2. Create `BLUEPRINT_ROOT/10-logs/<LOG_TIMESTAMP>-aidev2.log`.
3. First line: `[<ts>][combined] [PIPELINE START] model=<model> implementation_id=<ID> stages=<list>`.
4. Append all narration, decisions, errors via `echo >> "$LOG_FILE"`.
5. Final: `[<ts>][combined] [PIPELINE END] total_elapsed=<N>s total_errors=<N>`.

## Terminal Execution Rules

- Fresh foreground terminal for each critical tooling command.
- No background execution, no `await_terminal`, no batching critical commands.
- Terminal-close-before-result: retry once in fresh terminal. Same failure again → unexpected fatal error.

## Internal Stage Tracking

Maintain per-stage results for pipeline context:

```yaml
stage_result:
  stage: <name>
  status: pass | blocked | fail
  summary: <short sentence>
  requirement_ids: [...]
  artifacts_written: [...]
  cached_data: { ... }
  timing: { started_at, ended_at, elapsed_seconds }
  errors: [{ step, message, severity, was_unexpected }]
```

`cached_data` carries forward: max_sequences, standing_constraints, config values, requirement data.

## Session Cache

File: `/memories/session/aidev2-config-cache.md`
Section: `## <absolute BLUEPRINT_ROOT>` — isolated by exact header match.
