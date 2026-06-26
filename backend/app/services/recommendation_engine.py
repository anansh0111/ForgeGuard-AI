"""
recommendation_engine.py — Rule-based recommendation engine for ForgeGuard AI.

Thresholds (by failure_probability):
  > 0.90  →  critical   — Immediate Maintenance Required
  > 0.70  →  warning    — Schedule Maintenance
  > 0.50  →  inspection — Inspection Recommended
  else    →  healthy    — Machine Healthy
"""

from dataclasses import dataclass


@dataclass
class RecommendationResult:
    severity: str
    action: str
    details: str


_RULES = [
    (
        0.90,
        "critical",
        "Immediate Maintenance Required",
        (
            "Failure probability exceeds 90%. The machine poses an imminent risk of breakdown. "
            "Stop operations immediately, isolate the unit, and dispatch a maintenance team. "
            "Do not restart until a full inspection and sign-off is completed."
        ),
    ),
    (
        0.70,
        "warning",
        "Schedule Maintenance Within 24 Hours",
        (
            "Failure probability is between 70–90%. Degradation indicators are elevated. "
            "Reduce machine load where possible and schedule a maintenance window within the next 24 hours. "
            "Monitor sensor readings closely for any rapid changes."
        ),
    ),
    (
        0.50,
        "inspection",
        "Inspection Recommended",
        (
            "Failure probability is between 50–70%. Early warning signals detected. "
            "Conduct a visual inspection and run diagnostic checks at the next available opportunity. "
            "Log findings and continue monitoring."
        ),
    ),
]


def generate_recommendation(failure_probability: float) -> RecommendationResult:
    """
    Apply threshold rules and return a structured recommendation.
    """
    for threshold, severity, action, details in _RULES:
        if failure_probability > threshold:
            return RecommendationResult(severity=severity, action=action, details=details)

    return RecommendationResult(
        severity="healthy",
        action="Machine Healthy — No Action Required",
        details=(
            "Failure probability is below 50%. All sensor readings are within normal operating parameters. "
            "Continue routine monitoring and scheduled preventive maintenance."
        ),
    )


def severity_to_machine_status(severity: str) -> str:
    mapping = {
        "critical": "critical",
        "warning": "warning",
        "inspection": "warning",
        "healthy": "operational",
    }
    return mapping.get(severity, "operational")
