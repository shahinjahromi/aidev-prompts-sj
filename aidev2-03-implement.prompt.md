---
name: "aidev2-implement"
description: "Implementation pipeline dispatcher for aidev2 blueprints. Steps: 01-diff, 02-plan, 03-execute, 04-extract-interfaces, 05-fix, 06-create-tests, 07-run-tests. Same step parameters as aidev-implement, but uses user-level embedded policy and schemas instead of blueprint-local .instructions."
argument-hint: "[01-diff | 02-plan | 03-execute | 04-extract-interfaces | 05-fix | 06-create-tests | 07-run-tests | 02-07] [optional free-text]"
agent: "aidev2-dispatcher"
---

Route this request through the dispatcher with implementation intent.

Intent: diff, plan, execute, extract interfaces, fix, create tests, or run tests.
Expected step tokens: `01-diff` through `07-run-tests`, or ranges.

Use these relative references only:
- [Dispatcher Agent](./aidev2-dispatcher.agent.md)
- [Planning Specialist](./aidev2-planning-specialist.agent.md)
- [Implementation Specialist](./aidev2-implementation-specialist.agent.md)
- [Testing Specialist](./aidev2-testing-specialist.agent.md)
- [Validation Specialist](./aidev2-validation-specialist.agent.md)
- [Agent Handoff Contract](./aidev2-details/aidev2-agent-handoff.md)
- [Implementation Pipeline](./aidev2-details/aidev2-implementation-instructions.md)
