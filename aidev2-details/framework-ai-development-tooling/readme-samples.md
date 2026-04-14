# Full Path Command Sequence

## Paths

- Tool script: `$TOOL` (path to `ai-tooling.sh`)
- Requirements root: `$REQ` (path to `<blueprint>/01-requirements`)
- App root: `$APP` (path to the application repository)
- Implementation id: `$IMPL` (e.g. `MY_APP_01`)

## 1) Bootstrap (generic)

```bash
"$TOOL" bootstrap \
  -r "$REQ" \
  -a "$APP"
```

## 2) Promote pending requirements

```bash
"$TOOL" promote \
  -r "$REQ" \
  -a "$APP" \
  --implementation-id "$IMPL"
```

## 3) Generate delta

```bash
"$TOOL" delta \
  -r "$REQ" \
  -a "$APP" \
  --implementation-id "$IMPL"
```

Review delta in (01-delta-current/ contains only structured-diff.yaml):

- `<spec-root>/02-implementation-state/01-implementations/$IMPL/01-delta-current/structured-diff.yaml`
- `<spec-root>/02-implementation-state/01-implementations/$IMPL/02-delta-history/01-delta-current.yaml`

## 4) Generate AI plan

```bash
"$TOOL" plan \
  -r "$REQ" \
  -a "$APP" \
  --implementation-id "$IMPL"
```

Review plan in:

- `<spec-root>/02-implementation-state/01-implementations/$IMPL/03-ai-plan-current/current-plan.md`

## 5) Apply delta to app manifest state

```bash
"$TOOL" apply \
  -r "$REQ" \
  -a "$APP" \
  --implementation-id "$IMPL"
```

App manifest updated:

- `$APP/.aidev/requirements/requirements-state.yaml`
