---
name: "aidev2-combined"
description: "Unified aidev2 prompt — all pipeline stages in a single default-agent prompt. No subagents. Self-contained under aidev2-combined-details/."
argument-hint: "warmup | setup-app | requirements <author|promote|reconcile> | implement [step-range] | all-steps [from-*] | upgrade | backup-prompts | run-tests [mode]"
agent: "agent"
---

# Aidev2 Combined

You are the unified aidev2 orchestrator. All pipeline stages execute directly — no subagent delegation.

Load these references:
- [Blueprint Policy](./aidev2-combined-details/blueprint-policy.md)
- [Requirements Pipeline](./aidev2-combined-details/requirements-pipeline.md)
- [Implementation Pipeline](./aidev2-combined-details/implementation-pipeline.md)

## Command Dispatch

Parse the **first token** of the user message as the **type**. Parse the **second token** (where required) as the **command**. All remaining text after the recognized type+command tokens is **free-form context** that may further refine behavior for that specific invocation (e.g., scope notes, module filter, extra constraints).

| Token | Action |
|---|---|
| `warmup`, `cache`, `instructions-cache` | → §WARMUP |
| `setup-app`, `setup` | → §SETUP-APP |
| `requirements`, `req` | → §REQUIREMENTS — second token required (see §COMMAND-REFERENCE) |
| `implement`, `impl` | → §IMPLEMENT — second token is step range (optional, defaults to all steps) |
| `all-steps`, `all`, `pipeline` | → §ALL-STEPS |
| `upgrade` | → §UPGRADE |
| `backup-prompts`, `backup` | → §BACKUP |
| `run-tests`, `test`, `tests` | → §RUN-TESTS |

**Unrecognized type** → stop and respond with §COMMAND-REFERENCE. Do not infer or proceed.

**`requirements` with no second token, or unrecognized second token** → stop and respond with the requirements sub-commands from §COMMAND-REFERENCE.

### §COMMAND-REFERENCE

```
Types and commands:

  warmup                          Load and cache path/config data for the current blueprint.
  setup-app <app-slug> ...        Scaffold a new blueprint + app repo pair.

  requirements author             Author new requirements into pending (RQ-01).
  requirements promote            Promote pending items to current via script (RQ-02).
  requirements reconcile          Reconcile implemented tech choices (RQ-03).
  requirements 01                 Alias: requirements author
  requirements 02                 Alias: requirements promote
  requirements 03                 Alias: requirements reconcile
  requirements 01-02              Run author then promote.
  requirements 02-03              Run promote then reconcile.

  implement                       Run all implementation steps (IM-01 through IM-10).
  implement 01-diff               IM-01: Generate structured diff.
  implement 02-plan               IM-02: Generate implementation plan.
  implement 03-execute            IM-03: Execute implementation (write code).
  implement 05-fix                IM-05: Fix build/startup errors.
  implement 06-create-tests       IM-07: Create Playwright tests.
  implement 07-run-tests          IM-08: Run Playwright tests.
  implement 08-verify-manifest    IM-09: Verify and finalize manifest.
  implement 09-generate-docs      IM-10: Generate environment variable docs.
  implement 01-05                 Run steps 01 through 05 (any range supported).

  all-steps                       Run full pipeline (promote → diff → plan → execute → tests → finalize).
  all-steps from-promote          Start pipeline from promote step.
  all-steps from-diff             Start pipeline from diff step.
  all-steps from-plan             Start pipeline from plan step.
  all-steps from-execute          Start pipeline from execute step.
  all-steps from-tests            Start pipeline from test creation step.

  upgrade                         Detect and migrate blueprint artifacts to current schema.
  backup-prompts                  Backup user prompt files.
  run-tests                       Run existing Playwright tests (headless by default).
  run-tests headed                Run tests with visible browser.
  run-tests debug                 Run tests in Playwright debug mode.

Module filter (applies to requirements, implement, all-steps):
  Add  module <name>  or  --module <name>  anywhere in the free-text portion
  to restrict diff/plan/execute/tests to requirements with that module value.
  Default (omitted) = all modules.
```

### Module Filter Parsing

At command dispatch time, scan the full user message for either:
- `module <name>` (bare form, where `<name>` is a single non-flag word)
- `--module <name>` (flag form)

If found, set `MODULE_FILTER = <name>`. Otherwise `MODULE_FILTER = ""` (no filter — all modules included).

`MODULE_FILTER` is forwarded to all tooling commands that accept `--module`:
- `diff` and `summarize-diff` in §VALIDATE and IM-01.
- Pass as: `${MODULE_FILTER:+--module "$MODULE_FILTER"}` in bash.

Log the resolved value: `[dispatch] module_filter=<value|none>`.

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

Load, cache, and **pre-compute** everything downstream stages need — so they never re-read the same files.

