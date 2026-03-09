"""Tests for features/mouse_features.py."""
import pytest
import numpy as np
# from features.mouse_features import compute


class TestMouseFeatures:
    def _make_move(self, x, y, t):
        return {"type": "mouse_move", "x": x, "y": y, "timestamp": t}

    def _make_click(self, pressed, t, button="left"):
        return {"type": "mouse_click", "button": button, "pressed": pressed, "timestamp": t}

    def test_distance_straight_line(self):
        # 3-4-5 triangle: distance should be 5 pixels
        moves = [
            self._make_move(0, 0, 0.0),
            self._make_move(3, 4, 0.1),
        ]
        # TODO: result = compute(moves, [], [], window_duration=5.0)
        # assert result["mouse_distance"] == pytest.approx(5.0)
        pytest.skip("Implement compute() first")

    def test_zero_distance_no_movement(self):
        moves = [self._make_move(100, 100, 0.0)]
        # TODO: result = compute(moves, [], [], window_duration=5.0)
        # assert result["mouse_distance"] == pytest.approx(0.0)
        pytest.skip("Implement compute() first")

    def test_click_count(self):
        clicks = [
            self._make_click(True,  0.5),
            self._make_click(False, 0.6),
            self._make_click(True,  1.0),
            self._make_click(False, 1.1),
        ]
        # TODO: result = compute([], clicks, [], window_duration=5.0)
        # assert result["click_count"] == 2
        pytest.skip("Implement compute() first")

    def test_idle_ratio_all_idle(self):
        # Only 2 points with a large gap → mostly idle
        moves = [
            self._make_move(0, 0, 0.0),
            self._make_move(1, 0, 4.9),
        ]
        # TODO: result = compute(moves, [], [], window_duration=5.0)
        # assert result["mouse_idle_ratio"] > 0.9
        pytest.skip("Implement compute() first")
