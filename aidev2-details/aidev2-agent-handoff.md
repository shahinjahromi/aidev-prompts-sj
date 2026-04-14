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
    log_file_path: <absolute path to the pipeline activity log file, optional>
  timing:
    started_at: <ISO-8601 timestamp>
    ended_at: <ISO-8601 timestamp>
    elapsed_seconds: <number>
    script_invocations:
    - command_summary: <short description of the command>
      started_at: <ISO-8601>
      ended_at: <ISO-8601>
      elapsed_seconds: <number>
      exit_code: <number or null>
  errors:
  - step: <step token, e.g. IM-04, RQ-01>
    message: <error description>
    severity: error | warning
    was_unexpected: true | false
```

## Rules

- Include only data needed by the next stage.
- Do not include full prompt or instruction text in handoff payloads.
- Keep `summary` concise but specific.
- Include artifact paths whenever files are written.
- Include failed or skipped checks explicitly.
- Populate `cached_data` when the stage computed reusable state (sequences, standing constraints, config cache). Downstream stages should consume `cached_data` from the handoff before re-reading YAML files.

## Timing Rules

- Every specialist must populate `timing.started_at` and `timing.ended_at` with ISO-8601 timestamps and compute `timing.elapsed_seconds`.
- Every terminal command executed during the stage must be logged in `timing.script_invocations[]` with command summary, timestamps, elapsed seconds, and exit code.
- The dispatcher uses `timing` from each handoff to build the pipeline summary table.

## Error Rules

- Every error encountered (tool failures, script non-zero exits, validation failures) must be recorded in `errors[]`.
- Set `severity: error` for blocking failures and `severity: warning` for non-blocking issues.
- Set `was_unexpected: true` for unplanned errors (crashes, missing files, schema mismatches, tool timeouts, retries) — these are narrated in **bold** by both the specialist and the dispatcher.
- Set `was_unexpected: false` for known validation gate failures (e.g. diff not clear, manifest shape mismatch).
- `errors` may be an empty list when no errors occurred.
