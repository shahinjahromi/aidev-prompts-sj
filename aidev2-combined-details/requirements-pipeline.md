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

### Fast path (fresh project)

If `cached_data.max_sequences` shows all zeros (or warmup marked the project as `fresh: true` because pending + current directories have no items), skip the scan entirely — start all sequences at `0000001`. This avoids 6+ file reads for a brand-new project.

### Scan table (only when existing items exist)

| Type | Files to scan |
|---|---|
| `FR` | `functional_requirements.yaml` (pending + current) |
| `NFR`, `GLOBAL` | `nfr_and_global_cr*.yaml` (pending + current) |
| `TS` | `technology_selection.yaml` (pending + current) |
| `MAC` | `models_and_contracts.yaml` (pending + current) |
| `UIC` | All spec files under `models_and_contracts/` (pending + current) |
| `AC`, `AT` | All `functional_requirements.yaml` + `nfr_and_global_cr*.yaml` (pending + current) |

Before writing any new item:
1. Use `cached_data.max_sequences` from warmup as the floor. Only re-scan if warmup cache is missing.
2. `next_seq = max(cached, existing) + 1`. Never reuse.
3. After allocating, update `cached_data.max_sequences` in memory — don't re-scan for the next item in the same run.

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
Per-implementation mirrors: `PENDING_TECH_DIR/technology-selection-<ID>.yaml` and `CURRENT_TECH_DIR/technology-selection-<ID>.yaml`.

After any TS write, refresh the relevant mirror. Mirrors contain only entries for that implementation with `implementation_id`/`implementation_ids` stripped.

## Read Efficiency

1. **Use warmup cache first:** `cached_data` from §WARMUP contains requirement YAML content, max_sequences, and standing constraints. Always consume cache before reading files.
2. **Batch-read on entry (if cache miss):** All YAML under `PENDING/` and `CURRENT/` in one parallel batch. Cache for the session.
3. **Derive from cache:** Use cached contents for `next_seq` — don't re-read.
4. **Re-read only on write:** After writing a file, refresh only that file in cache.
5. **Consume `cached_data` first:** If prior stages provided data, use it.

### Inline Schema Quick-Reference (avoid reading schema JSON files)

The schemas rarely change. Use this quick-reference instead of opening `aidev2-schemas/*.json`:

**FR** (`functional_requirements.yaml`):
```yaml
schema_version: 1
type: functional_requirements
items:
- id: "FR-NNNNNNN-kebab-slug"   # pattern: ^FR-[0-9]{7}-[a-z0-9-]+$
  text: "Requirement text"
  section: "Section Name"
  module: "optional-module"      # optional
  action: update|delete          # omit for create
  replaces_id: "FR-..."          # required for update/delete
  contract_refs: [...]           # optional
  acceptance_criteria:           # MANDATORY
  - id: "AC-NNNNNNN-kebab-slug"  # pattern: ^AC-[0-9]{7}-[a-z0-9-]+(-v[0-9]+)?$
    title: "..."
    criteria: ["atomic condition 1", ...]
    scenarios: [{name, given, when, then}]
  acceptance_tests:              # MANDATORY
  - id: "AT-NNNNNNN-kebab-slug"  # pattern: ^AT-[0-9]{7}-[a-z0-9-]+(-v[0-9]+)?$
    name: "..."
    steps: ["step1", ..., "step12"]  # 6-12 Playwright-precise steps
    expected_result: "..."
```

**NFR/GLOBAL** (`nfr-and-global-cr-<impl-id>.yaml`): Same structure as FR but `id` pattern is `^(NFR|GLOBAL)-[0-9]{7}-[a-z0-9-]+$`.

**TS** (`technology-selection-<impl-id>.yaml`):
```yaml
schema_version: 1
type: technology_selection
entries:
- id: "TS-NNNNNNN-kebab-slug"  # pattern: ^TS-[a-z0-9-]+$
  category: "..."
  capability: "..."
  name: "..."
  version: "..."
  description: "..."
  module: "optional"            # optional
```

**MAC** (`models_and_contracts.yaml`): `id` pattern `^MAC-[0-9]{7}-[a-z0-9-]+$`, required fields: `logical_id`, `title`, `summary`, `spec_format` (openapi_yaml|graphql_sdl_yaml|logical_database_schema|physical_database_schema|domain_model), `spec_path`. Optional: `module`, `child_specifications` (list child IDs when spec file contains multiple named items).

Only read the actual schema JSON files when encountering an unusual validation error.

---

## RQ-01 Author

**Inputs:** Task description, artifact type, pending/current files, schemas (from `SCHEMAS_ROOT` — never from app blueprint `.schemas/`).
**Action:** Write/update pending artifacts only.
**Rules:** FR/NFR/GLOBAL drive code; MAC is metadata only; UI contracts are screen-only.

ID allocation: run uniqueness scan (above) before every new ID. Module handling: apply module rules (above). Contract refs: apply contract_refs rules (above).

### Acceptance Criteria & Acceptance Tests (Mandatory)

Every FR, NFR, and GLOBAL requirement **MUST** include both `acceptance_criteria` and `acceptance_tests`. Omitting either is a pipeline violation.

**Acceptance Criteria (AC):**
- Each AC has `id` (AC-NNNNNN), `title`, `criteria` (list of atomic verifiable conditions), and `scenarios` (Given/When/Then).
- Criteria must be specific and measurable — no vague language like "should work correctly" or "handles errors appropriately".
- Scenarios must cover happy path, key edge cases, and error conditions.

**Acceptance Tests (AT):**
- Each AT has `id` (AT-NNNNNN), `name`, `steps` (6-12 items), and `expected_result`.
- Steps are the **primary input for Playwright test generation** (IM-07). They must be precise enough that two developers produce near-identical Playwright code from the same AT.
- Steps must specify:
  - Exact user actions: "Click the Submit button", "Type 'test@example.com' into the Email field"
  - Navigation targets: "Navigate to /auth/login"
  - Expected DOM states: "The error banner with text 'Invalid credentials' is visible"
  - HTTP details where relevant: "POST /api/auth/login returns 200 with JSON body containing 'token' field"
  - Timing/sequencing: "After redirect completes, the dashboard page is visible"
  - Data preconditions: "Given a test user exists with email 'test@example.com'"
- **Low variability rule:** AT steps must leave minimal room for interpretation. Avoid abstract steps like "verify the page loads correctly" — instead specify which elements, text, or responses to assert.
- **Playwright mapping:** AT step language should map naturally to Playwright actions (`page.goto`, `page.click`, `page.fill`, `expect(locator).toBeVisible`, `expect(response).toHaveStatus`, `request.post`, etc.).

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
- Refresh `CURRENT_TECH_DIR/technology-selection-<IMPLEMENTATION_ID>.yaml`.

### Narration
- `[RQ-03] Reconcile started at <ts>` / `Syncing <N> entries` / `Reconcile completed at <ts> (elapsed: <N>s)`
