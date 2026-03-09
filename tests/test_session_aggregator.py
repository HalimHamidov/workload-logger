"""Tests for features/session_aggregator.py."""
import pytest
from features.session_aggregator import aggregate


class TestSessionAggregator:
    def _meta(self):
        return {
            "session_id": "test-123",
            "participant_id": "Zafar",
            "task_type": "writing",
            "task_name": "test",
            "session_start": 0.0,
            "session_end": 15.0,
        }

    def test_mean_computed_correctly(self):
        windows = [
            {"typing_rate": 2.0},
            {"typing_rate": 4.0},
            {"typing_rate": 6.0},
        ]
        row = aggregate(windows, self._meta())
        assert row["typing_rate_mean"] == pytest.approx(4.0)

    def test_std_computed_correctly(self):
        # pandas DataFrame.std() uses ddof=1 by default → std([2,4]) = sqrt(2) ≈ 1.414
        windows = [{"typing_rate": 2.0}, {"typing_rate": 4.0}]
        row = aggregate(windows, self._meta())
        assert row["typing_rate_std"] == pytest.approx(2**0.5, rel=0.01)

    def test_min_and_max(self):
        windows = [{"x": 1.0}, {"x": 5.0}, {"x": 3.0}]
        row = aggregate(windows, self._meta())
        assert row["x_min"] == pytest.approx(1.0)
        assert row["x_max"] == pytest.approx(5.0)

    def test_window_count_correct(self):
        windows = [{"a": 1}, {"a": 2}, {"a": 3}]
        row = aggregate(windows, self._meta())
        assert row["window_count"] == 3

    def test_tlx_mean_computed(self):
        tlx = {
            "tlx_mental_demand": 60,
            "tlx_temporal_demand": 40,
            "tlx_performance": 70,
            "tlx_effort": 50,
            "tlx_frustration": 30,
        }
        row = aggregate([{"typing_rate": 1.0}], self._meta(), tlx_ratings=tlx)
        assert row["tlx_mean"] == pytest.approx(50.0)

    def test_empty_windows_returns_meta(self):
        row = aggregate([], self._meta())
        assert row["window_count"] == 0
        assert row["session_id"] == "test-123"
