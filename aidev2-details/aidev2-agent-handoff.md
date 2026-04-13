# Aidev2 Agent Handoff Contract

All specialist agents must return a single `handoff` payload after each run.
The dispatcher may continue only when `status: pass`.

## Required Shape

```yaml
handoff:
  stage: requirements | planning | implementation | validation | testing
  status: pass | blocked | fail
  summary: <short sentence>
  implementation_id: <value-or-empty>
  requirement_ids:
  - <REQ-ID>
  step_tokens:
  - <e.g. 01-author>
  artifacts_written:
  - path: <relative-or-absolute path>
    purpose: <why this file changed>
  checks:
  - name: <check name>
    result: pass | fail | skipped
    details: <short detail>
  blockers:
  - <empty when pass>
  next_inputs:
  - key: <name>
    value: <summary value>
```

## Rules

- Include only data needed by the next stage.
- Do not include full prompt or instruction text in handoff payloads.
- Keep `summary` concise but specific.
- Include artifact paths whenever files are written.
- Include failed or skipped checks explicitly.

## Shared Agent Constraints

Every specialist agent must:
- Return exactly one `handoff` payload per run using the shape above.
- Respect scope boundaries defined in its own `## Constraints` section — never perform work owned by another specialist.
- Read only the files listed in its `Load only:` block (plus files discovered during execution).