1. Detect `BLUEPRINT_ROOT` per blueprint policy (template guard applies).
2. Read `config.yaml` → extract all variables per config resolution table.
3. Read `codebase-context.yaml` only if it has non-placeholder values (check first few fields).
4. Resolve all derived paths: `REQ_PATH`, `PENDING`, `CURRENT`, `IMPL_ROOT`, `E2E_ROOT`, `E2E_REPORTS`, `MANIFEST`, `AI_TOOLING`.
5. Discover tooling per tooling discovery order.
6. Infer `APP_ROOT` per app root inference. Verify directory exists on disk.
7. Bootstrap `.aidev` if `MANIFEST` missing (PF-03 logic).
8. `list_dir` on `PENDING` and `CURRENT` — record file names.
9. **Batch-read all requirement YAML** (FR, NFR/GLOBAL, MAC, TS) from both `PENDING` and `CURRENT` in parallel. Cache full content in `cached_data`. If a directory is empty or a file has zero items, record that as `empty`.
10. **Compute `max_sequence` per ID type** (FR, NFR, GLOBAL, MAC, TS, AC, AT) from the cached content. Store as `cached_data.max_sequences`. For fresh projects (all empty), all values are `0`.
11. **Extract standing constraints:** From cached NFR/GLOBAL items, build one-line summaries. Store as `cached_data.standing_constraints`.
12. **Read manifest** (`requirements-state.yaml`) and cache `requirements_version_target`, `requirements_version_implemented`, `requirement_baseline` IDs.
13. Write to `/memories/session/aidev2-config-cache.md` under `## <BLUEPRINT_ROOT>` — include resolved paths, max sequences, standing constraint summaries, and manifest state.
14. Report resolved values in a compact table.

Argument `refresh` → overwrite existing cache section.

---

## §SETUP-APP

**ISOLATION RULE:** Do NOT read, inspect, or reference any existing app or blueprint config files (e.g. other `.instructions/config.yaml`) to infer naming conventions, slug format, or any other values. All inputs come exclusively from the user message and the setup script defaults.

1. Parse user message for `APP_SLUG`, `IMPL_SUFFIX`, `OUTPUT_DIR`. Convert to kebab-case.
   - `OUTPUT_DIR`: if not explicitly provided in the user message, default to the workspace root (first workspace folder visible in Explorer). Do NOT ask for `OUTPUT_DIR` when it can be defaulted this way.
   - `CORE_STACK`: parse from `stack:<value>` or `stack <value>` in the free-form text (e.g. `stack:go` or `stack go` → `CORE_STACK=go`). If provided, pass `--core-stack` to the setup script.
   - `IMPL_SUFFIX`: if not explicitly provided, default to `CORE_STACK` value (e.g. `go`). If `CORE_STACK` is also absent, ask.
   - Only ask when `APP_SLUG`, `IMPL_SUFFIX`, or `CORE_STACK` are genuinely unresolvable.
2. Resolve `FRAMEWORK_ROOT` from this prompt's own bundled template:
   `<PROMPTS_DIR>/aidev2-combined-details/initial-folder-structure/framework-ai-blueprint-template-v2`
   where `<PROMPTS_DIR>` = `{{VSCODE_USER_PROMPTS_FOLDER}}`.
   Never search the workspace for `framework-ai-blueprint-template-v2`.
3. Pre-flight: OUTPUT_DIR exists, neither destination (`<APP_SLUG>-ai-blueprint`, `<APP_SLUG>-<IMPL_SUFFIX>`) exists under OUTPUT_DIR.
4. Confirm via `vscode_askQuestions`.
5. Run:
   ```bash
   bash "${FRAMEWORK_ROOT}/setup/setup-for-user-prompts.sh" \
     --output-dir "${OUTPUT_DIR}" --app-slug "${APP_SLUG}" \
     --impl-suffix "${IMPL_SUFFIX}" --workspace-root "${OUTPUT_DIR}" \
     --user-prompts-dir "${PROMPTS_DIR}" \
     ${CORE_STACK:+--core-stack "${CORE_STACK}"}
   ```
6. Report blueprint path, app repo path, implementation id.

---

## §REQUIREMENTS

Parse step tokens: `01-author`, `02-promote`, `03-reconcile`, or ranges like `01-02`.
Also accepts plain language (e.g. "author new requirements", "promote and reconcile").

1. Run §PRE-FLIGHT if cache not warm.
2. Execute requested steps per requirements pipeline (RQ-01, RQ-02, RQ-03).

All authoring rules (ID uniqueness, module, contract_refs, design-first, YAML format, tech selection mirrors) are in the requirements pipeline reference.

### Acceptance Criteria & Acceptance Tests Quality Gate

