---
description: "Embedded AI-dev v2 requirements pipeline for aidev2 prompts. Covers authoring, promotion, and reconciliation rules including module property handling, ID uniqueness, contract reference structure, design-first authoring, and models/contracts authoring."
---

# Aidev2 Requirements Pipeline

## Design-First Authoring

The framework follows a **design-first** approach. When authoring requirements:

1. Models, data contracts, API contracts, and UI contracts (MAC items and their spec files) shall be defined or updated **before or alongside** the functional requirements that reference them.
2. The user may request authoring of models and contracts as a standalone operation — without any accompanying FRs. This is a first-class operation, not secondary to FR authoring.
3. When authoring models or contracts, narrate: "Authoring design artifact: `<MAC-ID> <title>`" before writing.

### Models and Contracts Authoring

When the user requests creation or update of a model, contract, API contract, UI contract, or data schema:

1. Locate or create the relevant MAC catalog entry in `01-requirements/01-pending-promotion/models_and_contracts.yaml`.
2. Create or update the referenced spec file under `01-requirements/01-pending-promotion/models_and_contracts/`.
3. Sync `child_specifications` on the MAC catalog entry to match all child IDs in the spec file.
4. If the user also requests FRs referencing this contract, author them next using `contract_type: models_and_contracts` with the MAC ID.
5. Models and contracts can be authored in isolation — without accompanying FRs. Do not require an FR to author a contract.

### Design-First Order

When authoring a mix of contract and FR items in a single session:
1. First: author or update MAC catalog entries and spec files.
2. Second: author FRs, NFRs, or other requirement types that reference those contracts.
3. If the user specifies a different order, follow it — but narrate the deviation.

---

## YAML Output Rules

All YAML written by agents — whether authoring, promoting, reconciling, or generating artifacts — must follow these formatting rules:

1. **Indent with 2 spaces. Never use tabs.** Every nesting level is exactly 2 spaces.
2. **Block style only.** Use `|` or `>` for multi-line strings. Do not use inline `{key: value}` or `[a, b]` flow notation for mappings or sequences.
3. **Quote strings containing special characters.** Any value containing `{`, `}`, `[`, `]`, `:`, `#`, `&`, `*`, `!`, `|`, `>`, `'`, `"`, `%`, `@`, or backtick must be double-quoted.
4. **No trailing whitespace** on any line.
5. **Single newline at end of file.**

---

## Module Property

All requirement types (FR, NFR, GLOBAL, MAC, UIC, TS) support an optional `module` field.

### Authoring rules

- When the user specifies a module (in the task description or via follow-up), set the `module` field on every authored item.
- When the user does not specify a module, omit the field — do not default to an empty string.
- When updating an existing requirement (`action: update`), preserve the current `module` value unless the user explicitly requests a module change.
- When the user requests a module reassignment on an update, set the new `module` value on the replacement entry. The diff and implementation pipeline will detect the change and handle undo/redo.
- Module values are free-form strings (e.g. `auth`, `payments`, `account-detail`, `shared`). Use the value exactly as the user provides it — do not normalize or invent module names.

### Validation

- The `module` field is optional in all schemas; never reject an artifact for missing it.
- When writing artifacts, validate against the local schema bundle which now includes the `module` property definition.

---

## ID Uniqueness Rule

Sequence numbers must be **globally unique within each requirement type** across the entire blueprint (pending + current).

- No two items with the same type prefix (`FR`, `NFR`, `TS`, `MAC`, `UIC`, `AC`, `AT`, `CONTRACT`) may share the same 7-digit sequence number, even if their short-titles differ.
- Scope: all files under `01-requirements/01-pending-promotion/` and `01-requirements/03-current/`.

### Files to scan per type prefix before authoring

| Type prefix | Files to scan |
|---|---|
| `FR` | `pending: functional_requirements.yaml`, `current: functional_requirements.yaml` |
| `NFR` | `pending: nfr_and_global_cr.yaml`, `current: nfr_and_global_cr.yaml` |
| `TS` | `pending: technology_selection.yaml`, `current: technology_selection.yaml` |
| `MAC` | `pending: models_and_contracts.yaml`, `current: models_and_contracts.yaml` |
| `UIC` | `pending: models_and_contracts/ui_contracts.yaml` (and any other spec file), `current: models_and_contracts/ui_contracts.yaml` |
| `AC` | All `functional_requirements.yaml`, `nfr_and_global_cr.yaml` files in pending + current |
| `AT` | All `functional_requirements.yaml`, `nfr_and_global_cr.yaml` files in pending + current |

### Before authoring any new item

1. Scan all relevant files for the type being authored.
2. Collect all existing sequence numbers for that type.
3. Set `next_seq = max(existing sequences) + 1` and use that for the new item.
4. Never reuse a number that exists anywhere in pending or current, regardless of short-title.

---

## YAML Read Efficiency

Reading individual YAML files one-at-a-time is the dominant I/O cost during requirements authoring. Apply these rules to reduce round-trips:

1. **Batch-read on entry.** At the start of an authoring session, read all YAML files under `01-pending-promotion/` and `03-current/` in a single parallel batch. Cache the parsed contents in working memory for the duration of the session.
2. **Derive sequences from cache.** When computing `next_seq`, use the already-cached file contents — do not re-read files you have already loaded.
3. **Re-read only on write.** After writing a YAML file, re-read only that file to refresh the cache. Do not re-read the entire tree.
4. **Use the instructions cache.** If the session memory file `aidev2-config-cache.md` already contains `max_sequence` values for a type, use those as the starting point and scan only for IDs above that value. Update the cache after authoring.
5. **Script-first for promote (REQ-042).** RQ-02 Promote is mechanical — execute via `ai-tooling.sh promote`. Read only stdout/stderr and exit code. Do not parse pending-promotion or current YAML to replicate promote logic.
6. **Consume cached_data first (REQ-045).** If the dispatcher provides `cached_data` containing requirement paths, max_sequence values, or config data, use those. Do not re-read YAML files for data already in `cached_data`.

