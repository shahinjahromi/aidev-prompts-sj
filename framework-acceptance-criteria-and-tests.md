# Framework Acceptance Criteria and Acceptance Tests

## Test Configuration
- App name: test-framework-temp
- Core stack: go
- Implementation id suffix input: goimp
- Effective implementation id: test-framework-temp-goimp
- Blueprint under test: test-framework-temp-ai-blueprint
- App repo under test: test-framework-temp-goimp

## Scope
This document defines acceptance criteria and acceptance tests for the framework setup flow and generated blueprint structure, with explicit coverage for:
- NFR and technology stack preset folder creation
- Implementation-id-specific artifact expectations
- Merged requirements field parity with originals, including module
- Go core stack runtime validation using a hello-world execution test

## Acceptance Criteria

### AC-001 Setup creates blueprint and app repositories
- The setup command shall create one blueprint folder and one app folder.
- The blueprint folder name shall be <app-slug>-ai-blueprint.
- The app folder name shall be <app-slug>-<implementation-suffix>.

### AC-002 Implementation mapping is materialized
- The generated blueprint shall contain one implementation directory under 02-implementation/01-implementations.
- The implementation directory shall use the effective implementation id.

### AC-003 Core-stack NFR preset folder exists
- For core stack go, the blueprint shall contain user-prompts-content/aidev2-details/preset-requirements/nfr_and_global_cr_by_core_stack/go.

### AC-004 Core-stack technology selection preset folder exists
- For core stack go, the blueprint shall contain user-prompts-content/aidev2-details/preset-requirements/tech_selections_by-core-stack/go.

### AC-005 Technology selection implementation-specific file exists
- The go tech selection preset shall include an implementation-id-specific file.
- Expected file pattern: technology_selection_<implementation_id>.yaml resolved to concrete id.

### AC-006 NFR implementation-specific file exists
- The go NFR preset shall include an implementation-id-specific file.
- Expected file pattern: nfr_and_global_cr_<implementation_id>.yaml resolved to concrete id.

### AC-007 Merged requirements preserve original fields
- The merged requirements artifact shall preserve all relevant fields from original requirement files.
- For each requirement type included in merged output, original field sets shall be represented in merged output.
- The module field must be preserved when present in originals.

### AC-008 App manifest binds effective implementation id
- The app manifest file shall exist under manifests/requirements-manifest.yaml.
- implementation_id shall equal the effective implementation id.

### AC-009 Go core-stack runtime sanity passes with hello world
- A hello-world Go program shall execute successfully in the test environment.
- Standard output shall equal hello world.

## Acceptance Tests

### AT-001 Verify setup outputs
- Precondition: setup script is available.
- Steps:
  1. Run setup with app slug test-framework-temp and impl suffix goimp.
  2. Check for test-framework-temp-ai-blueprint.
  3. Check for test-framework-temp-goimp.
- Expected:
  - Both folders exist.

### AT-002 Verify implementation directory generation
- Steps:
  1. Check 02-implementation/01-implementations in the generated blueprint.
  2. Verify folder named test-framework-temp-goimp exists.
- Expected:
  - Folder exists exactly once.

### AT-003 Verify Go NFR preset folder
- Steps:
  1. Check user-prompts-content/aidev2-details/preset-requirements/nfr_and_global_cr_by_core_stack/go.
- Expected:
  - Directory exists.

### AT-004 Verify Go tech-stack preset folder
- Steps:
  1. Check user-prompts-content/aidev2-details/preset-requirements/tech_selections_by-core-stack/go.
- Expected:
  - Directory exists.

### AT-005 Verify implementation-id-specific tech selection file
- Steps:
  1. Resolve effective implementation id: test-framework-temp-goimp.
  2. Check for technology_selection_test-framework-temp-goimp.yaml in the Go tech folder.
  3. Check whether placeholder file technology_selection_[implementation_id].yaml remains.
- Expected:
  - Implementation-specific file exists.
  - Placeholder file does not remain.

### AT-006 Verify implementation-id-specific NFR file
- Steps:
  1. Resolve effective implementation id: test-framework-temp-goimp.
  2. Check for nfr_and_global_cr_test-framework-temp-goimp.yaml in the Go NFR folder.
- Expected:
  - Implementation-specific file exists.

### AT-007 Verify merged field parity including module
- Steps:
  1. Read originals from 01-requirements/03-current/functional_requirements.yaml, nfr_and_global_cr.yaml, technology_selection.yaml.
  2. Read merged artifact from 01-requirements/03-current/merged/merged_requirements.yaml.
  3. Compare field sets by type.
  4. Validate module field is preserved in merged when present in originals.
- Expected:
  - Original field sets are preserved in merged output.
  - module is present in merged wherever present in originals.

### AT-008 Verify app manifest implementation id
- Steps:
  1. Read test-framework-temp-goimp/manifests/requirements-manifest.yaml.
  2. Validate implementation_id value.
- Expected:
  - implementation_id equals test-framework-temp-goimp.

### AT-009 Verify Go hello-world runtime
- Steps:
  1. Create temporary hello-world Go program.
  2. Execute go run against it.
  3. Capture stdout and exit code.
- Expected:
  - Exit code is zero.
  - Output equals hello world.

## Traceability Matrix
- AC-001 -> AT-001
- AC-002 -> AT-002
- AC-003 -> AT-003
- AC-004 -> AT-004
- AC-005 -> AT-005
- AC-006 -> AT-006
- AC-007 -> AT-007
- AC-008 -> AT-008
- AC-009 -> AT-009

## Notes
- This specification is intentionally strict on implementation-id-specific preset files and merged-field parity, including module, to prevent silent schema drift during setup automation.
