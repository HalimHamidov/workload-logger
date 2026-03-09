"""Tests for features/keyboard_features.py."""
import pytest
# from features.keyboard_features import compute


class TestKeyboardFeatures:
    def _key(self, event_type, category, t):
        return {"type": event_type, "key_category": category, "timestamp": t}

    def test_typing_rate(self):
        # 10 CHAR presses in 5 seconds → rate = 2.0
        events = [self._key("key_down", "CHAR", i * 0.5) for i in range(10)]
        # TODO: result = compute(events, window_duration=5.0)
        # assert result["typing_rate"] == pytest.approx(2.0)
        pytest.skip("Implement compute() first")

    def test_hold_time(self):
        events = [
            self._key("key_down", "CHAR", 0.0),
            self._key("key_up",   "CHAR", 0.1),
            self._key("key_down", "CHAR", 0.5),
            self._key("key_up",   "CHAR", 0.7),
        ]
        # TODO: result = compute(events, window_duration=5.0)
        # assert result["hold_time_mean"] == pytest.approx(0.15)
        pytest.skip("Implement compute() first")

    def test_pause_between_chars(self):
        # Two chars at t=0 and t=0.3 → one pause of 0.3s
        events = [
            self._key("key_down", "CHAR", 0.0),
            self._key("key_down", "CHAR", 0.3),
        ]
        # TODO: result = compute(events, window_duration=5.0)
        # assert result["pause_mean"] == pytest.approx(0.3)
        pytest.skip("Implement compute() first")

    def test_non_char_keys_not_in_hold_times(self):
        events = [
            self._key("key_down", "CTRL",  0.0),
            self._key("key_up",   "CTRL",  5.0),   # very long — should not affect CHAR stats
            self._key("key_down", "CHAR",  0.1),
            self._key("key_up",   "CHAR",  0.15),
        ]
        # TODO: result = compute(events, window_duration=5.0)
        # assert result["hold_time_mean"] == pytest.approx(0.05)
        pytest.skip("Implement compute() first")
