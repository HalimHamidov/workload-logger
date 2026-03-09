"""
task_protocol.py — Gamified structured task runner for controlled data collection.

Runs tasks with predefined workload levels so that ground-truth cognitive load
is known. This helps calibrate models and verify feature-label alignment.

Task Levels
-----------
Level 1 — Low workload     Simple copy-paste (3 min)   Expected TLX: 10–25
Level 2 — Medium workload  Typing speed test (3 min)   Expected TLX: 30–55
Level 3 — High workload    Essay + mental math (3 min) Expected TLX: 60–90
Level 4 — Very high        Speed typing + fix all typos (2 min) TLX: 75–95

Usage
-----
protocol = TaskProtocol(event_logger, mini_tlx_timer)
protocol.run(task_index=2)   # runs Level 3 task end-to-end
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Task:
    name: str
    level: int                # 1–4
    duration_seconds: int
    instruction: str
    sample_text: str = ""     # text shown on screen for copy/typing tasks
    expected_tlx_range: tuple[int, int] = (0, 100)


TASKS: list[Task] = [
    Task(
        name="Copy-Paste Baseline",
        level=1,
        duration_seconds=180,
        instruction=(
            "Copy the text shown below into the text box. "
            "Take your time — there is no rush."
        ),
        expected_tlx_range=(10, 25),
    ),
    Task(
        name="Typing Speed Test",
        level=2,
        duration_seconds=180,
        instruction=(
            "Type the paragraph below as fast and accurately as you can."
        ),
        expected_tlx_range=(30, 55),
    ),
    Task(
        name="Dual Task: Write + Mental Math",
        level=3,
        duration_seconds=180,
        instruction=(
            "Write a short paragraph about your day. "
            "At the same time, count backwards from 300 by 7 in your head. "
            "Do both simultaneously."
        ),
        expected_tlx_range=(60, 90),
    ),
    Task(
        name="Speed Typing Under Pressure",
        level=4,
        duration_seconds=120,
        instruction=(
            "Type as fast as possible. "
            "You MUST fix every typo before continuing to the next word. "
            "A timer is counting down — do not stop!"
        ),
        expected_tlx_range=(75, 95),
    ),
]


class TaskProtocol:
    """Orchestrates structured task sessions end-to-end."""

    def __init__(self, event_logger, mini_tlx_timer) -> None:
        self.logger   = event_logger
        self.mini_tlx = mini_tlx_timer

    def run(self, task_index: int, participant_id: str = "default") -> None:
        """Run one task: show instructions → log → stop → show TLX survey.

        Parameters
        ----------
        task_index    : index into TASKS list (0–3)
        participant_id: identifier stored with the session
        """
        task = TASKS[task_index]

        # TODO: show instruction + countdown window (tkinter)
        # TODO: self.logger.start(participant_id, task_type=f"level{task.level}", task_name=task.name)
        # TODO: self.mini_tlx.start()
        # TODO: wait task.duration_seconds
        # TODO: self.mini_tlx.stop()
        # TODO: self.logger.stop()
        # TODO: show NasaTLXSurvey → save session
        raise NotImplementedError
