"""
train.py — Model training with leave-one-out cross-validation.

Usage
-----
python ml/train.py
python ml/train.py --data data/session_dataset.jsonl
python ml/train.py --target tlx_mental_demand
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import LeaveOneOut, GridSearchCV

from ml.pipeline import build_pipeline, ALPHA_GRID, TARGETS
from ml.evaluate import compute_metrics, print_results_table


def load_dataset(path: str) -> pd.DataFrame:
    """Load session_dataset.jsonl into a DataFrame."""
    records = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    return pd.DataFrame(records)


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return numeric columns that are not target or metadata columns."""
    exclude = set(TARGETS) | {
        "session_id", "participant_id", "task_type", "task_name",
        "session_start", "session_end", "window_count",
        "tlx_mean", "mini_tlx_samples",
    }
    return [c for c in df.select_dtypes(include=[np.number]).columns
            if c not in exclude]


def train_loo(df: pd.DataFrame, target: str, models_dir: str = "models/") -> dict:
    """Run nested LOO cross-validation for one target variable.

    Returns a dict with MAE, RMSE, R² and the final model trained on all data.
    """
    feature_cols = get_feature_columns(df)
    valid = df[target].notna()
    X = df.loc[valid, feature_cols].values
    y = df.loc[valid, target].values

    if len(y) < 2:
        print(f"[train] Skipping {target}: not enough labeled samples ({len(y)})")
        return {}

    loo = LeaveOneOut()
    y_true_all, y_pred_all = [], []

    for train_idx, test_idx in loo.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        inner_cv = LeaveOneOut() if len(y_train) > 1 else None
        pipe = build_pipeline()

        if inner_cv:
            search = GridSearchCV(pipe, {"model__alpha": ALPHA_GRID},
                                  cv=inner_cv, scoring="neg_mean_squared_error",
                                  refit=True)
            search.fit(X_train, y_train)
            best = search.best_estimator_
        else:
            pipe.fit(X_train, y_train)
            best = pipe

        y_pred_all.append(best.predict(X_test)[0])
        y_true_all.append(y_test[0])

    metrics = compute_metrics(np.array(y_true_all), np.array(y_pred_all), target)

    # Train final model on all data
    final_pipe = build_pipeline()
    final_search = GridSearchCV(final_pipe, {"model__alpha": ALPHA_GRID},
                                cv=LeaveOneOut(), scoring="neg_mean_squared_error",
                                refit=True)
    final_search.fit(X, y)
    final_model = final_search.best_estimator_

    Path(models_dir).mkdir(exist_ok=True)
    model_path = f"{models_dir}/ridge_model_{target}.pkl"
    joblib.dump(final_model, model_path)

    # Save feature importance
    coefs = final_model.named_steps["model"].coef_
    importance = pd.DataFrame({"feature": feature_cols, "coefficient": coefs})
    importance["abs_coefficient"] = importance["coefficient"].abs()
    importance = importance.sort_values("abs_coefficient", ascending=False)
    importance.to_csv(f"{models_dir}/feature_importance_{target}.csv", index=False)

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",   default="data/session_dataset.jsonl")
    parser.add_argument("--target", default=None, help="Single target or all if omitted")
    parser.add_argument("--models", default="models/")
    args = parser.parse_args()

    df = load_dataset(args.data)
    targets = [args.target] if args.target else TARGETS

    all_results = []
    for target in targets:
        if target not in df.columns:
            print(f"[train] Column '{target}' not found, skipping.")
            continue
        result = train_loo(df, target, args.models)
        if result:
            all_results.append(result)

    if all_results:
        print_results_table(all_results)


if __name__ == "__main__":
    main()
