# IM-06 Create Tests
Inputs: plan, results, functional requirements AC/AT, E2E_ROOT.
Action: create Playwright tests and config under IMPL_ROOT/06-e2e-tests.
Rules: traceability to AT IDs, keep reporter/template compatibility. Copy reporter templates from `aidev2-details/e2e-playwright-templates/helpers/` (canonical source in user prompts).

UI testing details (when UI is in scope):
- Include UI-contract acceptance coverage for all relevant `ui_contracts` items tied to the scoped requirements.
- Expand requirement references to individual `UIC-*` ids and generate one Playwright test per UIC so reporting is per UIC, not per requirement.
- Add screenshot steps for every page/screen visited by each scenario; do not limit screenshots to failures only.
- Ensure the generated test title includes the `UIC-*` id and that screenshots are attached for each visited UIC state.
- Configure Playwright/reporters so all artifacts stay under `03-test-results/<IMPLEMENTATION_ID>` only; do not leave `test-results`, `playwright-report`, or other report folders under `06-e2e-tests`.
- Define HTML pass/fail report generation as part of the run configuration and document expected report output paths.

API testing details:
- Keep the existing API output format unchanged.
- Preserve current request/response logging style and payload/response detail reporting.
