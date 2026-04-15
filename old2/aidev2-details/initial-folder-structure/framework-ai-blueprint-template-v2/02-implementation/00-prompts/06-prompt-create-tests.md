# Create Playwright acceptance tests

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml`.
2. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.
3. Pre-read (BEFORE inspecting source):
   - `02-implementation/01-implementations/<IMPLEMENTATION_ID>/ai-app-hints.yaml` (if it exists)

## Inputs (read-only)
- **Plan:** `02-implementation/01-implementations/<IMPLEMENTATION_ID>/02-plan-current/plan.yaml`
- **Structured diff:** `02-implementation/01-implementations/<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`
- **Execution results:** `02-implementation/01-implementations/<IMPLEMENTATION_ID>/03-plan-execution/results.yaml`
- **Current requirements:** `01-requirements/03-current/functional_requirements.yaml`
- **Contract spec (OpenAPI):** resolve from current MAC entries for the project's OpenAPI contract logical ID
- **Contract spec (DB when applicable):** resolve from `config.yaml → implementations.<IMPLEMENTATION_ID>.database_contract_alignment.mac_contract_logical_id` when requirements involve persistence/schema behavior

## Role
Generate Playwright acceptance tests that verify implemented requirements.
Each test maps to one or more acceptance criteria/tests from the requirements.
For UI work, expand requirement references to individual `UIC-*` ids and report coverage per UIC, not per requirement.

## Test type selection

### API endpoints (no UI rendering)
Generate **lightweight Playwright API tests** using `request` context:
- Use `playwright.request.newContext()` for HTTP calls.
- Manage cookies explicitly: capture `Set-Cookie` headers from responses and
  forward them on subsequent requests (session continuity).
- Return cookies from helper functions so tests can chain authenticated flows.
- Assert status codes, response body shapes, and error codes per the AC/AT.
- Do NOT launch a browser for pure API tests.
- **Traceability on every HTTP call:** Immediately above each HTTP request
  (e.g. `request.get` / `request.post` / equivalent), add a comment that always
  includes the **acceptance test ID and full title** exactly as in requirements
  (e.g. `AT-000013: Deposit account created with lifecycle events`). If the
  request directly carries out a step of that AT, say which step or outcome it
  verifies. If the request is setup, auth, prerequisite data, or other
  ancillary traffic **not** itself the AT step under test, label it as a
  **supporting action**, briefly describe what it does, and still cite the same
  **acceptance test ID and title** of the enclosing `test()` it serves.

### UI / browser endpoints
Generate **headless browser tests** using `playwright.chromium.launch()`:
- Navigate to the page URL.
- Assert rendered content, interactive elements, and navigation flows.
- Use headless mode by default; tests must also pass in headed mode.
- When scoped requirements reference multiple `UIC-*` ids, generate separate tests so each UIC has its own result row and screenshot attachments.

## Output location
Write all test files to `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests/`:
```
02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests/
├── playwright.config.ts        # Shared config (baseURL from env, timeouts)
├── helpers/
│   ├── traffic-html-reporter.ts   # COPY from 02-implementation/00-templates/e2e-playwright (do not fork)
│   ├── traffic-json-reporter.ts   # COPY from 02-implementation/00-templates/e2e-playwright (do not fork)
│   └── auth.ts                 # Cookie-aware session helper (implementation-specific)
├── api/                        # API-level tests
│   └── <feature>.spec.ts       # One file per feature/endpoint group
└── ui/                         # Browser-level tests (if applicable)
    └── <feature>.spec.ts
```

### Reusable report templates (required for consistency)
- **Canonical source:** `02-implementation/00-templates/e2e-playwright/helpers/traffic-html-reporter.ts` and
  `traffic-json-reporter.ts` (see `02-implementation/00-templates/e2e-playwright/README.txt`).
- When creating **or** updating E2E for any implementation, **copy both files verbatim**
  from that template into `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests/helpers/`. Do not edit reporter code inside
  the implementation folder for one project only — change the template, then re-copy to every
  implementation that uses this blueprint.
- `playwright.config.ts` continues to pass `outputFile` for each reporter (timestamp +
  `REQ_ID` under `E2E_REPORTS_ROOT`); template defaults are only a fallback.

## Config file (`playwright.config.ts`)
- `baseURL` from environment variable `BASE_URL` (default: `http://localhost:<port>`).
- `timeout`: 30 000 ms per test.
- `retries`: 0 (strict — no flaky retries).
- **Reports output folder** is passed via the `E2E_REPORTS_ROOT` environment variable.
  The `playwright.config.ts` MUST read it:
  ```
  const reportsRoot = process.env.E2E_REPORTS_ROOT ?? '<fallback absolute path to 03-test-results/<IMPLEMENTATION_ID>>';
  ```
  The fallback should be the absolute path to `03-test-results/<IMPLEMENTATION_ID>/` (relative to blueprint root).
- `reporter` MUST write both JSON and HTML reports to `reportsRoot` using
  timestamp-first naming:
  - JSON: `<reportsRoot>/<timestamp>-<REQ_ID>.json`
  - HTML: `<reportsRoot>/<timestamp>-<REQ_ID>.html`
