# Plan: Detailed Subagent Narration with Timing, Errors, and Issue Highlighting

**Target directory:** `C:\Users\AndrewGmail\AppData\Roaming\Code\User\prompts`
**Scope:** All aidev2 agent/prompt/instruction/handoff files in the framework
**Status:** Applied — all changes committed

---

## 1. Problem Statement

The current framework (REQ-013) requires only minimal per-step narration ("one sentence or less"). There is no:
- Task start/end timestamps or elapsed-time reporting
- Script (terminal command) start/end lifecycle narration
- Error capture and narration from subagent runs
- Visual highlighting of unexpected issues
- Structured timing data in the handoff payload

Users lose visibility into what each subagent is doing, how long it takes, and when something goes wrong.

---

## 2. Goals

| # | Goal |
|---|------|
| G1 | Every subagent emits **task-start** and **task-end** narration lines with **wall-clock timestamps** and **elapsed time** |
| G2 | Every terminal/script invocation emits **script-start** and **script-end** narration with the command summary and elapsed time |
| G3 | All errors (tool failures, script non-zero exits, validation failures, blocked handoffs) are narrated immediately with context |
| G4 | Unexpected issues (unplanned errors, retries, fallbacks, schema mismatches) are narrated in **bold** |
| G5 | The handoff payload carries structured timing data so the dispatcher can produce a pipeline summary |

---

## 3. Files to Modify

### 3.1 Handoff Contract — `aidev2-details/aidev2-agent-handoff.md`

**What changes:**
- Add `timing` block to the required handoff shape:
  ```yaml
  timing:
    started_at: <ISO-8601 timestamp>
    ended_at: <ISO-8601 timestamp>
    elapsed_seconds: <number>
    script_invocations:
      - command_summary: <short description>
        started_at: <ISO-8601>
        ended_at: <ISO-8601>
        elapsed_seconds: <number>
        exit_code: <number or null>
  ```
- Add `errors` list to the handoff shape:
  ```yaml
  errors:
    - step: <step token>
      message: <error description>
      severity: error | warning
      was_unexpected: true | false
  ```
- Add rule: "When `was_unexpected: true`, the narrated output line must use **bold** formatting."

### 3.2 Dispatcher Agent — `aidev2-dispatcher.agent.md`

**What changes:**
- Add a **Narration Protocol** section after the existing Sequence section:
  1. Before invoking each specialist, emit: `--- STAGE START: <stage> at <timestamp> ---`
  2. After each specialist returns, emit: `--- STAGE END: <stage> at <timestamp> (elapsed: Xs) ---`
  3. If the handoff contains `errors`, iterate and narrate each one; bold any with `was_unexpected: true`.
  4. If `status: blocked` or `status: fail`, emit a **bold** summary of blockers.
  5. After the final specialist, emit a **Pipeline Summary** table:

     | Stage | Status | Elapsed | Errors |
     |-------|--------|---------|--------|
     | requirements | pass | 12s | 0 |
     | planning | pass | 8s | 0 |
     | ... | ... | ... | ... |

- Add a **Context Optimization** sub-rule: timing data in `cached_data` is optional for downstream consumption but mandatory for the dispatcher summary.

### 3.3 All Specialist Agent Files (6 files)

Files:
- `aidev2-requirements-specialist.agent.md`
- `aidev2-planning-specialist.agent.md`
- `aidev2-implementation-specialist.agent.md`
- `aidev2-validation-specialist.agent.md`
- `aidev2-testing-specialist.agent.md`

**What changes (identical block added to each):**

Add a **Narration Rules** section:

