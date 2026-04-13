# Run Playwright acceptance tests

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml`.
2. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.
3. Paths:
   - E2E tests: `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests`
   - Test reports: `03-test-results/<IMPLEMENTATION_ID>` (fixed, no config lookup)
   - App startup script: resolve from `config.yaml → implementations.<IMPLEMENTATION_ID>.app_test_startup_script`

## Pre-checks
1. Verify `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests/playwright.config.ts` exists. If not, **stop** and tell the user to run prompt 06 (create tests) first.
2. Verify `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests/node_modules` exists. If not, install dependencies:
   ```
   cd 02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests && npm install
   npx playwright install chromium
   ```
3. If the current structured diff or plan indicates DB-schema MAC work, verify DB schema alignment/migrations were executed before running tests.

## Ensure application is running
- Check if the application is already running on the expected port.
- If not, start it using the app test startup script (resolve from `config.yaml → implementations.<IMPLEMENTATION_ID>.app_test_startup_script`) in a background terminal.
- Wait for the health endpoint or port to become available (poll with retries, max 30 seconds).

## Run tests
Pass `E2E_REPORTS_ROOT` as an environment variable so `playwright.config.ts` writes
reports to the configured folder. Test output files are stored at:
`03-test-results/<IMPLEMENTATION_ID>/` (relative to blueprint root).

Resolve `E2E_REPORTS_ROOT` as the absolute path to `03-test-results/<IMPLEMENTATION_ID>/`.
Treat any artifact created outside that folder as a configuration failure.

### Headless (default)
```
cd 02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests && E2E_REPORTS_ROOT="<absolute path to 03-test-results/<IMPLEMENTATION_ID>>" npx playwright test
```

### Headed (human-observable)
```
cd 02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests && E2E_REPORTS_ROOT="<absolute path to 03-test-results/<IMPLEMENTATION_ID>>" npx playwright test --headed
```

### Debug (step-through)
```
cd 02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests && E2E_REPORTS_ROOT="<absolute path to 03-test-results/<IMPLEMENTATION_ID>>" npx playwright test --debug
```

### Single feature
```
cd 02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests && E2E_REPORTS_ROOT="<absolute path to 03-test-results/<IMPLEMENTATION_ID>>" npx playwright test <feature>.spec.ts
```

## After tests complete
1. Read the exit code and terminal output.
2. If any tests failed:
   - Show the failure summary (test name, expected vs actual, line number).
   - Read the latest JSON report in `03-test-results/<IMPLEMENTATION_ID>/` named
     `<timestamp>-<REQ_ID>.json` for structured failure details.
   - Suggest specific fixes based on error messages.
3. If all tests passed:
   - Report pass count and execution time.
4. Confirm both report artifacts exist in `03-test-results/<IMPLEMENTATION_ID>/`:
   - `03-test-results/<IMPLEMENTATION_ID>/<timestamp>-<REQ_ID>.json`
   - `03-test-results/<IMPLEMENTATION_ID>/<timestamp>-<REQ_ID>.html`
5. For UI runs, confirm there is one result row per executed `UIC-*` and that each executed UIC has screenshot evidence in the report artifacts.
6. Confirm report content includes full raw HTTP request/response traffic for API tests:
   - report shows HTTP traffic and errors in one shared column (`HTTP Traffic and Errors`)
   - report does NOT include a separate `Error` column
   - if an error has no HTTP traffic, report includes `No HTTP traffic captured`
     plus technical error type/message in the same shared column
   - request/response entries use explicit labels: `request`, `response`
   - request includes absolutely raw HTTP request data (method + URL/path + all headers + raw body)
   - response includes absolutely raw HTTP response data (status line + all headers + raw body)
   - includes Set-Cookie and HttpOnly cookie details exactly as present in raw headers
   - HTML report force-wraps all long strings to browser width (no horizontal overflow for raw payload text)
   - HTML table widths: `RT` = 100px, `Status` = 150px, `Test` = 150px, shared traffic/error column uses remaining width
   - present in both JSON and HTML artifacts
7. Do NOT modify application code from this prompt — only diagnose.
   Use prompt 05 (fix) or prompt 03 (execute) to make code changes.
