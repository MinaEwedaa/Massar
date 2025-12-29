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
    """Extract numeric part from route_id (e.g., 'R3' -> 3).
    
    Clamps route numbers to training range (1-4) to prevent out-of-distribution predictions.
    Routes outside this range will be capped to the nearest valid value.
    """
    try:
        # Remove 'R' prefix and convert to int
        route_str = str(route_id).replace('R', '').strip()
        route_num = int(route_str) if route_str else 0
        
        # Clamp to training range (model was trained on R1-R4)
        # This prevents extreme predictions for routes not seen during training
        MAX_TRAINED_ROUTE = 4
        MIN_TRAINED_ROUTE = 1
        
        if route_num > MAX_TRAINED_ROUTE:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Route number {route_num} exceeds training range (1-4). "
                f"Clamping to {MAX_TRAINED_ROUTE} to prevent out-of-distribution prediction."
            )
            return MAX_TRAINED_ROUTE
        elif route_num < MIN_TRAINED_ROUTE:
            return MIN_TRAINED_ROUTE if route_num > 0 else 0
        
        return route_num
    except (ValueError, AttributeError):
        return 0


def _get_route_frequency(route_id: str) -> int:
    """Get route frequency - default values based on route patterns."""
    # This is a simplified version - in production, this would come from a database
    # For now, we'll use a default based on route number
    route_num = extract_route_number(route_id)
    # Model was trained on R1-R4, all with high frequency
    # Use high frequency for all routes in training range
    if route_num <= 4:
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

    # Use median GPS coordinates from training data if missing
    # Training data has no missing coordinates, so 0,0 would be out-of-distribution
    TRAINING_LAT_MEDIAN = 24.52131986
    TRAINING_LON_MEDIAN = 32.53798372
    
    latitude = cleaned_record.get("latitude")
    longitude = cleaned_record.get("longitude")
    
    # If coordinates are None or invalid (0,0), use training median
    if latitude is None or (latitude == 0 and longitude == 0):
        import logging
        logger = logging.getLogger(__name__)
        if latitude is None or longitude is None:
            logger.warning(
                "Missing GPS coordinates. Using training data median "
                f"({TRAINING_LAT_MEDIAN}, {TRAINING_LON_MEDIAN}) to prevent out-of-distribution prediction."
            )
        latitude = TRAINING_LAT_MEDIAN if latitude is None or latitude == 0 else latitude
        longitude = TRAINING_LON_MEDIAN if longitude is None or longitude == 0 else longitude

    # Create features in the EXACT order the model expects
    # This order matches what pd.get_dummies() produces when combined with base features
    features_dict = {
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "weather_severity": _weather_severity(str(cleaned_record.get("weather", "unknown"))),
        "route_frequency": route_frequency,
        "passenger_count": float(cleaned_record.get("passenger_count") or 0),
        "latitude": float(latitude),
        "longitude": float(longitude),
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




