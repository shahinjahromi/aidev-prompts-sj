# Implementation Pipeline

> **Root:** All paths in this file are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../`
> Read `instructions.md` first. This file covers the implementation pipeline from diff through testing.
> Resolve `implementation_id` from `config.yaml` before proceeding.
> **If no `implementation_id` is provided, stop and ask — do not guess.**

---

## Steps at a Glance

| Step ID | Step Name | Action Type |
|---------|-----------|-------------|
| [IM-00](#im-00--pre-step-verification) | Pre-step verification | AI: verify manifest and implementation_id |
| [IM-01](#im-01--diff) | Diff | Prompt: `02-implementation/00-prompts/01-prompt-diff.md` |
| [IM-02](#im-02--db-gate) | DB gate | AI: inspect diff for physical DB schema changes |
| [IM-03](#im-03--plan) | Plan | Prompt: `02-implementation/00-prompts/02-prompt-plan.md` |
| [IM-04](#im-04--execute) | Execute | Prompt: `02-implementation/00-prompts/03-prompt-execute.md` |
| [IM-05](#im-05--extract-library-interfaces) | Extract library interfaces | Prompt: `02-implementation/00-prompts/04-prompt-extract-library-interfaces.md` |
| [IM-06](#im-06--verify-diff-clear) | Verify diff clear | AI + Prompt: re-run diff, confirm zero entries |
| [IM-07](#im-07--fix-startup-issues) | Fix startup issues | Prompt: `02-implementation/00-prompts/05-prompt-fix.md` |
| [IM-08](#im-08--create-tests) | Create tests | Prompt: `02-implementation/00-prompts/06-prompt-create-tests.md` |
| [IM-09](#im-09--run-tests) | Run tests | Prompt: `02-implementation/00-prompts/07-prompt-run-tests.md` |

All prompt paths are relative to `../` (blueprint root). Shared prompts directory: `02-implementation/00-prompts` (fixed constant — see `instructions.md → Fixed Blueprint Paths`).

---

## Steps

### IM-00 — Pre-Step Verification

**Instruction:** Confirm all prerequisites before starting any pipeline step.

**Action (AI):**
1. Read `config.yaml` → confirm `implementation_id` is known. If not, stop and ask.
2. Read `implementations.<IMPLEMENTATION_ID>.manifest_path`.
3. Verify manifest structure conforms to `.schemas/in-application/requirements-state-schema.json`.
4. Confirm manifest `requirements_version_target` matches the promoted requirements version.
5. Confirm developer has set app manifest `iteration_id` appropriately.

---

### IM-01 — Diff

**Instruction:** Generate the structured diff comparing promoted requirements (`03-current`) against the app manifest. Output goes to `<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`.

**Action:** Execute step `github-config/aidev-02-diff.prompt.md`.

**Pre-checks:**
1. Verify promote has run: `01-requirements/03-current/` has content.
2. Verify the developer has updated the app manifest `iteration_id`. If stale or unconfirmed, warn and ask before proceeding.

**Also read before running:**
- `01-requirements/03-current/models_and_contracts.yaml`
- `01-requirements/03-current/nfr_and_global_cr.yaml`
- `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`

**Command:** Resolve `TOOLING_CMD` from `config.yaml → tooling_root`.
```
"$TOOLING_CMD" diff -r "$REQ_PATH" --implementation-id "<IMPLEMENTATION_ID>"
```
Verify exit code is 0. If non-zero, report the full error output and stop.

**After diff:**
Read `<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`. Report counts:
- `created`: N requirements
- `updated`: N requirements
- `removed`: N requirements
- `technology_selection`: N entries

List the requirement IDs in each bucket so the developer has a clear view of scope. Then proceed to IM-02.

---

### IM-02 — DB Gate

**Instruction:** Inspect the structured diff for physical database schema contract changes. If found, database alignment work is mandatory in the same pipeline run.

**Action (AI):**
1. Read `<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`.
2. Check for any MAC item whose contract family is `physical_database_schema` (resolved from `config.yaml → implementations.<ID>.database_contract_alignment.mac_contract_logical_id`).
3. If found → DB work is mandatory. Flag this and ensure the plan (IM-03) and execution (IM-04) include the steps in [Database Contract Alignment](#database-contract-alignment).

---

### IM-03 — Plan

**Instruction:** Generate the implementation plan from the structured diff. Output goes to `<IMPLEMENTATION_ID>/02-plan-current/plan.yaml` and `plan.md`. Also generates `<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml`.

**Action:** Execute step `github-config/aidev-03-plan.prompt.md`.

**Also read before running:**
- `<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`
- `01-requirements/03-current/models_and_contracts.yaml`
- `01-requirements/03-current/nfr_and_global_cr.yaml`
- `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`

**NFR-COD-* / GLOBAL-COD-* handling:**
1. Read all NFRs and Global CRs from `01-requirements/03-current/nfr_and_global_cr.yaml`.
2. Check the diff for NFR-COD items in `created` / `updated` / `removed`.
3. Rules:
   - **New NFR-COD in diff (`created`):** plan a change entry; apply to all code written/modified; manifest after implementation.
   - **No new NFR-COD in diff:** existing NFRs and Global CRs are already manifested — apply only to new/changed code.
   - **NFRs are mandatory.** Code that violates them is not acceptable.
4. Add `standing_nfr_and_global_cr_constraints` in `plan_metadata` listing all applicable NFR IDs + summaries.
5. Each change’s `implementation_steps` must note which NFRs apply.

**Preserve existing behavior (CRITICAL):**
Only plan changes the diff requires. Do NOT alter existing methods, classes, or logic unless the diff explicitly requires that change.

**Database contract alignment:**
If the diff contains DB schema MAC updates (resolved via `config.yaml → implementations.<ID>.database_contract_alignment.mac_contract_logical_id` or `physical_database_schema` type entries):
- Add explicit plan steps for runtime DB alignment (migration/DDL artifacts + data access layer).
- Include impacted schema contract file(s) from current MAC metadata.
- Include a validation step that verifies runtime schema matches the promoted SQL contract.
- Do NOT allow plan completion with contract-file-only changes.

**Manifest rule:**
Do NOT add requirement_ids to the manifest during planning. Code must exist first.

**Per-change fields** (every entry in `changes` array):

| Field | Description |
|-------|-------------|
| `change_id` | requirement_id from diff |
| `requirement_delta` | created / modified / removed |
| `business_intent` | short theme |
| `what_will_be_changed` | detailed description |
| `acceptance_criteria` | nested ACs/ATs from the requirement |
| `scope_for_this_change` | files/folders for this change only |
| `impacted_files` | concrete paths from code analysis |
| `impacted_symbols` | classes, functions, components, routes, schemas |
| `type_of_change` | add / modify / remove / refactor |
| `implementation_steps` | concrete steps; note which NFRs apply |
| `expected_behavior_after_change` | acceptance outcome |
| `dependencies_and_side_effects` | impact on other features |
| `risk_level` | low / medium / high |
| `validation` | tests, linters, manual_checks |
| `open_questions_or_assumptions` | list or "None" |

---

### IM-04 — Execute

**Instruction:** Implement all changes specified in the plan. Code first, manifest second. Apply DB alignment if IM-02 detected schema changes.

**Action:** Execute step `github-config/aidev-04-execute.prompt.md`.

**Also read before running:**
- `<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml`
- `<IMPLEMENTATION_ID>/02-plan-current/plan.yaml`
- `<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`
- `01-requirements/03-current/models_and_contracts.yaml`
- `01-requirements/03-current/nfr_and_global_cr.yaml`
- `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`

If secrets are required: resolve `config.yaml → implementations.<IMPLEMENTATION_ID>.secrets_instructions_path` and follow that file before starting the application.

**Execution order:**
1. Init `<IMPLEMENTATION_ID>/03-plan-execution/results.yaml` with `start_datetime` (current UTC), `total_diffs` (count from structured-diff), `implemented_diffs: 0`.
2. Read `paths.yaml` — source of truth for all roots.
3. Read `plan.yaml` — note steps per change.
4. For each requirement in the plan:
   a. Implement code within the defined scope.
   b. If the requirement includes DB-schema MAC work: complete runtime DB alignment (migration/DDL) and schema verification **before** anything else.
   c. Update the app manifest: append the requirement’s `requirement_baseline` entry.
   d. Re-run diff to verify that requirement no longer appears in the outstanding diff.
   e. Increment `implemented_diffs` in `results.yaml`. Proceed to the next requirement.
5. Continue until `remaining_diffs: 0` or blockers are recorded with explanations.

**Critical rules:**
1. **Code first, manifest second.** Never add a requirement_id to the manifest before its code exists.
2. **One at a time.** Add each requirement_id to manifest only after that requirement’s code is complete.
3. **No bulk manifest updates.** No speculative entries.
4. **Execution is incomplete while diff has remaining items.**
5. **For DB-schema MAC items:** do NOT mark implemented until schema verification evidence is recorded in `results.yaml`.
6. **Never write resolved secret values** to any blueprint artifact, plan file, manifest, requirement file, or log.

**Scope discipline:**
Only modify files/folders listed in the plan’s `scope_for_this_change` and `impacted_files` for the current requirement. Do not alter existing methods, classes, or logic unless the diff + plan explicitly require it.

**NFR compliance:**
Apply all standing NFRs and Global CRs (from `plan_metadata.standing_nfr_and_global_cr_constraints`) to every piece of code written or modified. Do not commit code that violates NFR constraints.

**After all requirements implemented:**
1. Finalize `results.yaml` with `end_datetime` and final counts.
2. Confirm touched runtimes compile/start cleanly.
3. Archive plan: copy `plan.yaml` and `plan.md` to `<IMPLEMENTATION_ID>/51-plan-history/` with timestamp prefix; copy `results.yaml` to `<IMPLEMENTATION_ID>/52-plan-execution-history/` with timestamp prefix.
4. Report: total implemented, any skipped with reasons, diff status (remaining items).

---

### IM-05 — Extract Library Interfaces

**Instruction:** Extract public API signatures of all imported libraries used by the implementation. Output goes to `<IMPLEMENTATION_ID>/04-extract-library-interfaces/ref-library-methods.yaml`.

**Action:** Execute step `github-config/aidev-05-extract-interfaces.prompt.md`.

**Tech-stack detection:**
Read `codebase-context.yaml → implementations.<IMPLEMENTATION_ID>.tech_stack` to determine the extractor.

**Node.js / TypeScript:**
```
python3 "$AI_TOOLING/interface-extractors/extract-nodejs-library-interfaces.py" \
  --project-root "$APP_ROOT" \
  --output "$IMPL_ROOT/04-extract-library-interfaces/ref-library-methods.yaml"
