"""Feature engineering utilities."""

from datetime import datetime
from typing import Dict

import pandas as pd

from .cleaning import _normalize_route, normalize_weather


def _time_of_day(hour: int) -> str:
    """Categorize hour into time-of-day buckets."""
    if 5 <= hour <= 11:
        return "morning"
    if 12 <= hour <= 17:
        return "afternoon"
    if 18 <= hour <= 22:
        return "evening"
    return "night"


def _weather_severity(weather: str) -> int:
    """Map weather string to severity index."""
    severity = {"sunny": 0, "clear": 0, "cloudy": 1, "fog": 1, "rainy": 2, "snow": 3, "unknown": 1}
    return severity.get(normalize_weather(weather), 1)


def create_features(cleaned_record: Dict[str, object]) -> pd.DataFrame:
    """Create a single-row DataFrame of model features from a cleaned record."""
    scheduled: datetime = cleaned_record.get("scheduled_time")
    delay_minutes = cleaned_record.get("delay_minutes") or 0.0
    hour = scheduled.hour if scheduled else 0
    day_of_week = scheduled.weekday() if scheduled else 0
    is_weekend = 1 if day_of_week >= 5 else 0

    features = {
        "day_of_week": day_of_week,
        "delay_minutes_if_any": float(delay_minutes),
        "hour_of_day": hour,
        "is_weekend": is_weekend,
        "latitude": cleaned_record.get("latitude"),
        "longitude": cleaned_record.get("longitude"),
        "passenger_count": cleaned_record.get("passenger_count"),
        "route_num": int(_normalize_route(str(cleaned_record.get("route_id", "")))[1:] or 0),
        "time_of_day": _time_of_day(hour),
        "weather_severity": _weather_severity(str(cleaned_record.get("weather", "unknown"))),
    }

    # Ensure deterministic column ordering
    ordered = dict(sorted(features.items()))
    df = pd.DataFrame([ordered])
    return df




