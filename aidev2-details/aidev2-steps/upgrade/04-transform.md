## Step 4 - Transform In Place

Normalize technology-selection mirror layout:
- Keep canonical stage files at `01-requirements/01-pending-promotion/technology_selection.yaml` and `01-requirements/03-current/technology_selection.yaml`.
- Ensure stage-local mirror folders exist at `01-requirements/01-pending-promotion/technology_selection/` and `01-requirements/03-current/technology_selection/`.
- Move any misplaced root-level mirror files into the matching stage-local `technology_selection/` folder.
- Refresh per-implementation mirror filenames as `technology_selections_<IMPLEMENTATION_ID>.yaml` from the authoritative stage-root `technology_selection.yaml` file for that stage.

Perform in-place naming upgrades for pending/current requirements and contracts:
- `contracts_and_models` -> `models_and_contracts`
- `data_and_api_contracts` -> `models_and_contracts`
- `DAC-` -> `MAC-`
- `dac_contract_logical_id` -> `mac_contract_logical_id`
- `non_functional_requirements.yaml` -> `nfr_and_global_cr.yaml` (rename files in `01-pending-promotion/`, `03-current/`, `02-implementation-mapping/`; update `type: non_functional_requirements` -> `type: nfr_and_global_cr` inside the file)
- `02-diff/non_functional/` -> `02-diff/nfr_and_global_cr/` (rename diff bucket directory if present)

Perform in-place ID format normalization:
- Normalize IDs to `<TYPE>-<7-digit-sequence>-<short-title>`.
- Apply to requirement/contract artifacts and references, including `FR`, `NFR`, `GLOBAL`, `TS`, `MAC`, `UIC`, `AC`, `AT`, and `CONTRACT` IDs.
- Preserve version suffixes like `-vN`, placing them after the short title.
- If an ID currently has sequence at the end (example: `MAC-MARQETA-CREDIT-PLATFORM-0000001`), rewrite to `MAC-0000001-marqueta-credit-platform`.
- Generate short-title as lowercase kebab-case from existing title/semantic label when available; otherwise derive from existing slug segments.
- Update all impacted references when IDs are changed (e.g., `replaces_id`, `contract_refs`, `specific_ids`, related links).

**Duplicate sequence renumbering** (apply after format normalization, on the post-normalization ID set):
- For each type prefix (`FR`, `NFR`, `TS`, `MAC`, `UIC`, `AC`, `AT`), collect all sequence numbers across pending + current files.
- If two or more items of the same type share the same sequence number, keep the lowest-positioned item (earliest position in `03-current`, then `01-pending-promotion`) at its current number; renumber all other conflicting items to new unused sequences starting from `max(existing for type) + 1`.
- Build a complete old-ID → new-ID map for all renumbered items.
- Apply the map to: all requirement files in pending + current + merged, diff bucket files (also rename diff filenames that embed old IDs), manifest baseline entries, and all cross-reference fields.
- Do not declare migration complete if duplicate sequences remain.

**Contract reference consolidation**:
- In all `contract_refs` across pending + current requirement files:
  - Replace `contract_type: ui_contracts` entries with `contract_type: models_and_contracts` referencing the parent MAC ID with `child_specifications: all` (or explicit list if the original entry had `specific_ids`).
  - Convert bare-string items in `specific_ids` to object form: `- id: MAC-XXXXXXX-short-title`.
  - Rename `sub_mac_ids` to `child_specifications`.
- When multiple separate `contract_refs` entries (e.g., one for `ui_contracts` and one for `models_and_contracts`) reference the same parent MAC, merge them into a single `contract_type: models_and_contracts` entry with `child_specifications`.

**MAC catalog `child_specifications`**:
- For each MAC entry in `models_and_contracts.yaml` (pending + current) whose `spec_file` references a file that defines multiple items (e.g., `ui_contracts.yaml` with many UIC entries):
  - Add or update `child_specifications` on the MAC catalog entry, listing all child IDs defined in the spec file.
  - Keep `child_specifications` synchronized with the actual items in the spec file.
- Single-item spec files do not require `child_specifications` on the catalog entry.

Reference-update checklist (apply when present):
- `requirement_id`, `replaces_id`, `related_requirement_ids`, `related_uic_ids`
- `contract_refs[].specific_ids`, `implements_contract_ids`, `consumes_upstream_contract_ids`
- `contract_id` and contract logical-ID fields
- manifest/baseline requirement references and merged-view embedded IDs

Maintain an old->new ID mapping during transformation and use it for all reference rewrites.

Apply transforms to:
- requirement files under `01-requirements/01-pending-promotion` and `01-requirements/03-current`
- contract catalog files and contract spec references
- relevant UI contract references that point to renamed contract IDs/paths

Preserve requirement meaning and app-specific content.
Do not delete implementation/test/history artifacts.

Manifest schema upgrade:
- Locate the app manifest from `BLUEPRINT_ROOT/.instructions/config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path` (path relative to BLUEPRINT_ROOT).
- For each entry in `requirement_baseline` that is missing `e2e_test_status`, add `e2e_test_status: NOT_TESTED`.
- Do NOT add `implementation_initial_date` or `implementation_last_date` — leave them absent; they are filled in by IM-04 Execute when code is implemented. Only add them if they are already present and need normalization.
- Timezone for any existing date fields comes from `config.yaml → variables.timezone`.
