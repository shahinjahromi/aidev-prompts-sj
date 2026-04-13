# Requirements Management

> **Root:** All paths in this file are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../`
> Read `instructions.md` first. This file covers requirements authoring and the promote pipeline only.
> Blueprint-internal paths are fixed constants — see `instructions.md → Fixed Blueprint Paths`.
> Resolve app-specific values (`variables.*`) from `config.yaml` before executing any step.
> All writes go to **pending only** (`01-requirements/01-pending-promotion`). Never modify `03-current`. Never promote unless executing RQ-2.

---

## Steps at a Glance

| Step ID | Step Name | Action Type | Dependencies |
|---------|-----------|-------------|--------------|
| [RQ-1](#rq-1--author-requirement) | Author requirement | AI: write FR / NFR / MAC / UIC / TS to pending | Read context, identify contracts (if needed) |
| [RQ-2](#rq-2--promote) | Promote | Script: `ai-tooling.sh promote` | RQ-1 complete |
| [RQ-3](#rq-3--reconcile-optional) | Reconcile (optional) | Prompt: `01-requirements/prompts/03-backfill-technology-selections.md` | None |

---


## Steps

### RQ-1 — Author Requirement

**Instruction:** Create or update a pending requirement artifact. All writes go to `01-requirements/01-pending-promotion` only.

**Action (AI):** Apply the [Authoring Rules](#authoring-rules) and [Authoring Procedures](#authoring-procedures) below. Return valid YAML for the target file with strict schema adherence.

#### Dependency: Read Context

Before authoring, load current state from `config.yaml` and the pending control file:

1. Read `config.yaml` → resolve app-specific values:
   - `variables.timezone`
   - `variables.version_suffix_start`
2. Read `01-requirements/control.yaml` → note `current_version`, `next_version`, `iteration_id`.
3. Identify which artifact files already exist in `01-requirements/01-pending-promotion/`.

#### Dependency: Identify Contracts and Models (if requirement touches contracts)

Required when authoring FR, NFR, MAC, or UIC — skip for TS only:

1. Read `01-requirements/03-current/contracts_and_models.yaml`.
2. Read `01-requirements/01-pending-promotion/contracts_and_models.yaml` (if it exists).
3. Read relevant contract spec files in `contracts_and_models/` as needed.
4. Note MAC `id` values and current spec versions.

#### Design-First Flow (when authoring FRs or NFRs that touch contracts)

1. Identify all contracts and models that will be impacted.
2. Read current and pending `contracts_and_models.yaml` and relevant spec files.
3. Create or update contracts in pending **first**.
4. Then write FRs/NFRs that reference them, using `contract_refs`.

---

### RQ-2 — Promote

**Instruction:** Validate and promote all pending artifacts to `03-current`, advancing the version in `control.yaml`.

**Pre-checks:**
1. Verify pending directory (`01-requirements/01-pending-promotion/`) has content (non-empty).
2. Confirm the developer has reviewed the pending files before proceeding.

**Action (Script):** Resolve `TOOLING_CMD` from `{{VSCODE_USER_PROMPTS_FOLDER}}/aidev2-details/framework-ai-development-tooling/ai-tooling.sh`.
```
"$TOOLING_CMD" promote -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "<IMPLEMENTATION_ID>"
```
Verify exit code is 0. If non-zero, report the full error output and stop.

**After promote:**
Review:
- `01-requirements/01-pending-promotion/` — should be clean.
- `01-requirements/03-current/` — updated with promoted artifacts.
- `01-requirements/02-diff/` — diff files updated.

Report: how many requirements were promoted (by type) and the new version from `control.yaml`.

**CRITICAL — Iteration gate (developer action required):**
After promote completes, the developer MUST manually update the app manifest's `iteration_id` before running diff.
- Manifest path: `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`
- The `iteration_id` field controls which iterations are included in the next diff.
- Tooling NEVER auto-updates this field.
- Do NOT run diff (IM-01) until the developer confirms `iteration_id` has been updated.

---

### RQ-3 — Reconcile (Optional)

**Instruction:** Backfill technology selections already implemented in code but missing or stale in canonical TS artifacts and the app manifest. Use when onboarding an existing app or correcting legacy state. NOT a substitute for the normal pending → promote → diff → plan → execute flow.

**Action:** Execute step `github-config/aidev-09-backfill-tech-selections.prompt.md`.

**Phase 1 — Analyse code for undeclared technologies:**
1. Read the application codebase at `APP_ROOT` — package manifests (`package.json`, `go.mod`, `requirements.txt`, `pom.xml`, etc.), framework configs, Docker images, CI configs.
2. Read `01-requirements/03-current/technology-selection/technology-selection-<IMPLEMENTATION_ID>.yaml`.
3. Treat `01-requirements/03-current/technology-selection/technology-selection-<IMPLEMENTATION_ID>.yaml` as the authoritative TS file for this implementation.
4. Identify technologies or version changes present in code but missing from the TS file.
4. For each new technology found:
   - Add a new `TS-NNNNNN` entry directly to `01-requirements/03-current/technology-selection/technology-selection-<IMPLEMENTATION_ID>.yaml`.
   - Set `created_version` and `updated_version` to the current version from `01-requirements/control.yaml → current_version`.
5. Add each new entry to the app manifest `requirement_baseline` (path from `config.yaml → implementations.<IMPLEMENTATION_ID>.manifest_path`).

**Phase 2 — Sync backported requirements into diff directory:**
After writing to `03-current/`, run:
```
"$TOOLING_CMD" sync-diff -r "$REQ_PATH"
```
This adds only missing diff files — does NOT rebuild existing ones.

Diff file naming:

| Requirement type | Bucket directory | File name |
|---|---|---|
| `FR-NNNNNN` | `02-diff/functional/` | `FR-NNNNNN.yaml` |
| `NFR-NNNNNN` | `02-diff/nfr-and-global-cr/` | `NFR-NNNNNN.yaml` |
| `TS-NNNNNN` | `02-diff/technology-selection/` | `TS-NNNNNN.yaml` |

**Phase 3 — Handle replaced requirements:**
If any backfilled entry replaces an existing requirement (`replaces_id`):
1. Read the diff file for the replaced requirement.
2. In the replaced entry's current file, set `superseded_by: <NEW_ID>`.
3. In the new entry, set `replaces_id: <OLD_ID>`.

**After:** Verify the diff directory has a file for every requirement in current. Report: technologies backfilled, diff files synced, any replacements made.

---

## Authoring Rules

Blueprint-internal paths are fixed constants. Resolve app-specific values from `config.yaml`:

| Value | Source |
|-------|--------|
| Pending path | `01-requirements/01-pending-promotion` (fixed) |
| Schemas path | `.schemas` (fixed) |
| Current path | `01-requirements/03-current` (fixed) |
| Timezone | `config.yaml → variables.timezone` |

All files must conform to their JSON schema in `.schemas`.

---

### Artifact Types

| Type | ID Pattern | Schema File | Target File in Pending |
|------|-----------|-------------|------------------------|
| functional_requirements | FR-NNNNNN | `functional_requirements.json` | `functional_requirements.yaml` |
| nfr_and_global_cr | NFR-NNNNNN | `nfr_and_global_cr.json` | `nfr-and-global-cr/nfr-and-global-cr-<IMPLEMENTATION_ID>.yaml` |
| contracts_and_models | MAC-NNNNNN | `contracts/contracts_and_models.json` | `contracts_and_models.yaml` |
| ui_contracts | UIC-NNNNNN | `contracts/ui_contracts.json` | `contracts_and_models/<file>.yaml` + catalog entry in `contracts_and_models.yaml` |
| technology_selection | TS-NNNNNN | `technology_selection.json` | `technology-selection/technology-selection-<IMPLEMENTATION_ID>.yaml` |

### Requirement ID Patterns

| Type | Format | Example |
|------|--------|---------|
| Functional | FR-NNNNNN | FR-000001 |
| Functional versioned | FR-NNNNNN-vN | FR-000020-v2 |
| Non-functional | NFR-NNNNNN | NFR-000009 |
| Technology selection | TS-NNNNNN | TS-000007 |
| Contracts and models | MAC-NNNNNN | MAC-000001 |
| UI contract | UIC-NNNNNN | UIC-000003 |

IDs are 6-digit zero-padded. Numbers are never reused after deletion.

---

### Critical Authoring Rules

1. **What drives code.** Only FR and NFR cause code to be written. MAC, UI contracts, and TS are reference-only.
2. **Pending-only writes.** All artifact types (including `contracts_and_models.yaml` and spec files) MUST go to pending first. NEVER modify `03-current`. NEVER promote.
3. **MAC entries are metadata only.** Catalog pointers: `id`, `title`, `summary`, `spec_format`, `spec_path`. No behavior, acceptance criteria, or tests. `spec_path` is relative within `contracts_and_models/`. Versioned MAC ids require `replaces_id`.
4. **Contract specs vs. requirements.** Contract specs define the interface (paths, schemas, DDL, screen layout). FRs/NFRs define behavior (logic, sequencing, error handling). Create/update the spec first, then write the FR referencing it.
5. **Requirements must declare contract coverage.** If a requirement depends on contracts or models, it MUST declare them in `contract_refs`. Each entry names the `contract_type` and uses exactly one scope style:
   - `selection: all` — all contracts of that type apply.
   - `selection: specific_ids` + explicit `specific_ids` list.
6. **UI contracts are screen-only models.** Describe only what the user sees and does: screens, fields, formats, labels, actions, states, validation messages, navigation. MUST NOT include backend details.
7. **Include detailed design decisions.** Requirements MUST include explicit design decisions — such as chosen patterns, data-flow approaches, error-handling strategies, naming conventions, component structures, and algorithmic choices — rather than leaving them open to interpretation. Detailed design decisions reduce variability in generative AI output and produce more consistent, deterministic implementations. When multiple valid approaches exist, state the selected approach and the rationale. Ambiguous or under-specified requirements lead to non-reproducible code generation.
8. **Include concrete test data.** Acceptance tests MUST include concrete input data and expected output data where the result is deterministic. For API tests: HTTP method, path, example request body, expected status code, expected response shape/key fields. For form/UI tests: field values and expected outcome. For non-deterministic values (timestamps, generated IDs), describe the expected type/shape rather than a literal. Concrete test data enables the implementation agent to write precise assertions without guessing.

---

### Authoring Procedures

**Add new item:**
- IDs: 6-digit zero-padded. Increment from highest existing ID.
- Follow schema exactly.
- FR and NFR: always include structured `acceptance_criteria` with `title`, `criteria` array, and `acceptance_tests` inline.
- UI contracts: create/update the definition file under `contracts_and_models/`, then add/update the MAC catalog entry.

**Add technology selection:**
- Required: `id` (TS-NNNNNN), `category`, `capability`, `name`, `version`, `description`.
- Optional: `implementation_ids` (default `["*"]`), `decision_ref`, `constraints`.

**Update existing item:**
- Locate by id in pending. Edit in place — do not duplicate IDs. Validate.

**Change a promoted item:**
1. If already in pending: edit in place.
2. If only in current: create a new versioned entry in pending with `-v<N>` suffix (start at `variables.version_suffix_start`), set `replaces_id` → original id.

**Remove a promoted item:**
Create a new versioned entry in pending with `-v<N>` suffix, set `replaces_id` → original id, and leave `text` empty (empty string `""`). All other fields (`section`, `contract_refs`, `acceptance_criteria`, etc.) may be omitted or left empty. On promote, both entries remain in `03-current/` — the original is kept with `superseded_by` set, and the empty-text replacement entry sits alongside it. The original is **never deleted** from the current requirements list; its presence preserves the history of what was implemented and tells the diff tooling exactly what to remove. The diff will place it in the `removed` bucket, and plan/execute will handle code deletion. To find the full prior state quickly, look up the per-requirement diff file by name: `02-diff/<bucket>/<REQUIREMENT_ID>.yaml` (see [Diff File Naming](#diff-file-naming)).

**Preservation:**
- Do not modify unrelated items.
- Maintain `schema_version`, `type`, `generated_at` headers.

---

## Requirements Directory Convention

All paths are relative to `../` (blueprint root). These are fixed constants — do not put them in `config.yaml`:

| Fixed path | Purpose |
|------------|---------|
| `01-requirements/01-pending-promotion/` | Pending artifacts awaiting promotion |
| `01-requirements/01-pending-promotion/contracts_and_models/` | Pending contract spec files |
| `01-requirements/03-current/` | Promoted, canonical requirements (by type) |
| `01-requirements/03-current/contracts_and_models/` | Promoted contract spec files |
| `01-requirements/03-current/merged/merged_requirements.yaml` | Merged view of all current requirements |
| `01-requirements/02-diff/` | Per-requirement diff history files (one file per requirement, see [Diff File Naming](#diff-file-naming)) |
| `.schemas/` | JSON schemas for requirement validation |

### Diff File Naming

Each requirement has exactly one diff history file under `02-diff/`, named by its requirement ID inside a type-specific bucket directory. This enables direct lookup by filename — no need to scan across all requirement files.

| Requirement type | Bucket directory | File name pattern | Example |
|---|---|---|---|
| `FR-NNNNNN` | `02-diff/functional/` | `<ID>.yaml` | `02-diff/functional/FR-000004.yaml` |
| `NFR-NNNNNN` | `02-diff/nfr-and-global-cr/` | `<ID>.yaml` | `02-diff/nfr-and-global-cr/NFR-000001.yaml` |
| `TS-*` | `02-diff/technology-selection/` | `<ID>.yaml` | `02-diff/technology-selection/TS-frontend-framework.yaml` |
| `MAC-NNNNNN` | `02-diff/contracts/` | `<ID>.yaml` | `02-diff/contracts/MAC-000001.yaml` |
| `UIC-NNNNNN` | `02-diff/ui_contracts/` | `<ID>.yaml` | `02-diff/ui_contracts/UIC-000001.yaml` |

Each diff file contains a `diffs` array with chronological entries recording every `create`, `update`, or `remove` operation on that requirement, including the full requirement snapshot at each step. When a requirement is superseded (removal or replacement), the diff file for the **original** ID is the authoritative record of what was previously implemented.

---

## Requirements Versioning

**Source of truth:** `01-requirements/control.yaml`

| Field | Meaning |
|-------|---------|
| `current_version` | Version of currently promoted requirements |
| `next_version` | Version assigned on next promote |
| `iteration_id` | Iteration counter (integer) |

The promote command reads and advances these values. App manifest fields `requirements_version_target` and `requirements_version_implemented` are downstream consumers — they NEVER drive the requirements version.

---

## Contract Spec Versioning

**Supported spec formats:** `openapi_yaml`, `graphql_sdl_yaml`, `logical_database_schema`, `physical_database_schema`, `domain_model`.

**Rules:**
- Never edit promoted contract specs in place. Edit/create one pending version under pending `contracts_and_models/`, exactly one version ahead of current.
- **Default version bump:** increment PATCH by default (e.g. v1.3.0 → v1.3.1). Only bump MINOR when explicitly instructed. MAJOR bumps require explicit instruction.
- **One pending version rule:** at most one pending version per contract spec per promotion cycle. If it exists, keep editing it; do not create a second one.
- **Version semantics:** MAJOR = breaking (removed endpoints, renamed fields, changed types); MINOR = additive (new endpoints, new optional fields); PATCH = fixes (corrected descriptions, typo fixes).
- **Naming example:** `rest_openapi.yaml` → `rest_openapi-v1.1.0.yaml`

After creating a new versioned spec file, update the corresponding MAC entry `spec_path` to point to it. Keep older files for history.

**MAC entry policy:**
- Each MAC entry MUST include `id` — the stable identifier for the contract. The MAC `id` does not change across versions (versioned updates use a new MAC entry with `-vN` suffix and `replaces_id`).
- `spec_path` MUST be a relative path within `contracts_and_models/` (e.g. `contracts_and_models/rest_openapi-v1.1.0.yaml`).
- Versioned/updated MAC entries MUST include `replaces_id` (e.g. `id: MAC-000001-v2` requires `replaces_id: MAC-000001`).

**Contract spec promotion flow:**
1. Edit the existing pending spec in place, or create a new versioned file one version ahead of current.
2. Add or update the MAC entry in `01-pending-promotion/contracts_and_models.yaml` with `spec_path` pointing to the pending file. If the MAC entry already exists in pending, update its summary — do not create a second entry.
3. Promote copies the MAC entry to `03-current`. Older spec files are retained for history.

---

## Retired Artifact Types

No longer having standalone files: decisions, glossary, business_context, change_log, requirements (aggregate), standalone acceptance_criteria, standalone acceptance_tests, standalone ui_contracts.yaml. AC and AT are embedded inline in FR/NFR items. Requirement removals are expressed via `replaces_id` with empty `text` (see [Authoring Procedures](#authoring-procedures)).
