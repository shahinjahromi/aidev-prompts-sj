## Step 4 - Transform In Place

Perform in-place naming upgrades for pending/current requirements and contracts:
- `contracts_and_models` -> `models_and_contracts`
- `data_and_api_contracts` -> `models_and_contracts`
- `DAC-` -> `MAC-`
- `dac_contract_logical_id` -> `mac_contract_logical_id`

Perform in-place ID format normalization:
- Normalize IDs to `<TYPE>-<7-digit-sequence>-<short-title>`.
- Apply to requirement/contract artifacts and references, including `FR`, `NFR`, `TS`, `MAC`, `UIC`, `AC`, `AT`, and `CONTRACT` IDs.
- Preserve version suffixes like `-vN`, placing them after the short title.
- If an ID currently has sequence at the end (example: `MAC-MARQETA-CREDIT-PLATFORM-0000001`), rewrite to `MAC-0000001-marqueta-credit-platform`.
- Generate short-title as lowercase kebab-case from existing title/semantic label when available; otherwise derive from existing slug segments.
- Update all impacted references when IDs are changed (e.g., `replaces_id`, `contract_refs`, `specific_ids`, related links).

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
