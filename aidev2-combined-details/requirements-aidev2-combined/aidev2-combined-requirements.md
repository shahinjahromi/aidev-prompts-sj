# aidev2-combined Requirements

Scope: artifacts in this folder apply to `aidev2-combined.prompt.md` only.

## REQ-C01 Single Default Agent

All stages execute within `agent: "agent"`. No custom agents, no subagent delegation.

## REQ-C02 Command Routing

Parse first token as command. Supported: `warmup`, `setup-app`, `requirements`, `implement`, `all-steps`, `upgrade`, `backup-prompts`, `run-tests` (with aliases).

## REQ-C03 Self-Contained References

The prompt references only files under `aidev2-combined-details/`. No dependencies on `aidev2-details/`. JSON schemas, TypeScript reporter templates, and all shared data assets are bundled locally under `aidev2-combined-details/aidev2-schemas/` and `aidev2-combined-details/e2e-playwright-templates/`.

## REQ-C04 Warmup

`warmup` pre-loads blueprint config, resolves paths, scans YAML for max sequences, writes session cache. Eliminates redundant I/O in subsequent stages.

## REQ-C05 Pipeline Orchestration

`all-steps` executes sequentially: pre-flight → warmup → requirements → planning → implementation → validation → testing → manifest → docs → final validation. Abort on any failure or unexpected error.

## REQ-C06 No Redundancy

YAML output rules stated once (blueprint-policy.md). ID uniqueness stated once (requirements-pipeline.md). Script-first execution stated once per step. Narration patterns stated per-step in compact form. No agent handoff overhead.

## REQ-C07 Performance

Session cache avoids redundant reads. `cached_data` accumulates across stages. Batch-read YAML on entry. Script-first for mechanical steps (promote, diff, summarize-diff, apply).
