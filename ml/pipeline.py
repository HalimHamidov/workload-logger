"""
pipeline.py — Scikit-learn preprocessing + Ridge regression pipeline.

Steps
-----
1. SimpleImputer(strategy="median")   — fills NaN from sparse windows
2. StandardScaler()                   — z-score normalisation
3. Ridge(alpha=α)                     — regularized linear regression

Alpha is selected via nested LOO cross-validation over the grid:
    [0.01, 0.1, 1, 10, 100, 1000, 10000]

Usage
-----
pipe = build_pipeline()
pipe.set_params(model__alpha=100)
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
"""

from __future__ import annotations
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

ALPHA_GRID = [0.01, 0.1, 1, 10, 100, 1000, 10000]

TARGETS = [
    "tlx_mental_demand",
    "tlx_temporal_demand",
    "tlx_performance",
    "tlx_effort",
    "tlx_frustration",
    "tlx_mean",
]


def build_pipeline() -> Pipeline:
    """Return a fresh untrained pipeline instance."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("model",   Ridge()),
    ])
