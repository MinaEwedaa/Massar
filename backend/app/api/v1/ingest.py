"""Record ingestion endpoints."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session

from ...cleaning import clean_record
from ...crud import create_prediction, create_record
from ...db import engine, get_session
from ...feature_engineering import create_features
from ...model_server import ModelNotLoadedError, model_server
from ...schemas import PredictOut, RecordIn, RecordOut

router = APIRouter(prefix="/api/v1/records", tags=["records"])
logger = logging.getLogger(__name__)


def _predict_and_store(record_id: int) -> None:
    """Background prediction task."""
    from ...models import Record  # local import to avoid cycles

    with Session(engine) as session:
        record = session.get(Record, record_id)
        if not record or not model_server.loaded:
            return
        try:
            features = create_features(record.dict())
            prediction_value = float(model_server.predict(features)[0])
            create_prediction(session, record_id, prediction_value, model_server.model_version or "v1")
        except ModelNotLoadedError:
            return


@router.post("/ingest", status_code=201)
def ingest_record(record_in: RecordIn, session: Session = Depends(get_session)) -> Any:
    """Ingest a single record synchronously."""
    cleaned = clean_record(record_in.dict(), session)
    record = create_record(session, cleaned)

    prediction_payload: Optional[PredictOut] = None
    if model_server.loaded:
        try:
            features = create_features(cleaned)
            prediction_value = float(model_server.predict(features)[0])
            prediction = create_prediction(
                session, record.id, prediction_value, model_server.model_version or "v1"
            )
            prediction_payload = PredictOut(
                record_id=record.id, predicted_delay=prediction_value, model_version=prediction.model_version
            )
            logger.info("Created prediction for record %s", record.id)
        except ModelNotLoadedError:
            logger.warning("Model not loaded during ingestion prediction")

    # Ensure datetime fields are JSON serializable for responses
    record_out = jsonable_encoder(RecordOut.from_orm(record))
    if prediction_payload:
        return {"record": record_out, "prediction": prediction_payload.dict()}
    if not model_server.loaded:
        return JSONResponse(status_code=202, content={"message": "Record stored but model not loaded", "record": record_out})
    return record_out


@router.post("/batch_ingest", status_code=202)
async def batch_ingest(
    records: List[RecordIn],
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Dict[str, int]:
    """Batch ingest records asynchronously, scheduling predictions."""
    ingested = 0
    scheduled = 0
    for record_in in records:
        cleaned = clean_record(record_in.dict(), session)
        record = create_record(session, cleaned)
        ingested += 1
        if model_server.loaded:
            scheduled += 1
            background_tasks.add_task(_predict_and_store, record.id)
    return {"ingested": ingested, "predictions_scheduled": scheduled}