```

**Other runtimes:** look under `$AI_TOOLING/interface-extractors/`. If no extractor exists for the detected stack, report and skip.

**Extraction rules:**
- Include all public types: exported, re-exported, aliased, declared.
- Resolve nested/inherited/aliased type names.
- Include type aliases even without methods.
- Omit empty collections from output.

**After:** Report number of libraries processed, number of types/interfaces extracted, and path to the output file. This file is used by IM-07 (fix) and IM-04 (execute) to resolve accurate library API usage.

---

### IM-06 — Verify Diff Clear

**Instruction:** Re-run the diff and confirm execution is complete. Execution is complete ONLY when the regenerated `structured-diff.yaml` has zero `created`, `updated`, `removed`, and `technology_selection` entries.

**Action (AI + Prompt):**
1. Re-execute IM-01 (prompt `02-implementation/00-prompts/01-prompt-diff.md`) to regenerate `structured-diff.yaml`.
2. Read the regenerated diff.
3. If any entries remain → return to IM-04 (Execute) or IM-07 (Fix Startup Issues) as appropriate.

---

### IM-07 — Fix Startup Issues

**Instruction:** Diagnose and fix startup errors or failing acceptance criteria identified after execution.

**Action:** Execute step `github-config/aidev-06-fix.prompt.md`.

**Pre-read before fixing:**
- `<IMPLEMENTATION_ID>/02-plan-current/plan.yaml` — intended scope.
- `<IMPLEMENTATION_ID>/04-extract-library-interfaces/ref-library-methods.yaml` — accurate public API signatures.
- `<IMPLEMENTATION_ID>/03-plan-execution/paths.yaml` — file roots.
- `01-requirements/03-current/nfr_and_global_cr.yaml` — ensure fixes remain compliant.

**Fix rules:**
1. Use terminal output (startup logs, compiler errors, type errors) to identify the failure.
2. Fix the root cause — do not suppress errors without understanding them.
3. **Missing dependency?** Add it to the workspace dependency manifest (`package.json`, `go.mod`, etc.) first, then install.
4. **Library usage or typing issue?** Consult `ref-library-methods.yaml` for correct API signatures before fixing.
5. **DB / migration / schema mismatch?** Fix migration/DDL and data-layer alignment before retrying startup.
6. Iterate: attempt startup → read errors → fix → attempt startup again.
7. Keep fixes consistent with the plan’s scope and intent.
8. **No unrelated changes** — only fix what is causing the errors.

**Attempt startup:**
Run `implementations.<IMPLEMENTATION_ID>.startup_script` (resolved from `config.yaml`), or use the appropriate start command from `codebase-context.yaml → implementations.<IMPLEMENTATION_ID>.npm_scripts`.

**Done when:**
- The startup script exits cleanly (exit code 0) or the server is listening on the expected port.
- No compile/type errors in terminal output.

**Report:**
- All files changed during fix iterations.
- Summary of root cause(s) fixed.
- Confirmation the application is running on the expected port (from `codebase-context.yaml`).

---

### IM-08 — Create Tests

**Instruction:** Generate Playwright acceptance tests for the active `implementation_id`. Output goes to `<IMPLEMENTATION_ID>/06-e2e-tests/`.

**Action:** Execute step `github-config/aidev-07-create-tests.prompt.md`.

**Inputs (read before generating):**
- `<IMPLEMENTATION_ID>/02-plan-current/plan.yaml`
- `<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`
- `<IMPLEMENTATION_ID>/03-plan-execution/results.yaml`
- `01-requirements/03-current/functional_requirements.yaml`
- Current OpenAPI contract spec (resolve from MAC entry with the project’s OpenAPI `contract_logical_id`).
- Current DB schema contract spec when requirements involve persistence (resolve from `config.yaml → implementations.<ID>.database_contract_alignment.mac_contract_logical_id`).

**Test type selection:**
- **API endpoints (no UI rendering):** use `playwright.request.newContext()`. Manage cookies explicitly (capture `Set-Cookie`, forward on subsequent requests). Return cookies from helper functions. Assert status codes, response body shapes, error codes per AC/AT. **No browser launch.** Add traceability comment above every HTTP call: AT ID + full title exactly as in requirements.
- **UI / browser endpoints:** use `playwright.chromium.launch()` headless. Navigate, assert rendered content, interactive elements, navigation. Default headless; must also pass headed.

**Output file structure:**
```
E2E_ROOT/
├── playwright.config.ts
├── helpers/
│   ├── traffic-html-reporter.ts   # COPY verbatim from E2E_REPORTER_TEMPLATE
│   ├── traffic-json-reporter.ts   # COPY verbatim from E2E_REPORTER_TEMPLATE
│   └── auth.ts                    # Cookie-aware session helper (implementation-specific)
├── api/
│   └── <feature>.spec.ts
└── ui/
    └── <feature>.spec.ts
