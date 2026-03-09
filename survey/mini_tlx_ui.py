"""
mini_tlx_ui.py — Adaptive 2-question micro-survey shown during a session.

A lightweight always-on-top popup appears every N minutes (default 2).
Asking only 2 questions keeps interruption minimal while multiplying
the number of labeled samples per session (~30 labels/hour instead of 1).

Questions
---------
1. Mental load right now?   (scale 1–10)
2. Frustration right now?   (scale 1–10)

Usage
-----
timer = MiniTLXTimer(interval_seconds=120, on_rating=save_mini_rating)
timer.start()
# ... session runs ...
timer.stop()
"""

from __future__ import annotations
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Callable


class MiniTLXTimer:
    """Schedules periodic micro-survey popups during an active session."""

    def __init__(self, interval_seconds: float = 120,
                 on_rating: Callable[[dict], None] | None = None) -> None:
        self.interval  = interval_seconds
        self.on_rating = on_rating
        self._running  = False
        self._timer: threading.Timer | None = None

    def start(self) -> None:
        self._running = True
        self._schedule_next()

    def stop(self) -> None:
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _schedule_next(self) -> None:
        if self._running:
            self._timer = threading.Timer(self.interval, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self) -> None:
        MiniTLXPopup(on_submit=self._handle_rating).show()
        self._schedule_next()

    def _handle_rating(self, rating: dict) -> None:
        rating["timestamp"] = time.time()
        if self.on_rating:
            self.on_rating(rating)


class MiniTLXPopup:
    """Small always-on-top window with 2 rating scales."""

    def __init__(self, on_submit: Callable[[dict], None]) -> None:
        self._on_submit = on_submit

    def show(self) -> None:
        """Display the popup (blocks until user submits)."""
        root = tk.Tk()
        root.title("Quick Check-In")
        root.attributes("-topmost", True)
        root.resizable(False, False)
        self._build_ui(root)
        root.mainloop()

    def _build_ui(self, root: tk.Tk) -> None:
        # TODO: build 2-question sliders + submit button
        raise NotImplementedError
