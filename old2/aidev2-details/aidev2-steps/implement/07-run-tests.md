# IM-07 Run Tests
Inputs: E2E_ROOT, E2E_REPORTS, APP_TEST_STARTUP_HINT.
Action: ensure app is running, run playwright, report pass/fail and artifact paths.
Rules: no app code edits in this step.

UI execution/reporting details (when UI is in scope):
- Capture screenshots for every tested page/screen state and store them as run artifacts.
- Execute and report all applicable UI contract acceptance tests.
- Verify the run produced one result row per executed `UIC-*` and did not collapse results to one row per requirement.
- Generate HTML pass/fail reports and include report locations in the final run summary.

Artifact location rule:
- All UI/API report outputs and attachments must be written under `03-test-results/<IMPLEMENTATION_ID>` only. If any artifact lands under `06-e2e-tests/` or another folder, treat the run as misconfigured.

API execution/reporting details:
- Keep existing API output format unchanged.
- Continue reporting request/response details in the current format.

## Narration
- On entry: `[IM-09] Run tests started at <timestamp>`
- Before test script: `[IM-09] Script start: <playwright-command>`
- After test script: `[IM-09] Script end: <playwright-command> (exit: <code>, elapsed: <N>s)`
- On test results: `[IM-09] Test run complete — passed: N, failed: N`
- On error: `[IM-09] ERROR: Test run failed — <details>`
- On unexpected: `[IM-09] **UNEXPECTED: <details>**`
- On exit: `[IM-09] Run tests completed at <timestamp> (elapsed: <N>s)`
