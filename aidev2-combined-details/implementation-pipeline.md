# Implementation Pipeline

All rules and steps for diff, planning, execution, testing, manifest updates, and documentation.

## Core Rules

- Code first, manifest second.
- Only modify files in active diff/plan scope.
- Standing NFRs and Global CRs constrain all new/changed code.
- Current technology selections constrain all code — no stack deviations unless requirements updated first.
- Module reassignment (`module` field changed between current and manifest baseline) → undo old module contributions then re-implement under new module.
- DB schema contract changes are mandatory work in the same run.
- `MODULE_FILTER` (set at dispatch time) narrows the diff and all downstream steps to requirements with `module == MODULE_FILTER`. Empty = all modules. Carry this value through every step in the run.

## Read Efficiency

1. **Batch-read on entry:** At IM-00, read current YAML and manifest in parallel. Cache for the run.
2. **Batch implementation YAML:** At IM-02 Plan, read `structured-diff.yaml` and manifest together.
3. **Re-read only on write.** After writing, refresh only that file.
4. **Module-scoped reads:** When targeting a specific module, limit source reads to the module's folder, shared entry points, and diff-referenced files.
5. **Same-run `cached_data` only.** Consume data from earlier stages in the **current run** before re-reading YAML. Never inherit cached_data or artifacts from a prior run.
6. **Script-first for mechanical steps.** IM-01 Diff and IM-09 Manifest use `ai-tooling.sh` scripts — read only stdout/stderr, not input YAML.
7. **Use `summarize-diff`.** After `ai-tooling.sh diff`, run `summarize-diff` for counts/IDs as text. Parse `structured-diff.yaml` only when full snapshots needed for planning.

---

## IM-00 Pre-Step Verification & Fresh Start

