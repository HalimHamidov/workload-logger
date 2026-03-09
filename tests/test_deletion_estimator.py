"""Tests for logger/deletion_estimator.py."""
import pytest
from logger.deletion_estimator import DeletionEstimator, WordLengthTracker


class TestWordLengthTracker:
    def test_fallback_when_empty(self):
        tracker = WordLengthTracker(fallback=5)
        assert tracker.median() == 5

    def test_median_single(self):
        tracker = WordLengthTracker()
        tracker.observe(7)
        assert tracker.median() == 7

    def test_median_multiple(self):
        tracker = WordLengthTracker()
        for length in [3, 5, 7, 9, 11]:
            tracker.observe(length)
        assert tracker.median() == 7


class TestDeletionEstimator:
    def setup_method(self):
        self.est = DeletionEstimator()

    def test_plain_backspace_is_high_confidence(self):
        self.est.observe_deletion("BACKSPACE", modifier_ctrl=False)
        features = self.est.get_window_features()
        assert features["del_total"] == 1.0
        assert features["del_high"] == 1.0
        assert features["del_conf_score"] == 1.0

    def test_ctrl_backspace_is_medium_confidence(self):
        self.est.observe_deletion("BACKSPACE", modifier_ctrl=True)
        features = self.est.get_window_features()
        assert features["del_medium"] > 0
        assert features["del_conf_score"] == pytest.approx(0.6)

    def test_selection_deletion_is_low_confidence(self):
        self.est.observe_deletion("BACKSPACE", modifier_ctrl=False, selection_size=10)
        features = self.est.get_window_features()
        assert features["del_low"] == 10.0
        assert features["del_conf_score"] == pytest.approx(0.3)

    def test_weighted_sum_mixed(self):
        self.est.observe_deletion("BACKSPACE", modifier_ctrl=False)        # 1 * 1.0
        self.est.observe_deletion("BACKSPACE", modifier_ctrl=False, selection_size=4)  # 4 * 0.3
        features = self.est.get_window_features()
        assert features["del_total"] == pytest.approx(5.0)
        assert features["del_weighted"] == pytest.approx(1.0 + 1.2)

    def test_zero_conf_score_when_no_deletions(self):
        features = self.est.get_window_features()
        assert features["del_conf_score"] == 0.0

    def test_reset_clears_bursts(self):
        self.est.observe_deletion("BACKSPACE", modifier_ctrl=False)
        self.est.reset_window()
        features = self.est.get_window_features()
        assert features["del_total"] == 0.0
