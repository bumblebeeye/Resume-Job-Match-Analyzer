# Backend (FastAPI)

Phase 1 backend provides:
- `POST /api/analyze`
- `GET /api/analyses`
- `GET /api/analyses/{id}`

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```
3. Set environment variables (copy from root `.env.example`).
4. Create PostgreSQL tables:
   ```bash
   psql "$DATABASE_URL" -f ../database/schema.sql
   ```
5. Start API:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
