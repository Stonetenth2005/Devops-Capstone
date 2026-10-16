"""Test fixtures: every test runs against a fresh in-memory SQLite database, never PostgreSQL."""

import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def doctor(client):
    response = client.post("/api/doctors", json={"name": "Dr. Test", "specialty": "Cardiology", "room": "204"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def appointment(client, doctor):
    response = client.post(
        "/api/appointments",
        json={
            "patient_name": "Asha Verma",
            "patient_phone": "9876543210",
            "doctor_id": doctor["id"],
            "scheduled_at": "2030-01-15T10:00:00Z",
            "reason": "Annual check-up",
        },
    )
    assert response.status_code == 201
    return response.json()
