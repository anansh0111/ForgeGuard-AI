from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.models import Prediction
from app.schemas.schemas import PredictionRecord

router = APIRouter()


@router.get("/", response_model=List[PredictionRecord])
def list_predictions(
    machine_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Prediction)
    if machine_id:
        q = q.filter(Prediction.machine_id == machine_id)
    return q.order_by(Prediction.predicted_at.desc()).offset(skip).limit(limit).all()
