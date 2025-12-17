"""CRUD operations."""

from typing import List, Optional

from sqlmodel import Session, select

from .models import Prediction, Record


def create_record(session: Session, cleaned_record_dict: dict) -> Record:
    """Insert a cleaned record."""
    record = Record(**cleaned_record_dict)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_record(session: Session, record_id: int) -> Optional[Record]:
    """Retrieve a record by id."""
    return session.get(Record, record_id)


def list_records(session: Session, limit: int = 100, offset: int = 0) -> List[Record]:
    """List records with pagination."""
    statement = select(Record).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def create_prediction(session: Session, record_id: int, predicted_delay: float, model_version: str) -> Prediction:
    """Store a prediction linked to a record."""
    prediction = Prediction(record_id=record_id, predicted_delay=predicted_delay, model_version=model_version)
    session.add(prediction)
    session.commit()
    session.refresh(prediction)
    return prediction


def list_predictions_with_records(session: Session, limit: int = 20, offset: int = 0) -> List[tuple[Prediction, Record]]:
    """List predictions with their associated records."""
    statement = (
        select(Prediction, Record)
        .join(Record, Prediction.record_id == Record.id)
        .order_by(Prediction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    results = session.exec(statement).all()
    return [(pred, rec) for pred, rec in results]




