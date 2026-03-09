"""
mouse_features.py — Computes mouse movement and click features for one window.

All features are computed from raw event dicts collected within a 5-second window.

Features returned
-----------------
mouse_distance          Total cursor path length (pixels)
mouse_speed_mean_time   Distance / active time (time-weighted mean speed)
mouse_speed_mean_sample Mean of per-sample instantaneous speeds
mouse_speed_std         Std dev of per-sample speeds
mouse_idle_time         Sum of gaps > τ between motion callbacks (seconds)
mouse_active_time       window_duration − idle_time
mouse_idle_ratio        idle_time / window_duration
mouse_active_ratio      1 − idle_ratio
click_count             Total mouse click-down events
click_rate              click_count / window_duration
click_hold_mean         Mean click press duration (down→up pairs)
click_hold_std          Std dev of click press durations
scroll_count            Total scroll events
scroll_dy_mean          Mean vertical scroll delta (dy)
"""

from __future__ import annotations
import numpy as np

IDLE_THRESHOLD = 0.15  # seconds — gap between samples treated as idle


def compute(move_events: list[dict], click_events: list[dict],
            scroll_events: list[dict], window_duration: float) -> dict:
    """Compute all mouse features for one 5-second window.

    Parameters
    ----------
    move_events     : list of {"x": int, "y": int, "timestamp": float}
    click_events    : list of {"button": str, "pressed": bool, "timestamp": float}
    scroll_events   : list of {"dy": int, "timestamp": float}
    window_duration : length of the window in seconds

    Returns
    -------
    dict of feature_name → float
    """
    # TODO: implement distance, speed, idle, click pairs, scroll aggregation
    raise NotImplementedError


def _zero_features() -> dict:
    """Return a dict of NaN values when there is insufficient data."""
    keys = [
        "mouse_distance", "mouse_speed_mean_time", "mouse_speed_mean_sample",
        "mouse_speed_std", "mouse_idle_time", "mouse_active_time",
        "mouse_idle_ratio", "mouse_active_ratio",
        "click_count", "click_rate", "click_hold_mean", "click_hold_std",
        "scroll_count", "scroll_dy_mean",
    ]
    return {k: np.nan for k in keys}
