"""
conftest.py — Shared pytest fixtures for ForgeGuard AI backend tests.

Strategy:
- Uses SQLite in-memory DB (no Postgres needed for tests).
- StaticPool ensures ALL connections share the same in-memory database instance
  (without it, each new connection gets a fresh empty DB — tables vanish!).
- Overrides the DB dependency so every test gets a clean, isolated session.
- Mocks the LightGBM model so /predict tests never touch the real .pkl file.
- Provides a seeded machine ("TEST-001") so API tests can focus on behaviour.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.models.models import Machine

# ── In-memory SQLite engine with StaticPool ───────────────────────────────────
# StaticPool: all connections reuse the SAME underlying connection,
# so tables created here are visible to every session in the test suite.
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Override DB dependency ─────────────────────────────────────────────────────
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ── Mock LightGBM model ────────────────────────────────────────────────────────
def make_mock_model(probability: float = 0.95):
    """Return a mock model whose predict_proba always returns [[1-p, p]]."""
    mock = MagicMock()
    mock.predict_proba.return_value = [[1 - probability, probability]]
    return mock


# ── Session-scoped: create tables once ────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ── Function-scoped: fresh DB state per test ──────────────────────────────────
@pytest.fixture(autouse=True)
def clean_db():
    """
    Wipe and recreate all tables between tests for full isolation.
    drop_all + create_all is simpler and safer than per-table DELETE
    (avoids FK ordering issues and missing-table errors).
    """
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# ── Seeded machine fixture ─────────────────────────────────────────────────────
@pytest.fixture
def seeded_machine():
    """Insert a test machine and return its machine_id."""
    db = TestingSessionLocal()
    machine = Machine(
        machine_id="TEST-001",
        name="Test CNC Unit",
        machine_type="CNC",
        location="Test Bay",
        status="operational",
    )
    db.add(machine)
    db.commit()
    db.close()
    return "TEST-001"


# ── Test client ────────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ── Test client with mocked predict model ─────────────────────────────────────
@pytest.fixture
def client_with_model(seeded_machine):
    """TestClient with a high-probability mock model (prob=0.95 → critical)."""
    mock_model = make_mock_model(probability=0.95)
    with patch("app.services.predict._model", mock_model):
        with TestClient(app) as c:
            yield c, seeded_machine


@pytest.fixture
def client_healthy_model(seeded_machine):
    """TestClient with a low-probability mock model (prob=0.10 → healthy)."""
    mock_model = make_mock_model(probability=0.10)
    with patch("app.services.predict._model", mock_model):
        with TestClient(app) as c:
            yield c, seeded_machine


# ── Sensor payload helper ──────────────────────────────────────────────────────
VALID_SENSOR_PAYLOAD = {
    "machine_id": "TEST-001",
    "Air_temperature__K_": 300.5,
    "Process_temperature__K_": 310.2,
    "Rotational_speed__rpm_": 1500.0,
    "Torque__Nm_": 40.0,
    "Tool_wear__min_": 120.0,
}
