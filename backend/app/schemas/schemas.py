from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SensorInput(BaseModel):
    machine_id: str
    Air_temperature__K_: float = Field(..., ge=295.0, le=310.0)
    Process_temperature__K_: float = Field(..., ge=305.0, le=315.0)
    Rotational_speed__rpm_: float = Field(..., ge=1000.0, le=3000.0)
    Torque__Nm_: float = Field(..., ge=3.0, le=80.0)
    Tool_wear__min_: float = Field(..., ge=0.0, le=300.0)
    temp_difference: Optional[float] = None


class PredictRequest(BaseModel):
    machine_id: str
    Air_temperature__K_: float
    Process_temperature__K_: float
    Rotational_speed__rpm_: float
    Torque__Nm_: float
    Tool_wear__min_: float
    temp_difference: Optional[float] = None


class PredictResponse(BaseModel):
    machine_id: str
    failure_prediction: int
    failure_probability: float
    prediction_id: int
    predicted_at: datetime


class RecommendRequest(BaseModel):
    machine_id: str
    failure_probability: float


class RecommendResponse(BaseModel):
    machine_id: str
    severity: str
    action: str
    details: str
    recommendation_id: int
    created_at: datetime


class MachineCreate(BaseModel):
    machine_id: str
    name: str
    machine_type: str
    location: Optional[str] = None


class MachineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: str
    name: str
    machine_type: str
    location: Optional[str]
    status: str
    created_at: datetime


class PredictionRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: str
    failure_prediction: int
    failure_probability: float
    predicted_at: datetime


class RecommendationRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: str
    severity: str
    action: str
    details: Optional[str]
    created_at: datetime


class DashboardStats(BaseModel):
    total_machines: int
    critical_machines: int
    warning_machines: int
    healthy_machines: int
    average_failure_risk: float
    total_predictions_today: int
