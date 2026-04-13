---
description: "Embedded AI-dev v2 implementation pipeline for aidev2 prompts. Covers diff, plan, execute, interface extraction, fix, test creation, and test execution using fixed blueprint layout and local user-level schemas."
---

# Aidev2 Implementation Pipeline

This file replaces blueprint-local implementation instructions for aidev2 prompts.

Do not read blueprint-local implementation instructions other than `.instructions/config.yaml`.

## Core Rules

- Use the local schema bundle at `{{VSCODE_USER_PROMPTS_FOLDER}}/aidev2-details/aidev2-schemas`.
- Code first, manifest second.
- Only modify files required by the active diff and plan.
- Existing NFRs and Global CRs constrain all new or changed code.
- Current technology selections (per-implementation files under `03-current/technology-selection/technology-selection-<IMPL_ID>.yaml`, and manifest baseline) constrain all new or changed code in every iteration; do not introduce stack/tool deviations unless requirements are explicitly updated first.
- DB schema contract changes are mandatory work in the same run.
- Module reassignment (a requirement's `module` field changed between current and manifest baseline) triggers undo/redo logic: remove the requirement's contributions from the old module location, then re-implement under the new module.

## IM-00 Pre-Step Verification

1. Read `BLUEPRINT_ROOT/.instructions/config.yaml` (if present) — extract `IMPLEMENTATION_ID`, `APP_ROOT`, `STARTUP_HINT`, `APP_TEST_STARTUP_HINT`, `MANIFEST`, and DB contract alignment settings. Resolve `TOOLING_CMD` and `AI_TOOLING` from the user prompts folder per **Tooling Discovery** in `aidev2-blueprint.instructions.md`.
2. Resolve `IMPLEMENTATION_ID`.
3. Resolve `APP_ROOT`, `MANIFEST`, `IMPL_ROOT`, `TOOLING_CMD`, `AI_TOOLING`, and startup hints.
4. Validate that the manifest shape matches the local manifest schema.
5. Confirm the manifest `iteration_id` and version targets are sensible for the current run.

## IM-01 Diff

Purpose:
- generate `IMPL_ROOT/01-delta-current/structured-diff.yaml`

Command:
```bash
"$TOOLING_CMD" diff -r "$REQ_PATH" --implementation-id "$IMPLEMENTATION_ID"
```

After diff:
- read the structured diff
- report counts and requirement ids for `created`, `updated`, `removed`, and `technology_selection`
- for each `updated` entry, compare the `module` field between the current requirement and the manifest baseline; flag entries where the module changed and report the count

## IM-02 DB Gate

Inspect the structured diff for any entry tied to `physical_database_schema` or equivalent MAC/database alignment work.

If found:
- mark DB alignment as mandatory in plan and execute
- do not consider the run complete until schema verification evidence exists

### DB Schema File Requirements

When implementing a `physical_database_schema` contract change, produce **two** output files for every schema change:

1. **Full schema file** — the complete resulting database schema as it should exist after the change. File name is determined by the contract spec (e.g. `user-account-schema.sql`, `schema.prisma`).
2. **Migration file** — a companion file with the **same base name** as the full schema file, plus a `-migration` suffix before the extension (e.g. `user-account-schema-migration.sql`, `schema-migration.prisma`). This file contains only the migration statements needed to transition from the previous schema version to the new one (ALTER TABLE, CREATE TABLE, DROP COLUMN, etc.).

Rules:
- Both files must be written before the DB gate is cleared.
- The migration file must be runnable as a deployment artifact against the previous schema version.
- If no previous schema exists (new table/schema), the migration file is equivalent to the full schema file (CREATE TABLE only).
- Place both files in the same output directory as determined by the contract spec path or the designated schema output location in `config.yaml`.
- Log: "Writing full schema: `<filename>`" and "Writing migration: `<filename>-migration.<ext>`" before each write.

## IM-03 Plan

Outputs:
- `IMPL_ROOT/02-plan-current/plan.yaml`
- `IMPL_ROOT/02-plan-current/plan.md`
- `IMPL_ROOT/03-plan-execution/paths.yaml`

Plan rules:
- include `standing_nfr_and_global_cr_constraints`
- include per-change scope, impacted files, symbols, steps, validation, and risks
- do not plan unrelated edits
- for module-reassignment entries, plan explicit undo (old module cleanup) and redo (new module implementation) steps before any content-level updates for the same requirement

## IM-04 Execute

Execution order:
1. initialize `IMPL_ROOT/03-plan-execution/results.yaml`
2. implement one requirement at a time
3. if DB work exists, complete and verify it first for that requirement
4. update manifest only after code for that requirement exists
5. re-run diff as needed to verify progress
6. archive plan/results when complete

Critical rules:
- never bulk-update manifest entries
- never mark a requirement complete before code exists
- do not finish while the diff still has outstanding items
- when executing a module-reassignment requirement: (1) undo — remove/relocate code from the old module, (2) redo — implement under the new module, (3) verify both modules build correctly, (4) update the manifest baseline `module` field to the new value

## IM-05 Extract Library Interfaces

Output:
- `IMPL_ROOT/04-extract-library-interfaces/ref-library-methods.yaml`

Use stack-aware extraction.
If a stack-specific tooling extractor is present under `AI_TOOLING/interface-extractors/`, prefer it over manual extraction.

## IM-06 Verify Diff Clear

Re-run IM-01.
Execution is complete only when the regenerated structured diff has zero remaining entries in all buckets.

## IM-07 Fix Startup Issues

Use terminal output and extracted library interfaces to fix root causes.
Prefer `STARTUP_HINT` or `APP_TEST_STARTUP_HINT` if available.
Iterate until startup succeeds or the blocker is fully explained.

## IM-08 Create Tests

Create acceptance tests under:
- `IMPL_ROOT/06-e2e-tests`

Prefer Playwright when the implementation layout is http web-based.

### Playwright config requirements

When generating or updating `playwright.config.ts`:
- Always set `outputDir` explicitly to a path **under** `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID` (e.g. `path.resolve(reportsRoot, 'playwright-raw-output')`).
- Never rely on Playwright's default `test-results/` directory, which would place artifacts inside `06-e2e-tests/test-results` — that location must remain empty.
- `reportsRoot` must resolve to `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID` (via `E2E_REPORTS_ROOT` env var or a relative `path.resolve` from `__dirname`).
- All report artifacts must stay under `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID`, including HTML, JSON, screenshots, traces, videos, attachments, raw output, and any custom reporter output.
- Do not emit report folders or files under `06-e2e-tests/`, including `test-results/`, `playwright-report/`, `blob-report/`, or any equivalent fallback output path.

### UI tests (browser-rendered apps)

- Test file location: `06-e2e-tests/ui/`
- Use a full Playwright browser context (`page` fixture). Render the real DOM — do **not** use `request`-only contexts.
- Expand the scoped requirements into their referenced UI contract IDs (`UIC-*`) using requirement `contract_refs`, `sub_mac_ids`, linked AC/AT text, and referenced `ui_contracts` specs.
- One test per UI contract (UIC-*) ID. Do not merge multiple UIC surfaces into a single test, and do not collapse multiple UICs into one requirement-level result row.
- Ensure each Playwright test title includes the UIC ID so the HTML/JSON report shows one result row per executed UIC.
- For reference contract models (MAC-*), reference the spec file name in a comment only — do not create a separate test row per model entry.
- Each test must:
  1. Navigate to the relevant route.
  2. Assert the expected element is visible in the DOM.
  3. Capture a full-page screenshot with `testInfo.attach('screenshot-<UIC-ID>', { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' })`.
- If the scenario visits more than one screen state within the same UIC, attach a screenshot for each visited state, while preserving one top-level test result row for that UIC.
- Report: use `ui-html-reporter.ts`. This reporter embeds screenshots inline and shows a plain-language "Why it passed / Why it failed" explanation instead of HTTP request/response traffic.
- Run UI tests with: `npx playwright test --project=ui` (default, `TEST_MODE` unset)
- API project reporter: use `traffic-html-reporter.ts` (HTTP request/response format retained for API tests).

### API tests (HTTP endpoints, BFF, backend services)

- Test file location: `06-e2e-tests/api/`
- Use Playwright `request` fixture (no browser). Cookie support is available via `request.storageState` or by injecting cookies through `injectCookie` helper.
- Do not launch a browser context for pure API tests.
- Capture HTTP traffic into the `http-traffic` attachment for the `traffic-html-reporter` and `traffic-json-reporter`.
- Run API tests with: `TEST_MODE=api npx playwright test --project=api`
Use requirement AC/AT content to drive coverage.

UI-specific requirements:
- if UI is in scope, include UI contract acceptance tests for all relevant `ui_contracts` items and linked AC/AT entries
- when a requirement references multiple UIC IDs, generate and execute separate UI tests for each referenced UIC ID
- include screenshot capture instructions in tests for every visited page/screen state covered by the scenario (not just failures)
- include explicit pass/fail HTML report generation instructions and output locations

API-specific requirements:
- keep existing API test output/report format unchanged
- preserve request/response detail capture already used by the implementation (request payloads, responses, and status assertions)

## IM-09 Run Tests

### Scope — default is partial

By default run **only the tests that correspond to requirements implemented in the current run** (i.e. the IDs from the active diff/plan).
- Derive the test file(s) or `--grep` pattern from those requirement IDs.
- Do **not** re-run the full suite unless the user explicitly requests it (e.g. "run all tests").

### Output file naming

Use this naming scheme for every output file written to `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID`:

| Run type | Pattern |
|---|---|
| Partial (default) | `<timestamp>-<REQ_ID>-partial.<ext>` |
| Full suite | `<timestamp>-<REQ_ID>-full.<ext>` |

`<timestamp>` = ISO-8601 with `:` and `.` replaced by `-` (e.g. `2026-04-10T13-07-44-505Z`).
`<ext>` = `html`, `json`, etc. as appropriate.

Examples:
- `2026-04-10T13-07-44-505Z-FR-000005-partial.html` — partial run for FR-000005
- `2026-04-10T13-07-44-505Z-FR-000005-full.html` — full suite run

Apply the same suffix to all output files from the same run (HTML, JSON, etc.).

### Execution rules

- Run tests using the implementation test setup.
- Write all outputs under `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID`.
- Treat any report or artifact written outside `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID` as a failure and fix the test configuration before considering the run complete.
- For UI test runs, ensure screenshots are produced for every tested page/screen and included in artifacts.
- For UI test runs, verify the report contains one executed result row per covered UIC ID, not one row per requirement.
- For UI test runs, generate HTML pass/fail reports and include paths in the execution summary.
- Verify UI contract acceptance coverage is executed and reported explicitly.
- For API test runs, keep existing output format unchanged, including request/response reporting style.

Do not modify application code in this step unless the user explicitly switches back to execute/fix.
