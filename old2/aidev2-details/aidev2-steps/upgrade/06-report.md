## Step 6 - Report

Report:
- changed files
- key naming conversions applied
- key ID-format corrections applied and notable reference updates
- confirmation that app-specific artifacts were preserved
- any residual manual follow-up needed

Obsolete v1 files notification:
- list any v1 prompt/instruction files found during verification under a clear heading: **"Obsolete v1 files — safe to remove"**
- explain that these are superseded by user-level aidev2 prompts and can be deleted
- do NOT delete them — only inform the user
- typical obsolete paths:
  - `02-implementation/00-prompts/` — replaced by user-level `aidev2-steps/implement/`
  - `github-config/aidev-*.prompt.md` — replaced by `.github/prompts/aidev2-*.prompt.md` wrappers
  - `github-config/aidev-framework.instructions.md` — replaced by user-level `aidev2-*.instructions.md`
  - `instructions/` — v1 documentation folder
  Note: `.instructions/config.yaml` and `.instructions/codebase-context.yaml` are KEPT — aidev2 reads both.

Manifest upgrade summary:
- report whether the manifest was upgraded (entries updated with `e2e_test_status: NOT_TESTED`)
- remind user that `implementation_initial_date` and `implementation_last_date` are set by IM-04 Execute, not by this upgrade
- remind user that the timezone for date fields comes from `config.yaml → variables.timezone`
