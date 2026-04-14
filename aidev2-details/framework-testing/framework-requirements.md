# Framework Requirements

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
- Prompt naming convention enforcing execution order via `aidev2-NN-` prefix
- Process overview file discoverable by AI and a README pointing to it
- Preset seeding destination (pending-promotion, not current) at setup time
- Add-implementation-to-existing-blueprint setup mode
- Prompt efficiency and minimal redundancy requirements
- Execution optimization strategy documentation (agent routing, communication, gates, read efficiency)
- Playwright as the standard e2e test framework for web-based implementations; one test per UIC ID; UI vs API test projects
- All test artifacts confined to `03-test-results/<IMPLEMENTATION_ID>`; none written inside `06-e2e-tests/`
- Screenshots captured for every visited screen state in UI tests and included as run artifacts
- Default test run scope is partial; full suite only on explicit user request
- Test output file naming convention: `<timestamp>-<REQ_ID>-<partial|full>.<ext>`
- Module reassignment triggers undo/redo; both old and new module locations must build after the change
- DB alignment gate mandatory when diff contains physical_database_schema entries
- Dispatcher enforces handoff contract; pipeline stops immediately on blocked or fail status
- Requirement IDs globally unique per type across pending and current (`next_seq = max + 1` rule)
- Per-implementation technology selection and NFR files are the canonical source in their respective folders; no flat aggregate files exist
- No `github-config` folder in the generated blueprint
- Framework prompt and instruction files contain no technology- or language-specific instructions; such content belongs exclusively in preset NFR, technology selection, and global requirement files
- NFR and technology selection live in per-implementation-id folders (`nfr-and-global-cr/`, `technology-selection/`) under both pending-promotion and current; flat aggregate files (`nfr_and_global_cr.yaml`, `technology_selection.yaml`) do not exist
- Contract references use `contract_type: models_and_contracts` and MAC ID object form only; `sub_mac_ids` is obsolete
- MAC catalog `child_specifications` kept in sync with spec file child IDs at all times
- Requirements state file located at `.aidev/requirements/requirements-state.yaml` relative to app root
- Design-first authoring: models and contracts are first-class authoring targets alongside functional requirements
- DB physical schema changes produce both a full resulting schema file and a companion `-migration` file
- Process instructions file named `aidev2-instructions.md`; README named `aidev2-readme.md` pointing to it
- Framework template's `initial-folder-structure` lives under `aidev2-details/`
- All YAML output uses 2-space indentation, block style, no tabs; `.editorconfig` enforces this at repository level

## Requirements

### REQ-001 Setup creates blueprint and app repositories

#### Acceptance Criteria
- AC-001: The setup command shall create one blueprint folder and one app folder.
- The blueprint folder name shall be <app-slug>-ai-blueprint.
- The app folder name shall be <app-slug>-<implementation-suffix>.

#### Acceptance Test — AT-001 Verify setup outputs
- Precondition: setup script is available.
- Steps:
  1. Run setup with app slug test-framework-temp and impl suffix goimp.
  2. Check for test-framework-temp-ai-blueprint.
  3. Check for test-framework-temp-goimp.
- Expected:
  - Both folders exist.

---

### REQ-002 Implementation mapping is materialized

#### Acceptance Criteria
- AC-002: The generated blueprint shall contain one implementation directory under 02-implementation/01-implementations.
- The implementation directory shall use the effective implementation id.

#### Acceptance Test — AT-002 Verify implementation directory generation
- Steps:
  1. Check 02-implementation/01-implementations in the generated blueprint.
  2. Verify folder named test-framework-temp-goimp exists.
- Expected:
  - Folder exists exactly once.

---

### REQ-003 Core-stack NFR preset folder exists

#### Acceptance Criteria
- AC-003: The user prompts folder shall contain a core-stack subfolder for Go NFR presets at `aidev2-details/preset-requirements/nfr-and-global-cr-by-core-stack/go`.
- The folder shall hold implementation-specific NFR files named `nfr_and_global_cr_<implementation_id>.yaml`, one per registered implementation.
- A placeholder template file (`nfr_and_global_cr-[implementation id].yaml`) shall also reside in this folder to serve as a copy-source for new implementations.

#### Acceptance Test — AT-003 Verify Go NFR preset folder
- Steps:
  1. Locate the user prompts root (e.g. `~/.config/Code/User/prompts` or Windows equivalent).
  2. Check that `aidev2-details/preset-requirements/nfr-and-global-cr-by-core-stack/go` exists.
  3. Verify at least one implementation-specific file matching `nfr_and_global_cr_<impl-id>.yaml` is present.
- Expected:
  - Directory exists.
  - At least one implementation-specific NFR file exists inside it.

---

### REQ-004 Core-stack technology selection preset folder exists

#### Acceptance Criteria
- AC-004: The user prompts folder shall contain a core-stack subfolder for Go technology selection presets at `aidev2-details/preset-requirements/tech_selections_by-core-stack/go`.
- The folder shall hold implementation-specific technology selection files named `technology_selection_<implementation_id>.yaml`, one per registered implementation.
- A placeholder template file (`technology_selection_[implementation_id].yaml`) shall also reside in this folder to serve as a copy-source for new implementations.

#### Acceptance Test — AT-004 Verify Go tech-stack preset folder
- Steps:
  1. Locate the user prompts root.
  2. Check that `aidev2-details/preset-requirements/tech_selections_by-core-stack/go` exists.
  3. Verify at least one implementation-specific file matching `technology_selection_<impl-id>.yaml` is present.
- Expected:
  - Directory exists.
  - At least one implementation-specific technology selection file exists inside it.

---

### REQ-005 Technology selection implementation-specific file exists

#### Acceptance Criteria
- AC-005: The go tech selection preset shall include an implementation-id-specific file.
- Expected file pattern: technology_selection_<implementation_id>.yaml resolved to concrete id.
- The placeholder file `technology_selection_[implementation_id].yaml` serves as a reusable template for new implementations and may remain alongside impl-specific files.

#### Acceptance Test — AT-005 Verify implementation-id-specific tech selection file
- Steps:
  1. Resolve effective implementation id: test-framework-temp-goimp.
  2. Check for technology_selection_test-framework-temp-goimp.yaml in the Go tech folder.
  3. Check whether placeholder file technology_selection_[implementation_id].yaml is still present (it may remain as template).
- Expected:
  - Implementation-specific file exists.
  - Placeholder template file may remain; its presence does not constitute a failure.

---

### REQ-006 NFR implementation-specific file exists

#### Acceptance Criteria
- AC-006: The go NFR preset shall include an implementation-id-specific file.
- Expected file pattern: nfr_and_global_cr_<implementation_id>.yaml resolved to concrete id.
- The placeholder file `nfr_and_global_cr-[implementation id].yaml` serves as a reusable template for new implementations and may remain alongside impl-specific files.

#### Acceptance Test — AT-006 Verify implementation-id-specific NFR file
- Steps:
  1. Resolve effective implementation id: test-framework-temp-goimp.
  2. Check for nfr_and_global_cr_test-framework-temp-goimp.yaml in the Go NFR folder.
- Expected:
  - Implementation-specific file exists.
  - Placeholder template file may remain; its presence does not constitute a failure.

---

### REQ-007 Merged requirements preserve original fields

#### Acceptance Criteria
- AC-007: The merged requirements artifact shall preserve all relevant fields from original requirement files.
- For each requirement type included in merged output, original field sets shall be represented in merged output.
- The module field must be preserved when present in originals.

#### Acceptance Test — AT-007 Verify merged field parity including module
- Steps:
  1. Read originals from `01-requirements/03-current/functional_requirements.yaml`, per-implementation files in `01-requirements/03-current/nfr-and-global-cr/`, and per-implementation files in `01-requirements/03-current/technology-selection/`.
  2. Read merged artifact from `01-requirements/03-current/merged/merged_requirements.yaml`.
  3. Compare field sets by type.
  4. Validate module field is preserved in merged when present in originals.
- Expected:
  - Original field sets are preserved in merged output.
  - module is present in merged wherever present in originals.

---

### REQ-008 App manifest binds effective implementation id

#### Acceptance Criteria
- AC-008: The app manifest file shall exist under `.aidev/requirements/requirements-state.yaml`.
- The `implementation_id` field shall equal the effective implementation id.

#### Acceptance Test — AT-008 Verify app manifest implementation id
- Steps:
  1. Read test-framework-temp-goimp/.aidev/requirements/requirements-state.yaml.
  2. Validate implementation_id value.
- Expected:
  - implementation_id equals test-framework-temp-goimp.

---

### REQ-009 Go core-stack runtime sanity passes with hello world

#### Acceptance Criteria
- AC-009: A hello-world Go program shall execute successfully in the test environment.
- Standard output shall equal hello world.

#### Acceptance Test — AT-009 Verify Go hello-world runtime
- Steps:
  1. Create temporary hello-world Go program.
  2. Execute go run against it.
  3. Capture stdout and exit code.
- Expected:
  - Exit code is zero.
  - Output equals hello world.

---

### REQ-010 Module-scoped implementation restricts work to specified modules only

#### Acceptance Criteria
- AC-010: When an implementation specifies one or more target modules, only requirements belonging to those modules shall be implemented.
- The diff step shall filter differences by the module property before passing them to the implementation step; only diff entries whose module value matches a specified target module shall be included.
- Any tool that operates on the diff must support filtering by the module property; unfiltered diff output shall not be passed to implementation when a module scope is active.
- Requirements whose module property is absent or does not match a specified target module shall not produce implementation artifacts in that run.

#### Acceptance Test — AT-010 Verify module-scoped implementation filters by module property
- Precondition: merged requirements contain entries with at least two distinct module values.
- Steps:
  1. Invoke the diff step with a target module (e.g. module: auth).
  2. Capture the diff output.
  3. Verify every diff entry in the output has module equal to the specified target.
  4. Verify no diff entry with a different module value is present in the output.
  5. Invoke the implementation step with the filtered diff.
  6. Verify only implementation artifacts for the target module are produced.
  7. Verify no artifacts for other modules are created.
- Expected:
  - Diff output contains only entries whose module matches the target.
  - Implementation artifacts exist only for the target module's requirements.
  - Requirements without a matching module property produce no artifacts in this run.

---

### REQ-011 Main prompts follow aidev2-NN-description naming convention

#### Acceptance Criteria
- AC-011: Every `.prompt.md` file at the top level of the user prompts folder that is intended to be invoked via the `/` slash command shall be named with the pattern `aidev2-NN-<description>.prompt.md`, where `NN` is a zero-padded two-digit integer (e.g. `01`, `02`, `10`).
- The numeric component shall reflect the order in which the prompt is commonly executed within the aidev2 pipeline (e.g. requirements before diff, diff before implementation).
- No main prompt file may omit the `aidev2-NN-` prefix; files without the prefix shall not appear as slash-command entries in the primary workflow.
- Sub-folder prompt files used as supporting assets are exempt from this convention, but top-level workflow prompts are not.

#### Acceptance Test — AT-011 Verify prompt naming convention
- Precondition: The user prompts folder is accessible.
- Steps:
  1. List all `.prompt.md` files at the root of the user prompts folder.
  2. For each file, check that the filename matches the regex `^aidev2-\d{2}-`.
  3. Record any file that does not match.
  4. Verify the numeric components form a contiguous or intentionally-gapped sequence that reflects documented pipeline order.
- Expected:
  - Every top-level `.prompt.md` filename starts with `aidev2-` followed by exactly two digits and a dash.
  - No top-level prompt file is found without the `aidev2-NN-` prefix.
  - The sequence of numeric components is consistent with the documented execution order.

---

### REQ-012 `aidev2-instructions.md` is the sole general instructions file