- All artifacts, including screenshots, traces, videos, attachments, and Playwright raw output, MUST be written under `03-test-results/<IMPLEMENTATION_ID>/` only.
- Do not leave report artifacts under `06-e2e-tests/`, including `test-results/`, `playwright-report/`, or `blob-report/`.
- Report artifacts MUST embed full raw HTTP traffic for API tests:
  - render HTTP traffic and errors in one shared column (`HTTP Traffic and Errors`)
  - do NOT render a separate `Error` column
  - if an error has no HTTP traffic at all, include `No HTTP traffic captured` and
    include the technical error type/message in that same shared column
  - render traffic with explicit labels per exchange: `request` then `response`
  - request: absolutely raw HTTP request (method + URL/path + all headers + raw body)
  - response: absolutely raw HTTP response (status line + all headers including Set-Cookie + raw body)
  - include cookies exactly as present in raw headers, including HttpOnly cookies
  - HTML report view MUST force-wrap long strings to browser width (including long unbroken values)
  - HTML table layout: `RT` width `100px`, `Status` width `150px`, `Test` width
    `150px`, and `HTTP Traffic and Errors` uses remaining width
  - include this traffic in both JSON and HTML report outputs
- **Acceptance test header above each HTTP payload (reports):** For every request/response
  pair in the report, BOTH JSON and HTML MUST show a **visible header block immediately
  above** the raw `request` and `response` payloads (not inside the raw HTTP text). The
  header MUST repeat **acceptance test ID**, **acceptance test title** (full title text
  from requirements), whether this exchange is a **direct AT step** or a **supporting
  action**, and a **short purpose** string. Implement by serializing these fields on each
  traffic object attached as `http-traffic` (see below) and having the custom JSON/HTML
  reporters render them before the `request` / `response` blocks.
- **`http-traffic` attachment schema (API tests):** Each element in the attached JSON array
  MUST include: `acceptanceTestId`, `acceptanceTestTitle`, `exchangeRole` (`direct` |
  `supporting`), `exchangePurpose` (human-readable), plus existing raw request/response
  fields. Provide a helper (e.g. `trafficMetaFromTest(testInfo, exchangeRole, purpose)`)
  that parses ID and title from the Playwright test title (`AT-NNNN: …`) and merges them
  into every `recordedPost` / `recordedGet` / auth helper call. `attachHttpTraffic` MUST
  validate that every entry has a non-empty `acceptanceTestId`.
- Error messages from Playwright contain ANSI escape codes (e.g. `\x1b[32m`).
  Reporters MUST strip all ANSI sequences before writing error text to JSON or HTML.
  Use a regex like `/\x1b\[[0-9;]*m/g` to remove them.
- Each test entry MUST include an `acceptanceTestId` field extracted from the test
  title (e.g. `AT-000013` from `AT-000013: Deposit account created...`).
- **Failure summary section** (both reporters):
  - JSON: include a top-level `failedAcceptanceTests` array with objects
    `{ acceptanceTestId, testTitle, reason }` for every failed test.
  - HTML: render a "Failed Acceptance Tests" table above the full results table
    with columns: AT ID, Test, Failure Reason. If all tests pass, show
    "All Acceptance Tests Passed" instead.
- Projects: `api` (no browser needed) and `ui` (chromium headless).

## Auth helper (`helpers/auth.ts`)
Export a function that:
1. Calls the dev auth endpoint with a given email.
2. Captures the `__Secure-session` cookie from `Set-Cookie`.
3. Returns a cookie-aware `APIRequestContext` (or raw cookie string)
   ready for authenticated requests.
4. For browser tests, injects the cookie into the browser context.
5. `autoLogin` and `devSignUpAndSignIn` MUST accept a **`TrafficReportMeta`** argument
   (same shape as `http-traffic` entries: id, title, `exchangeRole`, `exchangePurpose`)
   built with `trafficMetaFromTest` or equivalent. Auth traffic is usually
   `exchangeRole: 'supporting'` when the AT under test is not the auth call itself; use
   `direct` when the AT is specifically about that auth endpoint. The merged meta MUST
   flow into the `http-traffic` attachment so reporters can print the header above payloads.
6. Add a **source comment** above the auth HTTP call inside the helper referencing the
   passed meta for maintainers (in addition to report output).

## Test generation rules
1. One `.spec.ts` per logical feature group (e.g., `deposit-account.spec.ts`).
2. Each `test()` block maps to exactly one AT-* acceptance test from the requirements.
3. Use the AT name as the test name (e.g., `test('AT-000013: Deposit account created with lifecycle events', ...)`).
4. For UI coverage, split execution into one Playwright `test()` per referenced `UIC-*` id and include the UIC id in the title so reports show one row per UIC.
5. Follow the AT steps literally — they are the test script.
6. Assert every criterion from the parent AC-* acceptance criteria.
7. Attach screenshots for every visited page/screen state; at minimum attach a full-page screenshot for the UIC under test.
8. Mark tests that require external service mocking with `test.skip()` and a
   TODO comment explaining the mock setup needed.
9. Do NOT duplicate test logic — extract shared flows into helpers. If a helper
   performs HTTP, put the same AT id+title (and direct step vs supporting action)
   comment immediately above each request inside the helper body.
10. Email selection in tests MUST come from `.instructions/config.yaml`:
   - If the AT/AC requires a fixed email, use `variables.email_fixed`.
   - If the AT/AC requires a random email, generate `<lowercase-guid>@<variables.email_random_domain>`.
   - The generated GUID email-local-part MUST be lowercase.
   - Never hardcode literal email values (for example `e2e.fixed@example.com`); always resolve from config at generation time.

## Dependency management
- If `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests/package.json` does not exist, create it with:
  - `@playwright/test` (latest)
  - `typescript`, `@types/node`
  - Scripts: `test`, `test:headed`, `test:debug`
- Do NOT install dependencies — only generate files.
  The run-tests prompt handles installation.

## After generation
- List all created test files.
- Report mapping: AT-ID → test file → test name.
- Flag any AT that could not be automated (needs manual mock setup, etc.).
