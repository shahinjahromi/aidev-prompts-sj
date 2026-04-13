Requirement command sequence

Base:
- REQ={SPECS_ROOT}/01-requirements
- APP={APP_ROOT}
- IMPL=<<IMPLEMENTATION_ID>>
- TOOL={{VSCODE_USER_PROMPTS_FOLDER}}/aidev2-details/framework-ai-development-tooling/ai-tooling.sh

promote
- Command: "$TOOL" promote -r "$REQ" -a "$APP" --implementation-id "$IMPL"
- After promote: developer must manually update app manifest iteration_id to include new iteration.
- Review files:
  - 01-requirements/01-pending-promotion/*
  - 01-requirements/03-current/**/*
  - 01-requirements/02-diff/**/*

delta
- Command: "$TOOL" delta -r "$REQ" -a "$APP" --implementation-id "$IMPL"
- Review files:
  - 01-requirements/03-current/merged/merged_requirements.yaml
  - ../<<APP_REPO_DIR>>/.aidev/requirements/requirements-state.yaml
  - 02-implementation/01-implementations/$IMPL/01-delta-current/structured-diff.yaml

update-merged
- Command: "$TOOL" update-merged -r "$REQ" -a "$APP" --implementation-id "$IMPL"
- Review files:
  - 01-requirements/03-current/merged/**/*
  - 01-requirements/02-diff/**/*

plan
- Command: "$TOOL" plan -r "$REQ" -a "$APP" --implementation-id "$IMPL"
- Review files:
  - 02-implementation/01-implementations/$IMPL/01-delta-current/structured-diff.yaml
  - 02-implementation/01-implementations/$IMPL/02-plan-current/plan.md

apply
- Command: "$TOOL" apply -r "$REQ" -a "$APP" --implementation-id "$IMPL"
- Review files:
  - ../<<APP_REPO_DIR>>/.aidev/requirements/requirements-state.yaml
  - 02-implementation/01-implementations/$IMPL/50-delta-history/*.yaml
