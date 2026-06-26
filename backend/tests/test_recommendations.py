"""
test_recommendations.py — Tests for GET /recommendations/ endpoint.
"""


def _seed_recommendations(client, machine_id: str, probabilities: list):
    """Helper: POST /recommend for each probability value."""
    for prob in probabilities:
        client.post("/recommend", json={"machine_id": machine_id, "failure_probability": prob})


# ── Basic listing ──────────────────────────────────────────────────────────────

def test_list_recommendations_empty(client):
    response = client.get("/recommendations/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_recommendations_returns_seeded(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60, 0.20])
    response = client.get("/recommendations/")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_list_recommendations_response_structure(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95])
    data = client.get("/recommendations/").json()
    record = data[0]
    for field in ["id", "machine_id", "severity", "action", "created_at"]:
        assert field in record, f"Missing field: {field}"


def test_list_recommendations_ordered_newest_first(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60])
    data = client.get("/recommendations/").json()
    ids = [r["id"] for r in data]
    assert ids == sorted(ids, reverse=True)


# ── Filtering by machine_id ────────────────────────────────────────────────────

def test_filter_recommendations_by_machine_id(client, seeded_machine):
    client.post("/machines/", json={"machine_id": "OTHER-002", "name": "Other", "machine_type": "CNC"})
    _seed_recommendations(client, "TEST-001", [0.95, 0.75])
    _seed_recommendations(client, "OTHER-002", [0.60])

    response = client.get("/recommendations/?machine_id=TEST-001")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(r["machine_id"] == "TEST-001" for r in data)


def test_filter_recommendations_unknown_machine_empty(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95])
    response = client.get("/recommendations/?machine_id=GHOST")
    assert response.status_code == 200
    assert response.json() == []


# ── Filtering by severity ──────────────────────────────────────────────────────

def test_filter_recommendations_by_severity_critical(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60, 0.20])
    response = client.get("/recommendations/?severity=critical")
    data = response.json()
    assert len(data) == 1
    assert data[0]["severity"] == "critical"


def test_filter_recommendations_by_severity_warning(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60, 0.20])
    response = client.get("/recommendations/?severity=warning")
    data = response.json()
    assert len(data) == 1
    assert data[0]["severity"] == "warning"


def test_filter_recommendations_by_severity_inspection(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60, 0.20])
    response = client.get("/recommendations/?severity=inspection")
    data = response.json()
    assert len(data) == 1
    assert data[0]["severity"] == "inspection"


def test_filter_recommendations_by_severity_healthy(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60, 0.20])
    response = client.get("/recommendations/?severity=healthy")
    data = response.json()
    assert len(data) == 1
    assert data[0]["severity"] == "healthy"


def test_filter_by_both_machine_and_severity(client, seeded_machine):
    client.post("/machines/", json={"machine_id": "OTHER-003", "name": "Other", "machine_type": "CNC"})
    _seed_recommendations(client, "TEST-001", [0.95, 0.20])
    _seed_recommendations(client, "OTHER-003", [0.95])

    response = client.get("/recommendations/?machine_id=TEST-001&severity=critical")
    data = response.json()
    assert len(data) == 1
    assert data[0]["machine_id"] == "TEST-001"
    assert data[0]["severity"] == "critical"


# ── Pagination ─────────────────────────────────────────────────────────────────

def test_recommendations_pagination_limit(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60, 0.20])
    response = client.get("/recommendations/?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_recommendations_pagination_skip(client, seeded_machine):
    _seed_recommendations(client, "TEST-001", [0.95, 0.75, 0.60, 0.20])
    all_data = client.get("/recommendations/?limit=4").json()
    skipped = client.get("/recommendations/?skip=2&limit=4").json()
    assert len(skipped) == 2
    assert skipped[0]["id"] == all_data[2]["id"]


def test_recommendations_limit_over_200_returns_422(client):
    response = client.get("/recommendations/?limit=201")
    assert response.status_code == 422


def test_recommendations_negative_skip_returns_422(client):
    response = client.get("/recommendations/?skip=-1")
    assert response.status_code == 422
