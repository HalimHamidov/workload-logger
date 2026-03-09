"""
event_logger.py — Background keyboard and mouse event capture.

Listens to all keyboard and mouse events via pynput, applies the privacy
filter (no raw text stored), and writes structured JSON records to
data/input_events.jsonl.

Events emitted
--------------
key_down       Key pressed (privacy-safe category only)
key_up         Key released
mouse_move     Cursor position (sampled at max config.logging.mouse_sample_rate_hz)
mouse_click    Button press or release
scroll         Scroll wheel event
window_aggregate  Feature dict for the completed 5-second window

Usage
-----
logger = EventLogger(config, participant_id="Zafar", task_type="writing")
logger.start()
# ... user works ...
logger.stop()
session_row = logger.build_session_row(tlx_ratings)
"""

from __future__ import annotations
import time
import uuid
import threading

# TODO: import pynput.keyboard, pynput.mouse
# TODO: import logger.privacy_filter
# TODO: import logger.window_aggregator
# TODO: import logger.deletion_estimator


class EventLogger:
    """Captures keyboard and mouse events and manages the session lifecycle."""

    def __init__(self, config: dict, participant_id: str = "default",
                 task_type: str = "free", task_name: str = "") -> None:
        self.config         = config
        self.participant_id = participant_id
        self.task_type      = task_type
        self.task_name      = task_name
        self.session_id     = str(uuid.uuid4())

        self._keyboard_listener = None
        self._mouse_listener    = None
        self._window_thread     = None
        self._running           = False
        self._session_start: float | None = None

        # TODO: initialize WindowAggregator, DeletionEstimator

    # ------------------------------------------------------------------
    # Session control
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start keyboard/mouse listeners and the windowing loop."""
        self._running = True
        self._session_start = time.time()
        # TODO: start pynput listeners
        # TODO: start window timer thread
        raise NotImplementedError

    def stop(self) -> None:
        """Stop all listeners and finalize the last partial window."""
        self._running = False
        # TODO: stop pynput listeners
        # TODO: flush partial window
        raise NotImplementedError

    def flush_current_window(self) -> None:
        """Force-finalize the current window (e.g., before sleep)."""
        # TODO: delegate to WindowAggregator
        raise NotImplementedError

    def restart_listeners(self) -> None:
        """Re-create pynput listeners after system wake from sleep."""
        # TODO: stop old listeners, create new ones
        raise NotImplementedError

    def build_session_row(self, tlx_ratings: dict | None) -> dict:
        """Aggregate all window rows into a single session-level training row.

        Parameters
        ----------
        tlx_ratings : dict with keys matching config.survey.nasa_tlx_dimensions,
                      or None if the survey was skipped.
        """
        # TODO: delegate to SessionAggregator
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Keyboard callbacks (called by pynput in a background thread)
    # ------------------------------------------------------------------

    def _on_key_press(self, key) -> None:
        # TODO: categorize key, record timestamp, update DeletionEstimator
        raise NotImplementedError

    def _on_key_release(self, key) -> None:
        # TODO: record release timestamp
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Mouse callbacks
    # ------------------------------------------------------------------

    def _on_mouse_move(self, x: int, y: int) -> None:
        # TODO: throttle to mouse_sample_rate_hz, append event
        raise NotImplementedError

    def _on_mouse_click(self, x: int, y: int, button, pressed: bool) -> None:
        # TODO: record click event, finalize active trajectory
        raise NotImplementedError

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        # TODO: record scroll event
        raise NotImplementedError
