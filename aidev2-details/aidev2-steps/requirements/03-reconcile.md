# RQ-03 Reconcile
Inputs: app codebase, current technology-selection file, MANIFEST.
Action: backfill implemented TS entries and sync diff.
Rules: only for already-implemented tech choices.

After reconcile writes:
- update `01-requirements/03-current/technology-selection/technology-selection-<IMPLEMENTATION_ID>.yaml` with reconciled entries
- the per-implementation file is the authoritative source; no flat aggregate or mirror file is maintained
