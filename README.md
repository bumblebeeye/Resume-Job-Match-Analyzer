# Resume-Job Match Analyzer

Resume-Job Match Analyzer is a full-stack AI-assisted workflow app that compares an uploaded resume against a job description and returns a production-minded fit analysis. The project combines deterministic scoring, optional LLM-generated suggestions, persistent analysis history, and cloud-ready file storage to show how GenAI can be embedded into a practical business workflow.

This repository is being built in phases.  
Current status: **Phase 5 complete (AI-powered suggestion generation with fallback).**

## Why this project

This app demonstrates:
- full-stack product delivery with Next.js, FastAPI, and PostgreSQL
- deterministic analysis paired with optional LLM augmentation
- production-minded reliability through fallback paths and stored metadata
- cloud-aware backend design, including S3-backed resume storage with local fallback

## Why this matters for production AI

This project is intentionally not "LLM for everything." The core score and skill-gap analysis are deterministic so results stay explainable and resilient. AI is used only for suggestion generation, and only when the feature is enabled and credentials are configured.

That design makes the system easier to operate:
- deterministic matching logic remains available even when AI is disabled
- Gemini suggestions degrade safely to rule-based guidance on API errors or timeouts
- each analysis stores metadata such as scoring version, suggestion source, and AI model
- uploaded files can use S3 storage in AWS-oriented deployments, with local disk fallback for simpler environments

## Tech stack

- Frontend: Next.js App Router + TypeScript + Tailwind
- Backend: FastAPI + Python
- Database: PostgreSQL

## Project structure

```text
frontend/      # Next.js UI (Phase 2 implemented: / and /analyze)
backend/       # FastAPI backend (implemented in Phase 1)
database/      # SQL schema
docs/          # build phases and planning notes
```

## Phase 1 features implemented

- API endpoints:
  - `POST /api/analyze`
  - `GET /api/analyses`
  - `GET /api/analyses/{id}`
- Resume file handling:
  - supports PDF/TXT/MD input
  - extracts text for analysis
- Analysis pipeline:
  - keyword-based skill extraction for software, cloud, and AI-focused roles
  - explainable match score
  - overlapping skills
  - missing skills
  - summary and structured suggestions
- Persistence:
  - `resumes`, `job_descriptions`, `analyses` relational tables
  - JSONB fields for semi-structured analysis outputs

## Phase 2 features implemented

- Next.js App Router frontend with TypeScript + Tailwind
- Home page (`/`) with hero, workflow summary, and CTA
- Analyzer page (`/analyze`) with:
  - resume upload
  - role title
  - company name (optional)
  - job description textarea
  - loading/error state handling
  - result UI for match score, overlap skills, missing skills, summary, suggestions
- Frontend-to-backend integration with `POST /api/analyze`

## Phase 3 features implemented

- History page (`/history`) with:
  - analysis list view
  - loading state
  - empty state
  - error state
- Analysis detail page (`/history/[id]`) with:
  - role/company/resume metadata
  - match score
  - summary
  - overlapping and missing skills
  - improvement suggestions
  - not-found handling
- Frontend API integration with:
  - `GET /api/analyses`
  - `GET /api/analyses/{id}`

## Phase 4 features implemented

- Deployment-ready environment variable guidance for:
  - Vercel (frontend)
  - Render (backend)
  - Railway (PostgreSQL)
- Backend CORS parsing hardened for cloud env formats:
  - comma-separated string
  - JSON-array string
- Backend resume storage path normalized to avoid nested `backend/backend` writes
- Monorepo Next.js tracing root configured for cleaner Vercel builds

## Phase 5 features implemented

- AI-powered improvement suggestions (Gemini) for missing-skill scenarios
- Minimal-scope rollout:
  - score/overlap/missing logic remains deterministic
  - only suggestions can be AI-generated
- Automatic fallback to rule-based suggestions when:
  - AI is disabled
  - no API key is configured
  - AI request fails or times out
- AI source metadata stored in analysis metadata (`suggestions_source`, `ai_model` when used)

## Architecture overview

1. The frontend uploads a resume and job description to the FastAPI backend.
2. The backend extracts resume text, then identifies skill signals from the resume and job description.
3. The deterministic analysis layer calculates overlap, missing skills, and the match score.
4. The optional AI layer generates targeted improvement suggestions when missing skills exist.
5. The system stores the uploaded resume record, job description, analysis result, and metadata for later review.

This keeps the system explainable while still showing practical GenAI integration.

## Local setup

### 1. Environment variables

Copy `.env.example` to `.env` and update values as needed.

