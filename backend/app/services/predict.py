"""
predict.py — LightGBM inference wrapper for ForgeGuard AI.
Loads best_model.pkl once at import time and exposes a predict() function.
"""

import joblib
import pandas as pd
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()

_model = None


def _load_model():
    global _model
    if _model is None:
        model_path = Path(settings.model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Mount your best_model.pkl into /app/ml/ via Docker volume."
            )
        _model = joblib.load(model_path)
    return _model


FEATURE_ORDER = [
    "Air_temperature__K_",
    "Process_temperature__K_",
    "Rotational_speed__rpm_",
    "Torque__Nm_",
    "Tool_wear__min_",
    "temp_difference",
]


def predict(
    Air_temperature__K_: float,
    Process_temperature__K_: float,
    Rotational_speed__rpm_: float,
    Torque__Nm_: float,
    Tool_wear__min_: float,
    temp_difference: float,
) -> dict:
    """
    Run inference and return:
        { "failure_prediction": int, "failure_probability": float }
    """
    model = _load_model()

    # Use a named DataFrame so LightGBM receives the exact feature names
    # it was trained with — eliminates the feature-name warning.
    features = pd.DataFrame([{
        "Air_temperature__K_":    Air_temperature__K_,
        "Process_temperature__K_": Process_temperature__K_,
        "Rotational_speed__rpm_": Rotational_speed__rpm_,
        "Torque__Nm_":            Torque__Nm_,
        "Tool_wear__min_":        Tool_wear__min_,
        "temp_difference":        temp_difference,
    }])

    proba = model.predict_proba(features)[0]
    failure_probability = float(proba[1])
    failure_prediction = int(failure_probability >= 0.5)

    return {
        "failure_prediction": failure_prediction,
        "failure_probability": round(failure_probability, 6),
    }
