"""Utility to build a dummy model for local testing."""

import os

import joblib

from .dummy_model import DummyModel


if __name__ == "__main__":
    os.makedirs("./model", exist_ok=True)
    joblib.dump(DummyModel(), "./model/model.joblib")
    print("Dummy model saved to ./model/model.joblib")