#### Acceptance Criteria
- AC-012: The prompts folder shall contain a file named `aidev2-instructions.md` at its root. This is the single canonical file for all general aidev2 process instructions and pipeline overview.
- `aidev2-instructions.md` shall contain a succinct end-to-end description of the aidev2 pipeline: its stages, the order prompts are run, what inputs each stage consumes, and what artifacts it produces.
- The overview shall be self-contained enough that an AI agent reading only that file understands how to navigate to the correct stage prompt for any given task.
- No other file at the root of the prompts folder (including `aidev2-readme.md`) shall duplicate general pipeline instructions or process descriptions; any such content belongs exclusively in `aidev2-instructions.md`.
- `aidev2-readme.md` may exist as a minimal human pointer but shall contain no general instructions itself — only a reference to `aidev2-instructions.md`.

#### Acceptance Test — AT-012 Verify aidev2-instructions.md is the sole general instructions file
- Precondition: The user prompts folder is accessible.
- Steps:
  1. Check that `aidev2-instructions.md` exists at the root of the prompts folder.
  2. Read the file and verify it contains at minimum: a list of pipeline stages, the execution order, expected inputs per stage, and expected outputs per stage.
  3. If `aidev2-readme.md` exists, verify it contains no general pipeline instructions — only a brief pointer to `aidev2-instructions.md`.
  4. Verify no other root-level file duplicates the content of `aidev2-instructions.md`.
- Expected:
  - `aidev2-instructions.md` exists and contains the complete succinct pipeline overview.
  - No other root-level file contains general aidev2 process instructions.

---

### REQ-013 Prompts narrate each step succinctly as they execute

#### Acceptance Criteria
- AC-013: Each prompt shall emit a brief, human-readable status line before or immediately after each discrete action it performs (e.g. "Reading merged requirements…", "Writing diff artifact…", "Invoking implementation for module auth…").
- The narration shall be concise — one sentence or less per step — and shall not pad output with unnecessary explanation.
- The narration shall accurately describe the action being taken, not a generic progress message.
- Steps that produce no observable side-effect (pure reads used only for internal decisions) are exempt, but any step that writes, deletes, or invokes another tool must be narrated.
- Narration lines for errors must include the step token (e.g. `IM-04`, `RQ-01`) and enough context to diagnose without re-reading logs.
- Unexpected issues (unplanned crashes, missing files, schema mismatches, tool timeouts, retries) must be narrated in **bold** Markdown formatting: `**UNEXPECTED: <description>**`.

#### Acceptance Test — AT-013 Verify per-step narration in prompts
- Precondition: A representative prompt (e.g. the diff or implementation prompt) is executed in a controlled session.
- Steps:
  1. Execute the prompt against a known input set.
  2. Capture all output emitted during execution.
  3. For each write, delete, or tool-invocation step performed, check that a corresponding narration line appears in the output before or immediately after that step.
  4. Verify each narration line is one sentence or fewer.
  5. Verify no narration line is a generic placeholder (e.g. "Processing…" without context).
  6. If any errors occurred, verify they include the step token and are narrated immediately.
  7. If any unexpected issues occurred, verify they are rendered in **bold**.
- Expected:
  - Every side-effecting step has a matching narration line in the output.
  - All narration lines are concise and accurately describe the action taken.
  - Error narration includes step tokens.
  - Unexpected issues appear in **bold**.

---

---

### REQ-014 Setup seeds core-stack presets into pending-promotion, not directly into current

#### Acceptance Criteria
- AC-014: When `--core-stack` is provided and matching preset files exist in the user prompts preset folder, setup shall copy them into `01-requirements/01-pending-promotion/nfr-and-global-cr/` and `01-requirements/01-pending-promotion/technology-selection/` respectively.
- The seeded files shall be named `nfr_and_global_cr_<implementation_id>.yaml` and `technology_selection_<implementation_id>.yaml`.
- Presets shall NOT be written directly into `01-requirements/03-current/`; they must enter the blueprint via the promote step.
- If no `--core-stack` is provided or no preset file exists for the given stack, setup shall skip seeding without error.

#### Acceptance Test — AT-014 Verify preset seeding destination at setup
- Precondition: User prompts folder contains Go preset templates; setup is run with `--core-stack go`.
- Steps:
  1. Run setup with app slug test-framework-temp, impl suffix goimp, and `--core-stack go`.
  2. Check that `01-requirements/01-pending-promotion/technology-selection/technology_selection_test-framework-temp-goimp.yaml` exists in the blueprint.
  3. Check that `01-requirements/01-pending-promotion/nfr-and-global-cr/nfr_and_global_cr_test-framework-temp-goimp.yaml` exists in the blueprint.
  4. Verify neither file was written into `01-requirements/03-current/`.
- Expected:
  - Both preset files exist under `01-pending-promotion/`.
  - Neither file is present directly under `03-current/`.

---

### REQ-015 Setup supports adding a new implementation to an existing blueprint

#### Acceptance Criteria
- AC-015: The setup script shall support an `--add-impl` mode that operates when the blueprint folder already exists.
- In `--add-impl` mode, setup shall: create a new implementation directory under `02-implementation/01-implementations/<new-impl-id>`; create a new app repo folder with the new implementation ID; seed core-stack presets for the new implementation into `01-requirements/01-pending-promotion/` (if `--core-stack` is provided); and create `.aidev/requirements/requirements-state.yaml` in the new app repo.
- The existing blueprint, its existing requirements, and any existing implementation directories shall not be modified or deleted.
- If `--add-impl` is not specified and the blueprint already exists, setup shall fail with a clear error (existing behaviour preserved).

#### Acceptance Test — AT-015 Verify add-impl mode
- Precondition: A blueprint `test-framework-temp-ai-blueprint` already exists with one implementation.
- Steps:
  1. Run setup with `--add-impl`, app slug test-framework-temp, impl suffix goimp2, and `--core-stack go`.
  2. Verify `02-implementation/01-implementations/test-framework-temp-goimp2` was created in the existing blueprint.
  3. Verify `test-framework-temp-goimp2/.aidev/requirements/requirements-state.yaml` was created.
  4. Verify the original implementation directory and existing requirements files are unchanged.
- Expected:
  - New implementation directory and app repo exist.
  - Existing blueprint content is unmodified.

---

### REQ-016 Framework prompts are written efficiently with minimal redundancy

#### Acceptance Criteria
- AC-016: Each top-level prompt file shall not duplicate content already present in `aidev2-instructions.md` or in other prompt files; pipeline-level descriptions, stage overviews, and schema definitions shall be referenced by pointer or assumed as prior context rather than restated inline.
- Common logic required by multiple prompts (e.g. resolving `config.yaml`, computing paths, reading the manifest) shall be factored into a shared instruction file under `aidev2-details/` and referenced, not copy-pasted into each prompt.
- Each prompt shall be scoped to the actions and decisions unique to its stage; introductory pipeline summaries that merely repeat `aidev2-instructions.md` are not permitted.

#### Acceptance Test — AT-016 Verify prompt efficiency and low redundancy
- Precondition: All top-level prompt files and `aidev2-instructions.md` are accessible.
- Steps:
  1. For each top-level prompt, identify any block of text (3+ sentences or a numbered list) that also appears verbatim or near-verbatim in `aidev2-instructions.md` or another prompt.
  2. Check whether common setup logic (path resolution, config reading) is factored into a shared file under `aidev2-details/` rather than repeated inline.
  3. Check that each prompt contains no stage summary section that re-explains the full pipeline.
- Expected:
  - No substantial duplication of content between prompt files or between a prompt and `aidev2-instructions.md`.
  - Common logic is located in one shared instruction file, not in-lined across multiple prompts.

---

### REQ-017 Framework documents execution optimization methods for speed and quality

#### Acceptance Criteria
- AC-017: `aidev2-instructions.md` shall include a dedicated section specifying the execution optimization strategy for the aidev2 pipeline, covering at minimum:
  - **Agent routing**: which agent mode handles which stage (e.g. dispatcher routes to specialist agents; specialist agents do not re-route).
  - **Agent communication pattern**: how the dispatcher invokes a specialist (subagent call), how the specialist returns results (single report message back to dispatcher), and how the dispatcher continues after receiving the result.
  - **Sequencing gates**: explicit gates that must be satisfied before the next stage begins (e.g. plan artifact must exist and be reviewed before execute; diff must be non-empty before planning).
  - **Read efficiency**: agents shall use targeted file reads and exact-match searches rather than broad workspace scans; semantic search shall not be used when a file path is already known.
  - Any other technique explicitly adopted by the framework that provides a measurable improvement to response speed or output quality.
- The section shall be prescriptive, not aspirational — it shall state what the framework does, not what it recommends.

#### Acceptance Test — AT-017 Verify optimization strategy is documented in aidev2-instructions.md
- Precondition: `aidev2-instructions.md` exists at the root of the user prompts folder.
- Steps:
  1. Read `aidev2-instructions.md`.
  2. Locate the execution optimization section.
  3. Verify it names at least: dispatcher-to-specialist routing, subagent communication pattern, plan-before-execute gate, and read-efficiency rule.
  4. Verify the section is written as prescriptive statements (shall/must), not suggestions.
- Expected:
  - A dedicated optimization section exists.
  - All four required items are covered with prescriptive language.

---

### REQ-018 Playwright is the e2e test framework; UI tests are one-per-UIC-ID

#### Acceptance Criteria
- AC-018: When the implementation is web-based (HTTP), the framework shall generate Playwright tests as the e2e test mechanism.
- UI tests shall be placed under `IMPL_ROOT/06-e2e-tests/ui/` and shall use a full Playwright browser context (`page` fixture) — not a `request`-only context.
- There shall be exactly one Playwright test per `UIC-*` ID referenced by the in-scope requirements via `contract_refs`. Tests shall not be grouped per requirement or merged across multiple UICs.
- Each Playwright test title shall include the `UIC-*` ID so the report shows one result row per executed UIC.
- API tests shall be placed under `IMPL_ROOT/06-e2e-tests/api/` and shall use the Playwright `request` fixture — no browser context for pure API tests.
- The UI test project shall be run with `npx playwright test --project=ui`.
- The API test project shall be run with `TEST_MODE=api npx playwright test --project=api`.

#### Acceptance Test — AT-018 Verify Playwright test structure
- Precondition: Implementation run complete for at least one requirement referencing a UIC-* contract.
- Steps:
  1. List files under `06-e2e-tests/ui/` and `06-e2e-tests/api/`.
  2. For each UI test file, verify each test title contains a `UIC-XXXXXXX` ID.
  3. Verify no UI test covers more than one UIC ID in a single `test()` block.
  4. Verify `06-e2e-tests/ui/` tests import and use the `page` fixture.
  5. Verify `06-e2e-tests/api/` tests use the `request` fixture and do not open a browser context.
- Expected:
  - One test per UIC ID in `06-e2e-tests/ui/`.
  - UI tests use browser context; API tests use request context.
  - Test titles include UIC IDs.

---

### REQ-019 All Playwright artifacts are written under `03-test-results/IMPLEMENTATION_ID` only

#### Acceptance Criteria
- AC-019: The Playwright config shall set `outputDir` explicitly to a path under `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID`.
- All report artifacts — HTML reports, JSON reports, screenshots, traces, videos, attachments, and raw output — shall be written under `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID`.
- No artifact shall be written under `06-e2e-tests/` or any subdirectory thereof (including `test-results/`, `playwright-report/`, `blob-report/`).
- `reportsRoot` shall resolve to `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID` via the `E2E_REPORTS_ROOT` env var or a relative `path.resolve` from `__dirname`.
- Any test run that produces files outside `03-test-results/IMPLEMENTATION_ID` shall be treated as a misconfigured run.

#### Acceptance Test — AT-019 Verify artifact output location
- Precondition: A Playwright test run has been executed.
- Steps:
  1. Check `playwright.config.ts` for `outputDir` value; verify it resolves to a path under `03-test-results/IMPLEMENTATION_ID`.
  2. After a test run, scan `06-e2e-tests/` recursively for any generated report or artifact files.
  3. Confirm all HTML, JSON, screenshot, and trace files are located under `03-test-results/IMPLEMENTATION_ID`.
