"""
test_predictions.py — Tests for GET /predictions/ endpoint.
"""

from unittest.mock import patch, MagicMock
from tests.conftest import VALID_SENSOR_PAYLOAD, TestingSessionLocal
from app.models.models import Prediction
from datetime import datetime, timezone


def _make_mock():
    m = MagicMock()
    m.predict_proba.return_value = [[0.05, 0.95]]
    return m


def _seed_predictions(machine_id: str, count: int, client):
    """Helper: POST /predict `count` times for a machine using a mock model."""
    mock = _make_mock()
    with patch("app.services.predict._model", mock):
        payload = {**VALID_SENSOR_PAYLOAD, "machine_id": machine_id}
        for _ in range(count):
            client.post("/predict", json=payload)


# ── Basic listing ──────────────────────────────────────────────────────────────

def test_list_predictions_empty(client):
    response = client.get("/predictions/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_predictions_returns_seeded(client, seeded_machine):
    _seed_predictions("TEST-001", 3, client)
    response = client.get("/predictions/")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_predictions_response_structure(client, seeded_machine):
    _seed_predictions("TEST-001", 1, client)
    data = client.get("/predictions/").json()
    record = data[0]
    for field in ["id", "machine_id", "failure_prediction", "failure_probability", "predicted_at"]:
        assert field in record, f"Missing field: {field}"


def test_list_predictions_ordered_newest_first(client, seeded_machine):
    _seed_predictions("TEST-001", 3, client)
    data = client.get("/predictions/").json()
    ids = [r["id"] for r in data]
    assert ids == sorted(ids, reverse=True)


# ── Filtering by machine_id ────────────────────────────────────────────────────

def test_filter_predictions_by_machine_id(client, seeded_machine):
    # Seed second machine
    client.post("/machines/", json={"machine_id": "OTHER-001", "name": "Other", "machine_type": "CNC"})
    _seed_predictions("TEST-001", 2, client)
    mock = _make_mock()
    with patch("app.services.predict._model", mock):
        client.post("/predict", json={**VALID_SENSOR_PAYLOAD, "machine_id": "OTHER-001"})

    response = client.get("/predictions/?machine_id=TEST-001")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(r["machine_id"] == "TEST-001" for r in data)


def test_filter_predictions_unknown_machine_returns_empty(client, seeded_machine):
    _seed_predictions("TEST-001", 2, client)
    response = client.get("/predictions/?machine_id=NONEXISTENT")
    assert response.status_code == 200
    assert response.json() == []


# ── Pagination ─────────────────────────────────────────────────────────────────

def test_predictions_pagination_limit(client, seeded_machine):
    _seed_predictions("TEST-001", 5, client)
    response = client.get("/predictions/?limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_predictions_pagination_skip(client, seeded_machine):
    _seed_predictions("TEST-001", 5, client)
    all_data = client.get("/predictions/?limit=5").json()
    skipped = client.get("/predictions/?skip=2&limit=5").json()
    assert len(skipped) == 3
    assert skipped[0]["id"] == all_data[2]["id"]


def test_predictions_max_limit_200(client, seeded_machine):
    response = client.get("/predictions/?limit=200")
    assert response.status_code == 200


def test_predictions_limit_over_200_returns_422(client):
    response = client.get("/predictions/?limit=201")
    assert response.status_code == 422


def test_predictions_negative_skip_returns_422(client):
    response = client.get("/predictions/?skip=-1")
    assert response.status_code == 422
