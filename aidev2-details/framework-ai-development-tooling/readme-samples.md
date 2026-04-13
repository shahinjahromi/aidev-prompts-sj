# Sixert Full Path Command Sequence

## Paths

- Tool script: `/media/psf/z-work-ai-enablement/projects/ai-development-tooling/ai-tooling.sh`
- Requirements root: `/media/psf/z-work-ai-enablement/projects/sixert-bank-specs/01-requirements`
- App root: `/media/psf/z-work-ai-enablement/projects/sixert_bank-main`
- Implementation id: `SIXERT_NODEJS_01`

## 1) Bootstrap (generic)

```bash
/media/psf/z-work-ai-enablement/projects/ai-development-tooling/ai-tooling.sh bootstrap \
  -r /media/psf/z-work-ai-enablement/projects/sixert-bank-specs/01-requirements \
  -a /media/psf/z-work-ai-enablement/projects/sixert_bank-main
```

## 2) Promote pending requirements

```bash
/media/psf/z-work-ai-enablement/projects/ai-development-tooling/ai-tooling.sh promote \
  -r /media/psf/z-work-ai-enablement/projects/sixert-bank-specs/01-requirements \
  -a /media/psf/z-work-ai-enablement/projects/sixert_bank-main \
  --implementation-id SIXERT_NODEJS_01
```

## 3) Generate delta

```bash
/media/psf/z-work-ai-enablement/projects/ai-development-tooling/ai-tooling.sh delta \
  -r /media/psf/z-work-ai-enablement/projects/sixert-bank-specs/01-requirements \
  -a /media/psf/z-work-ai-enablement/projects/sixert_bank-main \
  --implementation-id SIXERT_NODEJS_01
```

Review delta in (01-delta-current/ contains only structured-diff.yaml):

- `/media/psf/z-work-ai-enablement/projects/sixert-bank-specs/02-implementation-state/01-implementations/SIXERT_NODEJS_01/01-delta-current/structured-diff.yaml`
- `/media/psf/z-work-ai-enablement/projects/sixert-bank-specs/02-implementation-state/01-implementations/SIXERT_NODEJS_01/02-delta-history/01-delta-current.yaml`

## 4) Generate AI plan

```bash
/media/psf/z-work-ai-enablement/projects/ai-development-tooling/ai-tooling.sh plan \
  -r /media/psf/z-work-ai-enablement/projects/sixert-bank-specs/01-requirements \
  -a /media/psf/z-work-ai-enablement/projects/sixert_bank-main \
  --implementation-id SIXERT_NODEJS_01
```

Review plan in:

- `/media/psf/z-work-ai-enablement/projects/sixert-bank-specs/02-implementation-state/01-implementations/SIXERT_NODEJS_01/03-ai-plan-current/current-plan.md`

## 5) Apply delta to app manifest state

```bash
/media/psf/z-work-ai-enablement/projects/ai-development-tooling/ai-tooling.sh apply \
  -r /media/psf/z-work-ai-enablement/projects/sixert-bank-specs/01-requirements \
  -a /media/psf/z-work-ai-enablement/projects/sixert_bank-main \
  --implementation-id SIXERT_NODEJS_01
```

App manifest updated:

- `/media/psf/z-work-ai-enablement/projects/sixert_bank-main/.aidev/requirements/requirements-state.yaml`
