"""
trajectory_features.py — Mouse trajectory segmentation and per-trajectory features.

A trajectory is a continuous mouse movement segment, bounded by:
  - Start of window
  - Inactivity gap > τ = 0.15 s
  - Mouse click

Trajectories outside [0.5s, 10s] duration are discarded.

Per-trajectory features
-----------------------
traj_speed          path_length / duration
traj_efficiency     straight_line_displacement / path_length
traj_curvature      mean absolute change in direction between segments
traj_dir_consist    proportion of segments preserving motion direction
traj_SAT            speed × (1 − direction_consistency)

Window-level features (aggregated over all valid trajectories)
--------------------------------------------------------------
traj_count              Number of valid trajectories
traj_speed_mean         Mean trajectory speed
traj_speed_std          Std dev of trajectory speeds
traj_efficiency_mean    Mean efficiency
traj_curvature_mean     Mean curvature
traj_dir_consist_mean   Mean direction consistency
traj_SAT_mean           Mean speed-accuracy tradeoff
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass


GAP_THRESHOLD    = 0.15   # seconds: inactivity gap → new trajectory
MIN_DURATION     = 0.5    # seconds: discard shorter trajectories
MAX_DURATION     = 10.0   # seconds: discard longer trajectories
MIN_DISPLACEMENT = 10.0   # pixels: min displacement to compute efficiency


@dataclass
class Trajectory:
    points: list[tuple[float, float, float]]  # (x, y, timestamp)

    @property
    def duration(self) -> float:
        if len(self.points) < 2:
            return 0.0
        return self.points[-1][2] - self.points[0][2]

    @property
    def path_length(self) -> float:
        # TODO: sum of Euclidean distances between consecutive points
        raise NotImplementedError

    @property
    def displacement(self) -> float:
        # TODO: Euclidean distance from first to last point
        raise NotImplementedError


def segment_trajectories(move_events: list[dict],
                         click_timestamps: list[float]) -> list[Trajectory]:
    """Split mouse move events into trajectory segments.

    Parameters
    ----------
    move_events       : list of {"x": int, "y": int, "timestamp": float}
    click_timestamps  : list of click timestamps that finalize trajectories
    """
    # TODO: iterate events, split on gaps > GAP_THRESHOLD and click times
    raise NotImplementedError


def compute_trajectory_features(traj: Trajectory) -> dict | None:
    """Compute features for a single trajectory.

    Returns None if the trajectory does not meet duration requirements.
    """
    # TODO: speed, efficiency, curvature, direction consistency, SAT
    raise NotImplementedError


def compute(move_events: list[dict], click_timestamps: list[float]) -> dict:
    """Compute window-level trajectory features.

    Returns aggregated mean/std/count across all valid trajectories.
    """
    # TODO: segment → filter → compute per-traj → aggregate
    raise NotImplementedError


def _zero_features() -> dict:
    keys = [
        "traj_count", "traj_speed_mean", "traj_speed_std",
        "traj_efficiency_mean", "traj_curvature_mean",
        "traj_dir_consist_mean", "traj_SAT_mean",
    ]
    return {k: np.nan for k in keys}
