# Bus Delay Prediction Backend

FastAPI + SQLModel backend for ingesting bus records, cleaning/imputing deterministic fields, persisting to SQLite, and serving delay predictions from a pre-trained joblib model.

## Stack
- Python 3.10+
- FastAPI, SQLModel, SQLite
- pandas, joblib
- Uvicorn
- Docker / docker-compose (optional)

## Getting Started
1. `git clone <your-repo-url>`
2. `cd backend`
3. Create venv: `python -m venv .venv && source .venv/bin/activate` (Windows PowerShell: `.venv\\Scripts\\Activate`)
4. Install deps: `pip install -r requirements.txt`
5. Place trained model at `./model/model.joblib` (use `python model/dummy_model_builder.py` to create a zero-output dummy model for testing).
6. Run dev server: `uvicorn app.main:app --reload --port 8000`
7. Or Docker: `docker compose up --build`

## Configuration
- Model path: `app/config.py` (`MODEL_PATH`)
- DB path: SQLite at `./data/db.sqlite`

## Endpoints (v1)
- `POST /api/v1/records/ingest` – ingest single record (sync prediction if model loaded).
- `POST /api/v1/records/batch_ingest` – ingest list, predictions scheduled via background tasks.
- `POST /api/v1/predict` – predict from RecordIn payload or raw features (`X-Raw-Features: true`); optional `persist=true`.
- `GET /api/v1/health` – health & model status.
- `GET /api/v1/metrics` – counts and last model version.
- `GET /api/v1/records/{id}` – fetch record.
- `GET /api/v1/records/` – list records with `limit`/`offset`.
- `PUT /api/v1/records/{id}` – update passenger_count, weather, actual_time; optional `repredict=true`.

## Sample cURL
Single ingest:
```bash
curl -X POST "http://localhost:8000/api/v1/records/ingest" -H "Content-Type: application/json" -d '{
"route_id": "Route-04",
"scheduled_time": "2025-12-07 08:30",
"actual_time": "8.45AM",
"weather": "Clody",
"passenger_count": 250,
"latitude": 999,
"longitude": 30
}'
```

Predict (non-persist):
```bash
curl -X POST "http://localhost:8000/api/v1/predict?persist=false" -H "Content-Type: application/json" -d '{
"route_id":"3",
"scheduled_time":"08:30",
"actual_time":"08:50",
"weather":"sun",
"passenger_count":12,
"latitude":25.7,
"longitude":32.64
}'
```

Health:
```bash
curl http://localhost:8000/api/v1/health
```

## Tests
- Run `pytest` from `backend/` (uses temp SQLite).
- To test with a dummy model: `python model/dummy_model_builder.py` then run tests.

## Extending
- Swap SQLite for Postgres by updating `DATABASE_URL` in `config.py` and engine options.
- Add async workers/queues (e.g., Celery) for heavier prediction loads.
- Add auth (API keys/JWT), rate limiting, and HTTPS for production.




