# AI Development Tooling

Reusable tooling for requirement-driven AI code generation.

## Copilot rollout guide

- Developer enablement and rollout training: [COPILOT-ROLLOUT-TRAINING.md](COPILOT-ROLLOUT-TRAINING.md)

## Tooling manifest

- Keep `tooling-manifest.yaml` updated whenever tooling/practice changes are requested.
- Required fields:
  - `current_version`
  - `implemented_version`

## Use action script (preferred)

Use `ai-tooling.sh` instead of calling Python scripts directly.

Detailed per-step checklist is in `readme-command-sequence.txt` (`promote`, `delta`, `plan`, `apply`), including which files to review before/after each command.
Update merged requirements from diffs: `ai-tooling.sh merge -r <requirements-path> ...` (or `update-merged` / `refresh-merged`) whenever diff artifacts change.

Examples:
- `./ai-tooling.sh bootstrap -r <requirements-path> -a <app-path>`
- `./ai-tooling.sh merge -r <requirements-path> --all-implementations`
- `./ai-tooling.sh refresh-merged -r <requirements-path> --all-implementations`
- `./ai-tooling.sh delta -r <requirements-path> --implementation-id <IMPL_ID>`
- `./ai-tooling.sh plan -r <requirements-path> --implementation-id <IMPL_ID>`
- `./ai-tooling.sh apply -r <requirements-path> --implementation-id <IMPL_ID>`
- `./ai-tooling.sh update-merged -r <requirements-path> --all-implementations`
- `./ai-tooling.sh diff -r <requirements-path> --implementation-id <IMPL_ID>`
- `./ai-tooling.sh promote -r <requirements-path> --implementation-id <IMPL_ID>`
- `./ai-tooling.sh all -r <requirements-path> --all-implementations`

## Required identifiers

- `requirement_set_id` must match between app manifest and requirements.
- `app_identifier` must be defined once in requirements manifest `01-requirements/manifest.yaml` and must match app manifest.
- Keep implementation runtime state in `02-implementation-state/01-implementations/<implementation_id>/`.
- Terminal tooling commands fail when app and requirements `app_identifier` do not match.
- App manifest must define:
  - `implementation_id`
  - `app_identifier`
  - `iteration_id` (integer, for example `1`)
  - `requirements_version_target`
  - `requirements_version_implemented`
  - `requirement_baseline` (versioned implemented requirement entries)
- Requirement artifacts should not duplicate `app_identifier`; keep it only in manifest files.
- Implementation-specific state belongs only under `02-implementation-state/`.

## App requirements manifest file

The file `$APP/.aidev/requirements/requirements-state.yaml`
is the app-side control and traceability manifest for requirement implementation state.

What this file represents:

- Declares app identity and targeting (`requirement_set_id`, `app_identifier`, `implementation_id`).
- Tracks rollout state (`iteration_id`, `requirements_version_target`, `requirements_version_implemented`).
- Tracks completion (`requirement_baseline` with `requirement_id` + `pinned_version`).
- Optionally stores release metadata and requirement baseline pin snapshots.

How it is generated and maintained:

- Initial creation is done during bootstrap workflow (directly or via project setup scripts).
- Tooling commands read this file on every run to validate app/requirements compatibility before proceeding.
- During implementation, engineers/automation update:
  - `requirements_version_target` when planning a rollout.
  - `requirements_version_implemented` only after implementation is complete.
  - `requirement_baseline` entries as requirements are delivered.
- If identifiers mismatch between app manifest and requirements manifest, tooling fails fast by design.

## End-to-end workflow (add/update -> implement -> promote)

Use this sequence for each iteration.

### 0) Set base paths

```bash
REQ=<path-to-blueprint>/01-requirements
APP=<path-to-app-repo>
IMPL=<IMPLEMENTATION_ID>
TOOL=<path-to>/ai-development-tooling/ai-tooling.sh
```

### 1) Add or update requirements in pending-promotion staging

The control file is:
- `$REQ/control.yaml`

