# ForgeGuard AI
### Industrial Predictive Maintenance Platform

> **Author:** Anansh  
> **Stack:** LightGBM · FastAPI · PostgreSQL · React + Vite · Docker Compose

---

## Architecture

```
Sensor Simulator (every 5s)
        ↓
FastAPI Backend  ←→  PostgreSQL
  ├── /predict        (LightGBM inference)
  └── /recommend      (Rule-based engine)
        ↓
React Dashboard
  ├── Dashboard       (KPIs, fleet status, risk trend)
  ├── Predictions     (probability table + distribution chart)
  └── Recommendations (maintenance action log)
```

---

## Quick Start

### 1. Add your model

```bash
cp /path/to/best_model.pkl ml/best_model.pkl
```

See `ml/README.md` for the expected interface.

### 2. Run

```bash
docker compose up --build
```

| Service       | URL                          |
|---------------|------------------------------|
| Dashboard     | http://localhost:3000        |
| API Docs      | http://localhost:8000/docs   |
| Backend       | http://localhost:8000        |
| PostgreSQL    | localhost:5432               |

---

## API Reference

| Method | Endpoint            | Description                         |
|--------|---------------------|-------------------------------------|
| GET    | `/health`           | Service health check                |
| GET    | `/machines/`        | List all machines                   |
| GET    | `/machines/stats`   | Dashboard KPI stats                 |
| POST   | `/predict`          | Run LightGBM prediction             |
| POST   | `/recommend`        | Generate maintenance recommendation |
| GET    | `/predictions/`     | List predictions (filterable)       |
| GET    | `/recommendations/` | List recommendations (filterable)   |

### POST `/predict` — Request body

```json
{
  "machine_id": "M-001",
  "Air_temperature__K_": 300.5,
  "Process_temperature__K_": 310.2,
  "Rotational_speed__rpm_": 1500.0,
  "Torque__Nm_": 40.0,
  "Tool_wear__min_": 120.0
}
```

### POST `/recommend` — Request body

```json
{
  "machine_id": "M-001",
  "failure_probability": 0.87
}
```

---

## Recommendation Rules

| Probability      | Severity    | Action                          |
|------------------|-------------|---------------------------------|
| > 90%            | Critical    | Immediate Maintenance Required  |
| 70% – 90%        | Warning     | Schedule Maintenance            |
| 50% – 70%        | Inspection  | Inspection Recommended          |
| < 50%            | Healthy     | No Action Required              |

---

## Project Structure

```
ForgeGuard-AI/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── core/         # Config & settings
│   │   ├── db/           # SQLAlchemy session
│   │   ├── models/       # ORM models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # predict.py + recommendation_engine.py
│   │   └── main.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios client
│   │   ├── components/   # Dashboard, Predictions, Recommendations, Shared
│   │   ├── hooks/        # usePolling
│   │   ├── pages/        # DashboardPage, PredictionsPage, RecommendationsPage
│   │   └── utils/        # helpers
│   └── Dockerfile
├── simulator/
│   └── simulator.py      # Sensor data generator
├── ml/
│   └── best_model.pkl    # ← Place your model here
└── docker-compose.yml
```

---

## Environment Variables

| Variable            | Default              | Description              |
|---------------------|----------------------|--------------------------|
| `POSTGRES_USER`     | `forgeguard`         | DB user                  |
| `POSTGRES_PASSWORD` | `forgeguard_secret`  | DB password              |
| `POSTGRES_DB`       | `forgeguard_db`      | DB name                  |
| `SIMULATOR_INTERVAL`| `5`                  | Seconds between readings |
| `VITE_API_URL`      | `http://localhost:8000` | Frontend API base URL |

---

*ForgeGuard AI — built by Anansh*
