"""Model loading and prediction service."""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import joblib
import pandas as pd


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

    def predict(self, df: pd.DataFrame):
        """Run prediction with the loaded model."""
        if not self._loaded:
            raise ModelNotLoadedError("Model not loaded")
        return self._loaded.model.predict(df)


# Shared model server instance
model_server = ModelServer()