For staging updates, set:
- `current_version` (already implemented baseline)
- `next_version` (target version being prepared)
- `iteration_id` (integer)
- `changes` (add/update/remove entries used by structured diff)

Example `changes` snippet:

```yaml
changes:
  - op: add
    requirement:
      requirement_id: FR-200
      title: "Support scheduled transfer cancellation"
      description: "The system must allow cancellation before cut-off."
      type: functional
      status: active
      iteration_id: 1
      versioning:
        created_on_version: 1.1.0
        updated_on_version: 1.1.0
  - op: update
    requirement_id: FR-001
    changes:
      - field: description
        old: "Old text"
        new: "Updated text"
```

Update artifact docs under:
- `$REQ/01-pending-promotion/<group>/<artifact_type>.yaml`

### 2) Update merged requirements from diffs

Run this whenever diff artifacts change and before generating implementation deltas.

```bash
"$TOOL" update-merged -r "$REQ" -a "$APP" --implementation-id "$IMPL"
# equivalent aliases:
"$TOOL" merge -r "$REQ" -a "$APP" --implementation-id "$IMPL"
"$TOOL" refresh-merged -r "$REQ" -a "$APP" --implementation-id "$IMPL"
```

Output:
- `$REQ/03-current/requirements.yaml`
- `$REQ/03-current/merged/**/*.yaml`

### 3) Generate implementation delta + plan for a target app/implementation

```bash
"$TOOL" delta -r "$REQ" -a "$APP" --implementation-id "$IMPL"
```

Output:
- `<specs-root>/02-implementation-state/01-implementations/<implementation_id>/02-delta-history/01-delta-current.yaml`
- Run `plan` to generate:
  - `<specs-root>/02-implementation-state/01-implementations/<implementation_id>/03-ai-plan-current/current-plan.md`
- Delta now includes explicit `scope` (globs/files/folders) at the document level; scope is global per implementation only.
- Scope (globs) is used only from the implementation folder: `02-implementation-state/02-implementation-mapping/scope.yaml` (`global_scopes` by `implementation_id`). Requirement files must not contain globs; scope is not read from requirement traceability.

### 4) Generate AI coding inputs (diff)

```bash
"$TOOL" diff -r "$REQ" -a "$APP" --implementation-id "$IMPL"
```

Outputs:
- `<specs-root>/02-implementation-state/01-implementations/<implementation_id>/01-delta-current/structured-diff.yaml` (only artifact in 01-delta-current/)

### 5) Implement in app and update app manifest

After app code is implemented for the promoted requirement set, update:
- `$APP/.aidev/requirements/requirements-state.yaml`

Set:
- `requirements_version_target`: target version for this rollout (for example `1.1.0`)
- `requirements_version_implemented`: same as target only when implementation is complete
- `requirement_baseline`: include implemented requirement entries with pinned version

### 6) Promote staged requirements into canonical requirements

```bash
"$TOOL" promote -r "$REQ" -a "$APP" --implementation-id "$IMPL"
```

Promotion effects:
- Merges pending-promotion artifacts into `$REQ/03-current/**/*.yaml`
- Clears pending-promotion item lists
- Rebuilds requirement diff files in `$REQ/02-diff/`
- Regenerates merged outputs in `$REQ/03-current/merged/`
- Updates control versions in `$REQ/control.yaml`:
  - `current_version = previous next_version`
  - `next_version = patch bump(current_version)`

### 7) Regenerate all outputs for all implementations (optional)

```bash
"$TOOL" all -r "$REQ" --all-implementations
```

### 8) Apply

```bash
"$TOOL" apply -r "$REQ" -a "$APP" --implementation-id "$IMPL"
```

Implementation ID updates in app manifest are conservative by default:
- `apply` only adds requirement IDs from delta items where `implementation_verified: true`.
- Delta `added/updated` items are generated with `implementation_verified: false` by default.
- This prevents requirements from being marked implemented purely from planning metadata.

## Version update rules (requirements vs app manifest)

Requirements versioning and app manifest versioning are **independent concerns**.