- Expected:
  - `outputDir` points to `03-test-results/IMPLEMENTATION_ID`.
  - No report or artifact files appear anywhere under `06-e2e-tests/`.
  - All run outputs are under `03-test-results/IMPLEMENTATION_ID`.

---

### REQ-020 Screenshots captured for every visited screen state in UI tests

#### Acceptance Criteria
- AC-020: Every UI test shall capture a full-page screenshot for each screen state visited during the scenario — not only on failure.
- Screenshots shall be attached to the test result using `testInfo.attach('screenshot-<UIC-ID>', { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' })`.
- When a test scenario visits more than one screen state within the same UIC, one screenshot attachment shall exist per visited state.
- The generated HTML report shall embed the screenshots inline and shall include a pass/fail explanation per test row (using `ui-html-reporter.ts`).

#### Acceptance Test — AT-020 Verify per-state screenshot capture in UI tests
- Precondition: UI test run completed for at least one UIC-linked requirement.
- Steps:
  1. Inspect the HTML test report under `03-test-results/IMPLEMENTATION_ID`.
  2. For each executed UIC test, verify at least one screenshot attachment is present.
  3. Verify the HTML report embeds screenshots inline (not just file links).
  4. Verify each result row includes a plain-language pass/fail explanation.
- Expected:
  - Every UI test result has at least one screenshot attachment.
  - Report embeds screenshots inline with pass/fail explanation.

---

### REQ-021 Default test run scope is partial; full suite requires explicit user request

#### Acceptance Criteria
- AC-021: When the testing step is invoked without an explicit "run all tests" instruction, only the tests corresponding to requirements implemented in the current run (i.e. IDs from the active diff/plan) shall be executed.
- The test file(s) or `--grep` pattern shall be derived from the current run's requirement IDs.
- Full suite execution shall be triggered only when the user explicitly requests it (e.g. "run all tests").
- The run type (partial vs full) shall be reflected in the output file name suffix.

#### Acceptance Test — AT-021 Verify partial run is the default scope
- Precondition: A multi-requirement implementation run has been completed.
- Steps:
  1. Invoke the testing step without any "run all" instruction.
  2. Verify that only test files/grep patterns matching the current run's requirement IDs are executed.
  3. Verify the output files use the `-partial` suffix.
  4. Invoke with "run all tests" and verify the full suite runs with `-full` suffix.
- Expected:
  - Partial scope triggered by default; only current-run tests execute.
  - Full scope triggered only on explicit request.

---

### REQ-022 Test output files follow the `<timestamp>-<REQ_ID>-<partial|full>.<ext>` naming convention

#### Acceptance Criteria
- AC-022: Every output file written to `BLUEPRINT_ROOT/03-test-results/IMPLEMENTATION_ID` during a test run shall follow the naming pattern: `<timestamp>-<REQ_ID>-<partial|full>.<ext>`.
- `<timestamp>` shall be ISO-8601 format with `:` and `.` replaced by `-` (e.g. `2026-04-10T13-07-44-505Z`).
- `<REQ_ID>` shall be the primary requirement ID for the run (e.g. `FR-000005`).
- `<partial|full>` shall reflect whether the run was scoped to the current diff or the full suite.
- `<ext>` is `html`, `json`, or equivalent. The same timestamp and suffix shall apply to all output files from the same run.

#### Acceptance Test — AT-022 Verify test output file naming
- Precondition: A test run has produced output files.
- Steps:
  1. List files under `03-test-results/IMPLEMENTATION_ID`.
  2. For each output file, verify the filename matches the pattern `^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-\d{3}Z-[A-Z]+-\d+-(?:partial|full)\.[a-z]+$`.
  3. Verify all files from the same run share the same timestamp prefix and partial/full suffix.
- Expected:
  - Every output file conforms to the naming pattern.
  - Timestamp does not use `:` or `.` as separators.
  - partial/full suffix correctly reflects the run scope.

---

### REQ-023 Module reassignment triggers undo/redo; both module locations must build after the change

#### Acceptance Criteria
- AC-023: When a requirement's `module` field changes between the manifest baseline and the current requirements (detected during diff), the implementation step shall treat it as a module reassignment.
- The diff shall flag the entry as `module_changed: true` and report a "Module reassignments: N" count.
- The implementation plan shall include explicit undo scope (removal from old module) and redo scope (placement under new module) for each reassigned requirement, before any content-level updates for the same requirement.
- After executing undo and redo, both the old module location and the new module location shall build and function correctly.
- The manifest baseline `module` field for the requirement shall be updated to the new value after code is in place.

#### Acceptance Test — AT-023 Verify module reassignment undo/redo
- Precondition: A requirement exists in current with `module: A`; the pending version of the same requirement has `module: B`.
- Steps:
  1. Run the diff step and verify the requirement is flagged with `module_changed: true`.
  2. Verify the diff report contains "Module reassignments: 1".
  3. Run the plan step and verify both undo scope (old module) and redo scope (new module) appear for the requirement.
  4. Execute and verify code under old module `A` no longer contains the requirement's contributions.
  5. Verify code under new module `B` contains the implementation.
  6. Verify the application builds successfully after the change.
  7. Verify the manifest baseline `module` field was updated to `B`.
- Expected:
  - Diff flags module change; plan documents undo and redo; both modules build after execution.
  - Manifest reflects the updated module value.

---

### REQ-024 DB alignment gate is mandatory when diff contains physical_database_schema entries

#### Acceptance Criteria
- AC-024: When the structured diff contains any entry tied to `physical_database_schema` or equivalent DB contract alignment work, the DB alignment gate shall be activated.
- DB alignment work shall be completed and verified before the implementation run is considered complete.
- The plan shall mark DB alignment as mandatory work.
- The run shall not be closed without schema verification evidence.

#### Acceptance Test — AT-024 Verify DB gate activation
- Precondition: Diff contains at least one entry with `physical_database_schema` in its contract_refs or MAC type.
- Steps:
  1. Run the diff step and observe the DB gate check output.
  2. Verify the plan marks DB alignment as mandatory.
  3. Attempt to close the run without DB schema verification; verify the framework blocks completion.
  4. Provide schema verification evidence and verify the run can be closed.
- Expected:
  - DB gate is activated when diff contains schema entries.
  - Run cannot be completed without DB schema verification evidence.

---

### REQ-025 Dispatcher enforces handoff contract; pipeline stops immediately on blocked or fail

#### Acceptance Criteria
- AC-025: Each specialist agent (requirements, planning, implementation, validation, testing) shall return exactly one `handoff` payload at the end of its run, conforming to the shape defined in `aidev2-agent-handoff.md`.
- The `handoff` payload shall include: `stage`, `status` (pass | blocked | fail), `summary`, `implementation_id`, `requirement_ids`, `step_tokens`, `artifacts_written`, `checks`, `blockers`, and `next_inputs`.
- The dispatcher shall require a valid `handoff` payload before allowing the pipeline to continue.
- If any specialist returns `status: blocked` or `status: fail`, the dispatcher shall stop immediately and report the blockers to the user — it shall not route to the next specialist.
- The dispatcher shall pass only `requirement_ids`, `step_tokens`, key check results, and required artifact paths to the next stage — it shall not pass full prompt or instruction file content.

#### Acceptance Test — AT-025 Verify handoff enforcement and pipeline gate
- Precondition: A full pipeline run is initiated.
- Steps:
  1. Execute a specialist that should return `status: pass`; verify the dispatcher routes to the next stage.
  2. Simulate a specialist returning `status: blocked`; verify the dispatcher halts and reports blockers.
  3. Verify the dispatcher does not pass full prompt or instruction text between specialists.
  4. Verify the payload passed between stages contains only `requirement_ids`, step tokens, artifact paths, and check summaries.
- Expected:
  - Pipeline continues only on `status: pass`.
  - Pipeline halts immediately on `status: blocked` or `status: fail`.
  - No full prompt content is passed between specialists.

---

### REQ-026 Requirement IDs are globally unique within each type across pending and current

#### Acceptance Criteria
- AC-026: Before assigning any new requirement ID, the authoring agent shall scan all relevant files for the type being authored across both `01-requirements/01-pending-promotion/` and `01-requirements/03-current/`.
- The new sequence number shall be `max(existing sequence numbers for that type) + 1`. No sequence number may be reused, even if the short-title is different from the existing holder.
- Scan scope per type prefix:
  - `FR`: `functional_requirements.yaml` in pending + current
  - `NFR` / `GLOBAL`: `nfr_and_global_cr.yaml` in pending + current
  - `TS`: `technology_selection.yaml` in pending + current
  - `MAC`: `models_and_contracts.yaml` in pending + current
  - `UIC`: `models_and_contracts/ui_contracts.yaml` (and any other spec file) in pending + current
  - `AC` / `AT`: all `functional_requirements.yaml` and `nfr_and_global_cr.yaml` in pending + current
- This rule applies to every authoring operation regardless of run context.

#### Acceptance Test — AT-026 Verify global ID uniqueness enforcement
- Precondition: Blueprint contains requirements in both pending and current with known max sequence numbers per type.
- Steps:
  1. Invoke requirements authoring for a new FR item.
  2. Verify the authoring agent scanned both pending and current FR files before assigning the ID.
  3. Verify the assigned sequence number is exactly `max(all existing FR sequences) + 1`.
  4. Attempt to author a second FR item and verify it receives a different sequence number.
  5. Verify no two authored items share the same sequence number within the same type.
- Expected:
  - New IDs are always one greater than the global maximum for their type.
  - No ID collisions appear in pending or current after authoring.

---

### REQ-027 Per-implementation NFR and TS files are canonical; no flat aggregate files exist

#### Acceptance Criteria
- AC-027: `nfr-and-global-cr` and `technology-selection` requirements shall reside exclusively in per-implementation-id files inside their respective type folders, under both `01-requirements/01-pending-promotion/` and `01-requirements/03-current/`.
- The pending folder structure shall be `01-requirements/01-pending-promotion/nfr-and-global-cr/<nfr_and_global_cr_<implementation_id>.yaml>` and `01-requirements/01-pending-promotion/technology-selection/technology_selection_<implementation_id>.yaml`.
- The current folder structure shall be `01-requirements/03-current/nfr-and-global-cr/nfr_and_global_cr_<implementation_id>.yaml` and `01-requirements/03-current/technology-selection/technology_selection_<implementation_id>.yaml`.
- No flat `nfr_and_global_cr.yaml` or `technology_selection.yaml` file shall exist at the `01-pending-promotion/` or `03-current/` directory level.
- These per-implementation files are the sole authoritative source; they are never treated as derived outputs or mirrors.
- After promote, the current folder shall contain an updated per-implementation file for each promoted pending file.

#### Acceptance Test — AT-027 Verify per-impl-id folder structure and absence of flat files
- Precondition: Setup has run with `--core-stack go` and promote has been executed.
- Steps:
  1. Verify `01-requirements/01-pending-promotion/nfr-and-global-cr/` directory exists.
  2. Verify `01-requirements/01-pending-promotion/technology-selection/` directory exists.
  3. Verify NO `nfr_and_global_cr.yaml` file exists at the `01-pending-promotion/` level.
  4. Verify NO `technology_selection.yaml` file exists at the `01-pending-promotion/` level.
  5. After promote: verify `01-requirements/03-current/nfr-and-global-cr/nfr_and_global_cr_<implementation_id>.yaml` exists.
  6. After promote: verify `01-requirements/03-current/technology-selection/technology_selection_<implementation_id>.yaml` exists.
  7. Verify NO `nfr_and_global_cr.yaml` or `technology_selection.yaml` flat file exists at the `03-current/` level.
- Expected:
  - Both type folders exist in pending-promotion and current.
  - All NFR and TS data is in per-implementation-id files inside the folders.
  - No flat aggregate files exist at any level.

