# RQ-01 Author
Inputs: TASK_DESCRIPTION, artifact type, pending/current files, local schemas.
Action: write/update pending artifacts only.
Rules: FR/NFR/GLOBAL drive code; MAC metadata only; UI contracts are screen-only.

Module handling:
- If the user specifies a module, set the `module` field on every authored item.
- If the user does not mention a module, omit the field.
- On updates (`action: update`), carry forward the existing `module` value unless the user explicitly changes it.
- Module reassignment is a valid update reason — set the new value and the diff/implementation pipeline detects the change.

## NFR Alignment (MAC authoring)

Before writing or updating any MAC catalog entry:

1. Read all NFR/GLOBAL files for the active implementation in both pending and current: `nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml`.
2. Scan for NFRs whose `section` or `text` relates to the MAC's spec format or domain (e.g., database schemas → performance/indexing/retention NFRs; API contracts → error-format/response-time/security NFRs).
3. For each relevant NFR, narrate: "NFR alignment: `<NFR-ID>` — <how MAC accounts for it>".
4. If the MAC is a database schema (`spec_format: physical_database_schema` or `logical_database_schema`) and NFRs mention indexing, query performance, data retention, or encryption — incorporate those constraints into the schema design.
5. Populate the `nfr_refs` field on the MAC catalog entry with the IDs of constraining NFRs found.
6. If conflicting constraints exist, flag to the user before proceeding.
7. If no NFRs exist or none relate, proceed without `nfr_refs` — this check is advisory.

## ID Uniqueness (mandatory before assigning any new ID)

Sequence numbers must be globally unique within each type across the entire blueprint (pending + current). Before writing any new item:

1. Scan the relevant files for the type being authored:
   - `FR`: `functional_requirements.yaml` in pending + current
   - `NFR` / `GLOBAL`: `nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml` in pending + current
   - `TS`: `technology-selection/technology-selection-<IMPL_ID>.yaml` in pending + current
   - `MAC`: `models_and_contracts.yaml` in pending + current
   - `UIC`: `models_and_contracts/ui_contracts.yaml` (and any other spec file) in pending + current
   - `AC` / `AT`: all `functional_requirements.yaml` and `nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml` in pending + current
2. Collect all existing sequence numbers for that type.
3. Set `next_seq = max(existing sequences) + 1` and use that for every new item.
4. Never reuse a sequence number that exists anywhere, even if the short-title is different.

NFR and technology selection files:
- NFR and TS requirements live in per-implementation-id files under their type subfolder: `nfr-and-global-cr/nfr-and-global-cr-<IMPL_ID>.yaml` and `technology-selection/technology-selection-<IMPL_ID>.yaml`.
- No flat aggregate files exist at the stage root. Read and write the per-implementation file directly.

Environment variable naming:
- Specify exact env var names (e.g. `FAKEBANK_OMB_WEB_DATABASE_URL`, not "the DB env var").
- Module-specific vars use `<MODULE>_<VAR_NAME>` prefix in UPPERCASE (e.g. `PAYMENTS_STRIPE_KEY`, `AUTH_JWT_SECRET`).
- Global/shared vars (not module-specific) must use the app identifier prefix: `<APP_IDENTIFIER>_<VAR_NAME>`. Derive from `config.yaml → identity.app_identifier`: uppercase, replace `-` with `_`, append `_` (e.g. `fakebank-omb-web` → `FAKEBANK_OMB_WEB_DATABASE_URL`).
- Exception: well-known universal vars (`PORT`, `HOME`, `PATH`, `TZ`) may omit the app identifier prefix.
- Existing requirements are not retroactively renamed — the app identifier prefix applies to newly authored env vars only.

Environment variable documentation:
- When requirements introduce new env vars, create or update `<APP_ROOT>/aidev/docs/env-variable-instructions.md`.
- Each entry: name, module scope, description, format/type, sensitivity (secret/non-secret), default value, required/optional.
- Create the file and `aidev/docs/` directory if they do not exist.

## Contract References (`contract_refs`)

When authoring `contract_refs` on FR, NFR, or GLOBAL items:

- Always use `contract_type: models_and_contracts`. Never use `contract_type: ui_contracts`.
- Reference contracts by MAC ID using object form: `- id: MAC-XXXXXXX-short-title`.
- For MAC entries that wrap multi-item spec files (e.g., a `ui_contracts.yaml` with many UICs), add `child_specifications: all` on the `specific_ids` entry (default — unless specific children are needed).
- Use an explicit list `child_specifications: [UIC-XXXXXXX-..., ...]` only when the requirement targets specific children of the MAC.

Correct form:
```yaml
contract_refs:
- contract_type: models_and_contracts
  selection: specific_ids
  specific_ids:
  - id: MAC-0000001-some-api-contract
  - id: MAC-0000002-ui-contracts-wrapper
    child_specifications: all
```

Never use:
- `contract_type: ui_contracts`
- Bare string `specific_ids`: `- MAC-0000001-foo`
- `sub_mac_ids` (obsolete field name — use `child_specifications`)

## MAC Catalog `child_specifications`

When authoring or updating a MAC entry in `models_and_contracts.yaml` that wraps a multi-item spec file:
- Include `child_specifications` listing all child IDs defined in the referenced spec file.
- When new child items are added to the spec file, update the MAC catalog entry's `child_specifications` to match.
- `child_specifications: all` in a `contract_refs` entry means "all items listed in the MAC catalog entry's `child_specifications` field".
- Single-item spec files (e.g., a MAC that wraps exactly one API contract schema) do not require `child_specifications` on the catalog entry.

## Deletion (action: delete)

When a promoted requirement in `current` is no longer needed, author a deletion entry in `pending`:

1. Assign a **new ID** (next available sequence number for the type — never reuse the target's ID).
2. Set `action: delete`.
3. Set `replaces_id` to the ID of the requirement being removed from `current`.
4. Set `text: ''` (empty string, as required by schema).
5. Set `section` to the section of the original requirement, or `Removals`.
6. Do **not** carry over `acceptance_criteria`, `acceptance_tests`, or `contract_refs` from the original.
7. If the requirement to be deleted already has a pending `action: update` item targeting it, **replace that update item** with the delete entry instead — do not leave both an update and a delete targeting the same source ID.

Example:
```yaml
- id: FR-0000006-remove-credit-platform-placeholder
  action: delete
  replaces_id: FR-0000004-credit-platform-ui-placeholder
  section: Removals
  text: ''
```

When the user asks to "remove", "delete", or "clean up" requirements from current, always author `action: delete` items in pending rather than physically removing lines from existing files.
