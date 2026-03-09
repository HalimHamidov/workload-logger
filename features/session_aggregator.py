"""
session_aggregator.py — Aggregates window rows into a single session training row.

For each window-level feature f the following are computed across all windows:
    session_f_mean    arithmetic mean
    session_f_std     standard deviation
    session_f_min     minimum
    session_f_max     maximum

With ~33 window features × 4 aggregations this yields ~134 session columns.
The output dict is written as one row to data/session_dataset.jsonl.

Public API
----------
aggregate(windows, session_meta, tlx_ratings) → dict
"""

from __future__ import annotations
import numpy as np
import pandas as pd


AGGREGATIONS = ("mean", "std", "min", "max")


def aggregate(windows: list[dict],
              session_meta: dict,
              tlx_ratings: dict | None = None) -> dict:
    """Build a single session-level row from a list of window feature dicts.

    Parameters
    ----------
    windows      : list of window feature dicts (one per 5-second window)
    session_meta : dict with session_id, participant_id, task_type, etc.
    tlx_ratings  : dict with NASA-TLX dimension scores, or None

    Returns
    -------
    dict — one flat row ready to append to session_dataset.jsonl
    """
    if not windows:
        return {**session_meta, "window_count": 0}

    df = pd.DataFrame(windows)

    row: dict = {**session_meta, "window_count": len(windows)}

    for col in df.select_dtypes(include=[np.number]).columns:
        row[f"{col}_mean"] = df[col].mean()
        row[f"{col}_std"]  = df[col].std()
        row[f"{col}_min"]  = df[col].min()
        row[f"{col}_max"]  = df[col].max()

    if tlx_ratings:
        row.update(tlx_ratings)
        numeric_scores = [v for v in tlx_ratings.values()
                          if isinstance(v, (int, float))]
        row["tlx_mean"] = sum(numeric_scores) / len(numeric_scores) if numeric_scores else None

    return row
