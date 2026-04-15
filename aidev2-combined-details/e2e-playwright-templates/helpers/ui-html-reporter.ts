import type { FullConfig, Reporter, Suite, TestCase, TestResult } from '@playwright/test/reporter';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';

type ReporterOptions = { outputFile?: string };

// eslint-disable-next-line no-control-regex
const ANSI_RE = /\x1b\[[0-9;]*m/g;

function stripAnsi(text: string): string {
    return text.replace(ANSI_RE, '');
}

function extractUicId(title: string): string | null {
    const m = title.match(/\bUIC-\d+/);
    return m ? m[0] : null;
}

function escapeHtml(value: string): string {
    return value
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

interface ScreenshotAttachment {
    name: string;
    base64: string;
}

interface TestEntry {
    title: string;
    uicId: string | null;
    status: string;
    durationMs: number;
    error: string;
    screenshots: ScreenshotAttachment[];
    explanation: string;
}

class UiHtmlReporter implements Reporter {
    private outputFile: string;
    private tests: TestEntry[] = [];

    constructor(options: ReporterOptions = {}) {
        this.outputFile =
            options.outputFile ?? path.join('playwright-output', 'ui-report.html');
    }

    onBegin(_config: FullConfig, _suite: Suite): void { }

    onTestEnd(test: TestCase, result: TestResult): void {
        const title = test.titlePath().join(' > ');
        const uicId = extractUicId(title);

        const screenshots: ScreenshotAttachment[] = [];
        for (const attachment of result.attachments) {
            if (attachment.contentType === 'image/png' && attachment.body) {
                screenshots.push({
                    name: attachment.name,
                    base64: Buffer.from(attachment.body).toString('base64'),
                });
            }
        }

        const error = stripAnsi(result.error?.message ?? '');
        let explanation: string;
        if (result.status === 'passed') {
            explanation = `Passed: All assertions for ${uicId ?? 'this test'} verified successfully. ${screenshots.length} screenshot(s) captured.`;
        } else if (result.status === 'failed') {
            explanation = `Failed: ${error || 'Unknown failure. Check test output for details.'}`;
        } else {
            explanation = `Skipped: Test was not executed.`;
        }

        this.tests.push({
            title,
            uicId,
            status: result.status,
            durationMs: result.duration,
            error,
            screenshots,
            explanation,
        });
    }

    onEnd(): void {
        const failed = this.tests.filter((t) => t.status === 'failed');
        const passed = this.tests.filter((t) => t.status === 'passed');
        const skipped = this.tests.filter((t) => t.status === 'skipped');

        const failureSummaryHtml = failed.length > 0
            ? `<div class="failure-summary">
  <h2>Failed UI Tests</h2>
  <table class="failure-table">
    <thead>
      <tr>
        <th style="width:120px">UIC ID</th>
        <th style="width:300px">Test</th>
        <th>Why it failed</th>
      </tr>
    </thead>
    <tbody>
${failed.map((t) => `      <tr>
        <td class="uic-id">${escapeHtml(t.uicId ?? 'unknown')}</td>
        <td>${escapeHtml(t.title)}</td>
        <td><pre>${escapeHtml(t.error || 'No error message captured')}</pre></td>
      </tr>`).join('\n')}
    </tbody>
  </table>
</div>`
            : '<div class="all-passed"><h2>All UI Tests Passed</h2></div>';

        const rows = this.tests
            .map((t) => {
                const statusClass = t.status === 'failed' ? ' status-failed'
                    : t.status === 'passed' ? ' status-passed'
                        : ' status-skipped';

                const screenshotHtml = t.screenshots.length > 0
                    ? t.screenshots
                        .map((s) =>
                            `<div class="screenshot">
  <div class="screenshot-label">${escapeHtml(s.name)}</div>
  <img src="data:image/png;base64,${s.base64}" alt="${escapeHtml(s.name)}" style="max-width:100%; border:1px solid #ddd; margin:4px 0;" />
</div>`)
                        .join('\n')
                    : '<div class="no-screenshots">No screenshots captured</div>';

                const explanationHtml = `<div class="explanation ${t.status === 'passed' ? 'explanation-pass' : t.status === 'failed' ? 'explanation-fail' : 'explanation-skip'}">
  <div class="label">${t.status === 'passed' ? 'Why it passed' : t.status === 'failed' ? 'Why it failed' : 'Status'}</div>
  <p>${escapeHtml(t.explanation)}</p>
</div>`;

                return `<tr>
  <td class="col-test">${escapeHtml(t.uicId ?? '')} ${escapeHtml(t.title)}</td>
  <td class="col-status${statusClass}">${escapeHtml(t.status)}</td>
  <td class="col-rt">${t.durationMs}</td>
  <td class="col-screenshots">${explanationHtml}${screenshotHtml}</td>
</tr>`;
            })
            .join('\n');

        const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Playwright UI Test Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 16px; }
    table { border-collapse: collapse; width: 100%; table-layout: fixed; }
    th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; overflow-wrap: anywhere; word-break: break-word; }
    th { background: #f5f5f5; }
    .col-test { width: 150px; }
    .col-status { width: 150px; }
    .col-rt { width: 100px; }
    .col-screenshots { width: auto; }
    pre { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; max-width: 100%; }
    .explanation { margin-bottom: 12px; padding: 8px; border-radius: 4px; }
    .explanation-pass { background: #dcfce7; border-left: 4px solid #166534; }
    .explanation-fail { background: #fee2e2; border-left: 4px solid #991b1b; }
    .explanation-skip { background: #f3f4f6; border-left: 4px solid #6b7280; }
    .label { font-weight: 700; text-transform: lowercase; margin: 0 0 4px 0; }
    .screenshot { margin: 8px 0; }
    .screenshot-label { font-size: 12px; color: #6b7280; margin-bottom: 2px; }
    .no-screenshots { color: #9ca3af; font-style: italic; padding: 8px 0; }
    .summary-bar { display: flex; gap: 24px; margin: 12px 0 20px 0; font-size: 15px; }
    .summary-bar span { padding: 4px 12px; border-radius: 4px; }
    .summary-passed { background: #dcfce7; color: #166534; }
    .summary-failed { background: #fee2e2; color: #991b1b; }
    .summary-skipped { background: #f3f4f6; color: #4b5563; }
    .failure-summary { margin: 0 0 24px 0; }
    .failure-summary h2 { color: #991b1b; }
    .failure-table { table-layout: auto; }
    .failure-table .uic-id { font-weight: 700; font-family: monospace; }
    .failure-table pre { font-size: 13px; }
    .all-passed h2 { color: #166534; margin: 0 0 24px 0; }
    .status-failed { background: #fee2e2; color: #991b1b; font-weight: 700; }
    .status-passed { color: #166534; }
    .status-skipped { color: #6b7280; }
  </style>
</head>
<body>
  <h1>Playwright UI Test Report</h1>
  <p>Generated: ${escapeHtml(new Date().toISOString())}</p>
  <div class="summary-bar">
    <span class="summary-passed">Passed: ${passed.length}</span>
    <span class="summary-failed">Failed: ${failed.length}</span>
    <span class="summary-skipped">Skipped: ${skipped.length}</span>
    <span>Total: ${this.tests.length}</span>
  </div>
  ${failureSummaryHtml}
  <h2>Full Test Results</h2>
  <table>
    <thead>
      <tr>
        <th class="col-test">Test</th>
        <th class="col-status">Status</th>
        <th class="col-rt">RT</th>
        <th class="col-screenshots">Screenshots &amp; Explanation</th>
      </tr>
    </thead>
    <tbody>
      ${rows}
    </tbody>
  </table>
</body>
</html>`;

        const outAbs = path.resolve(process.cwd(), this.outputFile);
        mkdirSync(path.dirname(outAbs), { recursive: true });
        writeFileSync(outAbs, html, 'utf8');
    }
}

export default UiHtmlReporter;