---

### REQ-028 Contract references use `contract_type: models_and_contracts` with MAC ID object form only

#### Acceptance Criteria
- AC-028: All `contract_refs` entries on FR, NFR, and GLOBAL requirements shall use `contract_type: models_and_contracts`. The type `contract_type: ui_contracts` is not a valid value and shall never appear.
- Contracts shall always be referenced by MAC ID using the object form: `- id: MAC-XXXXXXX-short-title`. Bare strings (e.g. `- MAC-0000001-foo`) are invalid and shall not appear.
- The obsolete field name `sub_mac_ids` shall not be used. The correct field is `child_specifications`.
- For MAC entries wrapping multi-item spec files (e.g., a `ui_contracts.yaml` defining multiple UIC items), the `specific_ids` entry shall include `child_specifications: all` unless the requirement targets specific children, in which case an explicit list `child_specifications: [UIC-XXXXXXX-...]` shall be used.
- Separate `contract_refs` entries for individual UICs are forbidden — all UICs must be consolidated under their parent MAC entry with `child_specifications`.

#### Acceptance Test — AT-028 Verify contract_refs structure in authored requirements
- Precondition: At least one FR requirement with contract references exists in pending or current.
- Steps:
  1. Read all `contract_refs` entries across `functional_requirements.yaml`, `nfr_and_global_cr.yaml` in pending and current.
  2. Verify every `contract_refs` entry uses `contract_type: models_and_contracts`.
  3. Verify every `specific_ids` entry is in object form (`- id: MAC-XXXXXXX-...`), not a bare string.
  4. Verify no entry uses the field name `sub_mac_ids`.
  5. Verify no `contract_refs` entry uses `contract_type: ui_contracts`.
  6. Verify MAC entries wrapping multi-UIC spec files have `child_specifications` set (either `all` or explicit list).
- Expected:
  - All contract_refs use only `contract_type: models_and_contracts`.
  - All specific_ids entries are in object form.
  - `sub_mac_ids` is absent throughout.
  - No isolated UIC-level contract_refs entries exist outside their parent MAC.

---

### REQ-029 MAC catalog entries keep `child_specifications` in sync with their spec files

#### Acceptance Criteria
- AC-029: When a MAC catalog entry in `models_and_contracts.yaml` wraps a spec file that defines multiple items (e.g., `ui_contracts.yaml` containing multiple UIC entries), the MAC catalog entry shall carry a `child_specifications` list that enumerates all child IDs defined in that spec file.
- Whenever a new child item is added to a spec file, the parent MAC catalog entry's `child_specifications` list shall be updated in the same authoring operation.
- The `child_specifications` list on the MAC catalog entry is the authoritative resolution target for `child_specifications: all` in `contract_refs`.
- MAC entries that wrap a single-item spec file (exactly one contract schema) do not require a `child_specifications` list on the catalog entry.

#### Acceptance Test — AT-029 Verify MAC catalog child_specifications sync
- Precondition: A MAC catalog entry wrapping a `ui_contracts.yaml` with multiple UIC items exists.
- Steps:
  1. Read the MAC catalog entry in `models_and_contracts.yaml` and note its `child_specifications` list.
  2. Read the referenced spec file (e.g. `models_and_contracts/ui_contracts.yaml`) and collect all defined UIC IDs.
  3. Verify the MAC catalog `child_specifications` list matches the set of UIC IDs in the spec file exactly (no missing, no extra entries).
  4. Author a new UIC item in the spec file and verify the MAC catalog entry is updated in the same operation.
- Expected:
  - MAC `child_specifications` matches spec file contents at all times.
  - New spec file children are always reflected immediately in the MAC catalog entry.

---

### REQ-030 Blueprint does not contain a github-config folder

#### Acceptance Criteria
- AC-030: The generated blueprint folder (`<app-slug>-ai-blueprint`) shall not contain a `github-config` directory or any subdirectory named `github-config` at any level.
- The setup script shall not create a `github-config` folder inside the blueprint.
- The blueprint template shall not include a `github-config` folder.

#### Acceptance Test — AT-030 Verify absence of github-config in blueprint
- Precondition: setup script has been run and a blueprint folder exists.
- Steps:
  1. After running setup, check the blueprint folder recursively for any directory named `github-config`.
  2. Check the blueprint template folder for any `github-config` directory.
- Expected:
  - No `github-config` directory exists inside the blueprint folder or the template.

---

### REQ-031 Framework prompt and instruction files contain no technology- or language-specific instructions

#### Acceptance Criteria
- AC-031: Top-level prompt files, agent files, and instruction files under `aidev2-details/` that are part of the framework itself shall contain no technology- or language-specific instructions (e.g. Go-specific module layout rules, JavaScript/TypeScript patterns, Python conventions, specific library APIs or version constraints).
- Technology- and language-specific instructions belong exclusively in preset files: `aidev2-details/preset-requirements/nfr-and-global-cr-by-core-stack/<stack>/`, `aidev2-details/preset-requirements/tech_selections_by-core-stack/<stack>/`, and similar preset locations.
- An instruction or prompt file "belongs to the framework" if it applies to all implementations regardless of technology stack. A preset file scoped to a named technology stack is not a framework file for this requirement.

#### Acceptance Test — AT-031 Verify no technology-specific content in framework instruction files
- Precondition: The user prompts folder is accessible.
- Steps:
  1. List all `.prompt.md`, `.agent.md`, and `.instructions.md` files at the root and under `aidev2-details/` (excluding `aidev2-details/preset-requirements/`).
  2. For each file, search for technology-specific keywords: specific language names (golang, python, typescript, javascript, ruby, rust, java), specific frameworks or libraries (chi, gin, react, angular, express, django, flask), specific runtime commands (go run, go build, gofmt, npm install, pip install, bundle install).
  3. Record any match outside the `preset-requirements/` subtree.
- Expected:
  - No technology-specific keywords appear in framework prompt, agent, or instruction files.
  - All technology- or stack-specific content is confined to preset files.

---

### REQ-032 Framework-predetermined folder names use only dashes (no underscores)

#### Acceptance Criteria
- AC-032: All folder names that are predetermined by the framework (i.e. created by setup and referenced in tooling) shall use only dashes — no underscores.
- The canonical folder names for the grouped requirement types shall be `nfr-and-global-cr/` and `technology-selection/` (not `nfr_and_global_cr/` or `technology_selection/`).
- These folder names shall be consistent under both `01-requirements/01-pending-promotion/` and `01-requirements/03-current/`.
- Diff bucket directories for these types shall be `02-diff/nfr-and-global-cr/` and `02-diff/technology-selection/`.
- Preset folder names under `aidev2-details/preset-requirements/` shall also follow this convention: `nfr-and-global-cr-by-core-stack/` (not `nfr_and_global_cr_by_core_stack/`).

#### Acceptance Test — AT-032 Verify dash-only folder names in blueprint and preset areas
- Precondition: Setup has run with `--core-stack go`.
- Steps:
  1. Verify `01-requirements/01-pending-promotion/nfr-and-global-cr/` exists (with dashes).
  2. Verify `01-requirements/01-pending-promotion/technology-selection/` exists (with dashes).
  3. Verify `01-requirements/03-current/nfr-and-global-cr/` exists (with dashes).
  4. Verify `01-requirements/03-current/technology-selection/` exists (with dashes).
  5. Verify no `nfr_and_global_cr/` or `technology_selection/` folder exists at any level in the blueprint.
  6. Verify preset folder `aidev2-details/preset-requirements/nfr-and-global-cr-by-core-stack/` exists (with dashes).
- Expected:
  - All grouped-type subdirectories use dashes only.
  - No underscore variants exist in the blueprint or preset areas.

---

### REQ-033 Requirements state file resides at `.aidev/requirements/requirements-state.yaml` in the app repo

#### Acceptance Criteria
- AC-033: The implementation manifest (requirements state file) shall be located at `.aidev/requirements/requirements-state.yaml` relative to `APP_ROOT`.
- The setup script shall create this file at that path when creating a new app repo or adding a new implementation.
- All framework tooling, blueprint instructions, and config templates shall reference this path — not `manifests/requirements-manifest.yaml` or any other location.
- The `manifest_path` field in `.instructions/config.yaml` shall default to `../<APP_REPO_DIR>/.aidev/requirements/requirements-state.yaml`.

#### Acceptance Test — AT-033 Verify requirements state file location
- Precondition: Setup has been run to create an app repo.
- Steps:
  1. After running setup, verify `.aidev/requirements/requirements-state.yaml` exists at `APP_ROOT`.
  2. Verify `manifests/requirements-manifest.yaml` does NOT exist at `APP_ROOT`.
  3. Read `.instructions/config.yaml` and verify `manifest_path` references `.aidev/requirements/requirements-state.yaml`.
  4. In `--add-impl` mode, run setup and verify the new app repo also creates the file at the correct location.
- Expected:
  - Requirements state file exists at `.aidev/requirements/requirements-state.yaml`.
  - Legacy `manifests/requirements-manifest.yaml` path is absent.
  - Config template reflects the correct path.

---

### REQ-034 Requirements authoring is design-first; models, contracts, and updates are supported

#### Acceptance Criteria
- AC-034: When authoring requirements, the framework shall follow a design-first approach: models, data contracts, API contracts, and UI contracts (MAC items) shall be defined or updated before or alongside the functional requirements that reference them.
- The requirements authoring step shall support explicit user requests to author or update models and contracts (MAC entries, UI contracts, API contracts, data schemas) as a first-class operation — not secondary to FR authoring.
- When a user requests changes to models or contracts, the authoring agent shall: (1) locate or create the relevant MAC catalog entry in `models_and_contracts.yaml`; (2) create or update the referenced spec file under `models_and_contracts/`; (3) sync `child_specifications` on the MAC catalog entry; and (4) update or create any FRs that reference those contracts.
- Models and contracts can be authored in isolation (without accompanying FRs) when the user requests it.
- The authoring step narration shall indicate when design artifacts (contracts, models) are being authored before functional requirements.

#### Acceptance Test — AT-034 Verify design-first authoring and models/contracts support
- Precondition: Blueprint with empty pending-promotion folder is available.
- Steps:
  1. Request authoring of a data contract without any accompanying FR.
  2. Verify the MAC catalog entry is created in `01-requirements/01-pending-promotion/models_and_contracts.yaml`.
  3. Verify the spec file is created under `01-requirements/01-pending-promotion/models_and_contracts/`.
  4. Request authoring of an FR that references that contract.
  5. Verify the FR uses `contract_type: models_and_contracts` with the correct MAC ID.
  6. Request an update to the contract (add a field); verify the spec file is updated and the MAC catalog entry's `child_specifications` is kept in sync.
- Expected:
  - MAC catalog entry and spec file are created on contract-only authoring requests.
  - FRs referencing contracts use correct contract_refs structure.
  - Contract updates are reflected in both the spec file and the MAC catalog entry.

---

### REQ-035 Physical database schema updates produce a full schema file and a companion migration file

#### Acceptance Criteria
- AC-035: When a database physical schema contract (MAC with `physical_database_schema` type) is created or updated, the implementation step shall produce two files:
  1. The full resulting schema file — containing the complete database schema as it should exist after the change.
  2. A companion migration file — named with the same base name as the schema file but with a `-migration` suffix (e.g. if the schema file is `user-account-schema.sql`, the migration file is `user-account-schema-migration.sql`). The migration file shall contain the scripts needed to migrate an existing database to the new schema.
- Both files shall be written under the contract spec path (relative to `APP_ROOT` or the designated schema output directory as configured).
- The migration file shall be usable as a deployment artifact — it should be runnable against the previous version of the schema to produce the new schema state.
- The framework shall not consider a DB schema change complete until both files exist.

