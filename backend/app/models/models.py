from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    machine_type = Column(String(50), nullable=False)
    location = Column(String(100))
    status = Column(String(20), default="operational")  # operational | warning | critical | offline
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sensor_data = relationship("SensorData", back_populates="machine", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="machine", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="machine", cascade="all, delete-orphan")


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    air_temperature = Column(Float, nullable=False)
    process_temperature = Column(Float, nullable=False)
    rotational_speed = Column(Float, nullable=False)
    torque = Column(Float, nullable=False)
    tool_wear = Column(Float, nullable=False)
    temp_difference = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    machine = relationship("Machine", back_populates="sensor_data")
    predictions = relationship("Prediction", back_populates="sensor_data")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    sensor_data_id = Column(Integer, ForeignKey("sensor_data.id"), nullable=True)
    failure_prediction = Column(Integer, nullable=False)   # 0 or 1
    failure_probability = Column(Float, nullable=False)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    machine = relationship("Machine", back_populates="predictions")
    sensor_data = relationship("SensorData", back_populates="predictions")
    recommendation = relationship("Recommendation", back_populates="prediction", uselist=False)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    severity = Column(String(30), nullable=False)  # critical | warning | inspection | healthy
    action = Column(String(200), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    machine = relationship("Machine", back_populates="recommendations")
    prediction = relationship("Prediction", back_populates="recommendation")
