"""Application configuration settings."""

from dataclasses import dataclass

import os
from pathlib import Path

# Get the absolute path to the model file
# __file__ is backend/app/config.py, so we go up one level to backend/
_BACKEND_DIR = Path(__file__).parent.parent.resolve()
MODEL_PATH = os.getenv("MODEL_PATH", str(_BACKEND_DIR / "model" / "model.joblib"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/db.sqlite")
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




