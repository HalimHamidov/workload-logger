"""
nasa_tlx_ui.py — Full post-session NASA-TLX survey (tkinter).

Displays 5 labeled sliders (0–100) and a live TLX Mean readout.
Calls the provided callback with the ratings dict when submitted.

Dimensions (Physical Demand excluded per paper design)
-------------------------------------------------------
1. Mental Demand       How mentally demanding was the task?
2. Temporal Demand     How hurried or rushed was the pace?
3. Own Performance     How successful were you?
4. Effort              How hard did you have to work?
5. Frustration Level   How stressed / annoyed were you?

Usage
-----
def on_submit(ratings: dict):
    print(ratings)  # {"mental_demand": 65, ..., "tlx_mean": 52.0}

NasaTLXSurvey(on_submit).show()
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable

DIMENSIONS = [
    ("mental_demand",    "Mental Demand",    "How mentally demanding was the task?"),
    ("temporal_demand",  "Temporal Demand",  "How hurried or rushed was the pace of the task?"),
    ("performance",      "Own Performance",  "How successful were you in accomplishing the task?"),
    ("effort",           "Effort",           "How hard did you have to work mentally?"),
    ("frustration",      "Frustration Level","How stressed, annoyed or frustrated were you?"),
]


class NasaTLXSurvey:
    """Modal tkinter window presenting the reduced NASA-TLX questionnaire."""

    def __init__(self, on_submit: Callable[[dict], None]) -> None:
        self._on_submit = on_submit
        self._sliders: dict[str, tk.IntVar] = {}

    def show(self) -> None:
        """Build and display the survey window (blocks until submitted)."""
        root = tk.Tk()
        root.title("NASA-TLX Workload Rating")
        root.resizable(False, False)
        self._build_ui(root)
        root.mainloop()

    def _build_ui(self, root: tk.Tk) -> None:
        # TODO: build labeled sliders, live mean label, submit button
        raise NotImplementedError

    def _on_slider_change(self, *_) -> None:
        """Update the live TLX mean display when any slider moves."""
        # TODO: recompute mean and update label
        raise NotImplementedError

    def _submit(self, root: tk.Tk) -> None:
        """Collect ratings, compute mean, call callback, close window."""
        ratings: dict = {}
        for key, var in self._sliders.items():
            ratings[f"tlx_{key}"] = var.get()

        values = list(ratings.values())
        ratings["tlx_mean"] = sum(values) / len(values)

        self._on_submit(ratings)
        root.destroy()
