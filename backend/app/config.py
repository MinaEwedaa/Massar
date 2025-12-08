"""Application configuration settings."""

from dataclasses import dataclass

MODEL_PATH = "./model/model.joblib"
DATABASE_URL = "sqlite:///./data/db.sqlite"
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




