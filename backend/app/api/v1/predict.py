"""Prediction endpoints."""

from typing import Any, Dict, Optional

import pandas as pd
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query
from sqlmodel import Session

from ...cleaning import clean_record
from ...crud import create_prediction, create_record
from ...db import get_session
from ...feature_engineering import create_features
from ...model_server import ModelNotLoadedError, model_server
from ...schemas import PredictOut, RecordIn, RecordOut

router = APIRouter(prefix="/api/v1", tags=["predict"])

EXPECTED_FEATURE_COLUMNS = [
    "day_of_week",
    "delay_minutes_if_any",
    "hour_of_day",
    "is_weekend",
    "latitude",
    "longitude",
    "passenger_count",
    "route_num",
    "time_of_day",
    "weather_severity",
]


@router.post("/predict", response_model=PredictOut)
async def predict_endpoint(
    payload: Dict[str, Any] = Body(...),
    x_raw_features: Optional[str] = Header(default=None),
    persist: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> PredictOut:
    """Predict delay either from raw features or cleaned record."""
    if not model_server.loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")

    is_raw = x_raw_features.lower() == "true" if x_raw_features else False

    if is_raw:
        missing = set(EXPECTED_FEATURE_COLUMNS) - set(payload.keys())
        extra = set(payload.keys()) - set(EXPECTED_FEATURE_COLUMNS)
        if missing or extra:
            raise HTTPException(
                status_code=400,
                detail=f"Feature columns mismatch. Missing: {missing}, Extra: {extra}",
            )
        df = pd.DataFrame([dict(sorted(payload.items()))])
        prediction_value = float(model_server.predict(df)[0])
        return PredictOut(record_id=None, predicted_delay=prediction_value, model_version=model_server.model_version or "v1")

    record_in = RecordIn(**payload)
    cleaned = clean_record(record_in.dict(), session)
    features = create_features(cleaned)
    prediction_value = float(model_server.predict(features)[0])

    record_id = None
    if persist:
        record = create_record(session, cleaned)
        record_id = record.id
        create_prediction(session, record_id, prediction_value, model_server.model_version or "v1")

    return PredictOut(record_id=record_id, predicted_delay=prediction_value, model_version=model_server.model_version or "v1")




