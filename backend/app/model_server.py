"""Model loading and prediction service."""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import joblib
import numpy as np
import pandas as pd

# Baseline statistics from training data (used as fallback)
# These are computed from cleaned_transport_dataset.csv
TRAINING_DELAY_MEDIAN = 61.0  # Median delay in minutes
TRAINING_DELAY_MEAN = 44.5    # Mean delay in minutes
TRAINING_DELAY_STD = 191.8    # Standard deviation


class ModelNotLoadedError(Exception):
    """Raised when prediction requested without a loaded model."""


@dataclass
class LoadedModel:
    """Container for loaded model and metadata."""

    model: object
    version: str


class ModelServer:
    """Handles model lifecycle and predictions."""

    def __init__(self) -> None:
        self._loaded: Optional[LoadedModel] = None
        self.logger = logging.getLogger(__name__)

    @property
    def loaded(self) -> bool:
        """Return True if model is loaded."""
        return self._loaded is not None

    @property
    def model_version(self) -> Optional[str]:
        """Return loaded model version if available."""
        return self._loaded.version if self._loaded else None

    def load_model(self, path: str) -> None:
        """Load model from disk."""
        if not os.path.exists(path):
            self.logger.warning("Model file missing at %s", path)
            self._loaded = None
            return
        model = joblib.load(path)
        mod_time = os.path.getmtime(path)
        version = datetime.utcfromtimestamp(mod_time).isoformat() if mod_time else "v1"
        self._loaded = LoadedModel(model=model, version=version)
        self.logger.info("Model loaded from %s (version %s)", path, version)

    def predict(self, df: pd.DataFrame, use_baseline: bool = False):
        """Run prediction with the loaded model.
        
        Args:
            df: Feature dataframe
            use_baseline: If True, use simple baseline instead of model
                          (useful when model quality is poor)
        
        Returns:
            Array of predictions
        """
        if not self._loaded:
            raise ModelNotLoadedError("Model not loaded")
        
        if use_baseline:
            # Use rule-based baseline that adjusts for weather and time
            # This is more reliable than the poor-quality model (R² = 0.26)
            predictions = self._baseline_predict(df)
            self.logger.info(f"Using baseline predictor: {predictions[0]:.1f} min")
            return predictions
        
        predictions = self._loaded.model.predict(df)
        
        # Clamp predictions to reasonable range
        # Based on training data: -1359 to 179 minutes, but clamp to -60 to 300 for sanity
        predictions = np.clip(predictions, -60.0, 300.0)
        
        return predictions
    
    def _baseline_predict(self, df: pd.DataFrame) -> np.ndarray:
        """Simple rule-based baseline predictor.
        
        Adjusts median delay based on weather severity and time of day.
        More reliable than the poor-quality linear regression model.
        """
        predictions = []
        
        for _, row in df.iterrows():
            base_delay = TRAINING_DELAY_MEDIAN  # Start with median (61 min)
            
            # Adjust for weather (higher severity = more delay)
            weather_severity = row.get('weather_severity', 2)
            if weather_severity == 3:  # Rainy/Snow
                base_delay += 20
            elif weather_severity == 2:  # Cloudy/Fog
                base_delay += 10
            # weather_severity == 1 (Clear/Sunny) stays at base
            
            # Adjust for time of day (evening rush hour = more delay)
            if row.get('time_of_day_evening', 0) == 1:  # Evening (6-10 PM)
                base_delay += 15
            elif row.get('time_of_day_afternoon', 0) == 1:  # Afternoon (12-5 PM)
                base_delay += 5
            # Morning and night stay at base
            
            # Adjust for weekend (usually less traffic)
            if row.get('is_weekend', 0) == 1:
                base_delay -= 10
            
            # Clamp to reasonable range
            base_delay = max(0, min(180, base_delay))
            predictions.append(base_delay)
        
        return np.array(predictions)


# Shared model server instance
model_server = ModelServer()


