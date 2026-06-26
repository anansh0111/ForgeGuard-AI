"""
test_recommend.py — Tests for POST /recommend endpoint.

Thresholds under test:
  prob > 0.90  → critical   (machine status: critical)
  prob > 0.70  → warning    (machine status: warning)
  prob > 0.50  → inspection (machine status: warning  ← important!)
  prob <= 0.50 → healthy    (machine status: operational)
"""


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_recommend_returns_200(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.95})
    assert response.status_code == 200


def test_recommend_response_structure(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.95})
    data = response.json()
    for field in ["machine_id", "severity", "action", "details", "recommendation_id", "created_at"]:
        assert field in data, f"Missing field: {field}"


def test_recommend_machine_id_in_response(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.5})
    assert response.json()["machine_id"] == "TEST-001"


def test_recommend_assigns_recommendation_id(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.5})
    assert isinstance(response.json()["recommendation_id"], int)
    assert response.json()["recommendation_id"] > 0


# ── Severity thresholds ────────────────────────────────────────────────────────

def test_recommend_critical_above_90(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.95})
    assert response.json()["severity"] == "critical"
    assert "immediate" in response.json()["action"].lower()


def test_recommend_critical_exactly_91(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.91})
    assert response.json()["severity"] == "critical"


def test_recommend_warning_between_70_and_90(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.80})
    assert response.json()["severity"] == "warning"


def test_recommend_warning_at_71(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.71})
    assert response.json()["severity"] == "warning"


def test_recommend_inspection_between_50_and_70(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.60})
    assert response.json()["severity"] == "inspection"


def test_recommend_inspection_at_51(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.51})
    assert response.json()["severity"] == "inspection"


def test_recommend_healthy_at_or_below_50(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.50})
    assert response.json()["severity"] == "healthy"


def test_recommend_healthy_at_zero(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.0})
    assert response.json()["severity"] == "healthy"


def test_recommend_healthy_at_49(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.49})
    assert response.json()["severity"] == "healthy"


# ── Machine status updates ─────────────────────────────────────────────────────

def test_recommend_critical_updates_machine_status_to_critical(client, seeded_machine):
    client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.95})
    machine = client.get(f"/machines/{seeded_machine}").json()
    assert machine["status"] == "critical"


def test_recommend_warning_updates_machine_status_to_warning(client, seeded_machine):
    client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.75})
    machine = client.get(f"/machines/{seeded_machine}").json()
    assert machine["status"] == "warning"


def test_recommend_inspection_updates_machine_status_to_warning(client, seeded_machine):
    """inspection severity maps to 'warning' machine status, NOT 'inspection'."""
    client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.60})
    machine = client.get(f"/machines/{seeded_machine}").json()
    assert machine["status"] == "warning"


def test_recommend_healthy_updates_machine_status_to_operational(client, seeded_machine):
    client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.20})
    machine = client.get(f"/machines/{seeded_machine}").json()
    assert machine["status"] == "operational"


# ── Error cases ────────────────────────────────────────────────────────────────

def test_recommend_unknown_machine_returns_404(client):
    response = client.post("/recommend", json={"machine_id": "GHOST-999", "failure_probability": 0.8})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_recommend_missing_probability_returns_422(client, seeded_machine):
    response = client.post("/recommend", json={"machine_id": "TEST-001"})
    assert response.status_code == 422


def test_recommend_missing_machine_id_returns_422(client, seeded_machine):
    response = client.post("/recommend", json={"failure_probability": 0.8})
    assert response.status_code == 422


# ── Action text sanity ─────────────────────────────────────────────────────────

def test_recommend_critical_action_text(client, seeded_machine):
    r = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.95}).json()
    assert "maintenance" in r["action"].lower()


def test_recommend_warning_action_text(client, seeded_machine):
    r = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.75}).json()
    assert "maintenance" in r["action"].lower() or "schedule" in r["action"].lower()


def test_recommend_healthy_action_text(client, seeded_machine):
    r = client.post("/recommend", json={"machine_id": "TEST-001", "failure_probability": 0.10}).json()
    assert "healthy" in r["action"].lower() or "no action" in r["action"].lower()
