"""Database models using SQLModel."""

from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel


class Record(SQLModel, table=True):
    """Represents an ingested bus record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    route_id: str
    scheduled_time: datetime
    actual_time: Optional[datetime] = None
    weather: str
    passenger_count: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cleaned: bool = Field(default=False)
    delay_minutes: Optional[float] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False))
    )


class Prediction(SQLModel, table=True):
    """Stores predictions linked to a record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    record_id: int = Field(foreign_key="record.id")
    predicted_delay: float
    model_version: str
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False))
    )




