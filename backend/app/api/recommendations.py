from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.models import Recommendation
from app.schemas.schemas import RecommendationRecord

router = APIRouter()


@router.get("/", response_model=List[RecommendationRecord])
def list_recommendations(
    machine_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Recommendation)
    if machine_id:
        q = q.filter(Recommendation.machine_id == machine_id)
    if severity:
        q = q.filter(Recommendation.severity == severity)
    return q.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit).all()
