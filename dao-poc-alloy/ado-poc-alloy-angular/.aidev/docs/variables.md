# Environment Variables

This document lists all environment variables used by the ADO POC Alloy Angular application.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ROOT` | No | Inferred from app path | Absolute path to the application root directory. Used by Playwright test configuration to resolve the Angular app location for `webServer.cwd`. |
| `BASE_URL` | No | `http://127.0.0.1:${PORT}` | Base URL for the application. Used by Playwright tests to configure the test base URL. Derived from PORT if not explicitly set. |
| `CI` | No | undefined | Boolean flag indicating whether the application is running in a CI/CD environment. When set, Playwright enables stricter test execution (retries: 2, workers: 1). |
| `E2E_REPORTS_ROOT` | No | Inferred from project structure | Absolute path where Playwright test reports should be written. Used to configure the output directory for HTML and JSON test reports. |
| `PORT` | No | `4200` | Port number on which the Angular development server listens. Used by `npm start` (ng serve) and referenced by Playwright configuration for test execution. |

## Usage

### Development

```bash
# Start the application on default port 4200
npm start

# Start the application on a custom port
PORT=3000 npm start
```

### Testing

```bash
# Run Playwright tests (headless)
cd 06-e2e-tests
npx playwright test --config playwright.config.ts

# Run Playwright tests on a custom port with custom base URL
PORT=5000 BASE_URL=http://localhost:5000 npx playwright test --config playwright.config.ts

# Run tests in headed mode (visible browser)
npx playwright test --config playwright.config.ts --headed
```

### CI/CD

```bash
# Run tests in CI mode (stricter retry/worker settings)
CI=true npx playwright test --config playwright.config.ts
```

## Notes

- **PORT**: The Angular development server automatically listens on the specified port. This variable is also used by Playwright to construct the base URL if not explicitly provided.
- **BASE_URL**: If not provided, Playwright defaults to constructing it from the PORT variable. Only set this explicitly if using a different host or protocol.
- **CI**: When true, Playwright enables 2 retries and limits workers to 1 for more stable CI execution.
- **APP_ROOT** and **E2E_REPORTS_ROOT**: These are typically set by test orchestration scripts and are required for proper Playwright configuration when running tests from non-standard locations.
