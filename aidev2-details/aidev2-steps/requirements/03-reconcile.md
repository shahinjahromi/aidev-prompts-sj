# RQ-03 Reconcile
Inputs: app codebase, current technology_selection, MANIFEST.
Action: backfill implemented TS entries and sync diff.
Rules: only for already-implemented tech choices.

After reconcile writes:
- refresh `01-requirements/03-current/technology-selection/technology_selections_<IMPLEMENTATION_ID>.yaml`
- keep the current mirror aligned with `01-requirements/03-current/technology_selection.yaml`