```
Copy reporter files verbatim from `02-implementation/00-templates/e2e-playwright/helpers/`. Do not fork or edit them in `E2E_ROOT`.

**playwright.config.ts requirements:**
- `baseURL` from env var `BASE_URL` (default: `http://localhost:<port>` from `codebase-context.yaml`).
- `timeout`: 30 000 ms. `retries`: 0.
- `E2E_REPORTS_ROOT` env var controls output folder (fallback: `BLUEPRINT_ROOT/03-test-results/<IMPLEMENTATION_ID>`).
- Reporter writes JSON and HTML to `reportsRoot`: `<timestamp>-<REQ_ID>.json` and `.html`.
- Projects: `api` (no browser) and `ui` (chromium headless).

**Report artifact requirements:**
- Render HTTP traffic and errors in one shared column: `HTTP Traffic and Errors`. No separate `Error` column.
- If error has no HTTP traffic: show `No HTTP traffic captured` + error type/message in the same column.
- Per exchange: explicit `request` label (method + URL + all headers + raw body) then `response` label (status line + all headers incl. `Set-Cookie` + raw body).
- HTML: force-wrap long strings to browser width. Table widths: `RT`=100px, `Status`=150px, `Test`=150px, traffic column = remaining.
- JSON and HTML must both contain the full traffic.

