# Massar

End-to-end bus delay prediction demo. The backend (FastAPI + SQLModel + SQLite) ingests trip records, cleans/imputes fields, and serves predictions from a Joblib model. The frontend (React Router 7 + Tailwind) lets drivers submit trips, view instant predicted delay, and explore stored records/metrics.

## Features
- FastAPI API with ingest, batch ingest, predict, records CRUD, metrics, and health checks.
- SQLite persistence with simple cleaning and deterministic imputation.
- Joblib model loader with a dummy model generator for local testing.
- React Router SSR app with driver console (geolocation capture, live prediction), dashboard metrics, and home/marketing pages.
- Docker support for backend and a standalone Dockerfile for the frontend.

## Project Structure
- `backend/` – FastAPI service, SQLModel schemas, prediction pipeline, Docker Compose for API + SQLite.
- `frontend/` – React Router 7 app (TypeScript, Tailwind) that talks to the backend at `http://localhost:8000/api/v1` by default (see `frontend/app/lib/api.ts`).
- `.gitignore` – excludes virtualenvs, build artifacts, and backend data.

## Quick Start
### Prereqs
- Python 3.10+
- Node.js 18+ and npm
- Docker (optional)

### Backend (API)
```bash
cd backend
python -m venv .venv
# PowerShell
.venv\\Scripts\\Activate
pip install -r requirements.txt

# Optional: create a dummy model for tests/dev
python model/dummy_model_builder.py

# Run API
uvicorn app.main:app --reload --port 8000

# Tests
pytest
```
- Key paths: model path `app/config.py` (`MODEL_PATH`), DB path `./data/db.sqlite`.
- API surface: `POST /api/v1/records/ingest`, `POST /api/v1/records/batch_ingest`, `POST /api/v1/predict`, `GET /api/v1/records/`, `GET /api/v1/records/{id}`, `PUT /api/v1/records/{id}`, `GET /api/v1/metrics`, `GET /api/v1/health`.
- Docker: `docker compose up --build` from `backend/`.

### Frontend (Driver & Dashboard)
```bash
cd frontend
npm install
npm run dev
```
- Dev server defaults to `http://localhost:5173`; ensure the backend is running at `http://localhost:8000`.
- Production build: `npm run build` then `npm run start` (serves the built SSR bundle).
- API base URL can be changed in `app/lib/api.ts` for deployments.
- Docker build: `docker build -t massar-frontend .`

## Notes & Next Steps
- Add auth/rate-limiting before exposing publicly.
- Swap SQLite for Postgres in `backend/app/config.py` if needed.
- Consider background workers for heavier prediction loads and HTTPS termination in production.

