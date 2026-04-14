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

These rules apply to every YAML file written during authoring, promote, reconcile, and merge operations.

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

Minimize redundant file I/O during authoring, promote, and reconcile operations:

1. **Batch reads.** When a step needs data from multiple YAML files (e.g. ID uniqueness scan across pending + current), read all required files in a single parallel batch — do not read them one at a time in sequence.
2. **Cache within the step.** Once a YAML file has been read during the current pipeline step, reuse the in-memory content for the remainder of that step. Do not re-read the same file unless it was written to since the last read.
3. **Session-level sequence cache.** After the first ID uniqueness scan in a session, store the per-type `max_seq` values in session memory. On subsequent authoring calls in the same session, read only files modified since the cache was populated instead of re-scanning all files.
4. **Skip unchanged files during promote.** When promoting, compare file modification timestamps or content hashes before copying. Skip files whose content has not changed since the last promote.

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
