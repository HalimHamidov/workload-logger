"""
window_aggregator.py — Aggregates raw events into fixed 5-second feature windows.

At the end of each window the aggregator:
1. Calls mouse_features, trajectory_features, keyboard_features
2. Calls DeletionEstimator.get_window_features()
3. Merges all feature dicts into one window row
4. Appends a window_aggregate record to input_events.jsonl
5. Stores the window row in memory for later session aggregation

Public API
----------
WindowAggregator.add_event(event: dict) → None
WindowAggregator.tick(timestamp: float) → None   # called every second
WindowAggregator.flush() → dict                  # force-close current window
WindowAggregator.get_all_windows() → list[dict]
"""

from __future__ import annotations
import time

# TODO: from features.mouse_features      import compute_mouse_features
# TODO: from features.trajectory_features import compute_trajectory_features
# TODO: from features.keyboard_features   import compute_keyboard_features


class WindowAggregator:
    """Manages the sliding 5-second window and triggers feature computation."""

    def __init__(self, window_size: float = 5.0, output_path: str = "") -> None:
        self.window_size  = window_size
        self.output_path  = output_path

        self._events:       list[dict] = []
        self._windows:      list[dict] = []
        self._window_start: float      = time.time()
        self._window_index: int        = 0

    def add_event(self, event: dict) -> None:
        """Buffer an incoming event."""
        self._events.append(event)

    def tick(self, timestamp: float) -> None:
        """Check if the current window has elapsed; if so, close it."""
        if timestamp - self._window_start >= self.window_size:
            self.flush()

    def flush(self) -> dict:
        """Force-close the current window and compute features.

        Returns the completed window feature dict.
        """
        # TODO: compute all feature groups
        # TODO: write window_aggregate record to JSONL
        # TODO: reset event buffer and window_start
        raise NotImplementedError

    def get_all_windows(self) -> list[dict]:
        """Return all completed window rows for this session."""
        return list(self._windows)

    def _write_to_disk(self, window_row: dict) -> None:
        """Append one window_aggregate record to input_events.jsonl."""
        # TODO: use jsonlines.open in append mode
        raise NotImplementedError
