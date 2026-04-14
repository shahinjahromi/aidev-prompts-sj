# RQ-01 Author
Inputs: TASK_DESCRIPTION, artifact type, pending/current files, local schemas.
Action: write/update pending artifacts only.
Rules: FR/NFR/GLOBAL drive code; MAC metadata only; UI contracts are screen-only.

Module handling:
- If the user specifies a module, set the `module` field on every authored item.
- If the user does not mention a module, omit the field.
- On updates (`action: update`), carry forward the existing `module` value unless the user explicitly changes it.
- Module reassignment is a valid update reason — set the new value and the diff/implementation pipeline detects the change.

## ID Uniqueness (mandatory before assigning any new ID)

Sequence numbers must be globally unique within each type across the entire blueprint (pending + current). Before writing any new item:

1. Scan the relevant files for the type being authored:
   - `FR`: `functional_requirements.yaml` in pending + current
   - `NFR` / `GLOBAL`: `nfr_and_global_cr.yaml` in pending + current
   - `TS`: `technology_selection.yaml` in pending + current
   - `MAC`: `models_and_contracts.yaml` in pending + current
   - `UIC`: `models_and_contracts/ui_contracts.yaml` (and any other spec file) in pending + current
   - `AC` / `AT`: all `functional_requirements.yaml` and `nfr_and_global_cr.yaml` in pending + current
2. Collect all existing sequence numbers for that type.
3. Set `next_seq = max(existing sequences) + 1` and use that for every new item.
4. Never reuse a sequence number that exists anywhere, even if the short-title is different.

Technology selection mirrors:
- The authoritative TS files are the stage-root files `01-pending-promotion/technology_selection.yaml` and `03-current/technology_selection.yaml`.
- Per-implementation mirrors under `01-pending-promotion/technology-selection/` and `03-current/technology-selection/` are derived outputs and must be refreshed after TS writes; do not treat mirror files as the source of truth for authoring.

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
