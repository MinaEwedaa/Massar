"""Deterministic cleaning and imputation utilities."""

import logging
import re
from datetime import datetime, time
from statistics import median
from typing import Any, Dict, Optional

from dateutil import parser
from sqlmodel import Session, select

from . import config
from .models import Record

logger = logging.getLogger(__name__)


def _parse_time_only(value: str) -> Optional[datetime]:
    """Parse time-only strings by attaching today's date in UTC."""
    value = value.strip()
    today = datetime.utcnow().date()
    time_match_colon = re.match(r"^(?P<hour>\d{1,2}):(?P<minute>\d{2})$", value)
    time_match_compact = re.match(r"^(?P<hour>\d{1,2})(?P<minute>\d{2})$", value)
    time_match_ampm = re.match(r"^(?P<hour>\d{1,2})[.:](?P<minute>\d{2})(?P<ampm>[AaPp][Mm])$", value)

    parsed_time: Optional[time] = None
    if time_match_colon:
        parsed_time = time(int(time_match_colon.group("hour")), int(time_match_colon.group("minute")))
    elif time_match_compact:
        parsed_time = time(int(time_match_compact.group("hour")), int(time_match_compact.group("minute")))
    elif time_match_ampm:
        hour = int(time_match_ampm.group("hour"))
        minute = int(time_match_ampm.group("minute"))
        ampm = time_match_ampm.group("ampm").lower()
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        parsed_time = time(hour, minute)

    if parsed_time:
        return datetime.combine(today, parsed_time)
    return None


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse various timestamp formats into timezone-naive datetime."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None

    time_only = _parse_time_only(value)
    if time_only:
        return time_only

    try:
        dt = parser.parse(value)
        return dt.replace(tzinfo=None)
    except (ValueError, TypeError):
        logger.warning("Failed to parse datetime string '%s'", value)
        return None


def normalize_weather(value: str) -> str:
    """Normalize weather strings to allowed values or 'unknown'."""
    normalized = value.strip().lower()
    typo_map = {"clody": "cloudy", "sun": "sunny", "sunny": "sunny", "sunny ": "sunny", "coudy": "cloudy"}
    if normalized in typo_map:
        normalized = typo_map[normalized]
    if normalized.upper() == "SUN":
        normalized = "sunny"
    if normalized not in config.ALLOWED_WEATHER:
        return "unknown"
    return normalized


def _median_passenger(session: Session) -> int:
    """Compute median passenger count or default to 10."""
    counts = session.exec(
        select(Record.passenger_count).where(Record.passenger_count.is_not(None))
    ).all()
    valid_counts = [c for c in counts if c is not None]
    if not valid_counts:
        return 10
    return int(median(valid_counts))


def _clean_passenger_count(raw_value: Optional[int], session: Session) -> int:
    """Validate and impute passenger count."""
    if raw_value is None or raw_value < config.MIN_PASSENGER or raw_value > config.MAX_PASSENGER:
        imputed = _median_passenger(session)
        logger.info("Imputing passenger_count with median/default %s", imputed)
        return imputed
    return raw_value


def _validate_gps(lat: Optional[float], lon: Optional[float]) -> tuple[Optional[float], Optional[float]]:
    """Validate latitude and longitude ranges."""
    valid_lat = lat if lat is not None and -90 <= lat <= 90 else None
    valid_lon = lon if lon is not None and -180 <= lon <= 180 else None
    if lat is not None and valid_lat is None:
        logger.info("Invalid latitude %s set to None", lat)
    if lon is not None and valid_lon is None:
        logger.info("Invalid longitude %s set to None", lon)
    return valid_lat, valid_lon


def _normalize_route(route_id: str) -> str:
    """Normalize route identifiers to R{int} format."""
    digits = re.findall(r"\d+", route_id)
    route_num = int(digits[0]) if digits else 0
    return f"R{route_num}"


def _compute_delay(scheduled: Optional[datetime], actual: Optional[datetime]) -> Optional[float]:
    """Compute delay in minutes if both times present."""
    if scheduled and actual:
        return (actual - scheduled).total_seconds() / 60.0
    return None


def clean_record(record_in: Dict[str, Any], db_session: Session) -> Dict[str, Any]:
    """Clean and impute a record according to deterministic rules."""
    scheduled_dt = parse_datetime(record_in.get("scheduled_time"))
    actual_dt = parse_datetime(record_in.get("actual_time"))
    weather = normalize_weather(str(record_in.get("weather", "")))
    raw_passenger = record_in.get("passenger_count")
    try:
        passenger_val = int(raw_passenger) if raw_passenger is not None else None
    except (TypeError, ValueError):
        passenger_val = None
    passenger_count = _clean_passenger_count(passenger_val, db_session)
    latitude, longitude = _validate_gps(record_in.get("latitude"), record_in.get("longitude"))
    route_id = _normalize_route(str(record_in.get("route_id", "")))
    delay_minutes = _compute_delay(scheduled_dt, actual_dt)

    cleaned_record = {
        "route_id": route_id,
        "scheduled_time": scheduled_dt,
        "actual_time": actual_dt,
        "weather": weather,
        "passenger_count": passenger_count,
        "latitude": latitude,
        "longitude": longitude,
        "cleaned": True,
        "delay_minutes": delay_minutes,
    }
    logger.info("Cleaned record for route %s with delay %s", route_id, delay_minutes)
    return cleaned_record


