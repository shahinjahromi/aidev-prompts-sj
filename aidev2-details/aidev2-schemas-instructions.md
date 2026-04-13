# Schema Instructions

## Schema Bundle Location

The authoritative schema bundle is at `{{VSCODE_USER_PROMPTS_FOLDER}}/aidev2-details/aidev2-schemas`.
Never read schemas from a blueprint's local `.schemas` folder.

## No `.schemas` in Application Blueprints

Application blueprints must not include a `.schemas` folder. Schemas are maintained exclusively in the aidev2 framework at the user-level schema bundle path above. All schema validation — during authoring, promotion, reconciliation, and implementation — references the framework bundle, never a blueprint-local copy. If a `.schemas` folder is found in an application blueprint, ignore it.

## Preset Requirements Are Blueprint-Only

The preset requirement templates in `aidev2-details/preset-requirements/` (NFR and technology selection files organized by core stack) are source templates only. When seeded during setup, the resulting implementation-specific copies must be written exclusively to the application blueprint's `01-requirements/01-pending-promotion/` folders — never back into the VS Code user prompts folder or the framework's preset-requirements directory. The framework preset folder must contain only the reusable `[implementation-id]` template files.

## File Naming

Schema JSON files use **underscores** in their names (e.g. `functional_requirements.json`, `nfr_and_global_cr.json`).
This matches the YAML `type:` field values they validate against.
Do not rename schema files to use dashes — it would break `$ref` cross-references.

Files prefixed with `_` (e.g. `_ac_definition.json`, `_at_definition.json`) are reusable partial definitions referenced via `$ref` from other schemas.

## Directory Layout

```
aidev2-schemas/
  functional_requirements.json    # FR items
  nfr_and_global_cr.json          # NFR and GLOBAL items
  technology_selection.json       # TS items
  requirements_manifest.json      # Diff/promote manifest envelope
  _ac_definition.json             # Partial: acceptance criteria
  _at_definition.json             # Partial: acceptance tests
  contracts/
    models_and_contracts.json     # MAC catalog entries (current)
    contracts_and_models.json     # DEPRECATED v1 — do not use for new work
    domain_model.json             # Domain model spec
    openapi_yaml.json             # OpenAPI spec
    graphql_sdl_yaml.json         # GraphQL SDL spec
    physical_database_schema.json # DB schema spec
    logical_database_schema.json  # Logical DB schema spec
    ui_contracts.json             # UIC spec items
  in-application/
    application_requirements_manifest.json  # App-side manifest (requirements-state.yaml)
```

## ID Format Patterns

| Type   | Pattern                 | Example                       |
|--------|-------------------------|-------------------------------|
| FR     | `FR-NNNNNNN`            | `FR-0000001-login`            |
| NFR    | `NFR-NNNNNNN`           | `NFR-0000001-response-time`   |
| GLOBAL | `GLOBAL-NNNNNNN`        | `GLOBAL-0000001-logging`      |
| TS     | `TS-NNNNNNN`            | `TS-0000001-web-framework`    |
| MAC    | `MAC-NNNNNNN`           | `MAC-0000001-user-api`        |
| UIC    | `UIC-NNNNNNN`           | `UIC-0000001-login-page`      |
| AC     | `AC-NNNNNNN`            | `AC-0000001-login-form`       |
| AT     | `AT-NNNNNNN`            | `AT-0000001-verify-login`     |

IDs are globally unique within their type prefix across pending and current folders.

## Key Rules

- `contract_type` enum: only `["models_and_contracts"]`. The value `ui_contracts` is invalid.
- `contract_refs.specific_ids` must use object form: `- id: MAC-NNNNNNN-short-title`. Bare strings are invalid.
- Use `child_specifications` (not the obsolete `sub_mac_ids`) on MAC catalog entries and in `contract_refs`.
- MAC catalog entries support an optional `nfr_refs` array listing NFR/GLOBAL IDs that constrain the contract's design. Populated during MAC authoring when the NFR alignment check finds relevant requirements.
- The in-application manifest (`requirements-state.yaml`) sets `additionalProperties: false` — only declared fields are valid.