#### Acceptance Test — AT-035 Verify DB schema full-schema and migration file generation
- Precondition: A blueprint with a pending physical_database_schema MAC change is available.
- Steps:
  1. Run the implementation step for a diff entry containing a `physical_database_schema` contract update.
  2. Verify the full resulting schema file is created at the expected output path.
  3. Verify a companion `-migration` suffixed file exists at the same directory with the same base name.
  4. Open the migration file and verify it contains valid migration statements (ALTER TABLE, CREATE TABLE, etc.) to transition from the previous schema to the new one.
  5. Attempt to close the run without both files present; verify the framework blocks completion.
- Expected:
  - Both schema file and migration file are created before the run is closed.
  - Migration file name follows `<schema-base-name>-migration.<ext>` pattern.
  - Migration file contains runnable migration statements.

---

### REQ-036 YAML output uses consistent formatting

#### Acceptance Criteria
- AC-036: All YAML files written by the framework (agent output and Python tooling) shall use 2-space indentation and block mapping style. Tab characters shall never appear in YAML output.

#### Acceptance Tests
- AT-036:
  1. Run a full pipeline that writes at least one requirement YAML, one manifest YAML, and one plan YAML.
  2. For each written file, verify indentation uses exactly 2 spaces per level (no tabs, no 4-space).
  3. Verify `yaml.safe_dump` / `yaml.dump` calls in Python tooling pass `indent=2, default_flow_style=False`.
  4. Verify `.editorconfig` exists at the prompts root and in the blueprint template with `indent_style = space` and `indent_size = 2` for `*.yaml` / `*.yml`.
- Expected:
  - No YAML file contains tab indentation.
  - All YAML files use 2-space block style.
  - `.editorconfig` files are present and correctly configured.

---

---

## Framework Testing Findings — fakebank-omb-bff-web-ai-blueprint Run

_Date: 2025-07-14_
_Blueprint: fakebank-omb-bff-web-ai-blueprint_
_Implementation: fakebank-omb-bff-web-go_

### Issues Found and Fixed

#### FINDING-001: Deployed tooling `MANIFEST_REL_PATH` stale (REQ-033 violation)
- **Symptom**: `common.py` in `framework-ai-development-tooling/` used `manifests/requirements-manifest.yaml` instead of `.aidev/requirements/requirements-state.yaml`.
- **Root Cause**: Deployed tooling was out of sync with the template version under `aidev2-details/initial-folder-structure/`.
- **Fix**: Updated `MANIFEST_REL_PATH` in `framework-ai-development-tooling/common.py` to `".aidev/requirements/requirements-state.yaml"`.
- **REQ Impact**: REQ-033 (requirements state file path) was already correct in the requirements doc; the tooling simply hadn't been updated.

#### FINDING-002: `CHANGES_REL_PATH` pointed to wrong file
- **Symptom**: `common.py` set `CHANGES_REL_PATH = f"{PENDING_PROMOTION_DIR}/_control.yaml"` which resolved to `01-requirements/01-pending-promotion/_control.yaml`. The actual file is `control.yaml` at blueprint root.
- **Root Cause**: Path was never updated when the control file location changed.
- **Fix**: Changed `CHANGES_REL_PATH` to `"control.yaml"`.

#### FINDING-003: Promote script did not handle per-implementation grouped files (REQ-027 violation)
- **Symptom**: Running promote on a blueprint with per-implementation NFR and TS files (in `nfr-and-global-cr/` and `technology-selection/` subfolders under pending-promotion) caused errors because the script expected flat files only.
- **Root Cause**: `promote_changes.py` only handled flat YAML files at the pending-promotion level; it had no logic for grouped subdirectories.
- **Fix**: (a) Added `GROUPED_REQUIREMENT_REL_DIRS` mapping in `common.py`. (b) Added helper functions `is_grouped_pending_file`, `grouped_current_target_path`, `iter_grouped_current_files`. (c) Updated `promote_changes.py` main loop to detect grouped files and copy them to corresponding current subfolders. (d) Updated `rebuild_requirement_diffs` to include items from per-implementation grouped folders.

#### FINDING-004: Missing `nfr_and_global_cr` in `DIFF_BUCKETS_BY_ARTIFACT_TYPE`
- **Symptom**: After promote, the structured diff generation skipped NFR/Global CR items because no diff bucket was mapped for that type.
- **Fix**: Added `"nfr_and_global_cr": "nfr-and-global-cr"` to `DIFF_BUCKETS_BY_ARTIFACT_TYPE` in `common.py`.

#### FINDING-005: `.sql` extension missing from `promote_contract_spec_files`
- **Symptom**: SQL schema spec files (`.sql`) under `models_and_contracts/` were not being promoted to current because the extension was not in the allowed list.
- **Fix**: Added `.sql` (along with `.prisma` and `.graphql`) to the extension list in `promote_contract_spec_files`.

#### FINDING-006: `generate_merged` did not include per-implementation grouped files (REQ-007 violation)
- **Symptom**: The merged requirements file only contained functional_requirements and models_and_contracts but omitted NFR/Global CR and technology selection items.
- **Fix**: Updated `generate_merged` in `common.py` to iterate grouped current folders and include their items in the merged output, preserving all fields including `module`.

#### FINDING-007: YAML parse errors from unquoted JSON in list items
- **Symptom**: Both `functional_requirements.yaml` and NFR file had list items containing `{key: value}` syntax that YAML parsed as inline mappings instead of strings.
- **Root Cause**: Requirement authoring did not quote list items containing curly braces.
- **Fix**: Quoted the affected list items with double quotes.
- **New Guidance**: Authoring agents should ensure that list item strings containing `{` or `}` are always quoted.

#### FINDING-008: `iter_pending_promotion_doc_paths` included `.gitkeep` files
- **Symptom**: The promote script tried to process `.gitkeep` placeholder files as YAML documents, causing parse errors.
- **Fix**: Added a skip condition for `.gitkeep` files in `iter_pending_promotion_doc_paths`.

### New Requirement Candidates

Based on findings above, the following gaps are not covered by existing REQs:

1. **Tooling sync with template**: Deployed tooling under `framework-ai-development-tooling/` shall match the template version under `aidev2-details/initial-folder-structure/framework-ai-development-tooling/`. There is currently no REQ enforcing this.
2. **YAML authoring safety for list items**: Authoring agents shall quote any list item string that contains `{` or `}` to prevent YAML parser misinterpretation. No existing REQ covers YAML authoring safety.
3. **Promote script grouped file support**: REQ-027 defines the folder structure but does not explicitly require the promote tooling to handle grouped subdirectories. The requirement could be strengthened.

---

### REQ-037 Subagent timing narration with task start/end and elapsed time

#### Acceptance Criteria
- AC-037: Every specialist agent (requirements, planning, implementation, validation, testing) shall emit a task-start narration line with an ISO-8601 timestamp at the beginning of its run and a task-end narration line with an ISO-8601 timestamp and elapsed time at the end.
- The narration format shall be: `[<stage>] Task started at <ISO-8601>` and `[<stage>] Task completed at <ISO-8601> (elapsed: <N>s)`.
- The handoff payload returned by every specialist shall include a `timing` block containing `started_at`, `ended_at`, and `elapsed_seconds`.

#### Acceptance Test — AT-037 Verify subagent timing narration
- Precondition: A full pipeline or single-specialist run is executed in a controlled session.
- Steps:
  1. Execute the pipeline against a known input set.
  2. Capture all output emitted by each specialist.
  3. For each specialist that ran, verify a task-start line with an ISO-8601 timestamp appears at the beginning of its output.
  4. Verify a task-end line with an ISO-8601 timestamp and elapsed time in seconds appears at the end.
  5. Parse the returned handoff payload and verify `timing.started_at`, `timing.ended_at`, and `timing.elapsed_seconds` are present and consistent with the narrated lines.
- Expected:
  - Every specialist emits task-start and task-end narration lines.
  - Handoff `timing` block is populated with valid values.

---

### REQ-038 Script lifecycle narration for every terminal command

#### Acceptance Criteria
- AC-038: Every terminal command or script invocation executed by any specialist or step shall be narrated with a start line before execution and an end line after execution.
- The start format shall be: `[<step>] Script start: <command-summary>`.
- The end format shall be: `[<step>] Script end: <command-summary> (exit: <code>, elapsed: <N>s)`.
- Script invocations shall be recorded in the handoff `timing.script_invocations[]` array with `command_summary`, `started_at`, `ended_at`, `elapsed_seconds`, and `exit_code`.

#### Acceptance Test — AT-038 Verify script lifecycle narration
- Precondition: A pipeline run that includes at least one terminal command (e.g. diff, promote, test run) is executed.
- Steps:
  1. Execute the pipeline against a known input set.
  2. Identify all terminal commands invoked during the run.
  3. For each command, verify a script-start narration line appears before execution.
  4. Verify a script-end narration line with exit code and elapsed time appears after execution.
  5. Parse the handoff payload and verify `timing.script_invocations[]` contains a matching entry for each command.
- Expected:
  - Every terminal command has matching start and end narration lines.
  - `timing.script_invocations[]` is populated with valid entries.

---

### REQ-039 Error narration for all failures with step token and context

#### Acceptance Criteria
- AC-039: Every error encountered during any specialist run — tool failures, script non-zero exits, validation failures, blocked handoffs — shall be narrated immediately with the step token and enough context to diagnose.
- The error format shall be: `[<step>] ERROR: <concise description of what failed and why>`.
- All errors shall be recorded in the handoff `errors[]` array with `step`, `message`, `severity` (error or warning), and `was_unexpected` (true or false).
- `errors` may be an empty list when no errors occurred.

#### Acceptance Test — AT-039 Verify error narration
- Precondition: A pipeline run encounters at least one error (intentionally injected or natural).
- Steps:
  1. Execute the pipeline with a known error condition (e.g. missing file, invalid YAML).
  2. Verify an error narration line appears immediately after the failure.
  3. Verify the narration includes the step token (e.g. `IM-04`, `RQ-01`).
  4. Parse the handoff payload and verify `errors[]` contains a matching entry.
  5. Verify `severity` and `was_unexpected` are set correctly.
- Expected:
  - Every error has a corresponding narration line with step token.
  - Handoff `errors[]` is populated with valid entries.

---

### REQ-040 Unexpected issues narrated in bold

#### Acceptance Criteria
- AC-040: Unplanned errors — crashes, missing files not anticipated by the plan, schema mismatches, tool timeouts, retries, and fallback paths — shall be narrated in **bold** Markdown formatting.
- The format shall be: `[<step>] **UNEXPECTED: <description>**`.
- In the handoff `errors[]` entry, `was_unexpected` shall be set to `true` for these errors.
- Known validation failures (e.g. diff not clear, manifest shape mismatch at a gate) are not unexpected and shall use the standard `ERROR` format without bold.

#### Acceptance Test — AT-040 Verify bold unexpected issue narration
- Precondition: A pipeline run encounters an unplanned error (e.g. tool timeout, missing file not in plan).
- Steps:
  1. Execute the pipeline with a condition that triggers an unexpected error.
  2. Verify the narration line for that error uses **bold** Markdown: `**UNEXPECTED: ...**`.
  3. Verify that known validation failures in the same run are NOT rendered in bold.
  4. Parse the handoff payload and verify the unexpected error has `was_unexpected: true` and the known failure has `was_unexpected: false`.
- Expected:
  - Unexpected issues are in **bold**; known failures are not.
  - Handoff `was_unexpected` flags are correct.

---

### REQ-041 Dispatcher emits pipeline summary table after final specialist

#### Acceptance Criteria
- AC-041: After the final specialist completes (or on early termination due to blocked/fail), the dispatcher shall emit a pipeline summary table.
- The table shall include columns: Stage, Status, Elapsed, Errors, Unexpected.
- Each row shall be derived from the `timing` and `errors` fields of the corresponding handoff payload.
- Skipped stages (due to `from-*` overrides) shall appear with status `skipped` and `0s` elapsed.
- A TOTAL row shall sum elapsed time, error count, and unexpected count across all stages.

