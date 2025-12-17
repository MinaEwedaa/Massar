"""Application entrypoint."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import health, ingest, predict, records
from .config import MODEL_PATH
from .db import create_db_and_tables
from .model_server import model_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bus Delay Prediction API", version="1.0.0")

# Get allowed origins from environment variable, with fallback to localhost for development
allowed_origins_env = os.getenv("CORS_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    # Default to localhost for development
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # Set to False when using specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database and load model."""
    create_db_and_tables()
    try:
        import os
        logger.info("Attempting to load model from: %s", MODEL_PATH)
        logger.info("Model file exists: %s", os.path.exists(MODEL_PATH))
        model_server.load_model(MODEL_PATH)
        if model_server.loaded:
            logger.info("Model loaded successfully. Version: %s", model_server.model_version)
        else:
            logger.warning("Model file not found or failed to load at: %s", MODEL_PATH)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to load model from %s: %s", MODEL_PATH, exc)


app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(predict.router)
app.include_router(records.router)


