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
  cached_data:
    max_sequences: <map of type->number, optional>
    standing_constraints: <list of NFR/GLOBAL one-line summaries, optional>
    config_cache_path: <session memory path if written, optional>
```

## Rules

- Include only data needed by the next stage.
- Do not include full prompt or instruction text in handoff payloads.
- Keep `summary` concise but specific.
- Include artifact paths whenever files are written.
- Include failed or skipped checks explicitly.
- Populate `cached_data` when the stage computed reusable state (sequences, standing constraints, config cache). Downstream stages should consume `cached_data` from the handoff before re-reading YAML files.