**http-traffic attachment schema** (every entry must include):
- `acceptanceTestId`, `acceptanceTestTitle`, `exchangeRole` (`direct`|`supporting`), `exchangePurpose`, raw `request` and `response`.
- Provide `trafficMetaFromTest(testInfo, exchangeRole, purpose)` helper.
- `attachHttpTraffic` MUST validate non-empty `acceptanceTestId`.

**Failure report:**
- JSON: top-level `failedAcceptanceTests: [{ acceptanceTestId, testTitle, reason }]`.
- HTML: “Failed Acceptance Tests” table (AT ID, Test, Failure Reason) above full results. If all pass: “All Acceptance Tests Passed”.

**ANSI stripping:** strip `/\x1b\[[0-9;]*m/g` before writing to JSON or HTML.

**auth.ts helper:**
- Call the dev auth endpoint with the given email. Capture the session cookie from `Set-Cookie`. Return cookie-aware `APIRequestContext` (or raw cookie string) for authenticated requests. For browser tests, inject cookie into browser context.
- `autoLogin` / `devSignUpAndSignIn` MUST accept a `TrafficReportMeta` argument (`{ id, title, exchangeRole, exchangePurpose }`) from `trafficMetaFromTest`. Auth traffic role: `supporting` unless AT is about the auth endpoint. Add source comment above auth HTTP call referencing the passed meta.