Required variables:
- `APP_ENV`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `RESUME_STORAGE_PATH`
- `NEXT_PUBLIC_API_BASE_URL`
- Optional AWS storage vars (backend):
  - `AWS_REGION`
  - `S3_BUCKET_NAME`
  - `S3_RESUME_PREFIX`
- Optional AI vars (backend):
  - `AI_SUGGESTIONS_ENABLED`
  - `GEMINI_API_KEY`
  - `AI_MODEL`
  - `AI_TIMEOUT_SECONDS`

### 2. Start PostgreSQL and create schema

Run:

```bash
psql "$DATABASE_URL" -f database/schema.sql
```

### 3. Run backend API

```bash
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

### 4. Run frontend app

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

### 5. Run backend tests (pytest)

```bash
cd backend
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Current tests cover:
- API health check (`GET /health`)
- Core analyze flow (`POST /api/analyze`)
- History list/detail retrieval (`GET /api/analyses`, `GET /api/analyses/{id}`)
- Basic validation and not-found paths

## API contract (current)

### `POST /api/analyze`

`multipart/form-data` fields:
- `resume_file` (required)
- `role_title` (required)
- `company_name` (optional)
- `job_description` (required)

Response includes:
- analysis id
- match score
- summary
- overlapping skills
- missing skills
- suggestions
- created timestamp

### `GET /api/analyses`

Returns analysis history records (id, role/company, match score, created time).

### `GET /api/analyses/{id}`

Returns one analysis in detail, including stored result sections.

## Deployment (Vercel + Render + Railway)

### 1. Create Railway PostgreSQL

- Create a Railway project and add PostgreSQL.
- Copy the Railway Postgres connection string.
- Initialize schema:

```bash
psql "<RAILWAY_DATABASE_URL>" -f database/schema.sql
```

### 2. Deploy backend to Render

- Create a Render Web Service from this repo.
- Configure:
  - Root Directory: `backend`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set environment variables:
  - `APP_ENV=production`
  - `DATABASE_URL=<RAILWAY_DATABASE_URL>`
  - `RESUME_STORAGE_PATH=storage/resumes`
  - `CORS_ORIGINS=["https://your-frontend.vercel.app","http://localhost:3000"]`
- Verify:
  - `https://<render-service>.onrender.com/health` returns `{"status":"ok"}`.

### 3. Deploy frontend to Vercel

- Import this repo in Vercel.
- Set Root Directory to `frontend`.
- Set environment variable:
  - `NEXT_PUBLIC_API_BASE_URL=https://<render-service>.onrender.com`
- Deploy and open the production domain.

### 4. Final cross-service wiring

- Ensure backend `CORS_ORIGINS` includes your Vercel production domain.
- Redeploy backend on Render after CORS changes.
- Run production smoke test:
  - upload resume in `/analyze`
  - verify result renders
  - verify record appears in `/history`
  - open `/history/[id]` detail page

## Required Production Environment Variables

### Backend (Render)

- `APP_ENV=production`
- `DATABASE_URL=postgresql://...` (Railway)
- `CORS_ORIGINS=["https://<vercel-domain>","http://localhost:3000"]`
- `RESUME_STORAGE_PATH=storage/resumes`
- `AWS_REGION=ap-southeast-2` (optional)
- `S3_BUCKET_NAME=<your-s3-bucket>` (optional)
- `S3_RESUME_PREFIX=resumes` (optional)
- `AI_SUGGESTIONS_ENABLED=true` (optional)
- `GEMINI_API_KEY=<your-gemini-api-key>` (required only when AI enabled)
- `AI_MODEL=gemini-2.5-flash` (optional)
- `AI_TIMEOUT_SECONDS=8` (optional)

### Frontend (Vercel)

- `NEXT_PUBLIC_API_BASE_URL=https://<render-service>.onrender.com`

## Production-readiness notes

- Core match scoring is deterministic keyword-overlap logic; suggestion text can be Gemini-powered when enabled.
- Uploaded resume files can be stored on local disk for simple deployments or pushed to S3 when AWS storage is configured.
- Add automated API/frontend tests and structured logging before scaling traffic.

## Honest future roadmap

These items are not implemented yet. They are the next logical steps for turning the project into a more complete production AI system.

- Add Terraform-managed infrastructure for repeatable cloud provisioning.
- Add CI/CD pipelines for automated test, build, and deploy workflows.
- Add AWS Bedrock support as an alternative model provider alongside Gemini.
- Add richer observability for request outcomes, fallback rates, and model behavior.
- Add structured evaluation runs for prompt/output quality over time.
- Add agent-style orchestration for multi-step resume review workflows.
- Replace keyword-only matching with embedding-assisted ranking.
- Improve parsing coverage for DOCX and scanned PDFs.
