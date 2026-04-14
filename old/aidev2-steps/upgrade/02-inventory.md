## Step 2 - Baseline Inventory

Inspect and summarize current state before edits:
- pending/current requirement files and naming conventions
- contract catalog filenames and contract spec folder names
- UI contract references tied to contract ids and paths
- legacy identifiers and fields (`DAC-*`, `dac_contract_logical_id`, old type names)
- ID format compliance and outliers for `FR`, `NFR`, `TS`, `MAC`, `UIC`, `AC`, `AT`, and `CONTRACT` IDs
- specifically flag IDs that are not `<TYPE>-<7-digit-sequence>-<short-title>`
- obsolete v1 prompt/instruction files superseded by user-level aidev2 prompts:
  - `02-implementation/00-prompts/` (v1 implementation step prompts)
  - `github-config/aidev-*.prompt.md` and `aidev-framework.instructions.md` (v1 framework prompts/instructions)
  - `instructions/` directory (v1 documentation)
  Note: `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are NOT obsolete — aidev2 reads both.
- app manifest status — locate via `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`:
  - check whether each `requirement_baseline` entry has `e2e_test_status`, `implementation_initial_date`, `implementation_last_date`
  - flag entries missing these fields as requiring upgrade

Do not write files in this step.
