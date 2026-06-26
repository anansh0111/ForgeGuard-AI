"""
test_health.py — Tests for GET /health endpoint.
"""

from tests.conftest import VALID_SENSOR_PAYLOAD


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_structure(client):
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ForgeGuard AI Backend"
    assert "timestamp" in data


def test_health_timestamp_is_iso_string(client):
    response = client.get("/health")
    timestamp = response.json()["timestamp"]
    # Should be a parseable ISO 8601 datetime string
    from datetime import datetime
    parsed = datetime.fromisoformat(timestamp)
    assert parsed is not None
