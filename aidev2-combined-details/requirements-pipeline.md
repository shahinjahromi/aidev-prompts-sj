# Requirements Pipeline

All rules and steps for requirements authoring, promotion, and reconciliation.

## Design-First Authoring

Models, contracts, and API/UI contracts (MAC items and specs) are defined **before or alongside** the FRs that reference them. MAC authoring is a first-class standalone operation.

When authoring a mix: (1) MAC catalog + spec files (2) FRs/NFRs referencing those contracts.

## Module Property

All requirement types support optional `module`:
- User specifies module → set it on every authored item.
- User silent → omit (no default).
- Update (`action: update`) → preserve existing value unless user explicitly changes it.
- Module reassignment is a valid update — diff/implementation pipeline detects the change.
- Values are free-form strings, used exactly as provided.

## ID Uniqueness

Sequence numbers must be **globally unique within each type** across pending + current.

### Scan table

| Type | Files to scan |
|---|---|
| `FR` | `functional_requirements.yaml` (pending + current) |
| `NFR`, `GLOBAL` | `nfr_and_global_cr*.yaml` (pending + current) |
| `TS` | `technology_selection.yaml` (pending + current) |
| `MAC` | `models_and_contracts.yaml` (pending + current) |
| `UIC` | All spec files under `models_and_contracts/` (pending + current) |
| `AC`, `AT` | All `functional_requirements.yaml` + `nfr_and_global_cr*.yaml` (pending + current) |

Before writing any new item:
1. Scan all relevant files for the type.
2. Collect all existing sequence numbers.
3. `next_seq = max(existing) + 1`. Never reuse.

## Contract References (`contract_refs`)

Rules for FR, NFR, GLOBAL items referencing contracts:
- **Always** `contract_type: models_and_contracts`. Never `ui_contracts`.
- Reference by MAC ID in object form: `- id: MAC-XXXXXXX-short-title`.
- For MAC entries wrapping multi-item specs (e.g., `ui_contracts.yaml`), add `child_specifications: all` (default) or explicit list `[UIC-XXXXXXX-..., ...]`.

```yaml
contract_refs:
- contract_type: models_and_contracts
  selection: specific_ids
  specific_ids:
  - id: MAC-0000001-some-api-contract
  - id: MAC-0000002-ui-contracts-wrapper
    child_specifications: all
```

**Never use:** `contract_type: ui_contracts`, bare string `specific_ids`, `sub_mac_ids` (obsolete → `child_specifications`).

## MAC Catalog `child_specifications`

When a MAC entry wraps a multi-item spec file:
- Include `child_specifications` listing all child IDs in the spec.
- Keep in sync when child items are added/removed.
- Single-item specs don't need `child_specifications`.

## Technology Selection Mirrors

Canonical files: `PENDING/technology_selection.yaml` and `CURRENT/technology_selection.yaml`.
Per-implementation mirrors: `PENDING_TECH_DIR/technology_selection_<ID>.yaml` and `CURRENT_TECH_DIR/technology_selection_<ID>.yaml`.

After any TS write, refresh the relevant mirror. Mirrors contain only entries for that implementation with `implementation_id`/`implementation_ids` stripped.

## Read Efficiency

1. **Batch-read on entry:** All YAML under `PENDING/` and `CURRENT/` in one parallel batch. Cache for the session.
2. **Derive from cache:** Use cached contents for `next_seq` — don't re-read.
3. **Re-read only on write:** After writing a file, refresh only that file.
4. **Use session cache:** If `aidev2-config-cache.md` has `max_sequence` values, use as floor.
5. **Consume `cached_data` first:** If prior stages provided data, use it.

---

## RQ-01 Author

**Inputs:** Task description, artifact type, pending/current files, schemas.
**Action:** Write/update pending artifacts only.
**Rules:** FR/NFR/GLOBAL drive code; MAC is metadata only; UI contracts are screen-only.

ID allocation: run uniqueness scan (above) before every new ID. Module handling: apply module rules (above). Contract refs: apply contract_refs rules (above).

### Deletion (`action: delete`)

When a promoted requirement must be removed:
1. Assign a **new ID** (next sequence — never reuse target's ID).
2. Set `action: delete`, `replaces_id: <target-ID>`, `text: ''`, `section: Removals`.
3. Omit `acceptance_criteria`, `acceptance_tests`, `contract_refs`.
4. If an `action: update` already targets the same source, replace it with the delete entry.

### Narration
- `[RQ-01] Author started at <ts>` / `Authoring <TYPE>-<ID> — <title>` / `Wrote <TYPE>-<ID>` / `Author completed at <ts> (elapsed: <N>s) — <N> items`

---

## RQ-02 Promote

**Inputs:** `TOOLING_CMD`, `REQ_PATH`, `IMPLEMENTATION_ID`, `APP_ROOT`.
**Action:** Run promote script. This step is **mechanical**.

Command:
```bash
"$TOOLING_CMD" promote -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"
```

Rules:
1. Run via fresh foreground terminal. Read only stdout/stderr and exit code.
2. Do NOT read/parse pending, current, or control.yaml to replicate promote logic.
3. After promote, trust that `03-current/` was updated — don't re-read inputs.
4. **No-op handling:** If promote says "No pending items", this is NOT unexpected. Log `severity: warning`, `was_unexpected: false`. Continue.
5. **Failure:** Unexpected promote failures are fatal → `status: fail`, stop stage.

### Narration
- `[RQ-02] Promote started at <ts>` / `Script start: ai-tooling.sh promote` / `Script end: ... (exit: <code>, elapsed: <N>s)` / `Promoted <N> items` / `Promote completed at <ts> (elapsed: <N>s)`

---

## RQ-03 Reconcile

**Inputs:** App codebase, current technology_selection, MANIFEST.
**Action:** Backfill implemented TS entries and sync diff. Only for already-implemented tech choices.

After writes:
- Refresh `CURRENT_TECH_DIR/technology_selection_<IMPLEMENTATION_ID>.yaml`.

### Narration
- `[RQ-03] Reconcile started at <ts>` / `Syncing <N> entries` / `Reconcile completed at <ts> (elapsed: <N>s)`
