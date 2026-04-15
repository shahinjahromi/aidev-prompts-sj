# aidev2-combined

Single-prompt alternative to the multi-agent aidev2 system. All pipeline stages run within the default agent — no dispatcher, no specialist agents.

This folder is scoped to `aidev2-combined.prompt.md` only.

## File Structure

| File | Purpose |
|---|---|
| `blueprint-policy.md` | Path resolution, config extraction, tooling discovery, YAML rules, session cache |
| `requirements-pipeline.md` | Authoring, promote, reconcile — all rules and steps |
| `implementation-pipeline.md` | Diff, plan, execute, extract, fix, tests, manifest, docs — all rules and steps |
| `requirements-aidev2-combined/` | Requirements and readme for this prompt |

## External Data Assets

JSON schemas and E2E reporter templates are shared infrastructure files referenced by path constants in `blueprint-policy.md` (`SCHEMAS_ROOT`, `E2E_TEMPLATES`). These are data files, not prompt instructions.

## Commands

`warmup` · `setup-app` · `requirements [step]` · `implement [step]` · `all-steps [from-*]` · `upgrade` · `backup-prompts` · `run-tests [mode]`
