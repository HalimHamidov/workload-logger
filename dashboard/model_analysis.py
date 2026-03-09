"""
model_analysis.py — Model analysis tab.

Views
-----
- Results table: MAE, RMSE, R² per target
- Feature importance bar chart (top 20 by |coefficient|)
- PCA scatter of sessions colored by TLX Mean
- Actual vs Predicted scatter per target
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def render(sessions_df: pd.DataFrame, importance_dfs: dict[str, pd.DataFrame],
           loo_results: list[dict]) -> None:
    """Render the model analysis tab.

    Parameters
    ----------
    sessions_df     : all sessions DataFrame
    importance_dfs  : {target_name: feature_importance_df}
    loo_results     : list of {target, MAE, RMSE, R2}
    """
    st.subheader("Model Analysis")

    if not loo_results:
        st.info("No model results yet. Run: python ml/train.py")
        return

    # Results table
    results_df = pd.DataFrame(loo_results)
    st.dataframe(results_df.set_index("target").style.format("{:.3f}"),
                 use_container_width=True)

    # Feature importance
    target = st.selectbox("Select target for feature importance",
                          list(importance_dfs.keys()))
    if target in importance_dfs:
        imp_df = importance_dfs[target].head(20)
        fig = px.bar(imp_df, x="abs_coefficient", y="feature",
                     orientation="h", title=f"Top 20 Features — {target}",
                     color="coefficient",
                     color_continuous_scale="RdBu_r")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    # PCA plot
    if "tlx_mean" in sessions_df.columns:
        st.plotly_chart(pca_plot(sessions_df), use_container_width=True)


def pca_plot(df: pd.DataFrame) -> "go.Figure":
    """2D PCA scatter of sessions colored by TLX Mean."""
    exclude = {"session_id", "participant_id", "task_type", "task_name",
               "session_start", "session_end", "window_count", "mini_tlx_samples"}
    tlx_cols = {c for c in df.columns if c.startswith("tlx_")}
    feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                    if c not in exclude and c not in tlx_cols]

    X = SimpleImputer(strategy="median").fit_transform(df[feature_cols])
    X = StandardScaler().fit_transform(X)
    components = PCA(n_components=2).fit_transform(X)

    plot_df = pd.DataFrame({
        "PC1": components[:, 0],
        "PC2": components[:, 1],
        "TLX Mean": df["tlx_mean"].values,
        "Participant": df.get("participant_id", ["?"]*len(df)),
    })
    return px.scatter(
        plot_df, x="PC1", y="PC2", color="TLX Mean",
        symbol="Participant",
        color_continuous_scale="RdYlGn_r",
        title="Session PCA (colored by TLX Mean workload)",
    )
