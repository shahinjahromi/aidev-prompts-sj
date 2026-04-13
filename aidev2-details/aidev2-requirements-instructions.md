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

### NFR Alignment Check

When authoring or updating any MAC item, check existing NFR and GLOBAL requirements for constraints that apply to the contract's domain:

1. Read all per-implementation NFR/GLOBAL files in both `01-pending-promotion/nfr-and-global-cr/` and `03-current/nfr-and-global-cr/`.
2. Identify NFRs whose `section` or `text` relates to the MAC's domain — e.g., performance, security, data retention, error format, API standards, pagination, encryption.
3. If relevant NFRs exist:
   - Narrate: "NFR alignment: found `<NFR-ID>` — <brief relevance>" for each.
   - Incorporate applicable constraints into the contract design (e.g., indexing strategy for performance NFRs, required fields for error-format NFRs, retention metadata for data-retention NFRs).
   - Populate the optional `nfr_refs` field on the MAC catalog entry with the IDs of constraining NFRs.
4. If a MAC design cannot satisfy an NFR constraint, flag the conflict to the user — do not silently ignore it.
5. If no NFRs exist or none are relevant, proceed normally — this is an advisory check, not a hard gate.

### Design-First Order

When authoring a mix of contract and FR items in a single session:
1. First: author or update MAC catalog entries and spec files.
2. Second: author FRs, NFRs, or other requirement types that reference those contracts.
3. If the user specifies a different order, follow it — but narrate the deviation.

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
| `NFR` | `pending: nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml`, `current: nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml` |
| `TS` | `pending: technology-selection/technology-selection-<IMPL_ID>.yaml`, `current: technology-selection/technology-selection-<IMPL_ID>.yaml` |
| `MAC` | `pending: models_and_contracts.yaml`, `current: models_and_contracts.yaml` |
| `UIC` | `pending: models_and_contracts/ui_contracts.yaml` (and any other spec file), `current: models_and_contracts/ui_contracts.yaml` |
| `AC` | All `functional_requirements.yaml`, `nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml` files in pending + current |
| `AT` | All `functional_requirements.yaml`, `nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml` files in pending + current |

### Before authoring any new item

1. Scan all relevant files for the type being authored.
2. Collect all existing sequence numbers for that type.
3. Set `next_seq = max(existing sequences) + 1` and use that for the new item.
4. Never reuse a number that exists anywhere in pending or current, regardless of short-title.

---

---

## Environment Variable Naming

When authoring requirements or acceptance tests that reference environment variables:

- Specify the **exact environment variable name** — never use vague descriptions like "the database connection env var". Use the actual name: e.g. `FAKEBANK_OMB_WEB_DATABASE_URL`, `AUTH_JWT_SECRET`, `REDIS_PORT`.
- If the variable is **specific to a module**, prefix it with the module name in UPPERCASE followed by underscore: `<MODULE>_<VAR_NAME>`. Examples: `PAYMENTS_STRIPE_KEY`, `AUTH_JWT_SECRET`, `NOTIFICATIONS_SMTP_HOST`.
- **Global or shared** env vars (not module-specific) must use the **app identifier prefix**: `<APP_IDENTIFIER>_<VAR_NAME>`. Derive the prefix from `config.yaml → identity.app_identifier`: uppercase all characters, replace every `-` with `_`, append trailing `_`. Example: `app_identifier: fakebank-omb-web` → prefix `FAKEBANK_OMB_WEB_` → `FAKEBANK_OMB_WEB_DATABASE_URL`, `FAKEBANK_OMB_WEB_LOG_LEVEL`.
- **Exception — well-known universal env vars** whose meaning is standard and unambiguous may omit the app identifier prefix: `PORT`, `HOME`, `PATH`, `TZ`.
- In acceptance criteria and acceptance tests, reference env vars by their exact name inside backticks.
- **Existing requirements are not retroactively renamed.** The app identifier prefix applies to newly authored env vars only.

---

## Environment Variable Documentation

When requirements introduce or reference new environment variables, the agent must maintain an env var documentation file at `<APP_ROOT>/aidev/docs/env-variable-instructions.md`.

- **Create** the file (and the `aidev/docs/` directory) if it does not exist.
- **Append** new env var entries; **update** existing entries if their definition changes.
- Each entry must document:
  - **Name** — exact variable name (e.g. `<APP_IDENTIFIER>_DATABASE_URL`)
  - **Module scope** — module name or `default` for non-module vars
  - **Description** — one-line purpose
  - **Format / type** — e.g. URL, integer, boolean, comma-separated list
  - **Sensitivity** — `secret` or `non-secret`
  - **Default value** — if any, or "none"
  - **Required / optional**
- Use a consistent markdown table or definition-list format.
- This file lives in the **application repo** (`APP_ROOT`), not the blueprint.

---

## Concrete Test Data in Acceptance Tests

Acceptance tests must include concrete input data and expected output data where the result is deterministic. Vague steps like "submit the form" or "verify success" are insufficient — they force the implementation agent to guess payloads and assertions.

### API endpoint ATs
- Include: HTTP method, path, example request body (JSON), expected status code, and expected response body shape with key fields.
- Example step: `POST /api/auth/login with body {"email": "user@example.com", "password": "Test1234!"} → expect 200 with {"token": "<string>", "expires_in": 3600}`

### Form / UI action ATs
- Include: field names with example values, the action (click, submit), and expected outcome (redirect URL, success message, state change).
- This is advisory when the AT is purely visual and covered by screenshot assertions.

### Data query ATs
- Include: query parameters or filter values and expected result shape/count.

### Deterministic vs. non-deterministic values
- **Deterministic** (status codes, error codes, redirect paths, cookie names, fixed field values): use exact literals.
- **Non-deterministic** (generated IDs, timestamps, tokens, session values): describe the expected type/shape — e.g. `"id": "<string UUID>"`, `"created_at": "<ISO 8601 timestamp>"`.

### Scope
- This rule applies to newly authored ATs. Existing ATs are not retroactively rewritten.
- AC `scenarios` (Given/When/Then) should also use concrete values where applicable.

---

## Per-Implementation NFR and Technology Selection Files

NFR and technology selection requirements live exclusively in per-implementation-id files inside their type folders.

- **Pending NFR**: `01-requirements/01-pending-promotion/nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml`
- **Current NFR**: `01-requirements/03-current/nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml`
- **Pending TS**: `01-requirements/01-pending-promotion/technology-selection/technology-selection-<IMPL_ID>.yaml`
- **Current TS**: `01-requirements/03-current/technology-selection/technology-selection-<IMPL_ID>.yaml`

Rules:
1. **No flat aggregate files** (`nfr_and_global_cr.yaml`, `technology_selection.yaml` at the stage root) — these do not exist; the per-implementation files are the only authoritative source.
2. When authoring NFR or TS items, read and write the per-implementation-id file for the active implementation directly.
3. ID uniqueness scanning (see above) covers all per-implementation files across both pending and current.
4. After promote, the current per-implementation file is updated; no separate mirror or aggregate step is needed.

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
