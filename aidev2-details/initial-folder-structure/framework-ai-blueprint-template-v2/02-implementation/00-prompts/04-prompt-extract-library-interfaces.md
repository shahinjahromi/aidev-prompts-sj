# Extract library interfaces

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml`.
2. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.

## Run
Extract public types and method signatures from libraries in the app root (resolve from `config.yaml → implementations.<IMPLEMENTATION_ID>.application_root`).

Use the shared extractor script appropriate for the implementation stack
(see `02-implementation/01-implementations/<IMPLEMENTATION_ID>/ai-app-hints.yaml` for the stack).
Resolve `TOOLING_ROOT` from `{{VSCODE_USER_PROMPTS_FOLDER}}/aidev2-details/framework-ai-development-tooling`.
```
python3 "<TOOLING_ROOT>/interface-extractors/extract-nodejs-library-interfaces.py" \
  --project-root <APP_ROOT> \
  --output 02-implementation/01-implementations/<IMPLEMENTATION_ID>/04-extract-library-interfaces/ref-library-methods.yaml
```

## Rules
- Include all public types: exported, re-exported, aliased, declared
- Resolve nested/inherited/aliased type names
- Include type aliases even without methods
- Omit empty collections from output
