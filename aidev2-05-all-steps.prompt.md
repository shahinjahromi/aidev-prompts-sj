---
name: "aidev2-all-steps"
description: "Full-pipeline orchestration for aidev2 blueprints. Runs requirements promote then full implementation pipeline (diff → plan → execute → extract-interfaces → fix → create-tests → run-tests) in a single supervised run."
argument-hint: "Optional: free-text context or 'from-promote' / 'from-diff' to start at a specific stage."
agent: "aidev2-dispatcher"
---

Run the full aidev2 sequence through the dispatcher.

Intent: full pipeline.
Stage start override: pass optional `from-promote`, `from-diff`, `from-plan`, `from-execute`, or `from-tests`.

Required sequence when not overridden:
1. Requirements stage
2. Diff and plan stage
3. Implementation stage
4. Validation gate
5. Testing stage (partial by default)
6. Final validation gate

Use these relative references only:
- [Dispatcher Agent](./aidev2-dispatcher.agent.md)
- [Agent Handoff Contract](./aidev2-details/aidev2-agent-handoff.md)
- [Blueprint Policy](./aidev2-details/aidev2-blueprint.instructions.md)
- [Requirements Pipeline](./aidev2-details/aidev2-requirements.instructions.md)
- [Implementation Pipeline](./aidev2-details/aidev2-implementation.instructions.md)
