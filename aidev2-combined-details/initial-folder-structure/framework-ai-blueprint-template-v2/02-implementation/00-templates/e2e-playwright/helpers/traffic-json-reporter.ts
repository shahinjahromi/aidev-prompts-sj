import type { FullConfig, Reporter, Suite, TestCase, TestResult } from '@playwright/test/reporter';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

type ReporterOptions = { outputFile?: string };

type TrafficEntry = {
  acceptanceTestId?: string;
  acceptanceTestTitle?: string;
  exchangeRole?: string;
  exchangePurpose?: string;
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
  file: string;
  status: string;
  durationMs: number;
  error: string;
  httpTraffic: TrafficEntry[];
}

class TrafficJsonReporter implements Reporter {
  private outputFile: string;
  private startedAt = new Date().toISOString();
  private tests: TestEntry[] = [];

  constructor(options: ReporterOptions = {}) {
    this.outputFile =
      options.outputFile ?? path.join('playwright-output', 'traffic-report.json');
  }

  onBegin(_config: FullConfig, _suite: Suite): void {
    this.startedAt = new Date().toISOString();
  }

  onTestEnd(test: TestCase, result: TestResult): void {
    const traffic = (parseAttachmentBody(result, 'http-traffic') as TrafficEntry[] | null) ?? [];
    const title = test.titlePath().join(' > ');
    this.tests.push({
      title,
      acceptanceTestId: extractAtId(title),
      file: test.location.file,
      status: result.status,
      durationMs: result.duration,
      error: stripAnsi(result.error?.message ?? ''),
      httpTraffic: traffic,
    });
  }

  onEnd(): void {
    const failed = this.tests.filter((t) => t.status === 'failed');
    const failedAcceptanceTests = failed.map((t) => ({
      acceptanceTestId: t.acceptanceTestId ?? 'unknown',
      testTitle: t.title,
      reason: t.error || 'No error message captured',
    }));

    const output = {
      generatedAt: new Date().toISOString(),
      startedAt: this.startedAt,
      summary: {
        total: this.tests.length,
        passed: this.tests.filter((t) => t.status === 'passed').length,
        failed: failed.length,
        skipped: this.tests.filter((t) => t.status === 'skipped').length,
      },
      failedAcceptanceTests,
      tests: this.tests,
    };

    const outAbs = path.resolve(process.cwd(), this.outputFile);
    mkdirSync(path.dirname(outAbs), { recursive: true });
    writeFileSync(outAbs, JSON.stringify(output, null, 2), 'utf8');
  }
}

export default TrafficJsonReporter;
