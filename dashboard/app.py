"""
app.py — Streamlit dashboard entry point.

Run:
    streamlit run dashboard/app.py

Tabs
----
1. Live Monitor     Real-time workload indicators during an active session
2. Session History  Browse past sessions; charts, heatmaps, TLX radar
3. Model Analysis   Feature importance, PCA, actual vs predicted scatter
4. Participants     Compare feature distributions across participants
"""

import streamlit as st


def main() -> None:
    st.set_page_config(
        page_title="Workload Logger",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Workload Logger — Dashboard")

    tab_live, tab_history, tab_model, tab_participants = st.tabs([
        "Live Monitor",
        "Session History",
        "Model Analysis",
        "Participants",
    ])

    with tab_live:
        # TODO: from dashboard.realtime_panel import render
        st.info("Live monitor: start a session to see real-time data.")

    with tab_history:
        # TODO: from dashboard.session_analysis import render
        st.info("Session history will appear here after sessions are recorded.")

    with tab_model:
        # TODO: from dashboard.model_analysis import render
        st.info("Train a model first: python ml/train.py")

    with tab_participants:
        # TODO: participant comparison plots
        st.info("Add multiple participants to enable comparison.")


if __name__ == "__main__":
    main()
