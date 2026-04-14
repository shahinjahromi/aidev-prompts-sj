---
name: "aidev2-all-steps"
description: "Full-pipeline orchestration for aidev2 blueprints. Runs requirements promote then full implementation pipeline (diff → plan → execute → extract-interfaces → fix → create-tests → run-tests) in a single supervised run."
argument-hint: "Optional: free-text context or 'from-promote' / 'from-diff' to start at a specific stage."
agent: "aidev2-dispatcher"
---

Run the full aidev2 sequence through the dispatcher.

Intent: full pipeline.
Stage start override: pass optional `from-promote`, `from-diff`, `from-plan`, `from-execute`, or `from-tests`.

Pre-flight: Run all pre-flight checks (PF-01 through PF-04) before the first specialist. Abort the pipeline if any check fails. If `.aidev` bootstrap files are missing, create them during PF-03. See dispatcher agent for details.

Required sequence when not overridden:
1. Requirements stage
2. Diff and plan stage
3. Implementation stage
4. Validation gate
5. Testing stage (partial by default)
6. Final validation gate

Pipeline abort: If any stage returns `status: blocked` or `status: fail`, or if a specialist fails to return a valid handoff, the pipeline must abort immediately — do not continue to the next stage.

Use these relative references only:
- [Dispatcher Agent](./aidev2-dispatcher.agent.md)
- [Agent Handoff Contract](./aidev2-details/aidev2-agent-handoff.md)

Do NOT load Blueprint Policy, Requirements Pipeline, or Implementation Pipeline here — the dispatcher and specialists load only what they need.
