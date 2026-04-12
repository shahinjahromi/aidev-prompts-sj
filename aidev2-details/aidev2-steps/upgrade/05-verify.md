## Step 5 - Verify

Verify:
- old naming tokens are removed or intentionally retained only for compatibility notes
- expected new files/folders exist and are referenced correctly
- stage-local technology-selection mirror folders exist under pending/current as applicable, mirror files use `technology_selections_<IMPLEMENTATION_ID>.yaml`, and no active mirror file remains under a misplaced root-level `technology/` folder
- pending/current requirement artifacts remain intact after transform
- UI contract references resolve correctly after rename operations
- all applicable IDs use `<TYPE>-<7-digit-sequence>-<short-title>` format with valid references after normalization
- **ID uniqueness**: for each type prefix (`FR`, `NFR`, `TS`, `MAC`, `UIC`, `AC`, `AT`), confirm no two items across pending + current share the same sequence number
- **Contract reference structure**: confirm all of the following are absent from all requirement files:
  - `contract_type: ui_contracts`
  - bare-string items in `specific_ids` (must be object form `- id: ...`)
  - `sub_mac_ids` field (must be `child_specifications`)
- **MAC catalog `child_specifications`**: confirm MAC entries in `models_and_contracts.yaml` that reference multi-item spec files have a `child_specifications` list

Reference integrity validation:
- confirm every rewritten ID target exists exactly once in scope
- confirm no reference fields still point to pre-normalized IDs
- confirm no unresolved/dangling IDs remain in requirement, contract, UI, or manifest references
- if any dangling reference is found, mark verification failed and report exact file/field

Obsolete v1 artifact detection:
- scan for v1 prompt/instruction files that are superseded by user-level aidev2 prompts
- check paths: `02-implementation/00-prompts/`, `github-config/aidev-*.prompt.md`, `github-config/aidev-framework.instructions.md`, `instructions/`
- `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are NOT obsolete — do not flag them
- record which obsolete paths exist for the report step
- do NOT delete any of these files

Manifest verification:
- confirm every `requirement_baseline` entry in the manifest has `e2e_test_status` set to one of `NOT_TESTED`, `PASSED`, or `FAILED`
- confirm all `requirement_id` values in the manifest match normalized IDs in scope
- validate overall manifest shape against the local schema at `/home/parallels/.config/Code/User/prompts/aidev2-schemas/requirements_manifest.json`
