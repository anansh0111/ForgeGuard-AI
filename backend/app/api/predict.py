from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Machine, SensorData, Prediction
from app.schemas.schemas import PredictRequest, PredictResponse
from app.services import predict as predict_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def run_prediction(payload: PredictRequest, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.machine_id == payload.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{payload.machine_id}' not found")

    # Compute temp_difference if not provided
    temp_diff = payload.temp_difference
    if temp_diff is None:
        temp_diff = payload.Process_temperature__K_ - payload.Air_temperature__K_

    # Persist sensor reading
    sensor = SensorData(
        machine_id=payload.machine_id,
        air_temperature=payload.Air_temperature__K_,
        process_temperature=payload.Process_temperature__K_,
        rotational_speed=payload.Rotational_speed__rpm_,
        torque=payload.Torque__Nm_,
        tool_wear=payload.Tool_wear__min_,
        temp_difference=temp_diff,
    )
    db.add(sensor)
    db.flush()

    # Run inference
    try:
        result = predict_service.predict(
            Air_temperature__K_=payload.Air_temperature__K_,
            Process_temperature__K_=payload.Process_temperature__K_,
            Rotational_speed__rpm_=payload.Rotational_speed__rpm_,
            Torque__Nm_=payload.Torque__Nm_,
            Tool_wear__min_=payload.Tool_wear__min_,
            temp_difference=temp_diff,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Persist prediction
    prediction = Prediction(
        machine_id=payload.machine_id,
        sensor_data_id=sensor.id,
        failure_prediction=result["failure_prediction"],
        failure_probability=result["failure_probability"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return PredictResponse(
        machine_id=payload.machine_id,
        failure_prediction=prediction.failure_prediction,
        failure_probability=prediction.failure_probability,
        prediction_id=prediction.id,
        predicted_at=prediction.predicted_at,
    )
