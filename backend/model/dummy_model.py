"""Reusable dummy model for local testing."""


class DummyModel:
    """Simple model returning zeros."""

    def predict(self, X):
        return [0.0 for _ in range(len(X))]

