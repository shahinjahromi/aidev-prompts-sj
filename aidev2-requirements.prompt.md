---
name: "aidev2-requirements"
description: "Requirements pipeline dispatcher for aidev2 blueprints. Steps: 01-author, 02-promote, 03-reconcile. Same step parameters as aidev-requirements, but uses user-level embedded policy and schemas instead of blueprint-local .instructions."
argument-hint: "[01-author | 02-promote | 03-reconcile | 01-02] [optional free-text task description]"
agent: "aidev2-dispatcher"
---

Route this request through the dispatcher with requirements intent.

Intent: requirements authoring, promote, or reconcile.
Expected step tokens: `01-author`, `02-promote`, `03-reconcile`, or ranges.

Use these relative references only:
- [Dispatcher Agent](./aidev2-dispatcher.agent.md)
- [Requirements Specialist](./aidev2-requirements-specialist.agent.md)
- [Agent Handoff Contract](./aidev2-details/aidev2-agent-handoff.md)
- [Requirements Pipeline](./aidev2-details/aidev2-requirements.instructions.md)