---

## Post-Write Technology Selection Mirrors

The canonical stage files remain:
- `01-requirements/01-pending-promotion/technology_selection.yaml`
- `01-requirements/03-current/technology_selection.yaml`

Per-implementation mirror files must live under stage-local subfolders:
- `01-requirements/01-pending-promotion/technology-selection/technology_selections_<implementation_id>.yaml`
- `01-requirements/03-current/technology-selection/technology_selections_<implementation_id>.yaml`

Rules:
1. Treat the stage-root `technology_selection.yaml` file as the authoritative source for that stage.
2. After any write that changes pending technology selections, refresh the pending per-implementation mirror file for each affected implementation.
3. After any write that changes current technology selections, refresh the current per-implementation mirror file for each affected implementation.
4. Mirror file naming must use the lowercase prefix `technology_selections_` and the exact implementation id.
5. Mirror files must contain only the entries applicable to that implementation, with `implementation_id` / `implementation_ids` stripped from the mirrored entries.

---

## Contract References (`contract_refs`)

All requirements (`FR`, `NFR`, `GLOBAL`) that reference contracts must follow this structure:

### Rules

1. **Always use `contract_type: models_and_contracts`** — never `contract_type: ui_contracts` or any other contract type. All contracts, including UI contracts, are referenced through their parent MAC entry.
2. **Reference by MAC ID** using `id: MAC-XXXXXXX-short-title` under `specific_ids`.
3. **`specific_ids` entries are objects**, not bare strings. Format:
   ```yaml
   contract_refs:
   - contract_type: models_and_contracts
     selection: specific_ids
     specific_ids:
     - id: MAC-0000001-some-contract
     - id: MAC-0000002-ui-contracts-wrapper
       child_specifications: all
   ```
4. **`child_specifications`** is required on any `specific_ids` entry whose MAC wraps a multi-item spec file (e.g., a `ui_contracts.yaml` that defines multiple UIC items):
   - Use `child_specifications: all` when the requirement consumes all items in the spec (default — use this unless specific children are needed).
   - Use an explicit list `child_specifications: [UIC-0000001-foo, UIC-0000003-bar]` only when the requirement targets specific child items.
5. **Default behavior**: if a MAC entry has `child_specifications` defined in the MAC catalog, assume `child_specifications: all` in contract_refs unless the user specifies otherwise.

### What NOT to do

- ❌ `contract_type: ui_contracts` — this type does not exist; UI contracts go through their parent MAC.
- ❌ Bare strings in `specific_ids`: `- MAC-0000001-foo` — always use object form `- id: MAC-0000001-foo`.
- ❌ `sub_mac_ids` — this field name is obsolete; the correct field is `child_specifications`.
- ❌ Separate `contract_refs` entries for each UIC — consolidate into the parent MAC entry with `child_specifications`.

---

## `child_specifications` on MAC Catalog Entries

When a MAC catalog entry in `models_and_contracts.yaml` wraps a spec file that defines multiple items (e.g., `ui_contracts.yaml` with many UIC entries), the MAC catalog entry must carry a `child_specifications` list enumerating all child IDs:

```yaml
- id: MAC-0000002-fakebank-frontend-ui-contracts
  title: Fakebank Frontend UI Contracts
  spec_file: models_and_contracts/ui_contracts.yaml
  child_specifications:
  - UIC-0000001-authenticated-app-shell
  - UIC-0000002-overview-dashboard
  # ... all child IDs
```

### Rules

- The `child_specifications` list on the MAC catalog entry must be kept in sync with the items defined in the referenced spec file.
- When new child items are added to a spec file, update the parent MAC entry's `child_specifications` accordingly.
- The `child_specifications` on the MAC catalog entry is the authoritative list of children for `child_specifications: all` resolution.
- Single-item spec files (e.g., a MAC that wraps exactly one API contract schema) do not require `child_specifications` on the catalog entry.

---

## Narration Standards

All requirements steps (RQ-01 through RQ-03) must follow these narration rules.

### Task Boundaries
- Emit `[RQ-<NN>] Started at <ISO-8601 timestamp>` at the beginning of each step.
- Emit `[RQ-<NN>] Completed at <ISO-8601 timestamp> (elapsed: <N>s)` at the end of each step.
- If a step is skipped, emit `[RQ-<NN>] Skipped: <reason>`.

### Script Invocations
- Before running any terminal command: `[RQ-<NN>] Script start: <command-summary>`
- After completion: `[RQ-<NN>] Script end: <command-summary> (exit: <code>, elapsed: <N>s)`
- If exit code != 0: `[RQ-<NN>] ERROR: <command-summary> failed with exit code <code>`

### Per-Item Narration
- Before authoring each artifact: `[RQ-01] Authoring <TYPE>-<ID> — <short-title>`
- After writing: `[RQ-01] Wrote <TYPE>-<ID>`
- Before promoting: `[RQ-02] Promoting <count> items`
- After promoting: `[RQ-02] Promoted <count> items (<N>s)`

### Error and Unexpected Issue Narration
- Known validation failures (schema mismatch, ID collision) are narrated as: `[RQ-<NN>] ERROR: <description>`
- Unplanned failures (file not found, tool crash, timeout) are narrated in **bold**: `[RQ-<NN>] **UNEXPECTED: <description>**`
- Every error must include the step token and enough context to diagnose without re-reading logs.
