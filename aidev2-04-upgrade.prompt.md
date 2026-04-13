---
name: "aidev2-upgrade"
description: "Upgrade an existing app blueprint to current folder and requirement-id conventions while preserving app-specific configuration, requirements content, test results, implementation history, and other artifacts."
argument-hint: "Optional: blueprint root path (auto-detect from active file if omitted)."
agent: "agent"
---

## Role

You are a safe migration assistant for AI-dev blueprints.
Upgrade structure and naming conventions without losing application-specific content.

Scope expectation:
- transform existing pending/current requirement artifacts to current naming conventions in place
- include contracts catalogs, contract spec folders, and UI contract references where present
- preserve semantic requirement content while normalizing identifiers and field names
- enforce ID formatting for requirement/contract artifacts as `<TYPE>-<7-digit-sequence>-<short-title>`

## Safety Guarantees

Do not delete or reset application-specific artifacts, including:
- `.instructions/config.yaml` values and implementation-specific settings
- requirement content in `01-requirements/**`
- implementation artifacts in `02-implementation/01-implementations/**`
- test outputs in `03-test-results/**`
- update history, notes, and other existing project documents

**MANDATORY** — Never run destructive git commands. No exceptions.
**MANDATORY** — Never remove files outside the target blueprint root. No exceptions.
**MANDATORY** — Never delete obsolete v1 prompt/instruction files — report them to the user for manual removal (see Phase 6).

## Phase 1 - Detect and Validate Blueprint Root

Detect `BLUEPRINT_ROOT` from active file by walking up to the first folder containing:
- `01-requirements`
- `02-implementation`
- `03-test-results`

If not found, ask user for absolute blueprint path.

## Phase 2 - Baseline Inventory (Read-only)

Run each sub-phase in order. Report results per sub-phase. If a sub-phase finds zero issues, report "clean" and proceed immediately to the next.

### 2a — File structure and naming conventions

Inspect:
- Existing requirement type files in pending/current
- Technology-selection mirror folders and files under pending/current; flag any misplaced root-level technology-selection folders
- Contract catalog filename and contract-spec folder names
- Presence of old/new naming conventions:
  - `contracts_and_models` vs `models_and_contracts`
  - `data_and_api_contracts` vs `models_and_contracts`
  - `DAC-` vs `MAC-`
  - `dac_contract_logical_id` vs `mac_contract_logical_id`

Early exit: if all files already use `models_and_contracts` / `MAC-` / dash-named folders, report "naming: clean" and skip to 2b.

### 2b — ID format and uniqueness

Inspect:
- ID format compliance for: `FR-*`, `NFR-*`, `TS-*`, `MAC-*`, `UIC-*`, `AC-*`, `AT-*`, `CONTRACT-*`
- **ID uniqueness violations**: for each type prefix, collect all sequence numbers across pending + current; flag any sequence number used by more than one item (duplicates must be renumbered in Phase 4)

Early exit: if all IDs match `<TYPE>-<7-digit>-<short-title>` and no duplicates exist, report "IDs: clean" and skip to 2c.

### 2c — Contract reference structure

Scan `contract_refs` in all requirement files for:
- `contract_type: ui_contracts` — obsolete; must become `contract_type: models_and_contracts` with MAC ID and `child_specifications`
- bare strings in `specific_ids` (e.g. `- MAC-0000001-foo`) — must be object form `- id: MAC-0000001-foo`
- `sub_mac_ids` field — obsolete; must be renamed to `child_specifications`
- MAC entries in `models_and_contracts.yaml` wrapping multi-item spec files but missing `child_specifications`

Early exit: if no `contract_refs` exist in any requirement file, report "contract_refs: not present" and skip to 2d.

### 2d — Manifest and v1 artifact compliance

