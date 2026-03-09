"""
realtime_panel.py — Live session monitor tab.

Displays current-window metrics refreshed every second:
  - Typing rate (chars/sec)
  - Mouse speed (px/sec)
  - Mouse idle ratio (%)
  - Estimated workload level (from last trained model)
  - Line chart: last 60 seconds of each metric
"""

from __future__ import annotations
import streamlit as st


def render(shared_state: dict) -> None:
    """Render the live monitor panel.

    Parameters
    ----------
    shared_state : dict updated by the logger background thread with
                   keys: session_active, latest_window, history_60s
    """
    st.subheader("Live Session Monitor")

    if not shared_state.get("session_active"):
        st.warning("No active session. Start a session from the command line.")
        return

    latest = shared_state.get("latest_window", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Typing Rate",  f"{latest.get('typing_rate', 0):.2f} k/s")
    col2.metric("Mouse Speed",  f"{latest.get('mouse_speed_mean_sample', 0):.0f} px/s")
    col3.metric("Idle Ratio",   f"{latest.get('mouse_idle_ratio', 0):.1%}")
    col4.metric("Est. Workload", latest.get("estimated_workload", "—"))

    # TODO: line chart over last 60 seconds
    # TODO: auto-refresh with st.rerun() on interval
