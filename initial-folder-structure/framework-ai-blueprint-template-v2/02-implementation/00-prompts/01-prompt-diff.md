# Generate structured diff

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml`.
2. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.

## Run
Resolve `TOOLING_ROOT` from `config.yaml → tooling_root`.
```
<TOOLING_ROOT>/ai-tooling.sh diff -r "01-requirements" --implementation-id "<IMPLEMENTATION_ID>"
```

## After
- Verify exit code 0.
- Read `02-implementation/01-implementations/<IMPLEMENTATION_ID>/01-delta-current/structured-diff.yaml`.
- Report counts: created, updated, removed, technology_selection entries.
- Run DB contract gate on the generated diff:
  - Search for the DB contract logical ID from config.yaml (implementations.<ID>.database_contract_alignment.mac_contract_logical_id), `physical_database_schema`, or the DB schema filename prefix.
  - If found, explicitly flag that DB schema alignment is REQUIRED in plan + execute.
