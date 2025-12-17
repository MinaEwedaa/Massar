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
    severity = {"sunny": 1, "clear": 1, "cloudy": 2, "fog": 2, "rainy": 3, "snow": 3, "unknown": 2}
    return severity.get(normalize_weather(weather), 2)


def extract_route_number(route_id: str) -> int:
    """Extract numeric part from route_id (e.g., 'R3' -> 3)."""
    try:
        # Remove 'R' prefix and convert to int
        route_str = str(route_id).replace('R', '').strip()
        return int(route_str) if route_str else 0
    except (ValueError, AttributeError):
        return 0


def _get_route_frequency(route_id: str) -> int:
    """Get route frequency - default values based on route patterns."""
    # This is a simplified version - in production, this would come from a database
    # For now, we'll use a default based on route number
    route_num = extract_route_number(route_id)
    # Common frequencies: R1-R5: high frequency, R6+: lower frequency
    if route_num <= 5:
        return 100
    elif route_num <= 10:
        return 50
    else:
        return 30


def create_features(cleaned_record: Dict[str, object]) -> pd.DataFrame:
    """Create a single-row DataFrame of model features from a cleaned record.
    
    Feature order must match exactly what the model was trained with:
    1. hour, 2. day_of_week, 3. is_weekend, 4. weather_severity, 5. route_frequency,
    6. passenger_count, 7. latitude, 8. longitude, 9. route_num,
    10. time_of_day_afternoon, 11. time_of_day_evening, 12. time_of_day_morning, 13. time_of_day_night
    """
    scheduled: datetime = cleaned_record.get("scheduled_time")
    hour = scheduled.hour if scheduled else 0
    day_of_week = scheduled.weekday() if scheduled else 0
    is_weekend = 1 if day_of_week >= 5 else 0
    time_of_day_str = _time_of_day(hour)
    
    route_id = str(cleaned_record.get("route_id", ""))
    route_num = extract_route_number(route_id)
    route_frequency = _get_route_frequency(route_id)

    # Create features in the EXACT order the model expects
    # This order matches what pd.get_dummies() produces when combined with base features
    features_dict = {
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "weather_severity": _weather_severity(str(cleaned_record.get("weather", "unknown"))),
        "route_frequency": route_frequency,
        "passenger_count": float(cleaned_record.get("passenger_count") or 0),
        "latitude": float(cleaned_record.get("latitude") or 0),
        "longitude": float(cleaned_record.get("longitude") or 0),
        "route_num": route_num,
        "time_of_day_afternoon": 1 if time_of_day_str == "afternoon" else 0,
        "time_of_day_evening": 1 if time_of_day_str == "evening" else 0,
        "time_of_day_morning": 1 if time_of_day_str == "morning" else 0,
        "time_of_day_night": 1 if time_of_day_str == "night" else 0,
    }

    # Create DataFrame with features in the exact order (don't sort!)
    # The order here must match the training script's output
    df = pd.DataFrame([features_dict])
    
    # Ensure columns are in the correct order (matching model.feature_names_in_)
    expected_columns = [
        "hour", "day_of_week", "is_weekend", "weather_severity", "route_frequency",
        "passenger_count", "latitude", "longitude", "route_num",
        "time_of_day_afternoon", "time_of_day_evening", "time_of_day_morning", "time_of_day_night"
    ]
    df = df[expected_columns]
    
    return df




