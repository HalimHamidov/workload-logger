"""
evaluate.py — Metrics computation and results reporting.

Metrics
-------
MAE     Mean Absolute Error
RMSE    Root Mean Squared Error
R²      Coefficient of Determination
"""

from __future__ import annotations
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, target: str) -> dict:
    """Compute MAE, RMSE, and R² for one target.

    Parameters
    ----------
    y_true  : ground-truth TLX values
    y_pred  : model predictions
    target  : target variable name (for display)

    Returns
    -------
    dict with keys: target, MAE, RMSE, R2
    """
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)

    print(f"  {target:<30} MAE={mae:6.3f}  RMSE={rmse:6.3f}  R²={r2:+.3f}")
    return {"target": target, "MAE": mae, "RMSE": rmse, "R2": r2}


def print_results_table(results: list[dict]) -> None:
    """Print a formatted summary table of all target results."""
    header = f"{'Target':<30} {'MAE':>8} {'RMSE':>8} {'R²':>8}"
    print("\n" + "=" * len(header))
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['target']:<30} {r['MAE']:>8.3f} {r['RMSE']:>8.3f} {r['R2']:>+8.3f}")
    print("=" * len(header))
