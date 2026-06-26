from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.models import Machine
from app.schemas.schemas import MachineCreate, MachineResponse, DashboardStats

router = APIRouter()


# BUG 6 FIX: /stats MUST be registered before /{machine_id}
# FastAPI matches routes in registration order — if /{machine_id} comes first,
# GET /machines/stats would be matched with machine_id="stats" and return 404.

@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    from app.models.models import Prediction

    total = db.query(Machine).count()
    critical = db.query(Machine).filter(Machine.status == "critical").count()
    warning = db.query(Machine).filter(Machine.status == "warning").count()
    healthy = db.query(Machine).filter(Machine.status == "operational").count()

    # BUG 8 FIX: Use func.date() which works on both SQLite and PostgreSQL
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_count = (
        db.query(Prediction)
        .filter(func.date(Prediction.predicted_at) == today_str)
        .count()
    )

    avg_risk_row = db.query(func.avg(Prediction.failure_probability)).scalar()
    avg_risk = round(float(avg_risk_row or 0), 4)

    return DashboardStats(
        total_machines=total,
        critical_machines=critical,
        warning_machines=warning,
        healthy_machines=healthy,
        average_failure_risk=avg_risk,
        total_predictions_today=today_count,
    )


@router.get("/", response_model=List[MachineResponse])
def list_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Machine).offset(skip).limit(limit).all()


@router.post("/", response_model=MachineResponse, status_code=201)
def create_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    existing = db.query(Machine).filter(Machine.machine_id == payload.machine_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Machine ID already registered")
    machine = Machine(**payload.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: str, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.machine_id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine
