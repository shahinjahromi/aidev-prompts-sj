import type { FullConfig, Reporter, Suite, TestCase, TestResult } from '@playwright/test/reporter';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

type ReporterOptions = { outputFile?: string };

type TrafficEntry = {
  acceptanceTestId?: string;
  acceptanceTestTitle?: string;
  exchangeRole?: string;
  exchangePurpose?: string;
  requestLabel?: string;
  responseLabel?: string;
  rawHttpRequest?: string;
  rawHttpResponse?: string;
  request: {
    method: string;
    url: string;
    headers: Record<string, string>;
    body: unknown;
  };
  response: {
    status: number;
    headers: Record<string, string>;
    body: unknown;
  };
};

// eslint-disable-next-line no-control-regex
const ANSI_RE = /\x1b\[[0-9;]*m/g;

function stripAnsi(text: string): string {
  return text.replace(ANSI_RE, '');
}

function extractAtId(title: string): string | null {
  const m = title.match(/\bAT-\d+/);
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

function parseAttachmentBody(result: TestResult, name: string): unknown {
  const hit = result.attachments.find((a) => a.name === name);
  if (!hit) return null;
  if (hit.body) {
    return JSON.parse(Buffer.from(hit.body).toString('utf8'));
  }
  if (hit.path) {
    return JSON.parse(readFileSync(hit.path, 'utf8'));
  }
  return null;
}

interface TestEntry {
  title: string;
  acceptanceTestId: string | null;
  status: string;
  durationMs: number;
  error: string;
  traffic: TrafficEntry[];
}

class TrafficHtmlReporter implements Reporter {
  private outputFile: string;
  private tests: TestEntry[] = [];

  constructor(options: ReporterOptions = {}) {
    this.outputFile =
      options.outputFile ?? path.join('playwright-output', 'traffic-report.html');
  }

  onBegin(_config: FullConfig, _suite: Suite): void {}

  onTestEnd(test: TestCase, result: TestResult): void {
    const traffic = (parseAttachmentBody(result, 'http-traffic') as TrafficEntry[] | null) ?? [];
    const title = test.titlePath().join(' > ');
    this.tests.push({
      title,
      acceptanceTestId: extractAtId(title),
      status: result.status,
      durationMs: result.duration,
      error: stripAnsi(result.error?.message ?? ''),
      traffic,
    });
  }

  onEnd(): void {
    const failed = this.tests.filter((t) => t.status === 'failed');
    const passed = this.tests.filter((t) => t.status === 'passed');
    const skipped = this.tests.filter((t) => t.status === 'skipped');

    const failureSummaryHtml = failed.length > 0
      ? `<div class="failure-summary">
  <h2>Failed Acceptance Tests</h2>
  <table class="failure-table">
    <thead>
      <tr>
        <th style="width:120px">AT ID</th>
        <th style="width:300px">Test</th>
        <th>Failure Reason</th>
      </tr>
    </thead>
    <tbody>
${failed.map((t) => `      <tr>
        <td class="at-id">${escapeHtml(t.acceptanceTestId ?? 'unknown')}</td>
        <td>${escapeHtml(t.title)}</td>
        <td><pre>${escapeHtml(t.error || 'No error message captured')}</pre></td>
      </tr>`).join('\n')}
    </tbody>
  </table>
</div>`
      : '<div class="all-passed"><h2>All Acceptance Tests Passed</h2></div>';

    const rows = this.tests
      .map((t) => {
        const statusClass = t.status === 'failed' ? ' status-failed'
          : t.status === 'passed' ? ' status-passed'
          : ' status-skipped';

        const technicalErrorBlock = t.error
          ? `<div class="message-block error-block">
  <div class="label">error</div>
  <pre>${escapeHtml(t.error)}</pre>
</div>`
          : '';

        const noTrafficBlock =
          t.traffic.length === 0 && t.error
            ? `<div class="message-block no-traffic">
  <div class="label">traffic</div>
  <pre>No HTTP traffic captured\nTechnical error:\n${escapeHtml(t.error)}</pre>
</div>`
            : '';

        const traffic = t.traffic
          .map((x, i) => {
            const requestLabel = x.requestLabel ?? 'request';
            const responseLabel = x.responseLabel ?? 'response';
            const requestRaw = x.rawHttpRequest ?? JSON.stringify(x.request, null, 2);
            const responseRaw = x.rawHttpResponse ?? JSON.stringify(x.response, null, 2);
            const atId = x.acceptanceTestId ?? '';
            const atTitle = x.acceptanceTestTitle ?? '';
            const role = x.exchangeRole ?? '';
            const purpose = x.exchangePurpose ?? '';
            const roleLabel =
              role === 'supporting'
                ? 'Supporting action (not the AT step itself)'
                : role === 'direct'
                  ? 'Direct AT step / assertion traffic'
                  : role;
            const atHeader =
              atId || atTitle || purpose
                ? `<div class="traffic-at-header">
  <div class="traffic-at-line"><span class="traffic-at-key">Acceptance test ID</span> ${escapeHtml(atId || '—')}</div>
  <div class="traffic-at-line"><span class="traffic-at-key">Acceptance test title</span> ${escapeHtml(atTitle || '—')}</div>
  <div class="traffic-at-line"><span class="traffic-at-key">This exchange</span> ${escapeHtml(roleLabel)}${purpose ? ` — ${escapeHtml(purpose)}` : ''}</div>
</div>`
                : '';
            return `<div class="traffic">
  <h5>HTTP ${i + 1}</h5>
  ${atHeader}
  <div class="message-block">
    <div class="label">${escapeHtml(requestLabel)}</div>
    <pre>${escapeHtml(requestRaw)}</pre>
  </div>
  <div class="message-block">
    <div class="label">${escapeHtml(responseLabel)}</div>
    <pre>${escapeHtml(responseRaw)}</pre>
  </div>
</div>`;
          })
          .join('');

        const trafficAndErrors = `${technicalErrorBlock}${noTrafficBlock}${traffic}`;
        return `<tr>
  <td class="col-test">${escapeHtml(t.acceptanceTestId ?? '')} ${escapeHtml(t.title)}</td>
  <td class="col-status${statusClass}">${escapeHtml(t.status)}</td>
  <td class="col-rt">${t.durationMs}</td>
  <td class="col-traffic-errors">${trafficAndErrors}</td>
</tr>`;
      })
      .join('\n');

    const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Playwright Traffic Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 16px; }
    table { border-collapse: collapse; width: 100%; table-layout: fixed; }
    th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; overflow-wrap: anywhere; word-break: break-word; }
    th { background: #f5f5f5; }
    .col-test { width: 150px; }
    .col-status { width: 150px; }
    .col-rt { width: 100px; }
    .col-traffic-errors { width: auto; }
    pre { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; max-width: 100%; }
    .message-block { margin-bottom: 8px; }
    .label { font-weight: 700; text-transform: lowercase; margin: 0 0 4px 0; }
    .error-block { border-left: 4px solid #d33; padding-left: 8px; }
    .no-traffic { border-left: 4px solid #f59e0b; padding-left: 8px; }
    .traffic { border: 1px solid #eee; margin-bottom: 8px; padding: 8px; }
    .traffic-at-header {
      background: #f0f9ff;
      border: 1px solid #bae6fd;
      border-radius: 4px;
      padding: 8px 10px;
      margin: 0 0 10px 0;
      font-size: 13px;
    }
    .traffic-at-line { margin: 4px 0; line-height: 1.35; }
    .traffic-at-key { font-weight: 700; color: #0369a1; margin-right: 6px; }
    h5 { margin: 0 0 6px 0; }
    .summary-bar { display: flex; gap: 24px; margin: 12px 0 20px 0; font-size: 15px; }
    .summary-bar span { padding: 4px 12px; border-radius: 4px; }
    .summary-passed { background: #dcfce7; color: #166534; }
    .summary-failed { background: #fee2e2; color: #991b1b; }
    .summary-skipped { background: #f3f4f6; color: #4b5563; }
    .failure-summary { margin: 0 0 24px 0; }
    .failure-summary h2 { color: #991b1b; }
    .failure-table { table-layout: auto; }
    .failure-table .at-id { font-weight: 700; font-family: monospace; }
    .failure-table pre { font-size: 13px; }
    .all-passed h2 { color: #166534; margin: 0 0 24px 0; }
    .status-failed { background: #fee2e2; color: #991b1b; font-weight: 700; }
    .status-passed { color: #166534; }
    .status-skipped { color: #6b7280; }
  </style>
</head>
<body>
  <h1>Playwright Traffic Report</h1>
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
        <th class="col-traffic-errors">HTTP Traffic and Errors</th>
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

export default TrafficHtmlReporter;
