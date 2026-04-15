# aidev2-combined Requirements

Scope: This file defines requirements for the `aidev2-combined` prompt only.

## REQ-C01 Single Default Agent

All pipeline stages execute within the default agent (`agent: "agent"`). No custom agents or subagent delegation.

## REQ-C02 Command Routing

Parse the first token of user input as a command. Supported commands:

| Command | Aliases | Scope |
|---|---|---|
| `warmup` | `cache` | Pre-load blueprint config + build session cache |
| `setup-app` | `setup` | Create new blueprint + app repo |
| `requirements` | `req` | Author, promote, reconcile requirements |
| `implement` | `impl` | Diff, plan, execute, extract, fix, manifest, docs |
| `all-steps` | `all`, `pipeline` | Full pipeline end-to-end |
| `upgrade` | — | Migrate blueprint to current conventions |
| `backup-prompts` | `backup` | Sync prompts to framework backup |
| `run-tests` | `test`, `tests` | Run Playwright acceptance tests |
| `instructions-cache` | — | Legacy cache command (alias for `warmup`) |

## REQ-C03 Warmup Command

On `warmup` or as implicit first step of `all-steps`:
1. Detect `BLUEPRINT_ROOT` from active file.
2. Read `config.yaml` + `codebase-context.yaml`.
3. Resolve all path variables (APP_ROOT, TOOLING_CMD, IMPL_ROOT, etc.).
4. Scan pending + current requirement IDs → compute max sequences per type.
5. Write session cache to `/memories/session/aidev2-config-cache.md`.
6. Report resolved values. No file modifications.

## REQ-C04 Pipeline Orchestration

When `all-steps` is invoked, execute sequentially within the same agent turn:
1. Pre-flight checks (PF-01..PF-04)
2. Requirements stage
3. Planning stage (diff + plan)
4. Implementation stage (execute + extract + fix + manifest + docs)
5. Validation gate (diff-clear + schema + manifest)
6. Testing stage (create + run tests)
7. Final validation gate

Abort on any `status: fail`, unexpected error, or missing artifact.

## REQ-C05 Narration & Logging

All stages emit structured narration and append to `BLUEPRINT_ROOT/10-logs/<timestamp>-aidev2.log`. Same format as dispatcher/specialist logs but with `[combined]` prefix for orchestration entries.

## REQ-C06 Step Files

The combined prompt loads step files on-demand from `aidev2-details/aidev2-steps/` only when the relevant command or pipeline stage is active. Step files are not pre-loaded at prompt parse time.

## REQ-C07 Performance Optimization

- Session cache avoids redundant YAML reads across stages.
- `cached_data` accumulates across pipeline stages within the same turn.
- Batch-read YAML on entry to each stage; re-read only on write.
- Script-first for mechanical steps (promote, diff, summarize-diff, apply).
