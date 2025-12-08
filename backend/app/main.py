"""Application entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import health, ingest, predict, records
from .config import MODEL_PATH
from .db import create_db_and_tables
from .model_server import model_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bus Delay Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database and load model."""
    create_db_and_tables()
    try:
        model_server.load_model(MODEL_PATH)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to load model: %s", exc)


app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(predict.router)
app.include_router(records.router)


