Canonical reusable Playwright reporter templates (JSON + HTML) for acceptance-test runs.

Usage when creating or refreshing 06-e2e-tests:
  Copy helpers/traffic-html-reporter.ts and helpers/traffic-json-reporter.ts from this folder
  into <IMPLEMENTATION>/06-e2e-tests/helpers/ verbatim.

Do not fork per-app variants unless a project truly needs a one-off; change the template here
first, then re-copy to all implementations so report layout and fields stay consistent.

playwright.config.ts should always pass reporter outputFile (with E2E_REPORTS_ROOT + timestamp);
the default paths inside these reporters are only a fallback if outputFile is omitted.
