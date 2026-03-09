"""
power_manager.py — Detects Windows sleep and wake events.

Uses pywin32 to register a hidden message-only window that receives
WM_POWERBROADCAST messages from Windows. When sleep is detected the
session is saved; when wake is detected the listeners are restarted
and a new session begins automatically.

Public API
----------
PowerManager(on_sleep, on_wake).start() → None
register_autostart(script_path) → None     # one-time setup
remove_autostart() → None
"""

from __future__ import annotations
import subprocess
import threading
from typing import Callable

# TODO: import win32api, win32con, win32gui  (requires pywin32)


class PowerManager:
    """Listens for Windows power events (sleep / wake) in a background thread."""

    def __init__(self, on_sleep: Callable, on_wake: Callable) -> None:
        self.on_sleep = on_sleep
        self.on_wake  = on_wake
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Spawn a daemon thread that pumps Windows messages."""
        self._thread = threading.Thread(target=self._message_loop, daemon=True)
        self._thread.start()

    def _message_loop(self) -> None:
        """Register a hidden window and process WM_POWERBROADCAST messages.

        WM_POWERBROADCAST wParam values:
            PBT_APMSUSPEND          (0x0004)  System is about to sleep
            PBT_APMRESUMEAUTOMATIC  (0x0012)  System resumed (even without user)
            PBT_APMRESUMESUSPEND    (0x0007)  System resumed by user interaction
        """
        # TODO: implement with win32gui.RegisterClass + win32gui.PumpMessages
        raise NotImplementedError

    def _wnd_proc(self, hwnd, msg, wparam, lparam) -> int:
        """Window procedure that handles power broadcast messages."""
        # TODO: check msg == win32con.WM_POWERBROADCAST
        #       wparam == win32con.PBT_APMSUSPEND    → self.on_sleep()
        #       wparam == win32con.PBT_APMRESUMEAUTOMATIC → self.on_wake()
        raise NotImplementedError


def register_autostart(script_path: str) -> None:
    """Register the program in Windows Task Scheduler to run on every login.

    This is a one-time setup call. Run via:
        python main.py --setup

    Uses schtasks (no admin rights required with /rl LIMITED).
    """
    cmd = [
        "schtasks", "/create",
        "/tn", "WorkloadLogger",
        "/tr", f'pythonw.exe "{script_path}" --tray',
        "/sc", "ONLOGON",
        "/rl", "LIMITED",
        "/f",
    ]
    subprocess.run(cmd, check=True)
    print(f"[setup] Auto-start registered: {' '.join(cmd)}")


def remove_autostart() -> None:
    """Remove the WorkloadLogger task from Windows Task Scheduler."""
    subprocess.run(["schtasks", "/delete", "/tn", "WorkloadLogger", "/f"], check=True)
    print("[setup] Auto-start removed.")
