"""
test_machines.py — Tests for the /machines endpoints.

Covers:
- GET  /machines/          list (empty + populated, pagination)
- POST /machines/          create (success, duplicate 409)
- GET  /machines/stats     dashboard KPIs
- GET  /machines/{id}      get one (success, 404)
"""


# ── GET /machines/ ─────────────────────────────────────────────────────────────

def test_list_machines_empty(client):
    response = client.get("/machines/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_machines_returns_seeded(client, seeded_machine):
    response = client.get("/machines/")
    assert response.status_code == 200
    machines = response.json()
    assert len(machines) == 1
    assert machines[0]["machine_id"] == "TEST-001"


def test_list_machines_pagination_skip(client, seeded_machine):
    # skip=1 → no results since we only have 1 machine
    response = client.get("/machines/?skip=1&limit=10")
    assert response.status_code == 200
    assert response.json() == []


def test_list_machines_pagination_limit(client):
    # Create 3 machines then fetch limit=2
    for i in range(1, 4):
        client.post("/machines/", json={
            "machine_id": f"LIMIT-{i:03d}",
            "name": f"Limit Machine {i}",
            "machine_type": "CNC",
        })
    response = client.get("/machines/?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ── POST /machines/ ────────────────────────────────────────────────────────────

def test_create_machine_success(client):
    payload = {
        "machine_id": "NEW-001",
        "name": "New Lathe",
        "machine_type": "Lathe",
        "location": "Workshop A",
    }
    response = client.post("/machines/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["machine_id"] == "NEW-001"
    assert data["name"] == "New Lathe"
    assert data["machine_type"] == "Lathe"
    assert data["location"] == "Workshop A"
    assert data["status"] == "operational"


def test_create_machine_without_location(client):
    payload = {
        "machine_id": "NO-LOC-001",
        "name": "No Location Machine",
        "machine_type": "CNC",
    }
    response = client.post("/machines/", json=payload)
    assert response.status_code == 201
    assert response.json()["location"] is None


def test_create_machine_duplicate_returns_409(client):
    payload = {
        "machine_id": "DUP-001",
        "name": "First",
        "machine_type": "CNC",
    }
    client.post("/machines/", json=payload)
    response = client.post("/machines/", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_create_machine_missing_required_fields(client):
    # name is required
    response = client.post("/machines/", json={"machine_id": "INCOMPLETE"})
    assert response.status_code == 422


# ── GET /machines/{machine_id} ─────────────────────────────────────────────────

def test_get_machine_by_id_success(client, seeded_machine):
    response = client.get(f"/machines/{seeded_machine}")
    assert response.status_code == 200
    data = response.json()
    assert data["machine_id"] == seeded_machine
    assert data["name"] == "Test CNC Unit"


def test_get_machine_by_id_not_found(client):
    response = client.get("/machines/DOES-NOT-EXIST")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_machine_response_has_all_fields(client, seeded_machine):
    response = client.get(f"/machines/{seeded_machine}")
    data = response.json()
    for field in ["id", "machine_id", "name", "machine_type", "status", "created_at"]:
        assert field in data, f"Missing field: {field}"


# ── GET /machines/stats ────────────────────────────────────────────────────────

def test_stats_empty_db(client):
    response = client.get("/machines/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_machines"] == 0
    assert data["critical_machines"] == 0
    assert data["warning_machines"] == 0
    assert data["healthy_machines"] == 0
    assert data["average_failure_risk"] == 0.0
    assert data["total_predictions_today"] == 0


def test_stats_counts_machines(client, seeded_machine):
    response = client.get("/machines/stats")
    data = response.json()
    assert data["total_machines"] == 1
    assert data["healthy_machines"] == 1  # status is "operational"


def test_stats_multiple_statuses(client):
    from tests.conftest import TestingSessionLocal
    from app.models.models import Machine

    db = TestingSessionLocal()
    db.add_all([
        Machine(machine_id="S-001", name="M1", machine_type="CNC", status="critical"),
        Machine(machine_id="S-002", name="M2", machine_type="CNC", status="warning"),
        Machine(machine_id="S-003", name="M3", machine_type="CNC", status="operational"),
    ])
    db.commit()
    db.close()

    response = client.get("/machines/stats")
    data = response.json()
    assert data["total_machines"] == 3
    assert data["critical_machines"] == 1
    assert data["warning_machines"] == 1
    assert data["healthy_machines"] == 1
