## Step 2 - Baseline Inventory

Inspect and summarize current state before edits:
- pending/current requirement files and naming conventions
- technology-selection stage-local mirror folders/files under pending/current and any misplaced root-level technology-selection mirror folders/files
- contract catalog filenames and contract spec folder names
- UI contract references tied to contract ids and paths
- legacy identifiers and fields (`DAC-*`, `dac_contract_logical_id`, old type names)
- ID format compliance and outliers for `FR`, `NFR`, `GLOBAL`, `TS`, `MAC`, `UIC`, `AC`, `AT`, and `CONTRACT` IDs
- specifically flag IDs that are not `<TYPE>-<7-digit-sequence>-<short-title>`
- **ID uniqueness violations**: for each type prefix, collect all sequence numbers across pending + current; flag any sequence number that appears on more than one item of the same type — these require renumbering in Step 4
- **Contract reference structure issues** (flag all of these for Step 4 to fix):
  - `contract_type: ui_contracts` in any `contract_refs` — obsolete; must use `contract_type: models_and_contracts` with parent MAC ID and `child_specifications`
  - bare strings in `specific_ids` (e.g. `- MAC-0000001-foo`) instead of object form (`- id: MAC-0000001-foo`)
  - `sub_mac_ids` field — obsolete name; must be `child_specifications`
  - MAC entries in `models_and_contracts.yaml` that wrap multi-item spec files but are missing `child_specifications` on the catalog entry
- obsolete v1 prompt/instruction files superseded by user-level aidev2 prompts:
  - `02-implementation/00-prompts/` (v1 implementation step prompts)
  - `github-config/aidev-*.prompt.md` and `aidev-framework.instructions.md` (v1 framework prompts/instructions)
  - `instructions/` directory (v1 documentation)
  Note: `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are NOT obsolete — aidev2 reads both.
- app manifest status — locate via `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`:
  - **flag if `manifest_path` still points to `manifests/requirements-manifest.yaml`** — this path is obsolete; migration target is `.aidev/requirements/requirements-state.yaml`
  - **flag if the app repo contains `manifests/requirements-manifest.yaml`** — this file must be moved to `.aidev/requirements/requirements-state.yaml`
  - check whether each `requirement_baseline` entry has `e2e_test_status`, `implementation_initial_date`, `implementation_last_date`
  - flag entries missing these fields as requiring upgrade

Do not write files in this step.
