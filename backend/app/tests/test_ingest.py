import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app import db
from app.main import app


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


def test_ingest_cleans_and_imputes(client: TestClient):
    payload = {
        "route_id": "Route-04",
        "scheduled_time": "2025-12-07 08:30",
        "actual_time": "8.45AM",
        "weather": "Clody",
        "passenger_count": 250,
        "latitude": 999,
        "longitude": 30,
    }
    response = client.post("/api/v1/records/ingest", json=payload)
    assert response.status_code in (201, 202)
    data = response.json()
    record = data["record"] if "record" in data else data
    assert record["route_id"] == "R4"
    assert record["weather"] == "cloudy"
    assert record["passenger_count"] == 10
    assert record["latitude"] is None




