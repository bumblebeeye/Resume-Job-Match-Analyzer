# Resume-Job Match Analyzer

Resume-Job Match Analyzer is a portfolio-oriented full-stack MVP that compares an uploaded resume against a job description and returns an AI-assisted fit analysis.

This repository is being built in phases.  
Current status: **Phase 3 complete (`/history` and `/history/[id]` added).**

## Why this project

This app demonstrates:
- web product thinking
- Python backend architecture
- SQL relational modeling
- AI-assisted text analysis in a practical workflow

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
  - keyword-based skill extraction
  - explainable match score
  - overlapping skills
  - missing skills
  - summary and suggestions
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

## Local setup

### 1. Environment variables

Copy `.env.example` to `.env` and update values as needed.

Required variables:
- `APP_ENV`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `RESUME_STORAGE_PATH`
- `NEXT_PUBLIC_API_BASE_URL` (used in Phase 2 frontend)

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

## Deployment preparation notes (for later phases)

Planned targets:
- Frontend: Vercel
- Backend: Render
- Database: Railway PostgreSQL

Phase 1 already aligns with deployment basics:
- backend start command compatible with Render:
  - `uvicorn main:app --host 0.0.0.0 --port $PORT`
- DB connection via `DATABASE_URL`
- CORS controlled with env variable

Detailed deployment steps will be finalized in Phase 4 after history pages are implemented.

## Planned future improvements

- Replace keyword-only matching with embedding-assisted ranking
- Add optional record deletion endpoint
- Add tests (unit + API integration)
- Improve parsing coverage for DOCX and scanned PDFs
