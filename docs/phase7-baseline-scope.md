# Phase 7 Baseline and Scope

Last updated: 2026-03-26  
Branch: `codex/aws-phase7`

## Goal

Phase 7 hardens the existing AWS deployment in small, beginner-friendly steps without rewriting the app architecture and without touching the legacy Vercel/Render/Railway deployment.

## Current baseline

### Deployment baseline

- AWS frontend (Phase 6 working): `https://codex-aws-phase6.d7aj7hvvxk2xv.amplifyapp.com/`
- AWS backend (Phase 6 working): `https://q22emiur7s.ap-southeast-2.awsapprunner.com/`
- Legacy deployment remains unchanged and out of scope for Phase 7 changes.

### Repository baseline

- Worktree path: `/Users/xinpeiye/Documents/portfolio-projects/resume-aws-phase7`
- Git status was clean when this document was created.
- Monorepo structure:
  - `frontend/`: Next.js App Router + TypeScript + Tailwind
  - `backend/`: FastAPI + SQLAlchemy + pytest
  - `database/`: PostgreSQL schema
  - `docs/`: phase and planning notes

### Backend baseline

- FastAPI app entry: `backend/app/main.py`
- Public routes currently in code:
  - `GET /health`
  - `POST /api/analyze`
  - `GET /api/analyses`
  - `GET /api/analyses/{id}`
- Existing protections/behavior already present:
  - request validation for blank `role_title` and `job_description`
  - resume parsing error handling via `ResumeParserError`
  - CORS origin normalization for AWS/cloud env formats
- Current gaps relevant to Phase 7:
  - no upload size limit
  - no explicit MIME allowlist check at request boundary
  - no standardized JSON error envelope
  - no request ID middleware/log correlation
  - no authentication/rate limiting layer in app code

### Frontend baseline

- Next.js frontend uses `NEXT_PUBLIC_API_BASE_URL` in `frontend/lib/api.ts`
- Current package scripts:
  - `npm run dev`
  - `npm run build`
  - `npm run start`
  - `npm run lint`
- There is no dedicated `typecheck` script yet.

### Tooling baseline

- Backend tests exist in `backend/tests/test_api.py`
- No CI workflow is present in the repository yet.
- No dedicated secrets scan or dependency audit workflow is present yet.
- Local dependency folders were not present when this document was created:
  - `backend/.venv`: not present
  - `frontend/node_modules`: not present
- Because of that, Step 1 did not execute backend/frontend verification commands locally.

## Phase 7 scope

Phase 7 will be executed in this exact order, with a confirmation gate after each step:

1. Baseline + Phase 7 scope doc
2. CI pipeline: backend tests + frontend build/type/lint
3. Security scanning in CI: secrets + dependency audit
4. Backend input safety: upload size + MIME validation
5. Standardized backend error handling + request IDs
6. Basic auth/rate limiting for API protection
7. AWS network hardening: remove temporary open RDS ingress and move to private path
8. Observability + CloudWatch alarms
9. Deployment safety: staging + approval + smoke tests
10. Runbook + portfolio case-study docs

## Delivery rules

- Keep each change minimal and practical.
- Prefer AWS console steps when faster than code or IaC changes.
- Do not change the core frontend/backend/database architecture unless a later step makes it necessary.
- Do not modify or migrate the legacy Vercel/Render/Railway deployment.
- Do not start the next step until the previous step is confirmed working.

## Step 1 completion criteria

Step 1 is complete when:

- the repo contains a Phase 7 baseline and scope document
- the document records the current AWS baseline and known hardening gaps
- the Phase 7 step order is explicit and matches the agreed gated process