Every authored FR, NFR, and GLOBAL requirement **MUST** include both `acceptance_criteria` and `acceptance_tests`. These are not optional summaries — they are the **specification contract** that drives Playwright test generation.

- **Acceptance criteria:** Each AC must have `criteria` (atomic verifiable conditions) and `scenarios` (Given/When/Then) that fully specify observable behavior.
- **Acceptance tests:** Each AT must have 6-12 `steps` that are precise enough to translate directly into Playwright test code with minimal interpretation. Steps must specify exact user actions (click, type, navigate), expected DOM states, HTTP status codes, response shapes, and timing constraints where relevant.
- **Low variability:** AT steps must leave little room for implementation variability — two developers reading the same AT should produce near-identical Playwright test code.
- **Playwright basis:** ATs are the primary input for IM-07 (Create Tests). AT step language should map naturally to Playwright actions (`page.goto`, `page.click`, `page.fill`, `expect(locator).toBeVisible`, `request.post`, etc.).

---

## §IMPLEMENT

Parse step tokens: `01-diff` through `09-generate-docs`, or ranges like `02-07`.
Also accepts plain language (e.g. "run from planning through tests", "just execute the code").

Mapping: `01-diff`→IM-01, `02-plan`→IM-02, `03-execute`→IM-03, `05-fix`→IM-05, `06-create-tests`→IM-07, `07-run-tests`→IM-08, `08-verify-manifest`→IM-09, `09-generate-docs`→IM-10.

1. Run §PRE-FLIGHT if cache not warm.
2. **Fresh-start (default):** Run IM-00 archive/clear before first step — moves leftover `01-delta-current`, `02-plan-current`, `03-plan-execution` to history folders. Always regenerate diff and plan from scratch based on current script output. Never reuse plans, deltas, or results from a prior run.
3. Execute requested steps per implementation pipeline.

Override: user says "reuse plan", "continue", or "resume" → skip fresh-start and reuse existing artifacts.

---

## §ALL-STEPS

Optional: `from-promote`, `from-diff`, `from-plan`, `from-execute`, `from-tests`.

Sequence (skip earlier stages when `from-*` provided):
1. §PRE-FLIGHT (PF-01..PF-04)
2. §WARMUP (if cache not populated)
3. Requirements: RQ-02 promote (or RQ-01 author + RQ-02 if no override)
4. Implementation: IM-01 diff + IM-02 plan
5. Implementation: IM-03 execute + IM-05 fix
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

Maintain `cached_data` across stages **within the same run only**. After each stage, merge computed state. Later stages consume before re-reading YAML.

**Cross-run isolation:** Never inherit plans, deltas, results, or cached_data from a prior run. Each pipeline invocation starts fresh unless user explicitly says "reuse", "continue", or "resume".

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
   - App manifest: verify `APP_ROOT/.aidev/requirements/requirements-state.yaml` exists. If only a legacy `manifests/requirements-manifest.yaml` or `manifests/requirements-manifest.yaml` is present, migrate content to `.aidev/requirements/requirements-state.yaml` and delete the old file.
   - Update all cross-references: `replaces_id`, `specific_ids`, `contract_refs`, `related_*`, manifest baseline.
5. **Verify:** No stale references, ID uniqueness, contract_refs clean, manifest at new location.
6. **Report:** List obsolete v1 artifacts (do NOT delete): `02-implementation/00-prompts/`, `02-implementation/02-implementation-mapping/`, `github-config/aidev-*.prompt.md`, `github-config/aidev-framework.instructions.md`, `instructions/`, `manifests/requirements-manifest.yaml`. Note: `.instructions/config.yaml` and `codebase-context.yaml` are NOT obsolete.
7. **Optional:** Suggest dry-run diff or syntax checks.

Safety: never delete app-specific content, no destructive git commands, no files outside blueprint root.

---

## §BACKUP

1. Resolve `FRAMEWORK_ROOT` from this prompt's own bundled template:
   `<PROMPTS_DIR>/aidev2-combined-details/initial-folder-structure/framework-ai-blueprint-template-v2`
   where `<PROMPTS_DIR>` = `{{VSCODE_USER_PROMPTS_FOLDER}}`.
   Never search the workspace for `framework-ai-blueprint-template-v2`.
2. Verify `FRAMEWORK_ROOT/scripts/backup-user-prompts-linux.sh` exists.
3. Confirm via `vscode_askQuestions`. If declined, stop.
4. Run: `bash "${FRAMEWORK_ROOT}/scripts/backup-user-prompts-linux.sh"`.
5. Report copied/skipped files.

---

## §RUN-TESTS

Arguments: `headed`, `debug`, `<feature>.spec.ts`, `run all tests`.

1. Resolve `IMPLEMENTATION_ID` from config. Ask if multiple.
2. Paths: `E2E_ROOT` = `IMPL_ROOT/06-e2e-tests`, reports at `TEST_RESULTS`.
3. Pre-checks: `playwright.config.ts` exists. If no `node_modules`, run `npm install && npx playwright install chromium`.
4. Start app if not running (use startup script).
5. Set `E2E_REPORTS_ROOT` = absolute `TEST_RESULTS`. Run: `cd "$E2E_ROOT" && E2E_REPORTS_ROOT="$TEST_RESULTS" npx playwright test` (add `--headed` or `--debug` per argument). **Never pass `--reporter` on the CLI** — it overrides `playwright.config.ts` reporters and leaves `TEST_RESULTS/` empty.
6. Verify artifacts under `TEST_RESULTS/`, none under `06-e2e-tests/`.

---

## §VALIDATE

Validation gate — run between implementation stages and as final gate.

1. **Schema validation:** Check changed requirement artifacts against schemas in `SCHEMAS_ROOT` (the local `aidev2-combined-details/aidev2-schemas/` folder). **Never copy schema files to the app blueprint `.schemas/` folder.** Schemas are always read from the prompt's own bundled location.
2. **Manifest shape:** Validate `MANIFEST` against `SCHEMAS_ROOT/in-application/requirements-state-schema.json`.
3. **Diff-clear:** Run:
   ```bash
   "$TOOLING_CMD" diff -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID" ${MODULE_FILTER:+--module "$MODULE_FILTER"}
   "$TOOLING_CMD" summarize-diff -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID" ${MODULE_FILTER:+--module "$MODULE_FILTER"}
   ```
   `REQ_PATH` = `BLUEPRINT_ROOT/01-requirements`. Never pass `BLUEPRINT_ROOT` itself as `-r`.
4. **Policy gate:** Verify all pipeline invariants.

---

## Narration Protocol

**Keep chat narration minimal.** The log file is the detailed record — chat is for the user.

- **Stage start:** One line: `[<stage>] Starting...`
- **Stage end:** One line: `[<stage>] Done (<N>s) — <one-line outcome>`
- **Errors:** `[<stage>] ERROR: <message>`
- **Unexpected:** `[<stage>] **UNEXPECTED: <message>**` (bold, fatal)
- **Do NOT repeat** in chat what the log already captures (requirement-by-requirement play-by-play, script stdout, file paths written). The user can read the log.
- Pipeline summary at end (this IS shown in chat):

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

**CRITICAL — Log Enforcement Rules (MANDATORY — violations invalidate the run):**
- Every stage **MUST** log its `STAGE START` line to `$LOG_FILE` **before** any stage work begins.
- Every stage **MUST** log its `STAGE END` line to `$LOG_FILE` **immediately after** stage work completes (before proceeding to the next stage).
- Within a stage, every script invocation, key decision, error, artifact write, and requirement completion **MUST** be logged.
- **Per-requirement logging in IM-03:** After implementing each requirement, log: `[<ts>][combined] Requirement <REQ-ID> — implemented, manifest updated`.
- **Batched log writes are preferred.** Accumulate log entries in a shell variable or heredoc and write them in a single `echo -e "$LOG_ENTRIES" >> "$LOG_FILE"` call at natural checkpoints (after each requirement, after each script invocation, at stage boundaries). Do NOT use a separate `run_in_terminal` for every individual log line — that wastes tool calls.
- **Inline logging with commands:** When running a tooling command, chain the log entry in the same terminal call: `"$TOOLING_CMD" ... && echo "[<ts>][combined] ..." >> "$LOG_FILE"`. This halves the number of terminal round-trips.
- **Stage-boundary logging** (STAGE START / STAGE END) may still use dedicated terminal calls for clarity.
- **Minimum log density:** A pipeline run that implements N requirements must produce at least `5 + (3 × N)` log lines (pipeline start/end, per-stage start/end, per-requirement entries). If the log has fewer lines than this after a run, the run is non-compliant.
- **Never skip logging due to context length or conversation complexity.** If nearing context limits, the log is the last thing to sacrifice — reduce narration verbosity in chat instead.
- If a conversation is interrupted mid-pipeline, the log must reflect all stages that actually completed.

## Terminal Execution Rules

- Fresh foreground terminal for each critical tooling command (`diff`, `delta`, `apply`, `promote`, `build`, `test`).
- Non-critical commands (echo, mkdir, cp, mv, cat, log writes) **may be chained** with `&&` onto a critical command or grouped together in a single terminal call.
- No background execution, no `await_terminal`.
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
Contents: resolved config variables, directory file listings, **max_sequences per ID type**, **standing constraint one-line summaries**, **manifest state** (version target/implemented, baseline IDs), and **cached requirement YAML content** (or `empty` markers). This is the primary data source for downstream stages — they consume cache before re-reading files.
