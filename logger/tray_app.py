"""
tray_app.py — System tray icon for background operation.

The program runs invisibly with a small colored dot in the Windows
system tray (notification area). The icon is:
  - Green  when a session is actively being recorded
  - Grey   when paused or no session is running

Right-click menu:
  Open Dashboard      → launches Streamlit dashboard in browser
  End Session Now     → stops logger and shows TLX survey
  Pause / Resume      → toggles logging without ending the session
  Exit                → stops everything cleanly

Public API
----------
TrayApp(session_manager, dashboard_launcher).start() → None
TrayApp.notify(message) → None
TrayApp.set_active(active: bool) → None
"""

from __future__ import annotations
from typing import Callable

# TODO: import pystray
# TODO: from PIL import Image, ImageDraw


class TrayApp:
    """Manages the system tray icon and its right-click context menu."""

    def __init__(self, on_open_dashboard: Callable,
                 on_end_session: Callable,
                 on_toggle_pause: Callable,
                 on_quit: Callable) -> None:
        self._on_open_dashboard = on_open_dashboard
        self._on_end_session    = on_end_session
        self._on_toggle_pause   = on_toggle_pause
        self._on_quit           = on_quit
        self._icon              = None

    def start(self) -> None:
        """Build and start the tray icon in a daemon thread."""
        # TODO: build pystray.Icon with menu
        # TODO: run icon in daemon thread
        raise NotImplementedError

    def notify(self, message: str, title: str = "Workload Logger") -> None:
        """Show a Windows balloon notification from the tray icon."""
        # TODO: self._icon.notify(message, title)
        raise NotImplementedError

    def set_active(self, active: bool) -> None:
        """Update icon color and tooltip to reflect session state."""
        # TODO: rebuild icon image (green/grey) and update title
        raise NotImplementedError

    def stop(self) -> None:
        """Remove the tray icon."""
        # TODO: self._icon.stop()
        raise NotImplementedError

    @staticmethod
    def _build_icon_image(active: bool):
        """Draw a 64×64 circle: green when active, grey when idle."""
        # TODO: PIL Image + ImageDraw circle
        raise NotImplementedError
