# Resume-Job Match Analyzer: Implementation Phases

## Phase 1 (implemented)
- Monorepo scaffolding (`frontend/`, `backend/`, `database/`, `docs/`)
- FastAPI backend architecture (routers, services, models, schemas, config, DB session)
- PostgreSQL schema setup script
- MVP analysis pipeline:
  - Resume text extraction (PDF/TXT/MD)
  - Job text skill signal extraction
  - Explainable keyword-overlap match score
  - Overlap/missing skills + summary + suggestions
- API endpoints:
  - `POST /api/analyze`
  - `GET /api/analyses`
  - `GET /api/analyses/{id}`

## Phase 2 (implemented)
- Next.js + TypeScript + Tailwind setup
- Home page (`/`)
- Analyzer page (`/analyze`) with upload form and result UI
- API integration for analysis submission/result rendering

## Phase 3 (implemented)
- History page (`/history`)
- Analysis detail page (`/history/[id]`)
- Frontend data loading states and empty states

## Phase 4 (implemented)
- Deployment-ready setup for Vercel (frontend), Render (backend), Railway (PostgreSQL)
- Production environment variable documentation
- Final UX polish and portfolio-level cleanup

## Phase 5 (implemented)
- Minimal AI integration for improvement suggestions only
- Gemini-backed suggestions when missing skills exist
- Rule-based fallback when AI is disabled/unavailable

## Phase 6 (implemented)
- AWS migration baseline established while keeping legacy Vercel/Render/Railway deployment untouched
- Frontend deployed on AWS Amplify
- Backend deployed on AWS App Runner
- Resume storage and backend configuration prepared for AWS environment variables
- Current known-good public endpoints:
  - Frontend: `https://codex-aws-phase6.d7aj7hvvxk2xv.amplifyapp.com/`
  - Backend: `https://q22emiur7s.ap-southeast-2.awsapprunner.com/`

## Phase 7 (planned)
- Hardening and DevOps improvements executed in small gated steps
- CI pipeline for backend/frontend checks
- CI security scanning for secrets and dependency issues
- Backend request/input safety improvements
- Standardized error handling and request tracing
- API protection controls
- AWS network hardening
- Observability and alarm setup
- Safer deployment workflow with smoke checks
- Runbook and portfolio case-study documentation
