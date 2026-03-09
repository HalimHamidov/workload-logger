"""
deletion_estimator.py — Estimates deleted character counts without storing text.

Because no actual text is logged, deletion sizes are estimated using heuristics
and tagged with a confidence level. A confidence-weighted sum is maintained
alongside the raw total.

Confidence levels and weights (from config)
-------------------------------------------
high   (1.0)  Plain Backspace / Delete → exactly 1 character
medium (0.6)  Ctrl+Backspace / Ctrl+Delete → estimated 1 word
low    (0.3)  Selection-based deletion → estimated from selection heuristics

Public API
----------
DeletionEstimator.observe(event, modifier_state) → None
DeletionEstimator.get_window_features() → dict
DeletionEstimator.reset_window() → None
"""

from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Deque

CONFIDENCE_WEIGHTS = {"high": 1.0, "medium": 0.6, "low": 0.3}


@dataclass
class DeletionBurst:
    estimated_chars: float
    confidence: str  # "high" | "medium" | "low"

    @property
    def weighted(self) -> float:
        return CONFIDENCE_WEIGHTS[self.confidence] * self.estimated_chars


class WordLengthTracker:
    """Tracks a rolling median of observed word lengths."""

    def __init__(self, maxlen: int = 20, fallback: int = 5) -> None:
        self._lengths: Deque[int] = deque(maxlen=maxlen)
        self._fallback = fallback

    def observe(self, word_length: int) -> None:
        if word_length > 0:
            self._lengths.append(word_length)

    def median(self) -> int:
        if not self._lengths:
            return self._fallback
        sorted_lengths = sorted(self._lengths)
        n = len(sorted_lengths)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_lengths[mid - 1] + sorted_lengths[mid]) // 2
        return sorted_lengths[mid]


class DeletionEstimator:
    """Estimates deleted character counts using confidence-weighted heuristics."""

    def __init__(self, confidence_weights: dict | None = None,
                 word_length_maxlen: int = 20, word_length_fallback: int = 5) -> None:
        self._weights = confidence_weights or CONFIDENCE_WEIGHTS
        self._word_tracker = WordLengthTracker(word_length_maxlen, word_length_fallback)
        self._bursts: list[DeletionBurst] = []
        self._chars_since_last_space: int = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def observe_char(self) -> None:
        """Call when a CHAR key is pressed (to track word length)."""
        self._chars_since_last_space += 1

    def observe_space_or_enter(self) -> None:
        """Call when SPACE or ENTER is pressed (word boundary)."""
        self._word_tracker.observe(self._chars_since_last_space)
        self._chars_since_last_space = 0

    def observe_deletion(self, key_category: str, modifier_ctrl: bool,
                         selection_size: int = 0) -> None:
        """Record a deletion event.

        Parameters
        ----------
        key_category    : "BACKSPACE" or "DELETE"
        modifier_ctrl   : True if Ctrl was held during the deletion
        selection_size  : estimated number of chars selected before deletion
                          (0 means no active selection)
        """
        if selection_size > 0:
            burst = DeletionBurst(float(selection_size), "low")
        elif modifier_ctrl:
            estimated = float(self._word_tracker.median())
            burst = DeletionBurst(estimated, "medium")
        else:
            burst = DeletionBurst(1.0, "high")

        self._bursts.append(burst)

    def get_window_features(self) -> dict:
        """Return deletion feature dict for the current window.

        Keys
        ----
        del_total        Total estimated deleted characters
        del_high         Deleted chars from high-confidence bursts
        del_medium       Deleted chars from medium-confidence bursts
        del_low          Deleted chars from low-confidence bursts
        del_weighted     Confidence-weighted total: Σ w(c_b) * d_b
        del_conf_score   del_weighted / del_total  (0 if del_total == 0)
        del_rate         del_total / window_duration (filled by aggregator)
        """
        total = sum(b.estimated_chars for b in self._bursts)
        high   = sum(b.estimated_chars for b in self._bursts if b.confidence == "high")
        medium = sum(b.estimated_chars for b in self._bursts if b.confidence == "medium")
        low    = sum(b.estimated_chars for b in self._bursts if b.confidence == "low")
        weighted = sum(b.weighted for b in self._bursts)

        return {
            "del_total":      total,
            "del_high":       high,
            "del_medium":     medium,
            "del_low":        low,
            "del_weighted":   weighted,
            "del_conf_score": weighted / total if total > 0 else 0.0,
        }

    def reset_window(self) -> None:
        """Clear burst buffer at the start of a new window."""
        self._bursts.clear()
