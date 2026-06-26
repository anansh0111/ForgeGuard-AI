"""
test_predict_service.py — Unit tests for the predict service (LightGBM wrapper).

All tests mock the model — no real .pkl file needed.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, PropertyMock


SAMPLE_INPUTS = dict(
    Air_temperature__K_=300.5,
    Process_temperature__K_=310.2,
    Rotational_speed__rpm_=1500.0,
    Torque__Nm_=40.0,
    Tool_wear__min_=120.0,
    temp_difference=9.7,
)


def make_mock(prob: float):
    m = MagicMock()
    m.predict_proba.return_value = [[1 - prob, prob]]
    return m


class TestPredictService:

    def test_returns_dict_with_required_keys(self):
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.8)):
            result = svc.predict(**SAMPLE_INPUTS)
        assert "failure_prediction" in result
        assert "failure_probability" in result

    def test_high_probability_gives_prediction_1(self):
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.9)):
            result = svc.predict(**SAMPLE_INPUTS)
        assert result["failure_prediction"] == 1

    def test_low_probability_gives_prediction_0(self):
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.1)):
            result = svc.predict(**SAMPLE_INPUTS)
        assert result["failure_prediction"] == 0

    def test_exactly_50_percent_is_failure(self):
        """Threshold is >= 0.5 so exactly 0.5 → prediction = 1."""
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.5)):
            result = svc.predict(**SAMPLE_INPUTS)
        assert result["failure_prediction"] == 1

    def test_just_below_50_is_not_failure(self):
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.4999)):
            result = svc.predict(**SAMPLE_INPUTS)
        assert result["failure_prediction"] == 0

    def test_probability_rounded_to_6_decimals(self):
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.123456789)):
            result = svc.predict(**SAMPLE_INPUTS)
        # Should have at most 6 decimal places
        prob_str = str(result["failure_probability"])
        decimals = len(prob_str.split(".")[-1]) if "." in prob_str else 0
        assert decimals <= 6

    def test_probability_is_float(self):
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.7)):
            result = svc.predict(**SAMPLE_INPUTS)
        assert isinstance(result["failure_probability"], float)

    def test_prediction_is_int(self):
        from app.services import predict as svc
        with patch.object(svc, "_model", make_mock(0.7)):
            result = svc.predict(**SAMPLE_INPUTS)
        assert isinstance(result["failure_prediction"], int)

    def test_model_called_with_dataframe(self):
        """predict() must pass a DataFrame (not a list/dict) to the model."""
        from app.services import predict as svc
        mock = make_mock(0.8)
        with patch.object(svc, "_model", mock):
            svc.predict(**SAMPLE_INPUTS)
        call_args = mock.predict_proba.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)

    def test_model_called_with_correct_feature_names(self):
        """DataFrame columns must match FEATURE_ORDER exactly."""
        from app.services import predict as svc
        mock = make_mock(0.8)
        with patch.object(svc, "_model", mock):
            svc.predict(**SAMPLE_INPUTS)
        df = mock.predict_proba.call_args[0][0]
        assert list(df.columns) == svc.FEATURE_ORDER

    def test_model_called_with_correct_values(self):
        from app.services import predict as svc
        mock = make_mock(0.8)
        with patch.object(svc, "_model", mock):
            svc.predict(**SAMPLE_INPUTS)
        df = mock.predict_proba.call_args[0][0]
        assert df["Air_temperature__K_"].iloc[0] == 300.5
        assert df["Rotational_speed__rpm_"].iloc[0] == 1500.0
        assert df["temp_difference"].iloc[0] == 9.7

    def test_model_called_exactly_once(self):
        from app.services import predict as svc
        mock = make_mock(0.8)
        with patch.object(svc, "_model", mock):
            svc.predict(**SAMPLE_INPUTS)
        assert mock.predict_proba.call_count == 1

    def test_load_model_raises_file_not_found_when_missing(self):
        """_load_model raises FileNotFoundError if pkl doesn't exist.

        We patch svc.settings directly (the module-level singleton captured at
        import time) rather than get_settings — the lru_cache means patching
        get_settings after import has no effect on the already-resolved value.
        """
        from app.services import predict as svc
        original_model = svc._model
        try:
            svc._model = None
            with patch.object(svc.settings, "model_path", "/nonexistent/path/model.pkl"):
                with pytest.raises(FileNotFoundError):
                    svc._load_model()
        finally:
            svc._model = original_model

    def test_load_model_singleton_caches_after_first_load(self):
        """_load_model should only call joblib.load once (cached in _model).

        We patch joblib.load directly instead of writing a real .pkl file
        because MagicMock objects cannot be pickled by joblib.
        """
        from app.services import predict as svc
        fake_model = make_mock(0.5)
        original_model = svc._model
        try:
            svc._model = None
            # Patch Path so .exists() returns True (so we don't get FileNotFoundError)
            with patch("app.services.predict.Path") as mock_path_cls:
                mock_path_cls.return_value.exists.return_value = True
                # Patch joblib so we don't touch the filesystem
                with patch("app.services.predict.joblib") as mock_joblib:
                    mock_joblib.load.return_value = fake_model
                    svc._load_model()   # first call: loads model
                    svc._load_model()   # second call: _model already set, skip load
                    assert mock_joblib.load.call_count == 1
        finally:
            svc._model = original_model
