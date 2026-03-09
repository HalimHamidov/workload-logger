"""Tests for features/trajectory_features.py — segmentation and features."""
import pytest
# from features.trajectory_features import segment_trajectories, Trajectory


class TestTrajectorySegmentation:
    def _move(self, x, y, t):
        return {"type": "mouse_move", "x": x, "y": y, "timestamp": t}

    def test_single_trajectory_no_gaps(self):
        moves = [self._move(0, 0, 0.0), self._move(10, 0, 0.1), self._move(20, 0, 0.2)]
        # TODO: trajs = segment_trajectories(moves, click_timestamps=[])
        # assert len(trajs) == 1
        pytest.skip("Implement segment_trajectories() first")

    def test_gap_creates_new_trajectory(self):
        moves = [
            self._move(0, 0, 0.0),
            self._move(1, 0, 0.1),
            self._move(2, 0, 0.4),   # gap of 0.3s > τ=0.15 → new trajectory
            self._move(3, 0, 0.5),
        ]
        # TODO: trajs = segment_trajectories(moves, click_timestamps=[])
        # assert len(trajs) == 2
        pytest.skip("Implement segment_trajectories() first")

    def test_short_trajectory_discarded(self):
        # Duration < 0.5s should be discarded
        moves = [self._move(0, 0, 0.0), self._move(10, 0, 0.2)]
        # TODO: trajs = segment_trajectories(moves, click_timestamps=[])
        # valid = [t for t in trajs if 0.5 <= t.duration <= 10.0]
        # assert len(valid) == 0
        pytest.skip("Implement segment_trajectories() first")

    def test_click_finalizes_trajectory(self):
        moves = [self._move(0, 0, 0.0), self._move(10, 0, 1.0), self._move(20, 0, 2.0)]
        # TODO: trajs = segment_trajectories(moves, click_timestamps=[1.5])
        # assert len(trajs) == 2
        pytest.skip("Implement segment_trajectories() first")


class TestTrajectoryMetrics:
    def test_efficiency_straight_line(self):
        # Straight line → efficiency = 1.0
        pytest.skip("Implement Trajectory.efficiency first")

    def test_curvature_straight_line(self):
        # Straight line → curvature = 0
        pytest.skip("Implement compute_trajectory_features() first")