**Email strategy:** resolve from `config.yaml → variables`:
- Fixed email: `variables.email_fixed` — only when AT/AC explicitly requires it.
- Random email: `<lowercase-guid>@<variables.email_random_domain>` — all other cases.

---

### IM-09 — Run Tests

**Instruction:** Start the application, then run the Playwright acceptance tests and report results.

**Action:** Execute step `github-config/aidev-08-run-tests.prompt.md`.

**Pre-checks:**
1. Verify `<IMPLEMENTATION_ID>/06-e2e-tests/playwright.config.ts` exists. If not, stop and tell user to run IM-08 first.
2. Verify `node_modules` exists in `06-e2e-tests/`. If not: `cd "$E2E_ROOT" && npm install && npx playwright install chromium`.
3. If the current diff or plan indicates DB-schema MAC work, verify DB schema alignment/migrations were executed before running tests.

**Start the application:**
- Check if already running on the expected port (from `codebase-context.yaml → implementations.<IMPLEMENTATION_ID>.ports`).
- If not, start via `implementations.<IMPLEMENTATION_ID>.app_test_startup_script` in a background terminal.
- Poll the health endpoint or port (max 30 seconds) before proceeding.

**Run tests (resolve `E2E_REPORTS_ROOT` from `config.yaml` or use `BLUEPRINT_ROOT/03-test-results/<IMPLEMENTATION_ID>`):**

| Mode | Command |
|------|---------|
| Headless (default) | `cd "$E2E_ROOT" && E2E_REPORTS_ROOT="<E2E_REPORTS>" npx playwright test` |
| Headed | `cd "$E2E_ROOT" && E2E_REPORTS_ROOT="<E2E_REPORTS>" npx playwright test --headed` |
| Debug | `cd "$E2E_ROOT" && E2E_REPORTS_ROOT="<E2E_REPORTS>" npx playwright test --debug` |
| Single feature | `cd "$E2E_ROOT" && E2E_REPORTS_ROOT="<E2E_REPORTS>" npx playwright test <feature>.spec.ts` |

