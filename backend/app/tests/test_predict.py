import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app import db
from app.main import app
from app.model_server import LoadedModel, model_server


class DummyModel:
    def predict(self, X):
        return [0 for _ in range(len(X))]


@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{test_db}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[db.get_session] = override_get_session
    db.engine = engine
    return TestClient(app)


def test_predict_without_model_returns_503(client: TestClient):
    model_server._loaded = None
    payload = {
        "route_id": "3",
        "scheduled_time": "08:30",
        "actual_time": "08:50",
        "weather": "sun",
        "passenger_count": 12,
        "latitude": 25.7,
        "longitude": 32.64,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 503


def test_predict_with_dummy_model(client: TestClient):
    model_server._loaded = LoadedModel(model=DummyModel(), version="test")
    payload = {
        "route_id": "3",
        "scheduled_time": "08:30",
        "actual_time": "08:50",
        "weather": "sun",
        "passenger_count": 12,
        "latitude": 25.7,
        "longitude": 32.64,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_delay"] == 0
    assert data["record_id"] is None




