# Backfill Technology Selections and Sync Diff Files

> **Root:** All paths in this prompt are relative to the blueprint root unless otherwise specified. Relative path from this file to blueprint root: `../../`

## Setup
1. Read `.instructions/config.yaml` → resolve app-specific values (`APP_ROOT`, implementation paths, etc.).
2. Read `.instructions/instructions.md` → canonical policy.
3. Read `.instructions/config.yaml → implementations` to list registered implementation IDs. If there is only one, use it automatically. If there are multiple and the user has not specified one and you cannot determine it from context or the previous exchange, **stop and ask**.
4. Path shorthands (fixed blueprint constants — all relative to the blueprint root):
   - `TOOLING_CMD` = resolve from `config.yaml → tooling_root`, append `/ai-tooling.sh` (default: `../framework-ai-development-tooling/ai-tooling.sh`)
   - `REQ_PATH` = `01-requirements`
   - `APP_ROOT` = `implementations.<IMPLEMENTATION_ID>.application_root` (from config.yaml)

## Phase 1 — Analyse code for undeclared technologies

1. Read the application codebase at `APP_ROOT`:
   - Package manifests (`package.json`, `go.mod`, `requirements.txt`, `pom.xml`, etc.)
   - Framework configuration files, Docker images, CI configs.
2. Read the current technology selection file:
   - `01-requirements/03-current/technology_selection.yaml`
   - The per-implementation mirror at `01-requirements/03-current/technology-selection/technology_selections_<IMPLEMENTATION_ID>.yaml` must be kept aligned with it.
3. Compare: identify technologies or version changes present in code but missing from the technology selection file.
4. For each new technology found:
   - Add a new `TS-<slug>` entry directly to `01-requirements/03-current/technology_selection.yaml`.
   - Set `created_version` and `updated_version` to the current version from `control.yaml → current_version`.
5. Refresh `01-requirements/03-current/technology-selection/technology_selections_<IMPLEMENTATION_ID>.yaml` after any update to the current TS file.
5. Mark each new entry as implemented in the application manifest at `implementations.<IMPLEMENTATION_ID>.manifest_path` by adding it to `requirement_baseline`.

## Phase 2 — Sync backported requirements into diff directory

After writing to `03-current/`, run the sync command to create diff entries for any requirement present in current but missing from `02-diff/`:

```
$TOOLING_CMD sync-diff -r "$REQ_PATH"
```

This efficiently adds only the missing diff files. It does NOT rebuild existing ones.

### Diff file naming convention (enforced by the sync script)

| Requirement type | Bucket directory | File name |
|---|---|---|
| `FR-NNNNNN` | `02-diff/functional/` | `FR-NNNNNN.yaml` |
| `NFR-NNNNNN` | `02-diff/nfr-and-global-cr/` | `NFR-NNNNNN.yaml` |
| `TS-<slug>` | `02-diff/technology-selection/` | `TS-<slug>.yaml` |

To look up any requirement's diff history, go directly to `02-diff/<bucket>/<REQUIREMENT_ID>.yaml` — no search needed.

## Phase 3 — Handle replaced requirements

If any backfilled entry **replaces** an existing requirement (via `replaces_id`):

1. Read the **specific** diff file for the replaced requirement:
   `02-diff/<bucket>/<REPLACED_ID>.yaml`
   (e.g. if `TS-frontend-framework-v2` replaces `TS-frontend-framework`, read `02-diff/technology-selection/TS-frontend-framework.yaml`).
2. The replaced entry's diff file gives you its full prior snapshot — use it to set `original_requirement` context.
3. In the replaced entry's current file, set `superseded_by: <NEW_ID>`.
4. In the new entry, set `replaces_id: <OLD_ID>`.

## After
- Verify the diff directory has a file for every requirement in current.
- Report: number of technologies backfilled, number of diff files synced, any replacements.