**After tests complete:**
- If any tests failed: show failure summary (test name, AT ID, expected vs actual, line number); read the latest JSON report in `E2E_REPORTS/` for structured details; suggest specific fixes; direct to IM-07 for code changes.
- If all passed: report total pass count and execution time.

**Report artifact verification:**
Confirm both `<timestamp>-<REQ_ID>.json` and `<timestamp>-<REQ_ID>.html` exist in `E2E_REPORTS/`. Verify:
- HTTP traffic and errors are in one shared `HTTP Traffic and Errors` column.
- No separate `Error` column.
- Each exchange has explicit `request` / `response` labels with raw HTTP data.
- HTML force-wraps long strings. Table widths: `RT`=100px, `Status`=150px, `Test`=150px.
- Both JSON and HTML contain the full traffic.

**Do NOT modify code.** If tests fail, diagnose only. Direct code changes to IM-07 (startup/build errors) or IM-04 (requirement changes).

Test output directory: `03-test-results/<IMPLEMENTATION_ID>/` (fixed path relative to blueprint root).

---

## Shared Prompts Reference

All prompts live under `02-implementation/00-prompts/` (relative to `specs_root`; shared across all implementations):

| Prompt Path | Pipeline Step |
|-------------|--------------|
| `02-implementation/00-prompts/01-prompt-diff.md` | IM-01 Diff |
| `02-implementation/00-prompts/02-prompt-plan.md` | IM-03 Plan |
| `02-implementation/00-prompts/03-prompt-execute.md` | IM-04 Execute |
| `02-implementation/00-prompts/04-prompt-extract-library-interfaces.md` | IM-05 Extract library interfaces |
| `02-implementation/00-prompts/05-prompt-fix.md` | IM-07 Fix startup issues |
| `02-implementation/00-prompts/06-prompt-create-tests.md` | IM-08 Create tests |
| `02-implementation/00-prompts/07-prompt-run-tests.md` | IM-09 Run tests |

---

## Implementation Subdirectory Layout

Every implementation uses this EXACT layout under `02-implementation/01-implementations/<IMPLEMENTATION_ID>/`:

| Subdir | Contents |
|--------|---------|
| `01-delta-current/` | `structured-diff.yaml` — created by IM-01 |
| `02-plan-current/` | `plan.yaml`, `plan.md` — created by IM-03 |
| `03-plan-execution/` | `paths.yaml` (IM-03), `results.yaml` (IM-04) |
| `04-extract-library-interfaces/` | `ref-library-methods.yaml` — created by IM-05 |
| `05-fix/` | Fix artifacts — created by IM-07 |
| `06-e2e-tests/` | `playwright.config.ts`, `helpers/`, `api/`, `ui/` — created by IM-08 |
| `50-delta-history/` | Timestamped copies of past deltas |
| `51-plan-history/` | Archived plans |
| `52-plan-execution-history/` | Archived execution results |
| `53-update-history/` | Implementation-specific change history |

Implementation-level files:
- `ai-app-hints.yaml` — tooling-maintained implementation-specific app hints (at `02-implementation/01-implementations/<IMPLEMENTATION_ID>/`)

---

## Implementation Mapping

Files under `02-implementation/02-implementation-mapping/` control which implementations each requirement type applies to:

- `scope.yaml` — global default execution scope (file globs) per `implementation_id`
- `<requirement_type>.yaml` — one file per requirement type (`functional_requirements`, `nfr_and_global_cr`, etc.)

`default_implementation_ids` accepts: `["*"]` (all), `["<IMPLEMENTATION_ID>"]` (specific), or `["MYAPP_*"]` (wildcard).

**Technology selection note:** By default, all TS entries apply to all implementations. When a technology is specific to one stack, add a mapping override.

---

## Manifest Format

**Schema:** `.schemas/in-application/requirements-state-schema.json`

