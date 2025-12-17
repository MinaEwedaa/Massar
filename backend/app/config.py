"""Application configuration settings."""

from dataclasses import dataclass

import os
from pathlib import Path

# Get the absolute path to the model file
# __file__ is backend/app/config.py, so we go up one level to backend/
_BACKEND_DIR = Path(__file__).parent.parent.resolve()

# Handle empty string from environment variable (Railway might set it to empty)
# If MODEL_PATH is not set or is empty, use default path
_MODEL_PATH_ENV = os.getenv("MODEL_PATH", "").strip()
if not _MODEL_PATH_ENV:
    MODEL_PATH = str(_BACKEND_DIR / "model" / "model.joblib")
else:
    MODEL_PATH = _MODEL_PATH_ENV

# Handle empty string from environment variable (Railway might set it to empty)
# If DATABASE_URL is not set or is empty, use SQLite default
_DB_URL = os.getenv("DATABASE_URL", "").strip()
if not _DB_URL:
    # Ensure data directory exists for SQLite
    _DATA_DIR = _BACKEND_DIR / "data"
    _DATA_DIR.mkdir(exist_ok=True)
    DATABASE_URL = "sqlite:///./data/db.sqlite"
else:
    DATABASE_URL = _DB_URL
ALLOWED_WEATHER = ["sunny", "cloudy", "rainy", "snow", "clear", "fog"]
MAX_PASSENGER = 200
MIN_PASSENGER = 0


@dataclass
class Settings:
    """Typed settings container."""

    model_path: str = MODEL_PATH
    database_url: str = DATABASE_URL
    allowed_weather: list[str] | None = None
    max_passenger: int = MAX_PASSENGER
    min_passenger: int = MIN_PASSENGER


def get_settings() -> Settings:
    """Return application settings."""
    return Settings(allowed_weather=ALLOWED_WEATHER)




