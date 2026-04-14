## Step 1 - Detect Blueprint Root

Detect `BLUEPRINT_ROOT` from the active file by walking up to the first directory containing:
- `01-requirements`
- `02-implementation`
- `03-test-results`

If not found, ask for an absolute blueprint path.