#### Acceptance Test — AT-041 Verify pipeline summary table
- Precondition: A full pipeline run (or partial with `from-*` override) is executed.
- Steps:
  1. Execute the pipeline against a known input set.
  2. Capture the final output from the dispatcher.
  3. Verify a pipeline summary table is emitted after the last specialist.
  4. Verify the table contains one row per stage that ran, plus any skipped stages.
  5. Verify elapsed times, error counts, and unexpected counts match the individual handoff payloads.
  6. Verify a TOTAL row is present with correct sums.
- Expected:
  - Pipeline summary table is emitted.
  - All values are consistent with individual handoff payloads.
  - TOTAL row sums are correct.

---

### REQ-042 Script-first execution for mechanical pipeline steps

#### Acceptance Criteria
- AC-042: Steps that perform deterministic, mechanical operations — specifically promote (RQ-02), diff (IM-01), merge, apply, and verify-execution — shall be executed by running the corresponding Python tooling script via terminal command rather than having the AI agent parse and manipulate YAML directly.
- The agent's role for these steps is limited to: (1) constructing the correct command, (2) running it, (3) reading the script's stdout/stderr and exit code, (4) reading the output artifact (structured-diff.yaml, control.yaml, etc.) to extract summary counts and IDs for narration and handoff.
- The agent shall NOT read input YAML files (pending-promotion docs, current docs, manifest) solely to replicate logic already implemented in the Python tooling.
- Agents may still read YAML output artifacts after script execution to extract summary data needed for plan construction or handoff population.

#### Acceptance Test — AT-042 Verify script-first execution for mechanical steps
- Precondition: A pipeline run that includes promote and diff steps.
- Steps:
  1. Execute the pipeline and capture agent behavior during RQ-02 (promote) and IM-01 (diff).
  2. Verify the agent invokes `ai-tooling.sh promote` and `ai-tooling.sh diff` via terminal commands.
  3. Verify the agent does NOT read individual pending-promotion YAML files to replicate promote logic.
  4. Verify the agent reads the output artifact (structured-diff.yaml) after the script completes.
  5. Verify the handoff payload contains summary counts derived from the output artifact, not from agent-side YAML parsing.
- Expected:
  - Mechanical steps use script execution, not AI-driven YAML parsing.
  - Agent reads only output artifacts, not input YAML for mechanical steps.

---

### REQ-043 Diff summary script provides structured text output

#### Acceptance Criteria
- AC-043: The Python tooling shall include a `summarize_diff.py` script (invocable via `ai-tooling.sh summarize-diff`) that reads a structured-diff.yaml file and outputs a plain-text summary to stdout.
- The summary shall include: diff metadata (implementation_id, base_version, target_version), counts for created/updated/removed requirements and MAC items, technology selection entry count, and a list of affected requirement IDs.
- For updated entries, if the `module` field changed between old and new, the summary shall flag it as `module_changed`.
- This summary output replaces the need for agents to parse the structured-diff.yaml themselves when they only need counts and IDs.

#### Acceptance Test — AT-043 Verify diff summary script
- Precondition: A structured-diff.yaml file exists for an implementation.
- Steps:
  1. Run `ai-tooling.sh summarize-diff -r <req-path> --implementation-id <id>`.
  2. Capture stdout.
  3. Verify the output contains implementation_id, base_version, target_version.
  4. Verify created/updated/removed counts and ID lists are present.
  5. Verify module_changed flags appear for entries where the module changed.
- Expected:
  - Script exits 0 and produces a structured plain-text summary.
  - All counts and IDs match the structured-diff.yaml content.

---

### REQ-044 Dispatcher pre-warms next specialist context during current specialist execution

#### Acceptance Criteria
- AC-044: When the dispatcher knows the next specialist in the pipeline sequence (e.g., after requirements, the next is planning), it shall include a `prefetch_context` hint in the specialist invocation prompt that lists the instruction files and step files the NEXT specialist will need.
- The dispatcher shall prepare the next specialist's invocation prompt (with all known inputs: implementation_id, requirement_ids, cached_data, instruction file paths) before the current specialist completes, so that upon receiving the current specialist's handoff, it can immediately dispatch the next specialist without re-reading instructions or re-discovering paths.
- The dispatcher shall maintain a `pipeline_context` accumulator that grows with each handoff's `cached_data`, avoiding redundant re-reads across the entire pipeline.
- Pre-built prompts for specialists that are skipped (via `from-*` overrides) shall be discarded without execution.

#### Acceptance Test — AT-044 Verify dispatcher pre-warms next specialist
- Precondition: A full pipeline run is executed.
- Steps:
  1. Execute the full pipeline and observe dispatcher behavior between specialist invocations.
  2. Verify the dispatcher maintains a `pipeline_context` accumulator across stages.
  3. Verify the dispatcher includes `cached_data` from the previous handoff in the next specialist's invocation.
  4. Verify no specialist re-reads YAML files that were already parsed and forwarded via `cached_data`.
  5. Verify that skipped stages do not trigger unnecessary file reads.
- Expected:
  - Each specialist receives `cached_data` from all prior stages.
  - No redundant YAML file reads occur across the pipeline.

---

### REQ-045 Agents shall not read YAML for data already available in script output or cached_data

#### Acceptance Criteria
- AC-045: When a pipeline step produces structured output (script stdout, output YAML artifact), agents shall use that output as the source of truth rather than re-reading the input YAML files.
- When `cached_data` from a prior handoff contains information needed by the current stage (e.g., requirement IDs, standing constraints, config paths), the agent shall consume it from `cached_data` rather than re-reading files.
- Agents shall not read `01-requirements/03-current/` YAML files during the planning or implementation stage if the structured diff already contains the full requirement snapshots needed.
- The only exception is when the agent needs data not present in the diff or cached_data (e.g., reading a specific source code file for implementation).

#### Acceptance Test — AT-045 Verify agents avoid redundant YAML reads
- Precondition: A pipeline run that passes through planning and implementation stages.
- Steps:
  1. Execute the pipeline with cached_data flowing from requirements → planning → implementation.
  2. Monitor file read operations during the planning stage.
  3. Verify the planning agent uses structured-diff.yaml (script output) for requirement data, not raw current YAML.
  4. Verify the implementation agent uses plan.yaml and cached_data, not re-reading current requirements.
  5. Verify any read of current YAML is for data not available in diff or cached_data (document the reason).
- Expected:
  - No redundant reads of current requirement YAML during planning or implementation.
  - cached_data is consumed before falling back to file reads.

---

### REQ-046 Pipeline activity log file

#### Acceptance Criteria
- AC-046: Every pipeline run (full or partial) shall produce a plain-text log file named `YYYY-MM-DD-HH-MM-SS-aidev2.log` where the timestamp is the ISO-8601-safe datetime (no colons, no dots) of the pipeline start.
- The log file shall be written to `BLUEPRINT_ROOT/10-logs/`. The directory shall be created if it does not exist.
- The dispatcher shall create the log file at pipeline start and pass the absolute path (`LOG_FILE`) to every specialist in `pipeline_context`.
- Every specialist (agent and subagent) shall append entries to `LOG_FILE` throughout execution. Logged entries must include:
  - Stage start/end with timestamps and elapsed time
  - Every narration line emitted (task lifecycle, script lifecycle, per-requirement progress)
  - Every tool call description (file reads, file writes, searches, terminal commands) with timestamps
  - Every error and unexpected issue with full context
  - Decision reasoning and thinking summaries — when the agent decides what to do and why, log the rationale
  - Script invocations with command, exit code, elapsed time, and stdout/stderr summary (first and last 20 lines if output exceeds 40 lines)
  - Handoff payload summary (stage, status, counts, errors count) at stage end
- Log entries shall be timestamped with `[YYYY-MM-DD HH:MM:SS]` prefix and tagged with the stage name: `[2026-04-14 09:15:32][requirements]`.
- The log shall be append-only during the pipeline run. No agent may truncate or overwrite prior entries.
- At pipeline end, the dispatcher shall append the pipeline summary table to the log file.
- The log file path shall be included in the final handoff under `artifacts_written`.

#### Acceptance Test — AT-046 Verify pipeline activity log
- Precondition: A full pipeline run completes (pass or fail).
- Steps:
  1. Verify `BLUEPRINT_ROOT/10-logs/` contains a file matching `????-??-??-??-??-??-aidev2.log`.
  2. Verify the first line contains `[PIPELINE START]` with a timestamp.
  3. Verify each stage has `STAGE START` and `STAGE END` entries with matching stage names.
  4. Verify at least one script invocation entry exists with command, exit code, and elapsed time.
  5. Verify at least one thinking/decision entry exists (tagged `[thinking]` or `[decision]`).
  6. Verify errors (if any) appear with `[ERROR]` or `[UNEXPECTED]` tags.
  7. Verify the last section contains the pipeline summary table.
  8. Verify the log file path appears in the final handoff's `artifacts_written`.
  9. Verify all timestamps are monotonically non-decreasing.
- Expected:
  - A single contiguous log file captures the full pipeline activity.
  - All agent and subagent actions are traceable in the log.

---

### REQ-047 YAML repair utility in framework tooling

#### Acceptance Criteria
- AC-047a: The framework tooling shall include a `repair_yaml.py` script invocable via `ai-tooling.sh repair-yaml`.
- AC-047b: The script shall accept a path argument (file or directory). When given a directory, it shall recursively process all `.yaml` and `.yml` files.
- AC-047c: The script shall fix the following issues in-place: (1) replace tab indentation with 2-space indentation, (2) normalize inconsistent indentation to 2-space block style, (3) strip trailing whitespace from lines, (4) ensure the file ends with a single newline.
- AC-047d: The script shall validate that each repaired file is parseable YAML. If a file cannot be parsed after repair, it shall report the error and leave the original file unchanged.
- AC-047e: The script shall print a summary of files processed, files repaired, and files that could not be repaired.
- AC-047f: The `ai-tooling.sh` shell wrapper shall include a `repair-yaml` action that routes to `repair_yaml.py`.

#### Acceptance Test — AT-047 Verify YAML repair utility
- Steps:
  1. Create a YAML file with tab indentation and inconsistent spacing.
  2. Run `ai-tooling.sh repair-yaml <file>`.
  3. Verify the file now uses 2-space indentation with no tabs.
  4. Verify the file is valid YAML.
  5. Run against a directory and verify all `.yaml`/`.yml` files are processed.
  6. Verify unparseable files are reported and left unchanged.
- Expected:
  - Tab indentation is replaced with 2-space indentation.
  - All output files are valid YAML.
  - Summary is printed to stdout.

---

### REQ-048 Requirements state schema file exists in framework

#### Acceptance Criteria
- AC-048a: The framework schemas directory (`aidev2-details/aidev2-schemas/in-application/`) shall contain a file named `requirements-state-schema.json` that defines the JSON Schema for `.aidev/requirements/requirements-state.yaml`.
- AC-048b: The schema shall validate the actual structure produced by `apply_delta_to_app.py`: `manifest_version`, `requirement_set_id`, `app_identifier`, `implementation_id`, `iteration_id`, `requirements_version_target`, `requirements_version_implemented`, and `requirement_baseline` (array of objects with `requirement_id` and `pinned_version`).
- AC-048c: The schema title shall be "Requirements State" (not "manifest"). The description shall reference `.aidev/requirements/requirements-state.yaml`.
- AC-048d: The older `application_requirements_manifest.json` schema in the same directory is superseded by this file. Both may coexist during transition, but `requirements-state-schema.json` is canonical.

#### Acceptance Test — AT-048 Verify requirements state schema
- Steps:
  1. Verify `aidev2-details/aidev2-schemas/in-application/requirements-state-schema.json` exists.
  2. Validate the schema against a known-good `requirements-state.yaml` file.
  3. Verify the schema title is "Requirements State".
  4. Verify required fields match what `apply_delta_to_app.py` writes.
