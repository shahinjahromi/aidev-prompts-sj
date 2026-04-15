Command sequence for requirement lifecycle

Base variables:
- REQ=<path-to-blueprint>/01-requirements
- APP=<path-to-app-repo>
- IMPL=<IMPLEMENTATION_ID>
- TOOL=<path-to>/ai-development-tooling/ai-tooling.sh

1) update merged requirements from diffs
Command:
- "$TOOL" merge -r "$REQ" --all-implementations
- "$TOOL" refresh-merged -r "$REQ" --all-implementations   # alias
Review before running:
- $REQ/02-diff/**/*.yaml
- $REQ/manifest.yaml
Review after running:
- $REQ/03-current/**/*.yaml
- $REQ/03-current/merged/*.yaml
- $REQ/03-current/requirements.yaml

2) promote
Command:
- "$TOOL" promote -r "$REQ" -a "$APP" --implementation-id "$IMPL"
Review before running:
- $REQ/manifest.yaml
- $REQ/control.yaml
- $REQ/01-pending-promotion/**/<artifact>.yaml
Review after running:
- $REQ/03-current/**/*.yaml
- $REQ/02-diff/**/*.yaml
- $REQ/03-current/merged/*.yaml
- $REQ/manifest.yaml

3) delta
Command:
- "$TOOL" delta -r "$REQ" -a "$APP" --implementation-id "$IMPL"
Review before running:
- $APP/.aidev/requirements/requirements-state.yaml
- $REQ/manifest.yaml
- $REQ/03-current/merged/requirements.yaml
Review after running:
- <spec-root>/02-implementation-state/01-implementations/$IMPL/01-delta-current/structured-diff.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/02-delta-history/01-delta-current.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/$IMPL.manifest.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/02-delta-history/*.yaml

4) plan
Command:
- "$TOOL" plan -r "$REQ" -a "$APP" --implementation-id "$IMPL"
Review before running:
- <spec-root>/02-implementation-state/01-implementations/$IMPL/01-delta-current/structured-diff.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/02-delta-history/01-delta-current.yaml
Review after running:
- <spec-root>/02-implementation-state/01-implementations/$IMPL/03-ai-plan-current/current-plan.md
- <spec-root>/02-implementation-state/01-implementations/$IMPL/03-ai-plan-current/requirements-version-manifest.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/04-ai-plan-history/*.md
- <spec-root>/02-implementation-state/01-implementations/$IMPL/05-ai-plan/plan.md

5) apply
Command:
- "$TOOL" apply -r "$REQ" -a "$APP" --implementation-id "$IMPL"
Review before running:
- App implementation code changes are complete and tested
- <spec-root>/02-implementation-state/01-implementations/$IMPL/01-delta-current/structured-diff.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/02-delta-history/01-delta-current.yaml
Review after running:
- $APP/.aidev/requirements/requirements-state.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/$IMPL.manifest.yaml
- <spec-root>/02-implementation-state/01-implementations/$IMPL/02-delta-history/*.yaml
