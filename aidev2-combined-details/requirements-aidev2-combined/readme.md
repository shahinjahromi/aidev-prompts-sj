# aidev2-combined

Single-prompt alternative to the multi-agent aidev2 system. Runs all pipeline stages within the default agent — no dispatcher, no specialist agents.

## Scope

This folder (`aidev2-combined-details/requirements-aidev2-combined/`) contains artifacts for the `aidev2-combined` prompt only. It does not affect the standard multi-agent aidev2 prompts.

## Commands

| Command | Description |
|---|---|
| `warmup` | Pre-load blueprint config, resolve paths, build session cache |
| `setup-app` | Create new blueprint + app repo from framework template |
| `requirements [step]` | Author, promote, or reconcile requirements |
| `implement [step]` | Diff, plan, execute, extract, fix, test, manifest, docs |
| `all-steps [from-*]` | Full pipeline with optional stage override |
| `upgrade` | Migrate blueprint to current naming/ID conventions |
| `backup-prompts` | Sync user prompts to framework backup location |
| `run-tests [mode]` | Run Playwright acceptance tests (headed/debug/partial/full) |

## Architecture

- Uses `agent: "agent"` (default). No custom agent definitions.
- Loads step files and instruction references on demand per command.
- Session cache (`/memories/session/aidev2-config-cache.md`) eliminates redundant YAML reads across stages.
- Internal stage results follow the same shape as the handoff contract for consistent pipeline tracking.

## Tradeoffs vs Multi-Agent

| Aspect | aidev2-combined | Multi-agent aidev2 |
|---|---|---|
| Context window | All policy in one prompt | Split across specialists |
| Latency | No inter-agent handoff | Agent invocation overhead |
| File read scoping | Self-enforced | Enforced per-specialist |
| Maintainability | Single file | Modular files |

## Files

- [aidev2-combined-requirements.md](./aidev2-combined-requirements.md) — requirements for the combined prompt
- [../../aidev2-combined.prompt.md](../../aidev2-combined.prompt.md) — the prompt file
