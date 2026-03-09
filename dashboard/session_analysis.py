"""
session_analysis.py — Per-session analysis tab.

Views
-----
- Sessions table with TLX scores (color-coded green→red)
- Feature time-series (per window) as line charts
- Mouse position density heatmap (plotly)
- NASA-TLX radar chart (plotly)
"""

from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


TLX_DIMENSIONS = [
    "tlx_mental_demand", "tlx_temporal_demand",
    "tlx_performance", "tlx_effort", "tlx_frustration",
]


def render(sessions_df: pd.DataFrame) -> None:
    """Render session history and per-session analysis."""
    st.subheader("Session History")

    if sessions_df.empty:
        st.info("No sessions recorded yet.")
        return

    # Sessions table
    display_cols = ["session_id", "participant_id", "task_type",
                    "window_count"] + TLX_DIMENSIONS + ["tlx_mean"]
    existing_cols = [c for c in display_cols if c in sessions_df.columns]
    st.dataframe(sessions_df[existing_cols], use_container_width=True)

    # Session selector
    session_ids = sessions_df["session_id"].tolist()
    selected_id = st.selectbox("Select session to inspect", session_ids)
    row = sessions_df[sessions_df["session_id"] == selected_id].iloc[0]

    col_radar, col_heat = st.columns(2)
    with col_radar:
        st.plotly_chart(tlx_radar(row), use_container_width=True)

    with col_heat:
        st.info("Mouse heatmap: requires raw input_events.jsonl for selected session.")
        # TODO: load move events and render mouse_heatmap(move_events)


def tlx_radar(session_row: pd.Series) -> go.Figure:
    """Radar chart of NASA-TLX dimensions for one session."""
    labels = ["Mental\nDemand", "Temporal\nDemand",
              "Performance", "Effort", "Frustration"]
    values = [session_row.get(col, 0) for col in TLX_DIMENSIONS]
    values.append(values[0])  # close the polygon

    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels + [labels[0]], fill="toself",
        line_color="royalblue",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="NASA-TLX Profile",
        showlegend=False,
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def mouse_heatmap(move_events: list[dict]) -> go.Figure:
    """2D density heatmap of mouse cursor positions."""
    xs = [e["x"] for e in move_events]
    ys = [e["y"] for e in move_events]
    fig = px.density_heatmap(
        x=xs, y=ys, nbinsx=80, nbinsy=60,
        color_continuous_scale="Viridis",
        title="Mouse Position Heatmap",
    )
    fig.update_yaxes(autorange="reversed")  # screen coordinates: y=0 at top
    return fig
