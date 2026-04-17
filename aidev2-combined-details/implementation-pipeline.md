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

## Speed Rules

- **Consume cache aggressively.** `cached_data` from warmup has standing constraints, max sequences, manifest state, and requirement content. Do NOT re-read files for data already in cache.
- **Minimize terminal calls.** Chain non-critical commands (echo, mkdir, log writes) with `&&` onto the preceding command. Never use a separate terminal call just to append one log line.
- **Fresh app shortcut:** When `requirements_version_implemented == 0.0.0` and `requirement_baseline` is empty, the app has no existing code. In IM-02, set `codebase_map: fresh_scaffold` and skip file-by-file source scanning. In IM-03, skip "verify existing behavior" steps — there is none.
- **Skip redundant diff re-runs.** In IM-03, only re-run diff to verify progress when 3+ requirements exist. For 1-2 requirements, verifying at IM-06 is sufficient.
- **IM-01: combine diff + summarize-diff** in a single terminal call: `"$TOOLING_CMD" diff ... && "$TOOLING_CMD" summarize-diff ...`

## Read Efficiency

1. **Use warmup cache first:** `cached_data` from §WARMUP contains requirement YAML content, max_sequences, standing constraints, and manifest state. Always consume cache before reading files.
2. **Batch-read on entry (if cache miss):** At IM-00, read current YAML and manifest in parallel. Cache for the run.
3. **Batch implementation YAML:** At IM-02 Plan, read `structured-diff.yaml` and manifest together.
4. **Re-read only on write.** After writing, refresh only that file.
5. **Module-scoped reads:** When targeting a specific module, limit source reads to the module’s folder, shared entry points, and diff-referenced files.
6. **Same-run `cached_data` only.** Consume data from earlier stages in the **current run** before re-reading YAML. Never inherit cached_data or artifacts from a prior run.
7. **Script-first for mechanical steps.** IM-01 Diff and IM-09 Manifest use `ai-tooling.sh` scripts — read only stdout/stderr, not input YAML.
8. **Use `summarize-diff`.** After `ai-tooling.sh diff`, run `summarize-diff` for counts/IDs as text. Parse `structured-diff.yaml` only when full snapshots needed for planning.
9. **Standing constraints from cache:** `cached_data.standing_constraints` was pre-computed in warmup. Consume it directly in IM-02 — do NOT re-read `CURRENT_MERGED` for NFR/GLOBAL items unless cache is missing.

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

Standing constraint lookup: (1) `cached_data.standing_constraints` (pre-computed in warmup — always available) (2) only if cache is missing: `read_file CURRENT_MERGED` (3) Never `grep_search` for YAML content.

Plan must include:
- `standing_nfr_and_global_cr_constraints` — one-line summaries of each NFR/GLOBAL constraint.
- `codebase_map` — key source files, purpose, relevant symbols. Reduces file-discovery I/O during execute.
- `test_coverage_mapping` — maps each requirement to test type (ui/api/none) and **full AT data**. For each requirement in the diff, extract all AT entries from `new_requirement.acceptance_tests` (already present in the diff snapshot — do NOT re-read requirements YAML). Each `test_coverage_mapping` entry must include: `requirement_id`, `test_type` (ui/api/none), and `acceptance_tests` (complete list with `id`, `name`, `steps`, `expected_result` copied verbatim from the diff). This is the sole AT source for IM-07 — no separate YAML read needed downstream.
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
2. **Run `delta` once at the start of IM-03** to generate the actionable delta document (`02-delta-history/01-delta-current.yaml`) that `apply` reads. This is separate from the `diff` command run in IM-01:
   ```bash
   "$TOOLING_CMD" delta -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"
   ```
   > **Why:** `diff` (IM-01) writes `01-delta-current/structured-diff.yaml` for planning. `delta` writes `02-delta-history/01-delta-current.yaml` for manifest updates. `apply` reads the latter — calling `apply` without running `delta` first causes a `FileNotFoundError`.
3. Implement one requirement at a time.
4. DB work first (if applicable) for each requirement.
5. **After each requirement's code is written and verified**, set `implementation_verified: true` for that requirement's entry in `02-delta-history/01-delta-current.yaml`, then immediately update the manifest. **Combine into a single terminal call** to minimize round-trips:
   ```bash
   # Set verified flag (use sed/python inline) then apply in one call:
   python3 -c "import yaml; p='$DELTA_FILE'; d=yaml.safe_load(open(p)); [e.__setitem__('implementation_verified',True) for e in d.get('delta',{}).get('added',[])+d.get('delta',{}).get('updated',[]) if str(e.get('requirement_id'))=='<REQ-ID>']; yaml.dump(d,open(p,'w'),default_flow_style=False)" && "$TOOLING_CMD" apply -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID" && echo "[$(date -u +%Y-%m-%dT%H:%M:%S)][$IMPLEMENTATION_ID] Requirement <REQ-ID> — implemented, manifest updated" >> "$LOG_FILE"
   ```
   > **Why:** The delta file defaults every entry to `implementation_verified: false`. `apply` silently skips entries that are not `true` — the manifest will not be updated unless the flag is set first.
   This keeps `requirements-state.yaml` in sync after every requirement — not deferred to IM-09. The combined command saves 2 terminal round-trips per requirement.
6. Log the manifest update result for that requirement to `$LOG_FILE`.
7. Re-run diff as needed to verify progress.
8. Archive plan/results when complete.

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

1. Read acceptance tests from `test_coverage_mapping` in `plan.yaml` — AT step data is already embedded there (extracted from the diff's `new_requirement.acceptance_tests` in IM-02). Do NOT re-read current requirements YAML or structured-diff.yaml for AT content.
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

**MANDATORY — Every API test must attach http-traffic. Pattern:**
```typescript
test('AT-XXXXXX — ...', async ({ request }, testInfo) => {
  const response = await request.get('/path');
  const body = await response.text();
  const responseHeaders = response.headers() as Record<string, string>;
  const traffic = [{
    acceptanceTestId: 'AT-XXXXXX',
    acceptanceTestTitle: '...',
    exchangeRole: 'direct',
    exchangePurpose: '...',
    requestLabel: 'GET /path',
    responseLabel: `HTTP ${response.status()}`,
    rawHttpRequest: `GET /path HTTP/1.1\nHost: ${new URL(response.url()).host}\nAccept: text/plain`,
    rawHttpResponse: `HTTP/1.1 ${response.status()}\n${Object.entries(responseHeaders).map(([k,v])=>`${k}: ${v}`).join('\n')}\n\n${body}`,
    request: { method: 'GET', url: response.url(), headers: {}, body: null },
    response: { status: response.status(), headers: responseHeaders, body },
  }];
  expect(response.status()).toBe(200);
  // ... other assertions ...
  await testInfo.attach('http-traffic', { body: Buffer.from(JSON.stringify(traffic)), contentType: 'application/json' });
});
```
Without this attachment, `traffic-html-reporter` and `traffic-json-reporter` produce empty traffic sections.

**MANDATORY — `playwright.config.ts` must use the custom reporters, not built-in ones:**
```typescript
reporter: [
  ['list'],
  ['./helpers/traffic-html-reporter.ts', { outputFile: path.resolve(reportsRoot, 'traffic-report.html') }],
  ['./helpers/traffic-json-reporter.ts', { outputFile: path.resolve(reportsRoot, 'traffic-report.json') }],
],
```
Do NOT use `['json', ...]` or `['html', ...]` built-in reporters for API test projects. They will not produce the required traffic HTML.

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
