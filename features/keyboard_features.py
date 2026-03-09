"""
keyboard_features.py — Computes keyboard dynamics features for one window.

Only CHAR key events are used for rhythm features. Other key categories
(CTRL, SHIFT, etc.) are counted but not used for timing.

Privacy guarantee: no key values, only timing of CHAR-category events.

Features returned
-----------------
typing_rate         CHAR key-down events per second
key_count_total     Total key-down events (all categories)
key_count_char      CHAR key-down count
hold_time_mean      Mean duration between CHAR key-down and key-up (seconds)
hold_time_std       Std dev of hold times
pause_mean          Mean inter-key interval between consecutive CHAR presses
pause_std           Std dev of inter-key intervals
"""

from __future__ import annotations
import numpy as np


def compute(key_events: list[dict], window_duration: float) -> dict:
    """Compute keyboard features for one 5-second window.

    Parameters
    ----------
    key_events      : list of {"type": "key_down"|"key_up",
                               "key_category": str,
                               "timestamp": float}
    window_duration : length of window in seconds

    Returns
    -------
    dict of feature_name → float
    """
    # TODO: separate key_down / key_up, filter CHAR, compute hold times and pauses
    raise NotImplementedError


def _match_hold_times(char_downs: list[dict], char_ups: list[dict]) -> list[float]:
    """Match key-down events to their corresponding key-up events.

    Uses a simple first-available-up strategy (not perfect but privacy-safe).
    """
    # TODO: for each down, find the first up with timestamp > down.timestamp
    raise NotImplementedError


def _zero_features() -> dict:
    keys = [
        "typing_rate", "key_count_total", "key_count_char",
        "hold_time_mean", "hold_time_std", "pause_mean", "pause_std",
    ]
    return {k: np.nan for k in keys}