```markdown
## Narration Rules

1. **Task lifecycle:** At the start of the run, emit:
   `[<STAGE>] Task started at <ISO-8601 timestamp>`
   At the end, emit:
   `[<STAGE>] Task completed at <ISO-8601 timestamp> (elapsed: <N>s)`

2. **Script lifecycle:** Before every terminal command, emit:
   `[<STAGE>] Script start: <command-summary>`
   After the command returns, emit:
   `[<STAGE>] Script end: <command-summary> (exit: <code>, elapsed: <N>s)`

3. **Error narration:** When any tool call, script, or validation fails, immediately emit:
   `[<STAGE>] ERROR: <concise description of what failed and why>`
   Include the step token (e.g. `IM-04`, `RQ-01`) for traceability.

4. **Unexpected issues in bold:** When an error is unplanned (not a known validation gate failure, but an unexpected crash, missing file, schema mismatch, tool timeout, or retry), narrate in **bold**:
   `[<STAGE>] **UNEXPECTED: <description>**`

5. **Per-requirement narration (implementation/testing only):**
   - Before starting a requirement: `[<STAGE>] Requirement <REQ-ID> — starting`
   - After completing: `[<STAGE>] Requirement <REQ-ID> — done (<N>s)`

6. **Populate handoff timing:** Fill `timing.started_at`, `timing.ended_at`, `timing.elapsed_seconds`, and `timing.script_invocations[]` in the handoff payload.

7. **Populate handoff errors:** Fill `errors[]` with every error encountered. Set `was_unexpected: true` for unplanned issues.
```

### 3.4 Implementation Pipeline Instructions — `aidev2-details/aidev2-implementation.instructions.md`

**What changes:**

Add a new section **## Narration Standards** after the existing **## Core Rules** section:

```markdown
## Narration Standards

All implementation steps (IM-00 through IM-08) must follow these narration rules:

### Task Boundaries
- Emit `[IM-<NN>] Started at <timestamp>` at the beginning of each step.
- Emit `[IM-<NN>] Completed at <timestamp> (elapsed: <N>s)` at the end of each step.
- If a step is skipped, emit `[IM-<NN>] Skipped: <reason>`.

### Script Invocations
- Before running any terminal command: `[IM-<NN>] Script start: <command-summary>`
- After completion: `[IM-<NN>] Script end: <command-summary> (exit: <code>, elapsed: <N>s)`
- If exit code != 0: `[IM-<NN>] ERROR: <command-summary> failed with exit code <code>`

### Error and Unexpected Issue Narration
- Known validation failures (diff not clear, manifest shape mismatch) are narrated as `ERROR`.
- Unplanned failures (file not found, tool crash, unknown schema field, timeout) are narrated as **bold** `**UNEXPECTED: ...**`.
- Every error must include the step token and enough context to diagnose without re-reading logs.

### Per-Requirement Progress
- Before starting implementation of a requirement: `[IM-04] Requirement <REQ-ID> — starting`
- After completing: `[IM-04] Requirement <REQ-ID> — done (<N>s)`
- If a requirement encounters an error: `[IM-04] Requirement <REQ-ID> — **ERROR: <description>**`
```

### 3.5 Requirements Pipeline Instructions — `aidev2-details/aidev2-requirements.instructions.md`

**What changes:**

Add a **## Narration Standards** section (same pattern as implementation, but with `RQ-<NN>` prefix):
- Task boundaries for RQ-01 Author, RQ-02 Promote, RQ-03 Reconcile
- Per-item narration for each authored/promoted/reconciled artifact
- Error and unexpected-issue narration with bold formatting

### 3.6 Step Files — `aidev2-details/aidev2-steps/implement/*.md` and `requirements/*.md`

**What changes (each step file):**

Add a `## Narration` footer section to each step file specifying the exact narration lines that step must emit. Example for `01-diff.md`:

```markdown
## Narration
- On entry: `[IM-01] Diff started at <timestamp>`
- Before script: `[IM-01] Script start: ai-tooling.sh diff`
- After script: `[IM-01] Script end: ai-tooling.sh diff (exit: <code>, elapsed: <N>s)`
- On error: `[IM-01] ERROR: Diff script failed — <details>`
- On unexpected: `[IM-01] **UNEXPECTED: <details>**`
- On exit: `[IM-01] Diff completed at <timestamp> (elapsed: <N>s) — created: N, updated: N, removed: N`
```

Each step file gets its own tailored narration block with step-specific summary details.

### 3.7 Framework Requirements — `aidev2-details/framework-testing/framework-requirements.md`

**What changes:**

Upgrade REQ-013 and add new requirements:

