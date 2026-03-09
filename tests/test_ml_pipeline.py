"""Tests for ml/pipeline.py and ml/evaluate.py."""
import pytest
import numpy as np
from ml.pipeline import build_pipeline, ALPHA_GRID, TARGETS
from ml.evaluate import compute_metrics


class TestPipeline:
    def test_pipeline_has_three_steps(self):
        pipe = build_pipeline()
        assert list(pipe.named_steps.keys()) == ["imputer", "scaler", "model"]

    def test_pipeline_fits_and_predicts(self):
        pipe = build_pipeline()
        X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        y = np.array([10.0, 20.0, 30.0])
        pipe.fit(X, y)
        y_pred = pipe.predict(X)
        assert y_pred.shape == (3,)

    def test_pipeline_handles_nan(self):
        pipe = build_pipeline()
        X = np.array([[1.0, np.nan], [3.0, 4.0], [5.0, 6.0]])
        y = np.array([10.0, 20.0, 30.0])
        pipe.fit(X, y)   # should not raise

    def test_alpha_grid_is_log_spaced(self):
        assert len(ALPHA_GRID) >= 5
        for i in range(1, len(ALPHA_GRID)):
            assert ALPHA_GRID[i] > ALPHA_GRID[i - 1]

    def test_all_six_targets_defined(self):
        assert len(TARGETS) == 6
        assert "tlx_mean" in TARGETS


class TestEvaluate:
    def test_perfect_predictions(self):
        y = np.array([10.0, 20.0, 30.0])
        metrics = compute_metrics(y, y, "tlx_test")
        assert metrics["MAE"]  == pytest.approx(0.0)
        assert metrics["RMSE"] == pytest.approx(0.0)
        assert metrics["R2"]   == pytest.approx(1.0)

    def test_negative_r2_when_worse_than_mean(self):
        y_true = np.array([10.0, 50.0, 90.0])
        y_pred = np.array([90.0, 10.0, 50.0])  # very wrong predictions
        metrics = compute_metrics(y_true, y_pred, "tlx_test")
        assert metrics["R2"] < 0