- Expected:
  - Schema file exists and validates real requirements-state.yaml files.
  - Title uses "Requirements State" terminology, not "manifest".

---

### REQ-049 Framework YAML writers always produce valid 2-space indented YAML without tabs

#### Acceptance Criteria
- AC-049a: All Python tooling that writes YAML shall use `yaml.safe_dump` with `indent=2, default_flow_style=False, sort_keys=False, allow_unicode=True`.
- AC-049b: All agent-generated YAML content shall use 2-space indentation, block mapping style, and no tab characters. Agent instructions shall specify this as a hard constraint.
- AC-049c: Before any promote or diff operation, the tooling shall validate that input YAML files are parseable. If a file contains tabs or is unparseable, the `repair-yaml` utility (REQ-047) shall be invoked automatically before proceeding.
- AC-049d: `.editorconfig` in both the prompts root and in blueprint templates shall enforce `indent_style = space` and `indent_size = 2` for `*.yaml` and `*.yml` files.

#### Acceptance Test — AT-049 Verify YAML output consistency
- Steps:
  1. Run a full pipeline that writes YAML files (promote, diff, apply).
  2. Check every written YAML file for tab characters — none shall be present.
  3. Verify indentation is consistently 2-space.
  4. Verify `yaml.safe_dump` calls in Python tooling use `indent=2, default_flow_style=False`.
- Expected:
  - No YAML file contains tabs.
  - All YAML files use 2-space block style.

---

### REQ-050 Every script-invoking step shall include the exact command template with all required flags

#### Acceptance Criteria
- AC-050a: Every step file (`aidev2-steps/**/*.md`) that invokes a Python tooling script shall include a literal command template in the `Action:` line showing the full command with all required flags and variable placeholders (e.g. `"$TOOLING_CMD" promote -r "$REQ_PATH" -a "$APP_ROOT" --implementation-id "$IMPLEMENTATION_ID"`).
- AC-050b: The agent shall use the command template verbatim — substituting only the variable values discovered during IM-00 / RQ-01. The agent shall not attempt to invoke a tooling command without all required flags.
- AC-050c: The required flag set for each tooling action is: `-r`/`--requirements-path` (always required), `-a`/`--app-path` (required when the script needs the app repo), `--implementation-id` (required when the script targets a specific implementation). The step file's `Inputs:` line shall list exactly which variables the command needs.
- AC-050d: If a variable required by the command template is not yet resolved, the agent shall stop and report the missing variable as a blocker rather than invoking the script without it.

#### Acceptance Test — AT-050 Verify all step files have exact command templates
- Steps:
  1. For each step file under `aidev2-steps/` that references `ai-tooling.sh` or `$TOOLING_CMD`:
     a. Verify an `Action:` line exists with the full command including `-r`, `-a` (if needed), and `--implementation-id` (if needed).
     b. Verify the `Inputs:` line lists all variables used in the command template.
  2. Run a pipeline and verify the agent does not invoke any tooling command without the required flags.
  3. Verify no script invocation fails with "missing required argument" errors.
- Expected:
  - Every script-invoking step has an unambiguous command template.
  - No "missing -r/--requirements-path" or similar errors occur.

---

### REQ-051 Python tooling scripts shall produce structured error output on failure

#### Acceptance Criteria
- AC-051a: Every Python tooling script (`promote_changes.py`, `generate_structured_diff.py`, `apply_delta_to_app.py`, `verify_execution_complete.py`, `merge_requirements.py`, `sync_diff_from_current.py`, `summarize_diff.py`, `bootstrap.py`) shall wrap its `main()` body in a try/except that catches all exceptions.
- AC-051b: On any exception, the script shall print a structured error message to stderr in the format: `ERROR [<script_name>]: <error_class>: <message>` and exit with code 1.
- AC-051c: For `ValueError` exceptions from validation functions (`validate_target_for_app`, `resolve_target_implementations`), the error message shall include the specific validation failure (e.g., `requirement_set_id mismatch`, `app_path not found`, `missing control.yaml`) — not just a Python traceback.
- AC-051d: The script shall never print a raw Python traceback to stdout. Tracebacks may appear on stderr only when a `--debug` flag is passed.
- AC-051e: The structured error output shall be parseable by agents for narration and error logging.

#### Acceptance Test — AT-051 Verify tooling scripts produce structured errors
- Steps:
  1. Invoke `promote_changes.py` with a valid `-r` but pointing to a directory with no `control.yaml` — verify stderr contains `ERROR [promote_changes]: FileNotFoundError: ...` and exit code is 1.
  2. Invoke `promote_changes.py` with valid `-r` and `-a` pointing to a mismatched app — verify stderr contains `ERROR [promote_changes]: ValueError: requirement_set_id mismatch ...`.
  3. Invoke `generate_structured_diff.py` with a non-existent `--implementation-id` — verify stderr contains `ERROR [generate_structured_diff]: ValueError: implementation_id not found ...`.
  4. Verify no raw Python traceback appears on stdout for any failure case.
- Expected:
  - Every failure produces a single structured error line on stderr.
  - Exit code is always 1 for errors, 0 for success.

---

### REQ-055 Pipeline log first entry includes AI model and version

#### Acceptance Criteria
- AC-055a: The first line of the pipeline activity log (`[PIPELINE START]`) shall include a `model=<name and version>` field that identifies the exact AI model and version powering the current session (e.g. `model=Claude Opus 4.6`, `model=GPT-4o 2025-04-14`).
- AC-055b: The model value shall be obtained from the runtime environment or the agent's self-identification — it shall not be hardcoded or guessed.
- AC-055c: The full first-line format shall be: `[<timestamp>][dispatcher] [PIPELINE START] model=<AI model and version> implementation_id=<ID> stages=<list>`.
- AC-055d: If the model identity cannot be determined, the agent shall write `model=unknown` rather than omitting the field.

#### Acceptance Test — AT-055 Verify AI model and version in log first entry
- Precondition: A pipeline run produces a log file under `BLUEPRINT_ROOT/10-logs/`.
- Steps:
  1. Open the log file and read the first line.
  2. Verify the line contains `[PIPELINE START]`.
  3. Verify a `model=` field is present with a non-empty value.
  4. Verify the model value matches the AI model actually used for the session.
  5. Verify the field appears before `implementation_id=`.
- Expected:
  - First log line includes `model=<name and version>` between `[PIPELINE START]` and `implementation_id=`.
  - The value is accurate and non-empty.

---

### REQ-052 Pipeline aborts on unrecoverable stage errors

#### Acceptance Criteria
- AC-052a: The dispatcher shall abort the entire pipeline — no further specialists invoked — when any specialist returns `status: blocked` or `status: fail`.
- AC-052b: The dispatcher shall abort when a specialist invocation completes without returning a parseable `handoff` object. The abort message shall be: `**PIPELINE ABORT: Specialist <stage> did not return a valid handoff payload.**`
- AC-052c: The dispatcher shall abort when a specialist returns a handoff with missing required fields (`stage`, `status`, or `summary`). The abort message shall identify the missing fields.
- AC-052d: The dispatcher shall abort when it encounters an unrecoverable system error (e.g., cannot write to the log file, cannot invoke a subagent).
- AC-052e: On abort, the dispatcher shall: (1) emit `**PIPELINE ABORT: <reason>**` in bold, (2) append the abort reason to the pipeline activity log, (3) emit the pipeline summary table with all completed stages and the aborted stage marked as `abort`, and (4) return a final handoff with `status: fail` and the abort reason in `blockers`.
- AC-052f: The dispatcher shall NOT attempt recovery, retry, or fallback when a stage fails. The only valid action is to abort and report.

#### Acceptance Test — AT-052 Verify pipeline abort on unrecoverable errors
- Precondition: A full pipeline run is initiated.
- Steps:
  1. Simulate a specialist returning `status: fail`; verify the dispatcher halts immediately and does not invoke any further specialists.
  2. Simulate a specialist returning no handoff payload; verify the dispatcher emits `**PIPELINE ABORT: ...**` and stops.
  3. Simulate a specialist returning a handoff with `status` missing; verify the dispatcher aborts with the specific missing-field message.
  4. Verify the pipeline activity log contains the abort reason.
  5. Verify the pipeline summary table is emitted with the aborted stage marked as `abort`.
  6. Verify the final handoff has `status: fail` with the reason in `blockers`.
- Expected:
  - Pipeline terminates immediately on any unrecoverable error.
  - No further specialists are invoked after abort.
  - Abort reason is logged and reported in the summary table and final handoff.

---

### REQ-053 Pipeline aborts when target app folder is missing

#### Acceptance Criteria
- AC-053a: Before invoking the first specialist, the dispatcher shall verify that the resolved `APP_ROOT` directory exists on disk.
- AC-053b: If `APP_ROOT` does not exist, the dispatcher shall abort the pipeline with: `**PIPELINE ABORT: Target app folder not found at <resolved path>. The app repository must exist before the pipeline can run.**`
- AC-053c: If `APP_ROOT` cannot be inferred (no config.yaml value, no sibling match, user not prompted), the dispatcher shall abort with: `**PIPELINE ABORT: Cannot infer APP_ROOT. Provide the app repo path or verify config.yaml.**`
- AC-053d: The dispatcher shall NOT create the app repository directory. Only `.aidev` bootstrap files inside an existing app repo may be auto-created (see REQ-054).
- AC-053e: This check shall run as part of the pre-flight sequence (PF-02) before any specialist is invoked.

#### Acceptance Test — AT-053 Verify pipeline abort when app folder is missing
- Precondition: A blueprint with config.yaml pointing to a non-existent app folder.
- Steps:
  1. Run the full pipeline with an `APP_ROOT` that does not exist on disk.
  2. Verify the dispatcher emits `**PIPELINE ABORT: Target app folder not found at ...**`.
  3. Verify no specialist is invoked.
  4. Verify the pipeline summary table shows all stages as `skipped` and the pre-flight as `abort`.
  5. Verify the pipeline activity log contains the abort entry.
  6. Change config.yaml to a valid app folder and verify the pipeline starts normally.
- Expected:
  - Pipeline aborts before any specialist runs when `APP_ROOT` is missing.
  - Error message includes the resolved path.
  - No app repo directory is created by the dispatcher.

---

### REQ-054 Dispatcher auto-creates missing `.aidev` bootstrap files

#### Acceptance Criteria
- AC-054a: When `APP_ROOT` exists but `APP_ROOT/.aidev/requirements/requirements-state.yaml` does not exist, the dispatcher shall create the file and its parent directories automatically during the pre-flight phase (PF-03).
- AC-054b: The created `requirements-state.yaml` shall contain: `manifest_version: '1.0'`, `requirement_set_id` (from config.yaml or derived), `app_identifier` (from config.yaml or derived), `implementation_id` (from config.yaml or derived), `iteration_id: 1`, `requirements_version_target: 1.0.0`, `requirements_version_implemented: 0.0.0`, and `requirement_baseline: []`.
- AC-054c: The file shall use 2-space YAML indentation, block style, no tabs — consistent with REQ-036 and REQ-049.
- AC-054d: The dispatcher shall never overwrite an existing `requirements-state.yaml`. Bootstrap creation only occurs when the file is absent.
- AC-054e: The creation shall be narrated: `[dispatcher] Created missing bootstrap file: APP_ROOT/.aidev/requirements/requirements-state.yaml`.
- AC-054f: The creation shall be logged in the pipeline activity log.