- **Requirements control version** (`$REQ/control.yaml`) — **sole source of truth**
  - `current_version`: the version of the currently promoted requirements
  - `next_version`: the version that will be assigned on the next promote
  - During promotion: tooling advances `current_version` to `next_version`, then bumps `next_version` by patch
  - Tooling **never** reads the app manifest to determine what version to promote to
- **Merged requirements version** (`$REQ/03-current/merged/requirements.yaml`)
  - Derived from control `current_version`
  - Changes after promotion/regeneration
- **App manifest versions** (`$APP/.aidev/requirements/requirements-state.yaml`) — **downstream consumer**
  - `requirements_version_target`: set by the app/engineer to indicate which requirements version the app intends to implement (does not influence requirements versioning)
  - `requirements_version_implemented`: set by tooling (`apply` command) or engineer after implementation is complete
  - Must never have `requirements_version_implemented > requirements_version_target`
  - These fields track the app's progress against requirements — they do not drive requirements versioning

## Source model for tooling requirements

- Tooling requirements are sourced from flat requirement files:
  - `01-requirements/03-current/functional_requirements.yaml`
  - `01-requirements/03-current/nfr_and_global_cr.yaml`
- `01-requirements/03-current/acceptance_criteria.yaml` should be maintained and used as the implementation
  verification contract for functional requirements.
- Every functional requirement should map to at least one acceptance criterion.
- Contract/test/context artifacts (for example `ui_contracts`, `api_contracts`, `data_contracts`,
  `acceptance_tests`, `business_context`, `decisions`, `glossary`, `change_log`) remain separate
  artifacts and are not converted into tooling requirement diffs.
- Implementation applicability is computed from app manifest versions/implemented ids against requirement diffs and merged state.

## Pending artifacts

- Pending promotion files (requirements change staging):
  - `01-requirements/control.yaml`
  - `01-requirements/01-pending-promotion/<artifact_type>.yaml`
- Per-implementation structured diff:
  - `02-implementation-state/01-implementations/<implementation_id>/01-delta-current/structured-diff.yaml`
- Acceptance criteria artifact:
  - `01-requirements/03-current/acceptance_criteria.yaml`
  - each item should include:
    - `id` (acceptance criterion id)
    - `functional_requirement_id` (FR linkage)
    - `acceptance_test_ids` (test linkage)
    - `text` (criterion statement)
- Per-implementation execution state:
  - `../02-implementation-state/01-implementations/<implementation_id>/02-delta-history/01-delta-current.yaml` (relative to `01-requirements`)
  - `../02-implementation-state/01-implementations/<implementation_id>/02-delta-history/`
  - `../02-implementation-state/02-implementation-mapping/scope.yaml` for global per-implementation default scope
  - `../02-implementation-state/01-implementations/<implementation_id>/03-ai-plan-current/current-plan.md`
  - `../02-implementation-state/01-implementations/<implementation_id>/03-ai-plan-current/requirements-version-manifest.yaml`
  - `../02-implementation-state/01-implementations/<implementation_id>/04-ai-plan-history/`
  - `../02-implementation-state/01-implementations/<implementation_id>/05-ai-plan/plan.md`
  - `02-implementation-state/01-implementations/<implementation_id>/<implementation_id>.manifest.yaml`
- Implementation mappings:
  - `02-implementation-state/02-implementation-mapping/*.yaml`

## Numbered requirement folders (practice)

Use numbered folders at specs root:

- `01-requirements/`
- `02-implementation-state/`

## Traceability and targeting

- Keep scope (globs, exclude_globs) only in the implementation folder: `02-implementation-state/02-implementation-mapping/scope.yaml` under `global_scopes`. Do not add globs or scope to requirement files or requirement traceability.
- Do not store implementation-specific metadata in requirement artifacts.
- Keep implementation deltas/plans/manifests only under `02-implementation-state/01-implementations/<implementation_id>/`.

## Update history diff files

On update promotion, tooling writes standalone history files:
- `02-diff/history/<REQUIREMENT_ID>/<timestamp>.yaml`
with `prior` + `current` snapshots.
