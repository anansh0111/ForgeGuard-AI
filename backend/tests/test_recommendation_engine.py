"""
test_recommendation_engine.py — Pure unit tests for the recommendation engine.

These tests have ZERO dependencies on FastAPI, DB, or models.
They test the business logic directly.
"""

import pytest
from app.services.recommendation_engine import (
    generate_recommendation,
    severity_to_machine_status,
    RecommendationResult,
)


# ── generate_recommendation ────────────────────────────────────────────────────

class TestGenerateRecommendation:

    def test_returns_recommendation_result_type(self):
        result = generate_recommendation(0.5)
        assert isinstance(result, RecommendationResult)

    def test_result_has_all_fields(self):
        result = generate_recommendation(0.5)
        assert hasattr(result, "severity")
        assert hasattr(result, "action")
        assert hasattr(result, "details")

    # -- Critical (prob > 0.90) --

    def test_critical_at_0_95(self):
        result = generate_recommendation(0.95)
        assert result.severity == "critical"

    def test_critical_at_0_91(self):
        result = generate_recommendation(0.91)
        assert result.severity == "critical"

    def test_critical_at_1_0(self):
        result = generate_recommendation(1.0)
        assert result.severity == "critical"

    def test_critical_action_contains_immediate(self):
        result = generate_recommendation(0.95)
        assert "immediate" in result.action.lower() or "maintenance" in result.action.lower()

    def test_critical_details_not_empty(self):
        result = generate_recommendation(0.95)
        assert len(result.details) > 10

    # -- Warning (0.70 < prob <= 0.90) --

    def test_warning_at_0_90_boundary(self):
        # prob == 0.90 is NOT > 0.90 so it's warning
        result = generate_recommendation(0.90)
        assert result.severity == "warning"

    def test_warning_at_0_80(self):
        result = generate_recommendation(0.80)
        assert result.severity == "warning"

    def test_warning_at_0_71(self):
        result = generate_recommendation(0.71)
        assert result.severity == "warning"

    def test_warning_action_contains_schedule(self):
        result = generate_recommendation(0.80)
        assert "schedule" in result.action.lower() or "maintenance" in result.action.lower()

    # -- Inspection (0.50 < prob <= 0.70) --

    def test_inspection_at_0_70_boundary(self):
        # prob == 0.70 is NOT > 0.70 so it's inspection
        result = generate_recommendation(0.70)
        assert result.severity == "inspection"

    def test_inspection_at_0_60(self):
        result = generate_recommendation(0.60)
        assert result.severity == "inspection"

    def test_inspection_at_0_51(self):
        result = generate_recommendation(0.51)
        assert result.severity == "inspection"

    def test_inspection_action_contains_inspection(self):
        result = generate_recommendation(0.60)
        assert "inspection" in result.action.lower() or "inspect" in result.action.lower()

    # -- Healthy (prob <= 0.50) --

    def test_healthy_at_0_50_boundary(self):
        result = generate_recommendation(0.50)
        assert result.severity == "healthy"

    def test_healthy_at_0_49(self):
        result = generate_recommendation(0.49)
        assert result.severity == "healthy"

    def test_healthy_at_0_0(self):
        result = generate_recommendation(0.0)
        assert result.severity == "healthy"

    def test_healthy_action_contains_no_action(self):
        result = generate_recommendation(0.0)
        assert "no action" in result.action.lower() or "healthy" in result.action.lower()

    # -- Strict boundary checks (no off-by-one errors) --

    def test_boundary_90_is_warning_not_critical(self):
        assert generate_recommendation(0.90).severity == "warning"

    def test_boundary_just_above_90_is_critical(self):
        assert generate_recommendation(0.901).severity == "critical"

    def test_boundary_70_is_inspection_not_warning(self):
        assert generate_recommendation(0.70).severity == "inspection"

    def test_boundary_just_above_70_is_warning(self):
        assert generate_recommendation(0.701).severity == "warning"

    def test_boundary_50_is_healthy_not_inspection(self):
        assert generate_recommendation(0.50).severity == "healthy"

    def test_boundary_just_above_50_is_inspection(self):
        assert generate_recommendation(0.501).severity == "inspection"


# ── severity_to_machine_status ─────────────────────────────────────────────────

class TestSeverityToMachineStatus:

    def test_critical_maps_to_critical(self):
        assert severity_to_machine_status("critical") == "critical"

    def test_warning_maps_to_warning(self):
        assert severity_to_machine_status("warning") == "warning"

    def test_inspection_maps_to_warning(self):
        """inspection severity → 'warning' machine status, NOT 'inspection'."""
        assert severity_to_machine_status("inspection") == "warning"

    def test_healthy_maps_to_operational(self):
        assert severity_to_machine_status("healthy") == "operational"

    def test_unknown_severity_maps_to_operational(self):
        assert severity_to_machine_status("unknown_value") == "operational"

    def test_empty_string_maps_to_operational(self):
        assert severity_to_machine_status("") == "operational"

    def test_all_severities_covered(self):
        """Ensure all 4 valid severities return a non-empty status."""
        for sev in ["critical", "warning", "inspection", "healthy"]:
            status = severity_to_machine_status(sev)
            assert status, f"Empty status for severity: {sev}"
            assert status in ("critical", "warning", "operational")
