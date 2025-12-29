"""Prediction endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlmodel import Session

from ...cleaning import clean_record
from ...crud import create_prediction, create_record
from ...db import get_session
from ...feature_engineering import create_features
from ...model_server import ModelNotLoadedError, model_server
from ...schemas import PredictOut, RecordIn, RecordOut

router = APIRouter(prefix="/api/v1", tags=["predict"])


@router.post("/predict", response_model=PredictOut)
async def predict_endpoint(
    payload: Dict[str, Any] = Body(...),
    persist: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> PredictOut:
    """Predict delay from cleaned record."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if not model_server.loaded:
            logger.error("Model not loaded")
            raise HTTPException(status_code=503, detail="Model not loaded")

        logger.info(f"Received prediction request: {payload}")
        record_in = RecordIn(**payload)
        cleaned = clean_record(record_in.dict(), session)
        logger.info(f"Cleaned record: {cleaned}")
        
        features = create_features(cleaned)
        logger.info(f"Features shape: {features.shape}, columns: {list(features.columns)}")
        
        # Use baseline predictor since model quality is poor (R² = 0.26)
        # TODO: Retrain with more data (need 1,000-5,000+ rows) for better model
        use_baseline = True  # Set to False to use the trained model (not recommended with current data)
        
        if use_baseline:
            logger.warning(
                "Using baseline predictor due to poor model quality. "
                "Model R² = 0.26, RMSE = 221 min. Need more training data."
            )
        
        prediction_value = float(model_server.predict(features, use_baseline=use_baseline)[0])
        logger.info(f"Prediction: {prediction_value} minutes (baseline={use_baseline})")

        record_id = None
        if persist:
            record = create_record(session, cleaned)
            record_id = record.id
            create_prediction(session, record_id, prediction_value, model_server.model_version or "v1")

        return PredictOut(record_id=record_id, predicted_delay=prediction_value, model_version=model_server.model_version or "v1")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in predict endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")




