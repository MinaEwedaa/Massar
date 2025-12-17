"""Record retrieval and update endpoints."""

from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ...cleaning import clean_record
from ...crud import create_prediction, get_record, list_predictions_with_records, list_records
from ...db import get_session
from ...feature_engineering import create_features
from ...model_server import ModelNotLoadedError, model_server
from ...models import Record
from ...schemas import PredictionWithRecord, RecordOut

router = APIRouter(prefix="/api/v1/records", tags=["records"])


@router.get("/", response_model=list[RecordOut])
def list_records_endpoint(
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[RecordOut]:
    """List records with pagination."""
    records = list_records(session, limit=limit, offset=offset)
    return [RecordOut.from_orm(r) for r in records]


@router.get("/predictions", response_model=list[PredictionWithRecord])
def list_predictions_endpoint(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[PredictionWithRecord]:
    """List recent predictions with their associated records."""
    predictions_with_records = list_predictions_with_records(session, limit=limit, offset=offset)
    return [
        PredictionWithRecord(
            id=pred.id,
            predicted_delay=pred.predicted_delay,
            model_version=pred.model_version,
            created_at=pred.created_at,
            record=RecordOut.from_orm(rec),
        )
        for pred, rec in predictions_with_records
    ]


@router.get("/{record_id}", response_model=RecordOut)
def read_record(record_id: int, session: Session = Depends(get_session)) -> RecordOut:
    """Fetch a record by id."""
    record = get_record(session, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return RecordOut.from_orm(record)


@router.put("/{record_id}", response_model=RecordOut)
def update_record(
    record_id: int,
    payload: Dict[str, Optional[str]],
    repredict: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> RecordOut:
    """Update mutable fields of a record and optionally rerun prediction."""
    record = session.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    allowed_fields = {"passenger_count", "weather", "actual_time"}
    updates = {k: v for k, v in payload.items() if k in allowed_fields}
    base_data = record.dict()
    base_data.update(updates)

    cleaned = clean_record(base_data, session)
    for key, value in cleaned.items():
        setattr(record, key, value)
    session.add(record)
    session.commit()
    session.refresh(record)

    if repredict and model_server.loaded:
        try:
            features = create_features(cleaned)
            prediction_value = float(model_server.predict(features)[0])
            create_prediction(session, record.id, prediction_value, model_server.model_version or "v1")
        except ModelNotLoadedError:
            pass

    return RecordOut.from_orm(record)