- **REQ-013 (update):** Expand to include timing, error, and bold-unexpected narration rules alongside the existing concise-step narration.
- **REQ-NEW-A: Subagent timing narration** — Every specialist agent emits task-start/task-end with timestamps and elapsed time. Handoff payload includes `timing` block.
- **REQ-NEW-B: Script lifecycle narration** — Every terminal command invocation emits start/end with command summary, exit code, and elapsed time.
- **REQ-NEW-C: Error narration** — Every error from any source (tool, script, validation) is immediately narrated with step token and context.
- **REQ-NEW-D: Bold unexpected issues** — Unplanned errors, retries, and fallbacks are narrated in **bold** Markdown formatting.
- **REQ-NEW-E: Pipeline summary table** — Dispatcher emits a summary table after the final specialist with per-stage status, elapsed time, and error count.

Each new REQ gets an AT (acceptance test) definition following the existing convention.

---

## 4. Implementation Sequence

| Order | Action | Files | Depends On |
|-------|--------|-------|------------|
| 1 | Update handoff contract with `timing` and `errors` blocks | `aidev2-agent-handoff.md` | — |
| 2 | Add narration standards to implementation instructions | `aidev2-implementation.instructions.md` | 1 |
| 3 | Add narration standards to requirements instructions | `aidev2-requirements.instructions.md` | 1 |
| 4 | Add narration protocol to dispatcher agent | `aidev2-dispatcher.agent.md` | 1 |
| 5 | Add narration rules section to all 5 specialist agents | `*-specialist.agent.md` (×5) | 1 |
| 6 | Add narration footer to all 12 step files | `aidev2-steps/**/*.md` (×12) | 2, 3 |
| 7 | Update/add framework requirements and acceptance tests | `framework-requirements.md` | 1–6 |

---

## 5. Narration Format Reference

### Task Lifecycle
```
[STAGE] Task started at 2026-04-14T10:05:00Z
[STAGE] Task completed at 2026-04-14T10:05:32Z (elapsed: 32s)
```

### Script Lifecycle
```
[IM-01] Script start: ai-tooling.sh diff
[IM-01] Script end: ai-tooling.sh diff (exit: 0, elapsed: 4s)
```

### Error
```
[IM-04] ERROR: File src/routes/auth.ts not found — expected by plan.yaml line 42
```

### Unexpected Issue (bold)
```
[IM-04] **UNEXPECTED: Tool read_file returned timeout after 30s on manifest.yaml**
```

### Per-Requirement Progress
```
[IM-04] Requirement FR-0000012-login-page — starting
[IM-04] Requirement FR-0000012-login-page — done (18s)
```

### Pipeline Summary (dispatcher only)
```
--- PIPELINE SUMMARY ---
| Stage          | Status  | Elapsed | Errors | Unexpected |
|----------------|---------|---------|--------|------------|
| requirements   | pass    | 12s     | 0      | 0          |
| planning       | pass    | 8s      | 0      | 0          |
| implementation | pass    | 45s     | 1      | 0          |
| validation     | pass    | 3s      | 0      | 0          |
| testing        | pass    | 22s     | 0      | 0          |
| validation     | pass    | 2s      | 0      | 0          |
| TOTAL          |         | 92s     | 1      | 0          |
```

---

## 6. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Token overhead from narration lines | Narration is concise (one line per event); timing is structured in handoff, not prose |
| Timestamp accuracy in agent context | Use `date -u +%Y-%m-%dT%H:%M:%SZ` via terminal when precise wall-clock is needed; otherwise note that agent-side timestamps are approximate |
| Breaking existing handoff consumers | `timing` and `errors` are additive optional fields; existing handoff shape remains valid |
| Bold formatting not visible in all output contexts | Bold is standard Markdown; works in VS Code chat, terminal may not render it |

---

## 7. Validation Criteria

- [ ] Every specialist agent file contains a `## Narration Rules` section
- [ ] Handoff contract schema includes `timing` and `errors` blocks
- [ ] Dispatcher emits stage-start/stage-end and pipeline summary
- [ ] Every step file has a `## Narration` footer
- [ ] Both instruction files (implementation + requirements) have `## Narration Standards`
- [ ] Framework requirements updated with new REQs and ATs
- [ ] Unexpected issues render in **bold** in all narration