**Example entry:**
```yaml
- requirement_id: NFR-000001
  pinned_version: 1.0.0
  functional_test_status:
    status: unspecified
    first_version: 1.0.0
    current_version: 1.0.0
    tested_version: null
```

**Field notes:**
- `pinned_version` — from the requirement's `versioning.updated_on_version` (or `created_on_version`)
- `functional_test_status.status` — `unspecified`, `passed`, or `failed`
- Append to `requirement_baseline` — do NOT replace existing entries
- `iteration_id` — developer-controlled; tooling NEVER auto-updates this field
- `requirements_version_target` — the requirements version the app intends to implement
- `requirements_version_implemented` — set after implementation is complete
- Manifest location: `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`

---

## Artifact Shapes (Quick Reference)

**Structured diff (`structured-diff.yaml`):**
- Top-level keys: `diff_metadata`, `technology_selection`, `requirements_diff`
- `requirements_diff` keys: `created`, `updated`, `removed`
- Each item has: `requirement_id`, `new_requirement` (`$schema`, `title`, `description`, `type`, `artifact_type`, `versioning`, `acceptance_criteria`)
- Updated items also have: `original_requirement` (`requirement_id`, `pinned_version`, `functional_test_status`)
- NFR/GLOBAL items appear in `created`/`updated`/`removed` like any other requirement and are manifestable.

**Plan (`plan.yaml`):**
- Top-level keys: `plan_metadata`, `changes`, `manifest_update_instructions`
- `plan_metadata` keys: `plan_id`, `implementation_id`, `requirement_set_id`, `delta_source`, `generated_at`, `total_diff_items`, `paths`, `scope`, `code_analysis`, `standing_nfr_and_global_cr_constraints`, `execution_completion_criteria`, `execution_results_artifact`
- Each change has: `change_id`, `requirement_delta`, `business_intent`, `what_will_be_changed`, `acceptance_criteria`, `scope_for_this_change`, `impacted_files`, `impacted_symbols`, `type_of_change`, `implementation_steps`, `expected_behavior_after_change`, `dependencies_and_side_effects`, `risk_level`, `validation`, `open_questions_or_assumptions`

**Results (`results.yaml`):**
- Required fields: `plan_id`, `implementation_id`, `start_datetime`, `end_datetime`, `total_diffs`, `implemented_diffs`, `remaining_diffs`
- Optional fields: `notes`, `blockers`
- Datetime format: ISO 8601 with Mountain Time offset and timezone name

---

## Database Contract Alignment

**Trigger:** IM-02 detects a MAC item whose contract family is `physical_database_schema` (from `config.yaml → implementations.<ID>.database_contract_alignment.mac_contract_logical_id`).

**Required plan content (IM-03):**
- Identify impacted SQL contract file(s) from current `models_and_contracts.yaml`.
- List app artifacts required to align runtime schema (migrations/DDL scripts, repositories/models/queries, bootstrap/seed updates if needed).
- Define a schema verification step (command or SQL probe) that proves runtime DB matches promoted contract.

**Required execution content (IM-04):**
- Apply DB schema changes in the application repo (no contract-only completion).
- Run the schema verification step and record evidence in execution outputs.
- Only then manifest the MAC-related requirement(s).

**Failure policy:** If schema verification cannot run (missing env/db), mark execution incomplete with blocker details. Do not mark MAC DB-schema items as implemented.

---

## History Naming

| Artifact | Naming Pattern |
|----------|---------------|
| Delta history | `YYYYMMDDTHHMMSSZ-01-delta-current.yaml` |
| Plan history | `YYYY-MM-DD-HH-MM-SS-plan.yaml` and `plan.md` |
| Results history | `YYYY-MM-DD-HH-MM-SS-mt-results.yaml` |
| Update history | `YYYY-MM-DD-NNNNNN.md` |

**Routing:** Implementation-specific changes (code, manifest, plan execution, requirement additions) go to `<IMPLEMENTATION_ID>/53-update-history/`. Tooling, process, prompt, schema, and pipeline changes go to the specs-root `update-history/` folder.