Inspect:
- App manifest: locate via `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`; **flag if `manifest_path` still points to `manifests/requirements-manifest.yaml`** — migration target is `.aidev/requirements/requirements-state.yaml`; check whether each `requirement_baseline` entry has `e2e_test_status`, `implementation_initial_date`, `implementation_last_date`
- Obsolete v1 prompt/instruction artifacts (superseded by user-level aidev2 prompts):
  - `02-implementation/00-prompts/` — v1 implementation step prompts, replaced by `aidev2-steps/implement/`
  - `github-config/aidev-*.prompt.md` — v1 framework prompts
  - `github-config/aidev-framework.instructions.md` — v1 framework instructions
  - `instructions/` — v1 documentation folder
  Note: `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are NOT obsolete — aidev2 reads both.
- Prompt/instruction references under: `github-config/`, `02-implementation/00-prompts/`, `.instructions/`, `instructions/`

## Phase 3 - Write Targets

Before writing, show a concise migration plan and proceed without asking for confirmation.

Must include planned write targets and explicitly state that app-specific content will be preserved.

## Phase 4 - Upgrade Actions

Apply only needed updates, in place:

0. Technology-selection and NFR folder normalization:
- There are NO flat aggregate files (`technology_selection.yaml`, `nfr_and_global_cr.yaml`) — only per-implementation files inside type-named subfolders.
- Ensure subfolders exist: `01-requirements/01-pending-promotion/technology-selection/`, `01-requirements/01-pending-promotion/nfr-and-global-cr/`, `01-requirements/03-current/technology-selection/`, `01-requirements/03-current/nfr-and-global-cr/`.
- Per-implementation file naming: `technology-selection-<IMPLEMENTATION_ID>.yaml` and `nfr-and-global-cr-<IMPLEMENTATION_ID>.yaml` (all dashes, no underscores).
- Rename any existing underscore-named files (e.g. `technology_selection_<ID>.yaml` → `technology-selection-<ID>.yaml`; `nfr_and_global_cr_<ID>.yaml` → `nfr-and-global-cr-<ID>.yaml`).
- If a flat aggregate file is found, migrate its content into the per-implementation file for this implementation ID and remove the flat file.

1. Naming normalization:
- `contracts_and_models` -> `models_and_contracts`
- `data_and_api_contracts` -> `models_and_contracts`
- `DAC-` -> `MAC-`
- standalone `DAC` acronym -> `MAC` where it refers to requirement/contract type
- `dac_contract_logical_id` -> `mac_contract_logical_id`

2. ID format normalization:
- convert IDs to the pattern `<TYPE>-<7-digit-sequence>-<short-title>`
- examples: `FR-0000001-credit-platform-ui-placeholder`, `FR-0000001-credit-platform-ui-placeholder-v2`, `NFR-0000002-code-quality`, `TS-0000007-frontend-framework`, `MAC-0000001-marqueta-credit-platform`, `UIC-0000001-authenticated-app-shell`, `AC-0000004-placeholder-ui-render`, `AT-0000004-verify-placeholder-navigation`, `CONTRACT-0000001-marqueta-credit-platform`
- short-title format: lowercase kebab-case, concise semantic slug, no spaces/underscores
- preserve meaning while normalizing order and numeric width; move numeric sequence immediately after type code
- update cross-references when an ID changes (e.g., `replaces_id`, `specific_ids`, `contract_refs`, related requirement/UI links)

3. **Duplicate sequence renumbering** (apply after step 2, using the post-normalization ID set):
- For each type prefix (`FR`, `NFR`, `TS`, `MAC`, `UIC`, `AC`, `AT`), collect all sequence numbers across pending + current files.
- If the same sequence number is used by more than one item of the same type, all items except the lowest-positioned one (earliest by position in current, then pending) must be renumbered to unused sequences starting from `max(existing for type) + 1`.
- Build a complete old-ID → new-ID map for all renumbered items.
- Apply the renumber map everywhere: all requirement files (pending + current + merged + diff), manifest baseline entries, and cross-reference fields (`replaces_id`, `related_requirement_ids`, `related_uic_ids`, `contract_refs`, etc.).
- Also rename any `02-diff/` files whose filenames embed an old ID.
- Do not declare migration complete if any duplicate sequence numbers remain in the ID space.

4. **Contract reference consolidation**:
- Replace `contract_type: ui_contracts` entries in all `contract_refs` with `contract_type: models_and_contracts` entries referencing the parent MAC ID.
- Set `child_specifications: all` on the MAC `specific_ids` entry when the requirement uses all children (default).
- Set `child_specifications: [UIC-XXXXXXX-..., ...]` when the requirement targets specific children.
- Replace bare-string items in `specific_ids` with object form: `- id: MAC-XXXXXXX-short-title`.
- Rename `sub_mac_ids` to `child_specifications` wherever present.

5. **MAC catalog `child_specifications`**:
- For each MAC entry in `models_and_contracts.yaml` (pending + current) that references a spec file containing multiple items (e.g., `ui_contracts.yaml` with multiple UIC entries), add or update `child_specifications` listing all child IDs defined in that spec file.
- Keep `child_specifications` on MAC catalog entries in sync with the actual items in the referenced spec file.
- Single-item spec files do not require `child_specifications` on the catalog entry.

6. **Requirements state file migration**:
- If the app repo manifest currently lives at `manifests/requirements-manifest.yaml`:
  1. Create `APP_ROOT/.aidev/requirements/` if absent.
  2. Copy the file to `APP_ROOT/.aidev/requirements/requirements-state.yaml`.
  3. Update `manifest_path` in `BLUEPRINT_ROOT/.instructions/config.yaml` to the new location (e.g. `../<APP_REPO_DIR>/.aidev/requirements/requirements-state.yaml`).
  4. Delete `APP_ROOT/manifests/requirements-manifest.yaml` after confirming the copy is intact.
  5. Remove `APP_ROOT/manifests/` if it is now empty.
  6. Log: "Migrated app manifest → `.aidev/requirements/requirements-state.yaml`"

Reference integrity requirements (mandatory):
- build an old->new ID mapping for every rewritten ID and apply it everywhere in scope
- update reference fields including (as applicable): `requirement_id`, `replaces_id`, `related_requirement_ids`, `related_uic_ids`, `contract_refs`, `specific_ids`, `implements_contract_ids`, `consumes_upstream_contract_ids`, `contract_id`, and manifest/baseline references
- update any string references in merged/current requirement views that embed rewritten IDs
- do not complete migration if any stale old IDs remain in scoped files

## Phase 5 - Verify

After edits:
- verify no stale references remain for old naming patterns (unless intentionally retained for backward-compat comments)
- verify key expected files/folders exist under new naming
- verify technology-selection mirror files exist under `01-pending-promotion/technology-selection/` and `03-current/technology-selection/` as applicable, and that no active mirror file remains under a misplaced root-level `technology/` folder
- verify IDs are normalized to `<TYPE>-<7-digit-sequence>-<short-title>` where applicable, with references updated consistently
- verify no dangling references exist (every rewritten ID must resolve to an existing target definition)
- **verify ID uniqueness**: for each type prefix, confirm no two items in pending + current share the same sequence number
- **verify contract_refs structure**: confirm no `contract_type: ui_contracts` remains; confirm all `specific_ids` entries use object form; confirm no `sub_mac_ids` remains
- **verify MAC catalog `child_specifications`**: confirm that MAC entries wrapping multi-item spec files have a `child_specifications` list
- **verify manifest location**: confirm app manifest exists at `.aidev/requirements/requirements-state.yaml` in the app repo; confirm `manifests/requirements-manifest.yaml` is absent; confirm `manifest_path` in `.instructions/config.yaml` references the new path
- if unresolved references remain, stop and report blockers instead of declaring success
- report changed files and a migration summary

## Phase 6 - Notify Obsolete v1 Artifacts

After verification, scan for v1 prompt/instruction artifacts that are superseded by user-level aidev2 prompts.
Do NOT delete these files. Instead, list them in the migration report and tell the user they can safely remove them.

Obsolete paths to check:
- `BLUEPRINT_ROOT/02-implementation/00-prompts/` — entire directory (replaced by user-level `aidev2-steps/implement/`)
- `BLUEPRINT_ROOT/github-config/aidev-*.prompt.md` — v1 prompt files (replaced by `.github/prompts/aidev2-*.prompt.md`)
- `BLUEPRINT_ROOT/github-config/aidev-framework.instructions.md` — v1 framework instructions
- `BLUEPRINT_ROOT/instructions/` — v1 documentation folder
Note: `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are NOT obsolete — aidev2 reads both.

Only report paths that actually exist. Group them under a clear "Obsolete v1 files — safe to remove" heading.
Also report the manifest upgrade summary: whether `e2e_test_status` was added to any entries, and remind user that date fields are set during IM-04 Execute.

## Phase 7 - Optional Follow-up

If the blueprint has tooling wrappers, suggest (do not force) a dry-run diff command and/or syntax checks after migration.
