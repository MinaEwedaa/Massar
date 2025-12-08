"""Pydantic schemas for requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecordIn(BaseModel):
    """Incoming record payload from drivers or clients."""

    route_id: str = Field(..., description="Route identifier e.g. R1 or Route-1")
    scheduled_time: str = Field(..., description="Scheduled timestamp in flexible formats")
    actual_time: Optional[str] = Field(
        None, description="Actual timestamp in flexible formats or null if unknown"
    )
    weather: str = Field(..., description="Weather description")
    passenger_count: Optional[int] = Field(
        None, description="Passenger count, may be null and will be imputed"
    )
    latitude: Optional[float] = Field(None, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, description="Longitude in decimal degrees")


class RecordOut(BaseModel):
    """Record representation returned to clients."""

    id: int
    route_id: str
    scheduled_time: datetime
    actual_time: Optional[datetime]
    weather: str
    passenger_count: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    cleaned: bool
    delay_minutes: Optional[float]
    created_at: datetime

    class Config:
        orm_mode = True


class PredictOut(BaseModel):
    """Prediction response."""

    record_id: Optional[int] = Field(None, description="Record identifier if persisted")
    predicted_delay: float
    model_version: str


class HealthOut(BaseModel):
    """Health and readiness response."""

    status: str
    model_loaded: bool
    model_path: str




