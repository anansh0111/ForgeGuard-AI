"""
test_predict.py — Tests for POST /predict endpoint.

Uses client_with_model fixture which injects a mock LightGBM model (prob=0.95).
Uses client_healthy_model fixture which injects a low-prob mock (prob=0.10).
"""

from tests.conftest import VALID_SENSOR_PAYLOAD


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_predict_returns_200(client_with_model):
    client, machine_id = client_with_model
    response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    assert response.status_code == 200


def test_predict_response_structure(client_with_model):
    client, machine_id = client_with_model
    response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    data = response.json()
    for field in ["machine_id", "failure_prediction", "failure_probability", "prediction_id", "predicted_at"]:
        assert field in data, f"Missing field: {field}"


def test_predict_machine_id_in_response(client_with_model):
    client, machine_id = client_with_model
    response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    assert response.json()["machine_id"] == "TEST-001"


def test_predict_high_probability_returns_failure_1(client_with_model):
    """Mock returns prob=0.95 → failure_prediction should be 1."""
    client, _ = client_with_model
    response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    data = response.json()
    assert data["failure_prediction"] == 1
    assert data["failure_probability"] >= 0.5


def test_predict_low_probability_returns_failure_0(client_healthy_model):
    """Mock returns prob=0.10 → failure_prediction should be 0."""
    client, _ = client_healthy_model
    response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    data = response.json()
    assert data["failure_prediction"] == 0
    assert data["failure_probability"] < 0.5


def test_predict_assigns_prediction_id(client_with_model):
    client, _ = client_with_model
    response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    assert isinstance(response.json()["prediction_id"], int)
    assert response.json()["prediction_id"] > 0


def test_predict_sequential_ids_increment(client_with_model):
    client, _ = client_with_model
    r1 = client.post("/predict", json=VALID_SENSOR_PAYLOAD).json()
    r2 = client.post("/predict", json=VALID_SENSOR_PAYLOAD).json()
    assert r2["prediction_id"] > r1["prediction_id"]


def test_predict_auto_computes_temp_difference(client_with_model):
    """Without temp_difference supplied, endpoint computes it from temps."""
    client, _ = client_with_model
    payload = dict(VALID_SENSOR_PAYLOAD)
    payload.pop("temp_difference", None)  # ensure it's absent
    response = client.post("/predict", json=payload)
    assert response.status_code == 200


def test_predict_with_explicit_temp_difference(client_with_model):
    client, _ = client_with_model
    payload = {**VALID_SENSOR_PAYLOAD, "temp_difference": 8.5}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200


# ── Error cases ────────────────────────────────────────────────────────────────

def test_predict_unknown_machine_returns_404(client_with_model):
    client, _ = client_with_model
    payload = {**VALID_SENSOR_PAYLOAD, "machine_id": "GHOST-999"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_predict_missing_fields_returns_422(client_with_model):
    client, _ = client_with_model
    # Missing all sensor fields
    response = client.post("/predict", json={"machine_id": "TEST-001"})
    assert response.status_code == 422


def test_predict_model_missing_returns_503(client, seeded_machine):
    """When _model is None and model file doesn't exist, should return 503."""
    from unittest.mock import patch
    import app.services.predict as svc
    # Reset the cached model and patch path to non-existent file
    with patch.object(svc, "_model", None):
        with patch("app.core.config.get_settings") as mock_settings:
            mock_settings.return_value.model_path = "/nonexistent/model.pkl"
            # Patch _load_model to raise FileNotFoundError directly
            with patch.object(svc, "_load_model", side_effect=FileNotFoundError("Model not found")):
                response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    assert response.status_code == 503


# ── Probability boundary ───────────────────────────────────────────────────────

def test_predict_exactly_50_percent_is_failure(client, seeded_machine):
    """prob = 0.5 exactly → failure_prediction = 1 (threshold is >=0.5)."""
    from unittest.mock import MagicMock, patch
    mock = MagicMock()
    mock.predict_proba.return_value = [[0.5, 0.5]]
    with patch("app.services.predict._model", mock):
        response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    assert response.json()["failure_prediction"] == 1


def test_predict_just_below_50_percent_is_healthy(client, seeded_machine):
    """prob = 0.4999 → failure_prediction = 0."""
    from unittest.mock import MagicMock, patch
    mock = MagicMock()
    mock.predict_proba.return_value = [[0.5001, 0.4999]]
    with patch("app.services.predict._model", mock):
        response = client.post("/predict", json=VALID_SENSOR_PAYLOAD)
    assert response.json()["failure_prediction"] == 0
