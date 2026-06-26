from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Machine, Recommendation
from app.schemas.schemas import RecommendRequest, RecommendResponse
from app.services.recommendation_engine import generate_recommendation, severity_to_machine_status

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def run_recommendation(payload: RecommendRequest, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.machine_id == payload.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{payload.machine_id}' not found")

    result = generate_recommendation(payload.failure_probability)

    # Update machine status
    machine.status = severity_to_machine_status(result.severity)

    rec = Recommendation(
        machine_id=payload.machine_id,
        severity=result.severity,
        action=result.action,
        details=result.details,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return RecommendResponse(
        machine_id=payload.machine_id,
        severity=rec.severity,
        action=rec.action,
        details=rec.details,
        recommendation_id=rec.id,
        created_at=rec.created_at,
    )