### Verification
1. Read `config.yaml` (if not cached) → extract `IMPLEMENTATION_ID`, `APP_ROOT`, `STARTUP_HINT`, `APP_TEST_STARTUP_HINT`, `MANIFEST`, `TOOLING_CMD`, DB settings.
2. Resolve `IMPL_ROOT`, `AI_TOOLING`, startup hints.
3. Validate manifest shape against `SCHEMAS_ROOT/in-application/requirements-state-schema.json`. (`SCHEMAS_ROOT` = bundled `aidev2-combined-details/aidev2-schemas/` — never read from the app blueprint's `.schemas/` folder.)
4. Confirm `iteration_id` and version targets are sensible.

### Archive & Clear (fresh-start default)
Unless user explicitly said "reuse", "continue", or "resume":
5. If `IMPL_ROOT/01-delta-current` has files → move to `IMPL_ROOT/50-delta-history/<timestamp>/`.
6. If `IMPL_ROOT/02-plan-current` has files → move to `IMPL_ROOT/51-plan-history/<timestamp>/`.
7. If `IMPL_ROOT/03-plan-execution` has files → move to `IMPL_ROOT/52-plan-execution-history/<timestamp>/`.
8. `<timestamp>` = `YYYY-MM-DD-HH-MM-SS` at archive time.

This ensures every implementation run starts from a clean slate — diff, plan, and execution are always regenerated from current script output.

---

## IM-01 Diff

**Mechanical step.** Run two commands in fresh foreground terminals:

```bash
"$TOOLING_CMD" diff -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID" ${MODULE_FILTER:+--module "$MODULE_FILTER"}
"$TOOLING_CMD" summarize-diff -r "$REQ_PATH" --implementation-id "$IMPLEMENTATION_ID" ${MODULE_FILTER:+--module "$MODULE_FILTER"}
```

If `MODULE_FILTER` is set, only requirements with `module == MODULE_FILTER` are included in the diff output and all downstream steps. Default (empty) includes all modules.

- Read text summary from stdout only — do NOT parse `structured-diff.yaml` or current YAML.
- Report `created`/`updated`/`removed`/`technology_selection` counts and IDs.
- Module-change detection: `summarize-diff` flags `module_changed: old -> new` automatically. Report from summary; don't compare YAML fields.

### Narration
`[IM-01] Diff started/completed at <ts> — created: N, updated: N, removed: N`

---

## IM-02 Plan

**Inputs:** Structured diff, current requirements, manifest, tech stack summary.
**Outputs:** `IMPL_ROOT/02-plan-current/plan.yaml`, `plan.md`, `IMPL_ROOT/03-plan-execution/paths.yaml`.

If `MODULE_FILTER` is set, the structured diff already contains only matching requirements. Plan scope is naturally limited to those requirements — do not expand to other modules. Note the active module filter in plan metadata.

Standing constraint lookup: (1) `cached_data.standing_constraints` (2) `read_file CURRENT_MERGED` (3) Never `grep_search` for YAML content.

Plan must include:
- `standing_nfr_and_global_cr_constraints` — one-line summaries of each NFR/GLOBAL constraint.
- `codebase_map` — key source files, purpose, relevant symbols. Reduces file-discovery I/O during execute.
- `test_coverage_mapping` — maps each requirement to test type (ui/api/none) and AC/AT IDs. Consumed by test creation.
- Per-change scope: impacted files, symbols, steps, validation, risks.

Module-reassignment planning (for `module_changed` entries):
1. **Undo scope** — code/routes/components to remove/relocate from old module.
2. **Redo scope** — implementation under new module with file locations, imports, registration.
3. Module reassignment steps appear before normal update steps for the same requirement.

### Narration
`[IM-02] Plan started/completed at <ts> — <N> requirements planned`

---

## IM-03 Execute

**Inputs:** `plan.yaml`, `paths.yaml`, `structured-diff.yaml`, manifest.
**Outputs:** Modified app files, updated `IMPL_ROOT/03-plan-execution/results.yaml`.

Execution order:
1. Initialize `results.yaml`.
2. Implement one requirement at a time.
3. DB work first (if applicable) for each requirement.
4. **After each requirement's code is written and verified**, immediately update the manifest by running:
   ```bash
   "$TOOLING_CMD" apply -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"
   ```
   This keeps `requirements-state.yaml` in sync after every requirement — not deferred to IM-09.
5. Log the manifest update result for that requirement to `$LOG_FILE`.
6. Re-run diff as needed to verify progress.
7. Archive plan/results when complete.

Use `codebase_map` from plan to locate files directly. Batch reads for each requirement.

Module-reassignment execution:
1. **Undo** — remove/relocate code from old module.
2. **Redo** — implement under new module per plan.
3. **Verify** — both modules build correctly.
4. Update manifest baseline `module` to new value.
5. Run `ai-tooling.sh apply` after module reassignment completes.

Critical: update manifest per-requirement (not in bulk at the end), never mark requirement complete before code exists, don't finish while diff has outstanding items.

### DB Schema File Requirements

When implementing `physical_database_schema` contract changes, produce **two** files per schema change:
1. **Full schema** — complete resulting schema (e.g., `user-account-schema.sql`).
2. **Migration** — same base name with `-migration` suffix (e.g., `user-account-schema-migration.sql`). Contains only ALTER/CREATE/DROP statements to transition from prior version.

Both required before DB gate clears. If no prior schema, migration = full schema.

### Narration
`[IM-03] Execute started at <ts>` / per requirement: `Requirement <REQ-ID> — starting` / `— implemented, manifest updated (<N>s)` / `Execute completed at <ts> — <N> requirements implemented`

---

## IM-04 Extract Interfaces

**Inputs:** `APP_ROOT`, `AI_TOOLING`, tech stack.
**Output:** `IMPL_ROOT/04-extract-library-interfaces/ref-library-methods.yaml`.

Prefer stack-aware extractor from `AI_TOOLING/interface-extractors/` if available.

Always regenerate — do not reuse prior `ref-library-methods.yaml` unless user explicitly requests it.

### Narration
`[IM-04] Extract interfaces started/completed at <ts>`

---

## IM-05 Fix

**Inputs:** Startup hint(s), terminal errors, extracted interfaces.
**Action:** Iterate startup/build diagnosis. Fix root causes only — no scope expansion.

### Narration
`[IM-05] Fix started at <ts>` / `Fixing: <issue>` / `Fix completed at <ts> — <outcome>`

---

## IM-06 Verify Diff Clear

Re-run IM-01. Complete only when structured diff has **zero** remaining entries in all buckets.

---

## IM-07 Create Tests

**Inputs:** Plan, results, AC/AT content, `E2E_ROOT`.
**Output:** Playwright tests under `IMPL_ROOT/06-e2e-tests`.

### AT-Driven Test Generation

Acceptance tests (AT) in the requirements are the **primary specification** for Playwright test code. Each AT's `steps` array maps directly to Playwright actions:

1. Read each requirement's `acceptance_tests` from current requirements YAML.
2. For each AT, translate `steps` into Playwright code in order — each step becomes one or more Playwright calls.
3. The AT `expected_result` becomes the final assertion block.
4. AT step language maps to Playwright: "Navigate to X" → `page.goto(X)`, "Click Y" → `page.click(Y)`, "Type Z into field W" → `page.fill(W, Z)`, "Expect element V visible" → `expect(page.locator(V)).toBeVisible()`, "POST /api/... returns 200" → `expect(response.status()).toBe(200)`.
5. Do not add assertions or flows beyond what the AT specifies. The AT is the contract — tests must verify exactly what the AT describes.

### Scaffold reuse
If `06-e2e-tests/` has files from prior iteration, reuse config/fixtures/helpers/reporters. Only add/update test files for current diff requirements.

### Playwright config rules
- `outputDir` must point under `TEST_RESULTS` (e.g., `path.resolve(reportsRoot, 'playwright-raw-output')`).
- `reportsRoot` must resolve to `TEST_RESULTS` via `E2E_REPORTS_ROOT` env var or relative `path.resolve`.
- All reports under `TEST_RESULTS`. Nothing under `06-e2e-tests/` (no `test-results/`, `playwright-report/`, `blob-report/`).

### UI tests (`06-e2e-tests/ui/`)
- Full Playwright browser context (`page` fixture). Render real DOM.
- Expand scoped requirements → `UIC-*` IDs via `contract_refs`/AC/AT/spec files.
- **One test per UIC ID.** Test title includes UIC ID for per-UIC result rows.
- Each test: navigate route → assert element visible → `testInfo.attach('screenshot-<UIC-ID>', ...)` full-page screenshot.
- Multi-state scenarios: screenshot per visited state, one result row per UIC.
- Reporter: `ui-html-reporter.ts` (inline screenshots, pass/fail explanation).
- Run: `npx playwright test --project=ui`

### API tests (`06-e2e-tests/api/`)
- Playwright `request` fixture (no browser). Cookie support via `request.storageState`.
- Capture HTTP traffic into `http-traffic` attachment for `traffic-html-reporter`/`traffic-json-reporter`.
- Run: `TEST_MODE=api npx playwright test --project=api`

Reporter templates: copy `traffic-html-reporter.ts`, `traffic-json-reporter.ts`, `ui-html-reporter.ts` from `E2E_TEMPLATES/helpers/` into `06-e2e-tests/helpers/` verbatim.

### Narration
`[IM-07] Create tests started at <ts>` / per req: `Requirement <REQ-ID> — creating tests` / `— tests created` / `Create tests completed at <ts> — <N> files written`

---

## IM-08 Run Tests

**Scope:** Default is **partial** — only tests for requirements in current diff/plan. Full suite only on explicit request.

### Output naming
| Run type | Pattern |
|---|---|
| Partial | `<timestamp>-<REQ_ID>-partial.<ext>` |
| Full | `<timestamp>-<REQ_ID>-full.<ext>` |

`<timestamp>` = ISO-8601 with `:`/`.` → `-`.

### Execution
1. Ensure app running (start via startup script if not).
2. Set `E2E_REPORTS_ROOT` to absolute path of `TEST_RESULTS`.
3. Run tests.
4. Verify: artifacts under `TEST_RESULTS/`, **none** under `06-e2e-tests/`.
5. UI runs: one result row per UIC, screenshot evidence in artifacts.
6. API runs: HTTP traffic in artifacts.

No app code edits in this step.

### Narration
`[IM-08] Run tests started at <ts>` / `Test run complete — passed: N, failed: N` / `Run tests completed at <ts>`

---

## IM-09 Verify & Finalize Manifest

By this point, `requirements-state.yaml` should already be up-to-date because IM-03 runs `ai-tooling.sh apply` after each requirement. This step **verifies** completeness and applies any missed updates.

1. Run the apply command one final time to catch any stragglers:
   ```bash
   "$TOOLING_CMD" apply -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"
   ```
2. Read manifest and verify:
   - Every `created`/`updated`/`models_and_contracts_diff` requirement has a `requirement_baseline` entry with `pinned_version: <requirements_version_target>`.
   - Every `removed` requirement is absent from `requirement_baseline`.
   - `requirements_version_implemented == requirements_version_target`.
3. If verification fails, diagnose and fix (manual fallback: add/update/remove entries, set version).

**Mandatory.** Pipeline incomplete if `requirements_version_implemented` differs from target.

### Narration
`[IM-09] Verify manifest started at <ts>` / `Manifest verified — <N> entries, version: <v>` / `completed at <ts>`

---

## IM-10 Generate Docs

Generate `APP_ROOT/.aidev/docs/variables.md`:

```markdown
# Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
```

Source from: `os.Getenv`/`os.LookupEnv` (Go), `process.env.*` (Node), `os.environ` (Python), config files, `.env.example`, `docker-compose.yml`, startup scripts.

Rules: one row per variable, alphabetical, Required=Yes if app fails without it, exclude test/CI-only vars. Regenerate every run.

### Narration
`[IM-10] Generate docs started at <ts>` / `Wrote variables.md — <N> variables` / `completed at <ts>`
