# IM-11 Generate App Docs

After implementation is complete and the manifest is updated, generate documentation artifacts under `APP_ROOT/.aidev/docs/`.

## variables.md

Generate `APP_ROOT/.aidev/docs/variables.md` listing every environment variable the application reads at runtime.

Source the variable list from:
- All `os.Getenv` / `os.LookupEnv` calls (Go)
- All `process.env.*` accesses (Node.js/TypeScript)
- All `os.environ` / `os.getenv` calls (Python)
- Config files, `.env.example`, `docker-compose.yml` env sections, and startup scripts

Output format — a Markdown table:

```markdown
# Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | postgres://postgres:postgres@localhost:5432/fakebank?sslmode=disable | PostgreSQL connection string |
| PORT | No | 8080 | HTTP listen port |
| ... | ... | ... | ... |
```

Rules:
- One row per unique variable name.
- Sort alphabetically.
- `Required` = "Yes" if the app fails to start without it; "No" if a default exists.
- `Default` = the fallback value from code, or empty if none.
- `Description` = one-sentence purpose derived from usage context.
- Do not include variables used only in tests or CI pipelines.
- Regenerate this file on every implementation run so it stays current.

## Narration
- On entry: `[IM-11] Generate docs started at <timestamp>`
- On write: `[IM-11] Wrote variables.md — <N> variables documented`
- On error: `[IM-11] ERROR: Doc generation failed — <details>`
- On unexpected: `[IM-11] **UNEXPECTED: <details>**`
- On exit: `[IM-11] Generate docs completed at <timestamp> (elapsed: <N>s)`
