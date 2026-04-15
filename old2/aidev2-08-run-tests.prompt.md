---
name: "aidev2-run-tests"
description: "Run Playwright acceptance tests against a blueprint implementation. Supports headless, headed, debug, and single-feature modes. Reports land under 03-test-results/<IMPLEMENTATION_ID>/ in the blueprint."
argument-hint: "Optional: 'headed', 'debug', '<feature>.spec.ts', or 'run all tests' for full suite."
agent: "aidev2-dispatcher"
---

Run Playwright acceptance tests.

Intent: run tests.
Stage start override: `from-tests`

Execution details:

1. Read `.instructions/config.yaml` → resolve `IMPLEMENTATION_ID`.
   If multiple implementations and the user did not specify one, stop and ask.
2. Paths (all relative to blueprint root):
   - E2E tests: `02-implementation/01-implementations/<IMPLEMENTATION_ID>/06-e2e-tests`
   - Test reports: `03-test-results/<IMPLEMENTATION_ID>`
   - App startup script: resolve from `config.yaml → implementations.<IMPLEMENTATION_ID>.app_test_startup_script`
3. Pre-checks:
   - `06-e2e-tests/playwright.config.ts` must exist, otherwise stop.
   - `06-e2e-tests/node_modules` must exist, otherwise `npm install && npx playwright install chromium`.
4. Ensure the application is running on the expected port (start via startup script if not).
5. Set `E2E_REPORTS_ROOT` to the absolute path of `03-test-results/<IMPLEMENTATION_ID>`.
6. Run tests (default: headless, partial scope matching current diff IDs).
7. After tests: verify artifacts exist under `03-test-results/<IMPLEMENTATION_ID>/` and none under `06-e2e-tests/`.
8. For UI runs: verify one result row per UIC-* and screenshot evidence in report artifacts.
9. For API runs: verify HTTP traffic in report artifacts.

Use these relative references only:
- [Dispatcher Agent](./aidev2-dispatcher.agent.md)
- [Agent Handoff Contract](./aidev2-details/aidev2-agent-handoff.md)

Do NOT load Blueprint Policy or Implementation Pipeline here — the dispatcher and testing specialist load only what they need.
