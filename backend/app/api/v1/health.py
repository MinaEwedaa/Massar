"""Health and metrics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from ...config import MODEL_PATH
from ...db import get_session
from ...model_server import model_server
from ...models import Prediction, Record
from ...schemas import HealthOut

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    """Return service health and model status."""
    return HealthOut(status="ok", model_loaded=model_server.loaded, model_path=MODEL_PATH)


@router.get("/metrics")
def metrics(session: Session = Depends(get_session)) -> dict:
    """Return simple service metrics."""
    total_records = session.exec(select(func.count()).select_from(Record)).one()
    total_predictions = session.exec(select(func.count()).select_from(Prediction)).one()
    last_version = session.exec(
        select(Prediction.model_version).order_by(Prediction.created_at.desc())
    ).first()
    return {
        "total_records": total_records[0] if isinstance(total_records, tuple) else total_records,
        "total_predictions": total_predictions[0] if isinstance(total_predictions, tuple) else total_predictions,
        "last_model_version": last_version,
    }


