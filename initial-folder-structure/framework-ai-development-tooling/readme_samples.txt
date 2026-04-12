AI Development Tooling - Samples (Action Script Only)

Copy/paste variable exports:
export AI_DEV_TOOLING_BASE=/media/psf/z-work-ai-enablement/projects/ai-development-tooling
export AI_DEV_REQ=/media/psf/z-work-ai-enablement/projects/sixert-bank-specs/01-requirements
export AI_DEV_IMPL_ROOT=/media/psf/z-work-ai-enablement/projects/sixert-bank-specs/02-implementation-state/01-implementations
export AI_DEV_APP=/media/psf/z-work-ai-enablement/projects/sixert_bank-main
export AI_DEV_IMPL=SIXERT_NODEJS_01
export AI_DEV_TOOLING_CMD="$AI_DEV_TOOLING_BASE/ai-tooling.sh"

Requirements source examples (flat layout):
$AI_DEV_REQ/03-current/acceptance_criteria.yaml
$AI_DEV_REQ/03-current/acceptance_tests.yaml
$AI_DEV_REQ/03-current/functional_requirements.yaml
$AI_DEV_REQ/03-current/ui_contracts.yaml
$AI_DEV_REQ/03-current/api_contracts.yaml

Tooling manifest:
$AI_DEV_TOOLING_BASE/tooling-manifest.yaml
Update `current_version` and `implemented_version` on each tooling/practice change request.

Manifest required fields (app):
implementation_id
app_identifier (must match 02-implementation/index.yaml app_identifier)
iteration_id (integer, for example 1)
requirements_version_target
requirements_version_implemented
requirement_baseline

0) Generate pending-to-run list for an implementation

$AI_DEV_TOOLING_CMD delta -r "$AI_DEV_REQ" --implementation-id "$AI_DEV_IMPL"

Output:
$AI_DEV_IMPL_ROOT/<IMPLEMENTATION_ID>/01-delta-current.yaml
$AI_DEV_IMPL_ROOT/<IMPLEMENTATION_ID>/03-plan-current/current-plan.md

0.1) Update merged requirements from diffs

$AI_DEV_TOOLING_CMD merge -r "$AI_DEV_REQ" --all-implementations
# alias:
$AI_DEV_TOOLING_CMD refresh-merged -r "$AI_DEV_REQ" --all-implementations

1) Add a new requirement (pending)

Edit $AI_DEV_REQ/01-pending-promotion/_control.yaml and per-artifact pending files, then append:

changes:
  - op: add
    requirement:
      $schema: http://internal.schemas.com/ai-requirement-draft-01
      requirement_id: FR-200
      title: "Example new requirement"
      description: "The system must ..."
      type: functional
      status: active
      versioning:
        created_on_version: 1.1.0
        updated_on_version: 1.1.0
      traceability: {}   # scope is global per implementation in scope.yaml only

Then generate diff:
$AI_DEV_TOOLING_CMD diff -r "$AI_DEV_REQ" --implementation-id "$AI_DEV_IMPL"

2) Update an existing requirement (pending)

Append in $AI_DEV_REQ/01-pending-promotion/_control.yaml:

changes:
  - op: update
    requirement_id: FR-001
    changes:
      - field: description
        old: "Old text ..."
        new: "New text ..."
      - field: versioning.updated_on_version
        old: "1.0.0"
        new: "1.1.0"

Regenerate diff:

3) Commit/promote pending changes into next version

$AI_DEV_TOOLING_CMD promote -r "$AI_DEV_REQ" --implementation-id "$AI_DEV_IMPL"

3.1) Update merged requirements from diff artifacts

$AI_DEV_TOOLING_CMD merge -r "$AI_DEV_REQ" --all-implementations

Notes:
Update promotions create history diff files:
  - $AI_DEV_REQ/02-diff/history/<REQUIREMENT_ID>/<timestamp>.yaml
  - includes prior/current snapshots.

4) Generate code inputs for requirements

$AI_DEV_TOOLING_CMD diff -r "$AI_DEV_REQ" --implementation-id "$AI_DEV_IMPL"

Use generated:
$AI_DEV_REQ/../02-implementation-state/01-implementations/$AI_DEV_IMPL/01-delta-current/structured-diff.yaml

5) Rebuild all artifacts

$AI_DEV_TOOLING_CMD all -r "$AI_DEV_REQ" --all-implementations

6) Rules

requirement_set_id must match app and requirements.
app_identifier must match app and requirements manifests.
keep app_identifier only in manifest files (not requirement artifacts).
keep implementation-specific state only under $AI_DEV_IMPL_ROOT/<IMPLEMENTATION_ID>/.