#### Acceptance Test — AT-054 Verify auto-creation of .aidev bootstrap files
- Precondition: An app repo exists at `APP_ROOT` but contains no `.aidev/` directory.
- Steps:
  1. Run the full pipeline targeting the app repo.
  2. Verify `APP_ROOT/.aidev/requirements/requirements-state.yaml` was created before the first specialist runs.
  3. Verify the file content matches the expected default structure with correct `implementation_id`, `requirement_set_id`, and `app_identifier`.
  4. Verify the file uses 2-space YAML indentation with no tabs.
  5. Verify the dispatcher narration includes the creation message.
  6. Verify the pipeline activity log records the bootstrap creation.
  7. Run the pipeline again and verify the file is NOT overwritten (existing file is preserved).
  8. Verify the pipeline continues normally after bootstrap creation.
- Expected:
  - `.aidev/requirements/requirements-state.yaml` is created with correct defaults when missing.
  - File is never overwritten if it already exists.
  - Pipeline proceeds normally after bootstrap.

---

## Traceability Matrix
- REQ-001 -> AC-001 -> AT-001
- REQ-002 -> AC-002 -> AT-002
- REQ-003 -> AC-003 -> AT-003
- REQ-004 -> AC-004 -> AT-004
- REQ-005 -> AC-005 -> AT-005
- REQ-006 -> AC-006 -> AT-006
- REQ-007 -> AC-007 -> AT-007
- REQ-008 -> AC-008 -> AT-008
- REQ-009 -> AC-009 -> AT-009
- REQ-010 -> AC-010 -> AT-010
- REQ-011 -> AC-011 -> AT-011
- REQ-012 -> AC-012 -> AT-012
- REQ-013 -> AC-013 -> AT-013
- REQ-014 -> AC-014 -> AT-014
- REQ-015 -> AC-015 -> AT-015
- REQ-016 -> AC-016 -> AT-016
- REQ-017 -> AC-017 -> AT-017
- REQ-018 -> AC-018 -> AT-018
- REQ-019 -> AC-019 -> AT-019
- REQ-020 -> AC-020 -> AT-020
- REQ-021 -> AC-021 -> AT-021
- REQ-022 -> AC-022 -> AT-022
- REQ-023 -> AC-023 -> AT-023
- REQ-024 -> AC-024 -> AT-024
- REQ-025 -> AC-025 -> AT-025
- REQ-026 -> AC-026 -> AT-026
- REQ-027 -> AC-027 -> AT-027
- REQ-028 -> AC-028 -> AT-028
- REQ-029 -> AC-029 -> AT-029
- REQ-030 -> AC-030 -> AT-030
- REQ-031 -> AC-031 -> AT-031
- REQ-032 -> AC-032 -> AT-032
- REQ-033 -> AC-033 -> AT-033
- REQ-034 -> AC-034 -> AT-034
- REQ-035 -> AC-035 -> AT-035
- REQ-036 -> AC-036 -> AT-036
- REQ-037 -> AC-037 -> AT-037
- REQ-038 -> AC-038 -> AT-038
- REQ-039 -> AC-039 -> AT-039
- REQ-040 -> AC-040 -> AT-040
- REQ-041 -> AC-041 -> AT-041
- REQ-042 -> AC-042 -> AT-042
- REQ-043 -> AC-043 -> AT-043
- REQ-044 -> AC-044 -> AT-044
- REQ-045 -> AC-045 -> AT-045
- REQ-046 -> AC-046 -> AT-046
- REQ-047 -> AC-047 -> AT-047
- REQ-048 -> AC-048 -> AT-048
- REQ-049 -> AC-049 -> AT-049
- REQ-050 -> AC-050 -> AT-050
- REQ-051 -> AC-051 -> AT-051
- REQ-052 -> AC-052 -> AT-052
- REQ-053 -> AC-053 -> AT-053
- REQ-054 -> AC-054 -> AT-054
- REQ-055 -> AC-055 -> AT-055

## Notes
- This specification is intentionally strict on implementation-id-specific preset files and merged-field parity, including module, to prevent silent schema drift during setup automation.
- AC-010/AT-010 enforce that module-scoped runs are filtered at the diff stage; any tool consuming diffs must expose module filtering rather than passing full unfiltered diff to the implementation step.
- AC-011/AT-011 enforce the `aidev2-NN-` naming convention so slash-command discovery reflects pipeline execution order.
- AC-012/AT-012 enforce that `aidev2-instructions.md` is the sole canonical general instructions file; no other file may duplicate pipeline or process overview content.
- AC-013/AT-013 enforce per-step narration: every side-effecting action must emit a concise status line; silent execution of writes or deletions is not permitted.
- AC-014/AT-014 enforce that preset files are seeded into pending-promotion at setup time, never directly into 03-current; this ensures all requirement changes go through the promote pipeline.
- AC-015/AT-015 enforce that adding a second implementation to a blueprint is a supported operation that leaves existing content intact.
- AC-016/AT-016 enforce prompt efficiency; prompts must not re-explain the pipeline or duplicate shared logic inline.
- AC-017/AT-017 enforce that the optimization strategy (agent routing, communication, gates, read efficiency) is prescribed in aidev2-instructions.md so all agents operate consistently.
- AC-018/AT-018 enforce that e2e tests use Playwright with one test per UIC ID for UI; tests split into `ui/` and `api/` projects with correct fixture types.
- AC-019/AT-019 enforce that no Playwright artifact lands in `06-e2e-tests/`; all outputs must be under `03-test-results/IMPLEMENTATION_ID`.
- AC-020/AT-020 enforce per-state screenshot capture in UI tests; every visited screen state must have a screenshot attached and the HTML report must embed them inline.
- AC-021/AT-021 enforce that the default test run scope is partial (current diff only); full suite requires an explicit user instruction.
- AC-022/AT-022 enforce the test output file naming pattern: ISO-8601 timestamp (no `:` or `.`) + REQ ID + partial/full suffix.
- AC-023/AT-023 enforce module reassignment undo/redo: diff must flag `module_changed`, plan must document both scopes, and both module locations must build after execution.
- AC-024/AT-024 enforce the DB alignment gate: runs touching physical_database_schema cannot be closed without schema verification evidence.
- AC-025/AT-025 enforce the handoff contract: every specialist must return a valid handoff payload; the dispatcher must stop immediately on blocked or fail and must not pass full prompt content between stages.
- AC-026/AT-026 enforce global ID uniqueness within each requirement type: the authoring agent must scan both pending and current before assigning, and use `max + 1` — reuse of any existing sequence number is forbidden.
- AC-027/AT-027 enforce the folder-based structure for NFR and TS: per-implementation-id files inside type folders (`nfr-and-global-cr/`, `technology-selection/`) are the canonical source under both pending-promotion and current; flat aggregate files at those directory levels are forbidden.
- AC-028/AT-028 enforce contract_refs structure: only `contract_type: models_and_contracts`, only MAC ID object form in specific_ids, no sub_mac_ids, no contract_type: ui_contracts, no isolated UIC-level entries.
- AC-029/AT-029 enforce MAC catalog sync: child_specifications on a MAC catalog entry must match its spec file contents at all times; adding a child to a spec file must update the MAC catalog entry in the same operation.
- AC-030/AT-030 enforce that no github-config folder appears inside the generated blueprint; this folder has no role in the blueprint structure.
- AC-031/AT-031 enforce that framework-level prompt, agent, and instruction files are technology-agnostic; any language- or stack-specific rules belong in the preset files under aidev2-details/preset-requirements/.
- AC-032/AT-032 enforce that all framework-predetermined folder names use only dashes: canonical grouped-type folders shall be `nfr-and-global-cr/` and `technology-selection/`; underscore variants are forbidden.
- AC-033/AT-033 enforce that the requirements state file (implementation manifest) is located at `.aidev/requirements/requirements-state.yaml` in the app repo; the legacy `manifests/requirements-manifest.yaml` path is forbidden.
- AC-034/AT-034 enforce design-first authoring: models and contracts are first-class authoring targets; MAC catalog entries and spec files must be created/updated when requested, with or without accompanying FRs.
- AC-035/AT-035 enforce DB schema migration artifacts: every physical_database_schema change must produce both a full resulting schema file and a companion `-migration` file before the run is considered complete.
- AC-037/AT-037 enforce subagent timing narration: every specialist must emit task-start/task-end with ISO-8601 timestamps and elapsed time, and populate `timing` in the handoff payload.
- AC-038/AT-038 enforce script lifecycle narration: every terminal command must have start/end narration with command summary, exit code, elapsed time, and a matching `timing.script_invocations[]` entry.
- AC-039/AT-039 enforce error narration: every error must be narrated immediately with the step token and context, and recorded in the handoff `errors[]` array.
- AC-040/AT-040 enforce bold unexpected issues: unplanned errors must be narrated in **bold** (`**UNEXPECTED: ...**`); known validation failures must not use bold.
- AC-041/AT-041 enforce the dispatcher pipeline summary table: after the final specialist, a table with Stage, Status, Elapsed, Errors, Unexpected columns and a TOTAL row must be emitted.
- AC-042/AT-042 enforce script-first execution for mechanical pipeline steps: promote, diff, merge, apply, and verify-execution steps must run via Python tooling scripts; agents must not parse input YAML to replicate script logic.
- AC-043/AT-043 enforce diff summary script availability: `summarize_diff.py` (via `ai-tooling.sh summarize-diff`) produces a plain-text summary with counts, IDs, and module_changed flags, replacing agent-side structured-diff.yaml parsing.
- AC-044/AT-044 enforce dispatcher pre-warming: the dispatcher must accumulate `pipeline_context` across stages, pre-build next specialist prompts before current specialist completes, and include `cached_data` to prevent redundant file reads.
- AC-045/AT-045 enforce no redundant YAML reads: agents must consume script output and `cached_data` before falling back to file reads; reading current-requirements YAML during planning or implementation is forbidden when the data is available in the structured diff or cached_data.
- AC-046/AT-046 enforce pipeline activity logging: every run must produce a `YYYY-MM-DD-HH-MM-SS-aidev2.log` file in `BLUEPRINT_ROOT/10-logs/` capturing all agent/subagent activity, thinking, tool calls, script invocations, errors, and the pipeline summary table.
- AC-047/AT-047 enforce a YAML repair utility: `ai-tooling.sh repair-yaml` shall fix tab indentation, normalize to 2-space block style, and validate parseability; this prevents the "YAML indentation error in pending-promotion files" runtime fix that previously required manual intervention.
- AC-048/AT-048 enforce that a `requirements-state-schema.json` exists in `aidev2-schemas/in-application/` and uses "Requirements State" terminology rather than "manifest", aligning with REQ-033's established path at `.aidev/requirements/requirements-state.yaml`.
- AC-049/AT-049 enforce that all YAML output — from both Python tooling and AI agents — uses 2-space indentation, block style, and no tabs; input YAML is auto-repaired before promote/diff if it contains tabs or parse errors.
- AC-050/AT-050 enforce that every script-invoking step file contains the exact command template with all required flags (`-r`, `-a`, `--implementation-id`); agents shall never guess which flags to pass.
- AC-051/AT-051 enforce that Python tooling scripts produce structured error messages (`ERROR [<script>]: <class>: <message>`) on stderr instead of raw tracebacks; agents can parse these for narration and logging.
- AC-052/AT-052 enforce pipeline abort semantics: the dispatcher must terminate the entire pipeline on specialist failure (`blocked`/`fail`), missing handoff payload, incomplete handoff fields, or unrecoverable system errors — no recovery, retry, or fallback is permitted.
- AC-053/AT-053 enforce target app folder validation: the dispatcher must verify `APP_ROOT` exists on disk before invoking any specialist; a missing app folder is an unrecoverable abort condition; the dispatcher never creates the app repo directory.
- AC-054/AT-054 enforce auto-bootstrap of `.aidev` files: when `APP_ROOT` exists but `.aidev/requirements/requirements-state.yaml` is absent, the dispatcher creates it with default values during pre-flight; an existing file is never overwritten.
- AC-055/AT-055 enforce that the first pipeline log entry includes the AI model name and version (`model=<value>`), obtained from runtime self-identification; this enables traceability of which model produced a given pipeline run.
