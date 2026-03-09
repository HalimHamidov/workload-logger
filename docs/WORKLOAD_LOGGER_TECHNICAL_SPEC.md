# Workload Logger — Full Technical Implementation Specification

**Project:** Privacy-Preserving Workload Logger Using Keyboard and Mouse Dynamics
**Author:** Zafar Hamidov
**Based on:** Workload_Logger.pdf (February 26, 2026)
**Created:** 2026-03-09

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Dependencies & Environment Setup](#3-dependencies--environment-setup)
4. [Module 1 — Event Logger](#4-module-1--event-logger)
5. [Module 2 — Window Aggregator](#5-module-2--window-aggregator)
6. [Module 3 — Session Aggregator](#6-module-3--session-aggregator)
7. [Module 4 — Deletion Estimator](#7-module-4--deletion-estimator)
8. [Module 5 — NASA-TLX Survey UI](#8-module-5--nasa-tlx-survey-ui)
9. [Module 6 — ML Pipeline](#9-module-6--ml-pipeline)
10. [Module 7 — Interactive Dashboard](#10-module-7--interactive-dashboard)
11. [Module 8 — Adaptive Mini-TLX System](#11-module-8--adaptive-mini-tlx-system)
12. [Module 9 — Gamified Task Protocol](#12-module-9--gamified-task-protocol)
13. [Module 10 — System Tray & Power Events](#13-module-10--system-tray--power-events)
14. [Data Schemas](#14-data-schemas)
15. [Privacy & Security](#15-privacy--security)
16. [Testing Plan](#16-testing-plan)
17. [Improvement Roadmap](#17-improvement-roadmap)

---

## 1. Project Overview

### Goal
Build a lightweight desktop application that:
- Captures keyboard/mouse interaction dynamics **without recording typed content**
- Aggregates raw events into behavioral features in 5-second windows
- Collects subjective workload ratings via NASA-TLX after each session
- Trains a regression model to predict cognitive workload from input dynamics
- Displays a real-time interactive dashboard for live feedback and analysis

### Core Principles
- **Privacy-first:** No keystrokes, no text, no screenshots stored
- **Local-only:** All data stays on the user's machine
- **Scalable:** Architecture supports growing from 7 → 200+ sessions
- **Interactive:** Real-time feedback + adaptive micro-surveys

### Expected Outputs
| File | Description |
|---|---|
| `data/input_events.jsonl` | Raw events + per-window aggregates |
| `data/session_dataset.jsonl` | One row per session with 134 features + TLX labels |
| `data/mini_tlx_labels.jsonl` | Within-session 2-min micro-ratings |
| `models/ridge_model_<target>.pkl` | Trained Ridge regression models |
| `models/feature_importance_<target>.csv` | Feature importance per target |

---

## 2. Repository Structure

```
workload_logger/
├── README.md
├── requirements.txt
├── config.yaml                    # All tunable parameters
├── main.py                        # Entry point: start/stop session
│
├── logger/
│   ├── __init__.py
│   ├── event_logger.py            # Captures keyboard + mouse events
│   ├── privacy_filter.py          # Sanitizes key identities
│   ├── deletion_estimator.py      # Confidence-weighted deletion counts
│   └── window_aggregator.py       # 5-second feature windows
│
├── features/
│   ├── __init__.py
│   ├── mouse_features.py          # Distance, speed, idle, clicks
│   ├── trajectory_features.py     # Efficiency, curvature, SAT
│   ├── keyboard_features.py       # Typing rate, hold times, pauses
│   └── session_aggregator.py      # mean/std/min/max across windows
│
├── survey/
│   ├── __init__.py
│   ├── nasa_tlx_ui.py             # Full post-session TLX popup (tkinter)
│   └── mini_tlx_ui.py             # Adaptive 2-question micro-survey popup
│
├── ml/
│   ├── __init__.py
│   ├── pipeline.py                # Impute → Scale → Ridge regression
│   ├── train.py                   # LOO cross-validation + hyperparameter tuning
│   └── evaluate.py                # MAE, RMSE, R² reporting
│
├── dashboard/
│   ├── __init__.py
│   ├── app.py                     # Streamlit dashboard entry point
│   ├── realtime_panel.py          # Live workload meter
│   ├── session_analysis.py        # Per-session feature plots
│   └── model_analysis.py          # Feature importance, PCA, predictions
│
├── tasks/
│   ├── __init__.py
│   └── task_protocol.py           # Gamified structured task runner
│
└── data/
    ├── input_events.jsonl
    ├── session_dataset.jsonl
    └── mini_tlx_labels.jsonl
```

---

## 3. Dependencies & Environment Setup

### requirements.txt
```
pynput>=1.7.6          # keyboard + mouse event capture
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
joblib>=1.3.0          # model serialization
streamlit>=1.32.0      # dashboard
plotly>=5.18.0         # interactive charts
pyyaml>=6.0            # config loading
jsonlines>=4.0.0       # JSONL read/write
cryptography>=42.0.0   # optional: encrypt data at rest
tkinter                # bundled with Python (survey UI)
```

### config.yaml (all tunable parameters)
```yaml
logging:
  window_size_seconds: 5          # W: feature window length
  trajectory_gap_threshold: 0.15  # τ: inactivity threshold (seconds)
  trajectory_min_duration: 0.5    # discard trajectories shorter than this
  trajectory_max_duration: 10.0   # discard trajectories longer than this
  trajectory_min_displacement: 10 # pixels: minimum to compute efficiency

deletion:
  confidence_weights:
    high: 1.0       # plain Backspace/Delete
    medium: 0.6     # Ctrl+Backspace (word delete)
    low: 0.3        # selection-based deletion

survey:
  mini_tlx_interval_minutes: 2    # how often mini-TLX appears mid-session
  nasa_tlx_dimensions:
    - Mental Demand
    - Temporal Demand
    - Own Performance
    - Effort
    - Frustration Level

ml:
  alpha_grid: [0.01, 0.1, 1, 10, 100, 1000, 10000]
  random_seed: 42

data:
  output_dir: "data/"
  models_dir: "models/"
```

### Setup Commands
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4. Module 1 — Event Logger

**File:** `logger/event_logger.py`

### Responsibility
Use `pynput` to listen for keyboard and mouse events and write them to `data/input_events.jsonl`.

### Privacy Filter (`logger/privacy_filter.py`)
Map every key to a privacy-safe category before logging:

```python
KEY_CATEGORIES = {
    "char":      "CHAR",         # a-z, A-Z, 0-9, punctuation
    "backspace":  "BACKSPACE",
    "delete":     "DELETE",
    "space":      "SPACE",
    "enter":      "ENTER",
    "tab":        "TAB",
    "ctrl":       "CTRL",
    "shift":      "SHIFT",
    "alt":        "ALT",
    "arrow":      "ARROW",       # Left, Right, Up, Down
    "function":   "FUNCTION",    # F1–F12
    "other":      "OTHER",
}
```

**Rule:** If a key is alphanumeric or punctuation → log as `CHAR`. Never log the actual character.

### Event Schema
Each line in `input_events.jsonl` is one of the following JSON objects:

```jsonc
// Keyboard event
{
  "type": "key_down",          // or "key_up"
  "key_category": "CHAR",      // privacy-safe category
  "timestamp": 1741500000.123, // Unix epoch float
  "session_id": "abc123"
}

// Mouse move event (sampled, not every pixel)
{
  "type": "mouse_move",
  "x": 854,
  "y": 432,
  "timestamp": 1741500000.456,
  "session_id": "abc123"
}

// Mouse click event
{
  "type": "mouse_click",
  "button": "left",            // "left", "right", "middle"
  "pressed": true,             // true = down, false = up
  "x": 854,
  "y": 432,
  "timestamp": 1741500000.789,
  "session_id": "abc123"
}

// Scroll event
{
  "type": "scroll",
  "dx": 0,
  "dy": -3,
  "timestamp": 1741500001.000,
  "session_id": "abc123"
}

// Window aggregate (appended at end of each 5s window)
{
  "type": "window_aggregate",
  "window_index": 0,
  "window_start": 1741500000.0,
  "window_end": 1741500005.0,
  "session_id": "abc123",
  "features": { /* see Section 5 */ }
}
```

### Implementation Notes
- Use `pynput.keyboard.Listener` and `pynput.mouse.Listener` running in background threads
- Mouse move events: sample at most every 16ms (≈60Hz) to avoid log bloat
- Store all events in an in-memory list during the window, flush to disk at window end
- Session ID: generate with `uuid.uuid4()` at session start

---

## 5. Module 2 — Window Aggregator

**File:** `logger/window_aggregator.py`
**File:** `features/mouse_features.py`
**File:** `features/trajectory_features.py`
**File:** `features/keyboard_features.py`

### Window Processing Loop
```
Every W=5 seconds:
1. Take snapshot of events collected since last window boundary
2. Compute mouse features  → mouse_features.compute(events)
3. Compute trajectory features → trajectory_features.compute(mouse_moves)
4. Compute keyboard features → keyboard_features.compute(key_events)
5. Compute deletion features → deletion_estimator.compute(key_events, state)
6. Merge all feature dicts into one window row
7. Append window row to in-memory window list
8. Append "window_aggregate" record to input_events.jsonl
9. Clear event buffer
```

---

### 5.1 Mouse Features

**File:** `features/mouse_features.py`

| Feature Name | Formula / Description |
|---|---|
| `mouse_distance` | Sum of Euclidean distances between consecutive (x,y) samples |
| `mouse_speed_mean_time` | Total distance / total active time (time-weighted) |
| `mouse_speed_mean_sample` | Mean of per-sample speeds (sample-weighted) |
| `mouse_speed_std` | Std dev of per-sample speeds |
| `mouse_idle_time` | Sum of gaps > τ=0.15s between motion callbacks |
| `mouse_active_time` | Window duration − idle time |
| `mouse_idle_ratio` | idle_time / window_duration |
| `mouse_active_ratio` | 1 − idle_ratio |
| `click_count` | Total mouse click-down events |
| `click_rate` | click_count / window_duration |
| `click_hold_mean` | Mean duration between click-down and click-up pairs |
| `click_hold_std` | Std dev of click-hold durations |
| `scroll_count` | Total scroll events |
| `scroll_dy_mean` | Mean vertical scroll delta |

**Implementation detail — speed calculation:**
```python
import numpy as np

def compute_mouse_features(move_events, window_duration):
    if len(move_events) < 2:
        return zeros_dict()

    xs = np.array([e["x"] for e in move_events])
    ys = np.array([e["y"] for e in move_events])
    ts = np.array([e["timestamp"] for e in move_events])

    dists = np.sqrt(np.diff(xs)**2 + np.diff(ys)**2)
    dts   = np.diff(ts)
    dts   = np.where(dts < 1e-6, 1e-6, dts)  # avoid divide-by-zero

    speeds = dists / dts
    total_distance = dists.sum()

    # idle: gaps where dt > 0.15s
    idle_mask = dts > 0.15
    idle_time = dts[idle_mask].sum()
    active_time = window_duration - idle_time

    return {
        "mouse_distance": total_distance,
        "mouse_speed_mean_time": total_distance / max(active_time, 1e-6),
        "mouse_speed_mean_sample": speeds.mean(),
        "mouse_speed_std": speeds.std(),
        "mouse_idle_time": idle_time,
        "mouse_active_time": active_time,
        "mouse_idle_ratio": idle_time / window_duration,
        "mouse_active_ratio": active_time / window_duration,
    }
```

---

### 5.2 Mouse Trajectory Features

**File:** `features/trajectory_features.py`

**Trajectory Segmentation:**
- Start a new trajectory at: window start, after a gap > τ=0.15s, or after a click
- End/finalize a trajectory at: next click or large time gap
- **Discard** trajectories with duration < 0.5s or > 10s

**Per-trajectory computed values:**

| Feature | Formula |
|---|---|
| `traj_speed` | path_length / duration |
| `traj_efficiency` | straight_line_displacement / path_length (if displacement > min_threshold) |
| `traj_curvature` | mean( abs( angle_change between consecutive segments ) ) |
| `traj_direction_consistency` | proportion of consecutive segments preserving direction sign |
| `traj_SAT` | traj_speed × (1 − direction_consistency) |

**Window-level trajectory features (aggregated over all valid trajectories):**

| Feature | Description |
|---|---|
| `traj_count` | Number of valid trajectories in window |
| `traj_speed_mean` | Mean of per-trajectory speeds |
| `traj_speed_std` | Std dev of per-trajectory speeds |
| `traj_efficiency_mean` | Mean efficiency (NaN if no valid trajectories) |
| `traj_curvature_mean` | Mean curvature |
| `traj_direction_consistency_mean` | Mean direction consistency |
| `traj_SAT_mean` | Mean speed-accuracy tradeoff |

**Curvature calculation:**
```python
def compute_curvature(xs, ys):
    dx = np.diff(xs)
    dy = np.diff(ys)
    # angle of each segment
    angles = np.arctan2(dy, dx)
    # absolute change in angle between consecutive segments
    angle_changes = np.abs(np.diff(angles))
    # wrap to [0, pi]
    angle_changes = np.minimum(angle_changes, 2*np.pi - angle_changes)
    return angle_changes.mean() if len(angle_changes) > 0 else np.nan
```

---

### 5.3 Keyboard Features

**File:** `features/keyboard_features.py`

Only events with `key_category == "CHAR"` are used for typing rhythm features.

| Feature | Formula |
|---|---|
| `typing_rate` | count(CHAR key_down) / window_duration |
| `key_count_total` | count(all key_down) |
| `key_count_char` | count(CHAR key_down) |
| `hold_time_mean` | mean(key_up.ts − key_down.ts) for CHAR keys |
| `hold_time_std` | std of above |
| `pause_mean` | mean(next_key_down.ts − prev_key_down.ts) for consecutive CHAR pairs |
| `pause_std` | std of above |

**Implementation detail:**
```python
def compute_keyboard_features(key_events, window_duration):
    char_downs = [e for e in key_events if e["type"]=="key_down" and e["key_category"]=="CHAR"]
    char_ups   = [e for e in key_events if e["type"]=="key_up"   and e["key_category"]=="CHAR"]
    all_downs  = [e for e in key_events if e["type"]=="key_down"]

    typing_rate = len(char_downs) / window_duration

    # Match key_down → key_up pairs by order (simple approximation)
    hold_times = []
    for i, down in enumerate(char_downs):
        # find first key_up after this key_down
        matching_up = next((u for u in char_ups if u["timestamp"] > down["timestamp"]), None)
        if matching_up:
            hold_times.append(matching_up["timestamp"] - down["timestamp"])

    # Inter-key intervals (pauses between consecutive CHAR downs)
    char_ts = [e["timestamp"] for e in char_downs]
    pauses = np.diff(char_ts) if len(char_ts) > 1 else []

    return {
        "typing_rate": typing_rate,
        "key_count_total": len(all_downs),
        "key_count_char": len(char_downs),
        "hold_time_mean": np.mean(hold_times) if hold_times else np.nan,
        "hold_time_std":  np.std(hold_times)  if hold_times else np.nan,
        "pause_mean": np.mean(pauses) if len(pauses) > 0 else np.nan,
        "pause_std":  np.std(pauses)  if len(pauses) > 0 else np.nan,
    }
```

---

## 6. Module 3 — Session Aggregator

**File:** `features/session_aggregator.py`

After all windows are collected, produce one training row per session.

### Aggregation Formula
For each window-level feature `f`:
```
session_f_mean = mean(f across all windows)
session_f_std  = std(f across all windows)
session_f_min  = min(f across all windows)
session_f_max  = max(f across all windows)
```

With ~33 window-level features × 4 aggregations = **~132–134 session features**.

### Session Row Schema
```jsonc
{
  "session_id": "abc123",
  "participant_id": "Zafar",
  "task_type": "writing",           // typing | composing | writing | qa
  "task_name": "essay_climate",
  "session_start": 1741500000.0,
  "session_end":   1741503600.0,
  "window_count": 720,

  // 134 aggregated features
  "mouse_distance_mean": 12450.3,
  "mouse_distance_std":  3200.1,
  "mouse_distance_min":  800.0,
  "mouse_distance_max":  28000.0,
  // ... all other features ...

  // NASA-TLX labels
  "tlx_mental_demand":    65,
  "tlx_temporal_demand":  40,
  "tlx_performance":      70,
  "tlx_effort":           55,
  "tlx_frustration":      30,
  "tlx_mean":             52.0,

  // Mini-TLX samples (optional)
  "mini_tlx_samples": [
    {"timestamp": 1741500120.0, "mental": 6, "frustration": 3},
    {"timestamp": 1741500240.0, "mental": 8, "frustration": 6}
  ]
}
```

---

## 7. Module 4 — Deletion Estimator

**File:** `logger/deletion_estimator.py`

### State Maintained Across a Session
```python
state = {
    "rolling_word_lengths": deque(maxlen=20),  # for median word length
    "total_deleted": 0,
    "deleted_high": 0,
    "deleted_medium": 0,
    "deleted_low": 0,
    "del_weighted": 0.0,
}
```

### Detection Rules

| Trigger | Estimate | Confidence | Weight |
|---|---|---|---|
| Single `BACKSPACE` or `DELETE` | 1 character | high | 1.0 |
| `CTRL + BACKSPACE` | median word length (rolling) | medium | 0.6 |
| `CTRL + DELETE` | median word length (rolling) | medium | 0.6 |
| `SHIFT + ARROW` selection then `BACKSPACE/DELETE` | estimated selection length based on arrow key count | low | 0.3 |
| Mouse drag + `BACKSPACE/DELETE` | estimated by time of drag × avg char density | low | 0.3 |
| Double-click + `BACKSPACE/DELETE` | 1 word = median word length | medium | 0.6 |

### Window-Level Deletion Features

| Feature | Formula |
|---|---|
| `del_total` | total estimated deleted characters this window |
| `del_high` | deleted chars from high-confidence bursts |
| `del_medium` | deleted chars from medium-confidence bursts |
| `del_low` | deleted chars from low-confidence bursts |
| `del_weighted` | Σ w(c_b) × d_b over all bursts |
| `del_conf_score` | del_weighted / del_total (0 if del_total == 0) |
| `del_rate` | del_total / window_duration |

### Rolling Median Word Length
```python
from collections import deque
import numpy as np

class WordLengthTracker:
    def __init__(self, maxlen=20):
        self.lengths = deque(maxlen=maxlen)
        self._default = 5  # fallback if no data yet

    def observe_space_or_enter(self, chars_since_last_space):
        if chars_since_last_space > 0:
            self.lengths.append(chars_since_last_space)

    def median_word_length(self):
        return int(np.median(self.lengths)) if self.lengths else self._default
```

---

## 8. Module 5 — NASA-TLX Survey UI

**File:** `survey/nasa_tlx_ui.py`

### Full Post-Session Survey (tkinter)

Launch automatically when the session ends. Show 5 sliders (0–100) with labels:

```
+------------------------------------------+
|  NASA-TLX Workload Rating                |
|                                          |
|  Mental Demand     [====|====]  50       |
|  Temporal Demand   [====|====]  50       |
|  Own Performance   [====|====]  50       |
|  Effort            [====|====]  50       |
|  Frustration Level [====|====]  50       |
|                                          |
|  TLX Mean: 50.0                          |
|                                          |
|          [ Submit ]                      |
+------------------------------------------+
```

**Implementation:**
```python
import tkinter as tk
from tkinter import ttk

DIMENSIONS = [
    ("Mental Demand",    "How mentally demanding was the task?"),
    ("Temporal Demand",  "How hurried or rushed was the pace of the task?"),
    ("Own Performance",  "How successful were you in accomplishing what you were asked to do?"),
    ("Effort",           "How hard did you have to work mentally to accomplish your performance level?"),
    ("Frustration",      "How insecure, discouraged, irritated, stressed, annoyed were you?"),
]

class NasaTLXSurvey:
    def __init__(self, on_submit_callback):
        self.root = tk.Tk()
        self.root.title("NASA-TLX Workload Rating")
        self.sliders = {}
        self.on_submit = on_submit_callback
        self._build_ui()

    def _build_ui(self):
        for dim_name, tooltip in DIMENSIONS:
            frame = ttk.Frame(self.root)
            frame.pack(fill="x", padx=20, pady=5)
            ttk.Label(frame, text=dim_name, width=20).pack(side="left")
            var = tk.IntVar(value=50)
            slider = ttk.Scale(frame, from_=0, to=100, variable=var, orient="horizontal", length=300)
            slider.pack(side="left")
            ttk.Label(frame, textvariable=var, width=4).pack(side="left")
            self.sliders[dim_name] = var

        ttk.Button(self.root, text="Submit", command=self._submit).pack(pady=10)
        self.root.mainloop()

    def _submit(self):
        ratings = {k: v.get() for k, v in self.sliders.items()}
        ratings["tlx_mean"] = sum(ratings.values()) / len(ratings)
        self.on_submit(ratings)
        self.root.destroy()
```

---

## 9. Module 6 — ML Pipeline

**File:** `ml/pipeline.py`, `ml/train.py`, `ml/evaluate.py`

### Pipeline Architecture
```python
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import joblib

TARGETS = [
    "tlx_mental_demand",
    "tlx_temporal_demand",
    "tlx_performance",
    "tlx_effort",
    "tlx_frustration",
    "tlx_mean",
]

ALPHA_GRID = [0.01, 0.1, 1, 10, 100, 1000, 10000]

def build_pipeline():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("model",   Ridge()),
    ])

def train_loo(X, y, target_name):
    """Leave-one-out cross-validation with inner CV for alpha tuning."""
    loo = LeaveOneOut()
    y_true_all, y_pred_all = [], []

    for train_idx, test_idx in loo.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Inner CV for alpha (leave-one-out on training fold)
        inner_loo = LeaveOneOut()
        pipe = build_pipeline()
        search = GridSearchCV(
            pipe,
            param_grid={"model__alpha": ALPHA_GRID},
            cv=inner_loo,
            scoring="neg_mean_squared_error",
            refit=True,
        )
        search.fit(X_train, y_train)

        y_pred = search.predict(X_test)
        y_true_all.append(y_test[0])
        y_pred_all.append(y_pred[0])

    y_true_all = np.array(y_true_all)
    y_pred_all = np.array(y_pred_all)

    mae  = mean_absolute_error(y_true_all, y_pred_all)
    rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    r2   = r2_score(y_true_all, y_pred_all)

    print(f"\n{target_name}: MAE={mae:.3f}, RMSE={rmse:.3f}, R²={r2:.3f}")
    return {"target": target_name, "MAE": mae, "RMSE": rmse, "R2": r2}

def train_final_model(X, y, target_name, models_dir="models/"):
    """Train final model on all data and save."""
    pipe = build_pipeline()
    search = GridSearchCV(pipe, {"model__alpha": ALPHA_GRID}, cv=LeaveOneOut(), scoring="neg_mse")
    search.fit(X, y)
    path = f"{models_dir}/ridge_model_{target_name}.pkl"
    joblib.dump(search.best_estimator_, path)
    print(f"Saved: {path}")
    return search.best_estimator_
```

### Feature Importance (Ridge Coefficients)
```python
def extract_feature_importance(model, feature_names, target_name, models_dir):
    coefs = model.named_steps["model"].coef_
    df = pd.DataFrame({"feature": feature_names, "coefficient": coefs})
    df["abs_coef"] = df["coefficient"].abs()
    df = df.sort_values("abs_coef", ascending=False)
    path = f"{models_dir}/feature_importance_{target_name}.csv"
    df.to_csv(path, index=False)
    return df
```

---

## 10. Module 7 — Interactive Dashboard

**File:** `dashboard/app.py`

Run with: `streamlit run dashboard/app.py`

### Pages / Tabs

#### Tab 1: Live Session Monitor
- Real-time gauge showing estimated cognitive load (from rolling window model)
- Live line chart: typing rate, mouse speed, idle ratio over last 60 seconds
- Status: current window number, session duration, events captured

```python
# Pseudo-code for real-time update
import streamlit as st
import time

def render_live_monitor(shared_state):
    placeholder = st.empty()
    while shared_state["session_active"]:
        with placeholder.container():
            latest = shared_state["latest_window"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Typing Rate", f"{latest['typing_rate']:.2f} k/s")
            col2.metric("Mouse Speed", f"{latest['mouse_speed_mean_sample']:.1f} px/s")
            col3.metric("Idle Ratio", f"{latest['mouse_idle_ratio']:.2%}")
        time.sleep(1)
```

#### Tab 2: Session History
- Table of all sessions with TLX scores color-coded (green=low, red=high)
- Select any session to see:
  - Feature time-series (per window) as line charts
  - Mouse trajectory heatmap (plotly density_mapbox or 2D histogram)
  - Radar chart of NASA-TLX dimensions

```python
import plotly.express as px
import plotly.graph_objects as go

def radar_chart(tlx_scores):
    dims = ["Mental Demand", "Temporal Demand", "Performance", "Effort", "Frustration"]
    fig = go.Figure(data=go.Scatterpolar(
        r=[tlx_scores[d] for d in dims],
        theta=dims,
        fill="toself"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    return fig

def mouse_heatmap(move_events):
    xs = [e["x"] for e in move_events]
    ys = [e["y"] for e in move_events]
    fig = px.density_heatmap(x=xs, y=ys, nbinsx=80, nbinsy=60,
                              title="Mouse Position Heatmap")
    return fig
```

#### Tab 3: Model Analysis
- Feature importance bar chart (top 20 features by Ridge coefficient)
- PCA scatter plot of sessions colored by TLX Mean
- Actual vs. Predicted scatter plot per target
- Results table (MAE, RMSE, R²) per target

```python
def pca_plot(X, y, feature_names):
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    X_scaled = StandardScaler().fit_transform(
        SimpleImputer(strategy="median").fit_transform(X)
    )
    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)

    df = pd.DataFrame({
        "PC1": components[:, 0],
        "PC2": components[:, 1],
        "TLX Mean": y,
    })
    fig = px.scatter(df, x="PC1", y="PC2", color="TLX Mean",
                     color_continuous_scale="RdYlGn_r",
                     title="Session PCA (colored by TLX Mean)")
    return fig
```

#### Tab 4: Participant Comparison
- Side-by-side box plots of feature distributions per participant
- TLX score distributions per participant
- Identifies if participant style is dominating the signal

---

## 11. Module 8 — Adaptive Mini-TLX System

**File:** `survey/mini_tlx_ui.py`

### Purpose
Collect short 2-question ratings every 2 minutes during a session. This converts 1 label/session → ~30 labels/hour, massively increasing training data without recruiting more participants.

### Implementation
```python
import threading
import tkinter as tk
from tkinter import ttk

class MiniTLXTimer:
    def __init__(self, interval_seconds=120, on_rating_callback=None):
        self.interval = interval_seconds
        self.callback = on_rating_callback
        self.running = False
        self.timer = None

    def start(self):
        self.running = True
        self._schedule_next()

    def stop(self):
        self.running = False
        if self.timer:
            self.timer.cancel()

    def _schedule_next(self):
        if self.running:
            self.timer = threading.Timer(self.interval, self._show_popup)
            self.timer.daemon = True
            self.timer.start()

    def _show_popup(self):
        self._show_mini_tlx_popup()
        self._schedule_next()

    def _show_mini_tlx_popup(self):
        root = tk.Tk()
        root.title("Quick Check-In")
        root.attributes("-topmost", True)  # always on top
        root.geometry("350x180")

        ttk.Label(root, text="Quick workload check (2 questions):",
                  font=("Arial", 11, "bold")).pack(pady=8)

        mental_var = tk.IntVar(value=5)
        frustration_var = tk.IntVar(value=5)

        frame1 = ttk.Frame(root); frame1.pack(fill="x", padx=15, pady=3)
        ttk.Label(frame1, text="Mental load (1-10):", width=20).pack(side="left")
        ttk.Scale(frame1, from_=1, to=10, variable=mental_var, orient="horizontal").pack(side="left")
        ttk.Label(frame1, textvariable=mental_var, width=3).pack(side="left")

        frame2 = ttk.Frame(root); frame2.pack(fill="x", padx=15, pady=3)
        ttk.Label(frame2, text="Frustration (1-10):", width=20).pack(side="left")
        ttk.Scale(frame2, from_=1, to=10, variable=frustration_var, orient="horizontal").pack(side="left")
        ttk.Label(frame2, textvariable=frustration_var, width=3).pack(side="left")

        def submit():
            import time
            rating = {
                "timestamp": time.time(),
                "mental": mental_var.get(),
                "frustration": frustration_var.get(),
            }
            if self.callback:
                self.callback(rating)
            root.destroy()

        ttk.Button(root, text="Submit", command=submit).pack(pady=8)
        root.mainloop()
```

---

## 12. Module 9 — Gamified Task Protocol

**File:** `tasks/task_protocol.py`

### Purpose
Provide structured tasks with known workload levels to generate labeled ground-truth data for calibration.

### Task Types

#### Level 1 — Low Workload (Baseline)
- Simple copy-paste: user sees text on screen, copies it to a text box
- Duration: 3 minutes
- Expected TLX: 10–25

#### Level 2 — Medium Workload
- Typing test: user types a provided paragraph as accurately as possible
- Duration: 3 minutes
- Expected TLX: 30–55

#### Level 3 — High Workload (Dual Task)
- Essay writing while mental arithmetic: write a short paragraph AND count backwards from 300 by 7s in their head
- Duration: 3 minutes
- Expected TLX: 60–90

#### Level 4 — Very High Workload
- Speed typing test under time pressure with correction requirement (must fix every typo immediately)
- Duration: 2 minutes
- Expected TLX: 75–95

### Task Runner UI
```python
class TaskProtocol:
    TASKS = [
        {"name": "Copy-Paste Baseline", "level": 1, "duration": 180,
         "instruction": "Copy the text shown below into the box. Take your time."},
        {"name": "Typing Speed Test",   "level": 2, "duration": 180,
         "instruction": "Type the paragraph below as fast as you can."},
        {"name": "Dual Task: Write + Mental Math", "level": 3, "duration": 180,
         "instruction": "Write about your day while mentally counting backwards from 300 by 7."},
        {"name": "Speed Typing Under Pressure",    "level": 4, "duration": 120,
         "instruction": "Type as fast as possible. Fix every typo before continuing!"},
    ]

    def run_session(self, task_index, logger, mini_tlx_timer):
        task = self.TASKS[task_index]
        # Show countdown + instructions
        # Start logger + mini_tlx_timer
        # Wait task["duration"] seconds
        # Stop logger + mini_tlx_timer
        # Launch full NASA-TLX survey
        # Save session with task metadata
        pass
```

---

## 13. Module 10 — System Tray & Power Events

**Files:** `logger/power_manager.py`, `logger/tray_app.py`

### Additional dependencies
```
# requirements.txt — add:
pywin32>=306        # Windows power/sleep/wake events
pystray>=0.19.5     # system tray icon
Pillow>=10.0.0      # icon image (required by pystray)
```

### Problem
When the laptop lid is closed, Windows suspends all processes (sleep/hibernate).
`pynput` listeners may silently die or drop events after resume. Without handling this:
- Data is lost on sleep
- Listeners are broken on wake
- User must manually restart the program every time they open the laptop

### Solution Architecture

```
Windows startup  →  main.py --tray  →  TrayApp (system tray icon)
                                              │
                          ┌───────────────────┼───────────────────┐
                          ↓                   ↓                   ↓
                   PowerManager         SessionManager       MiniTLXTimer
                 (sleep/wake events)   (start/stop/save)    (2-min prompts)
```

### Power Event Manager (`logger/power_manager.py`)

```python
import win32api
import win32con
import win32gui
import threading

class PowerManager:
    """Listens for Windows sleep and wake power events."""

    def __init__(self, on_sleep_callback, on_wake_callback):
        self.on_sleep = on_sleep_callback
        self.on_wake  = on_wake_callback
        self._thread  = None

    def start(self):
        self._thread = threading.Thread(target=self._message_loop, daemon=True)
        self._thread.start()

    def _message_loop(self):
        # Register a hidden window to receive WM_POWERBROADCAST messages
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = "WorkloadLoggerPowerWatcher"
        wc.lpfnWndProc   = self._wnd_proc
        win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(
            wc.lpszClassName, "", 0, 0, 0, 0, 0, 0, 0, None, None
        )
        win32gui.PumpMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_POWERBROADCAST:
            if wparam == win32con.PBT_APMSUSPEND:
                # System is going to sleep
                self.on_sleep()
            elif wparam == win32con.PBT_APMRESUMEAUTOMATIC:
                # System woke up (even without user input)
                self.on_wake()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
```

### System Tray App (`logger/tray_app.py`)

```python
import pystray
from PIL import Image, ImageDraw
import threading

class TrayApp:
    def __init__(self, session_manager, dashboard_launcher):
        self.session  = session_manager
        self.launcher = dashboard_launcher
        self.icon     = None

    def build_icon_image(self, active: bool) -> Image.Image:
        """Draw a simple colored circle as tray icon."""
        img = Image.new("RGB", (64, 64), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        color = (0, 200, 80) if active else (180, 180, 180)
        draw.ellipse([8, 8, 56, 56], fill=color)
        return img

    def start(self):
        self.icon = pystray.Icon(
            name="WorkloadLogger",
            icon=self.build_icon_image(active=True),
            title="Workload Logger — Active",
            menu=pystray.Menu(
                pystray.MenuItem("Open Dashboard",     self._open_dashboard),
                pystray.MenuItem("End Session Now",    self._end_session),
                pystray.MenuItem("Pause Logging",      self._pause),
                pystray.MenuItem("Exit",               self._quit),
            )
        )
        # Run tray in its own thread; does not block main
        t = threading.Thread(target=self.icon.run, daemon=True)
        t.start()

    def notify(self, message: str):
        if self.icon:
            self.icon.notify(message, "Workload Logger")

    def set_active(self, active: bool):
        if self.icon:
            self.icon.icon  = self.build_icon_image(active)
            self.icon.title = f"Workload Logger — {'Active' if active else 'Paused'}"

    def _open_dashboard(self): self.launcher.open()
    def _end_session(self):    self.session.end(show_survey=True)
    def _pause(self):          self.session.toggle_pause()
    def _quit(self):           self.session.end(show_survey=False); self.icon.stop()
```

### Session Lifecycle with Sleep/Wake

```python
class SessionManager:
    def __init__(self, logger, tray, power_manager, config):
        self.logger        = logger
        self.tray          = tray
        self.config        = config
        self.session_start = None
        self.paused        = False

        # Wire power events
        power_manager.on_sleep_callback = self.on_sleep
        power_manager.on_wake_callback  = self.on_wake

    def start_new_session(self, participant_id, task_type="free"):
        self.session_start = time.time()
        self.logger.start(participant_id=participant_id, task_type=task_type)
        self.tray.set_active(True)
        self.tray.notify("New session started")

    def on_sleep(self):
        """Called automatically when lid closes / sleep begins."""
        duration_min = (time.time() - self.session_start) / 60
        self.logger.flush_current_window()   # save partial window
        if duration_min >= self.config["survey"]["min_session_minutes"]:
            show_nasa_tlx_survey(callback=self._save_and_end)
        else:
            self._save_and_end(tlx_ratings=None)  # save without survey

    def on_wake(self):
        """Called automatically when lid opens / system resumes."""
        self.logger.restart_listeners()      # recreate pynput listeners
        self.start_new_session(
            participant_id=self.current_participant,
            task_type="free"
        )
        self.tray.notify("Session resumed after wake")

    def _save_and_end(self, tlx_ratings):
        self.logger.stop()
        session_row = self.logger.build_session_row(tlx_ratings)
        append_jsonl("data/session_dataset.jsonl", session_row)
        self.tray.set_active(False)
```

### Windows Auto-Start Setup

Add this call once during first-run setup to register the program in Windows Task Scheduler:

```python
import subprocess

def register_autostart(script_path: str):
    """Register program to start automatically on Windows login."""
    cmd = [
        "schtasks", "/create",
        "/tn",       "WorkloadLogger",
        "/tr",       f'pythonw.exe "{script_path}" --tray',
        "/sc",       "ONLOGON",
        "/rl",       "LIMITED",    # no admin rights needed
        "/f",                      # overwrite if exists
    ]
    subprocess.run(cmd, check=True)
    print("Auto-start registered in Task Scheduler.")

def remove_autostart():
    subprocess.run(["schtasks", "/delete", "/tn", "WorkloadLogger", "/f"])
```

Run `register_autostart` once on first launch:
```python
# main.py
if "--setup" in sys.argv:
    register_autostart(os.path.abspath(__file__))
```

```bash
# One-time setup command:
python main.py --setup
```

### Typical User Day — With This Implementation

```
08:00  Boot laptop
       → Task Scheduler triggers: python main.py --tray
       → New session starts automatically
       → Green dot appears in system tray ✅

10:30  Close lid (go to class)
       → WM_POWERBROADCAST PBT_APMSUSPEND received
       → Session saved to disk
       → If session > 20 min: TLX survey shown briefly ✅

14:00  Open lid (back home)
       → WM_POWERBROADCAST PBT_APMRESUMEAUTOMATIC received
       → pynput listeners restarted
       → New session begins automatically
       → Tray notification: "Session resumed after wake" ✅

18:30  Close lid again
       → Same as 10:30 ✅

Result: 2–3 sessions captured per day, zero manual effort from user.
```

### config.yaml additions
```yaml
session:
  autostart_on_wake: true
  min_session_minutes: 20          # minimum duration to show TLX survey
  show_tray_notifications: true
  tray_icon_path: "assets/icon.png"
```

---

## 14. Data Schemas

### input_events.jsonl
One JSON object per line. Types: `key_down`, `key_up`, `mouse_move`, `mouse_click`, `scroll`, `window_aggregate`.

### session_dataset.jsonl
One JSON object per line. Each session row includes:
- Metadata: `session_id`, `participant_id`, `task_type`, `task_name`, `session_start`, `session_end`, `window_count`
- 134 aggregated features (mean/std/min/max of each window feature)
- 6 TLX labels: `tlx_mental_demand`, `tlx_temporal_demand`, `tlx_performance`, `tlx_effort`, `tlx_frustration`, `tlx_mean`
- Optional: `mini_tlx_samples` array

### mini_tlx_labels.jsonl
```jsonc
{
  "session_id": "abc123",
  "timestamp": 1741500120.0,
  "elapsed_seconds": 120,
  "mental": 7,
  "frustration": 4
}
```

---

## 14. Privacy & Security

### Data Collection Policies
- **No raw text stored.** All keys are mapped to categories before any logging.
- **No screenshots.** No screen capture of any kind.
- **Local only.** No network calls. No cloud sync.
- **Participant consent.** Show consent dialog before session start.

### Consent Dialog
Display this text before any logging begins:
```
This application records timing patterns of your keyboard and mouse
movements to study cognitive workload.

What IS recorded:
  - Key press/release timing (not which key)
  - Mouse cursor position and movement
  - Click timing and scroll activity

What is NOT recorded:
  - Typed text or characters
  - Screenshots
  - Audio

All data is stored locally on this machine only.
Data retention: [X days / until you delete it]

[ I Consent — Start Session ]    [ Cancel ]
```

### Optional Encryption
```python
from cryptography.fernet import Fernet

def encrypt_file(filepath, key):
    f = Fernet(key)
    with open(filepath, "rb") as file:
        data = file.read()
    encrypted = f.encrypt(data)
    with open(filepath + ".enc", "wb") as file:
        file.write(encrypted)
```

---

## 15. Testing Plan

### Unit Tests

| Test | File | What to Test |
|---|---|---|
| Privacy filter | `tests/test_privacy_filter.py` | Every key type maps to correct category; no actual characters leak |
| Mouse features | `tests/test_mouse_features.py` | Known positions → expected distance/speed |
| Trajectory segmentation | `tests/test_trajectory.py` | Gaps > 0.15s create new trajectory; short trajectories discarded |
| Keyboard features | `tests/test_keyboard_features.py` | Known timestamps → correct typing rate, hold times, pauses |
| Deletion estimator | `tests/test_deletion.py` | Backspace=1 high, Ctrl+Backspace=median word low/medium |
| Session aggregator | `tests/test_session_aggregator.py` | 3 windows with known features → correct mean/std/min/max |
| ML pipeline | `tests/test_ml_pipeline.py` | Pipeline fits/predicts without error; LOO runs on small dataset |

### Integration Tests
- Start logger → type for 15s → stop → verify `input_events.jsonl` has correct structure
- Full session → TLX survey → `session_dataset.jsonl` has all expected columns
- Train model on synthetic data → verify output files exist

### Manual QA Checklist
- [ ] No actual characters appear in `input_events.jsonl`
- [ ] Window aggregates appear every 5 seconds in the log
- [ ] TLX sliders save values correctly
- [ ] Mini-TLX popups appear at correct intervals
- [ ] Dashboard loads without errors
- [ ] Mouse heatmap renders correctly
- [ ] PCA plot shows sessions as dots
- [ ] Feature importance CSV sorts by abs coefficient

---

## 16. Improvement Roadmap

### Phase 1 — Foundation (Weeks 1–2)
- [x] Event logger with privacy filter
- [x] Window aggregator (mouse + keyboard + trajectory + deletion)
- [x] Session aggregator → JSONL output
- [x] Post-session NASA-TLX survey UI
- [x] Ridge regression baseline + LOO evaluation

### Phase 2 — Data Collection Scale-Up (Weeks 3–4)
- [ ] Mini-TLX adaptive timer (every 2 minutes)
- [ ] Gamified task protocol (4 levels)
- [ ] Participant ID management
- [ ] Target: collect 50+ sessions across 5+ participants

### Phase 3 — Interactive Dashboard (Weeks 5–6)
- [ ] Streamlit app with 4 tabs
- [ ] Real-time live monitor
- [ ] Mouse heatmap visualization
- [ ] Radar chart per session
- [ ] PCA + feature importance plots

### Phase 4 — Modeling Improvements (Weeks 7–8)
- [ ] Per-task-type model variants
- [ ] PCA-based feature reduction (from 134 → 20–30 features)
- [ ] Add task_type as categorical input (one-hot)
- [ ] Try gradient boosting (XGBoost) as alternative to Ridge
- [ ] Within-session mini-TLX as window-level labels (not just session-level)

### Phase 5 — Production Hardening (Week 9+)
- [ ] Encryption at rest option
- [ ] Export/import data for multi-machine studies
- [ ] Participant-specific calibration mode
- [ ] Per-user personalized model fine-tuning

---

## Quick Start

```bash
# 1. Clone / create project directory
mkdir workload_logger && cd workload_logger

# 2. Set up environment
python -m venv venv
venv\Scripts\activate           # Windows
pip install -r requirements.txt

# 3. Start a session
python main.py --participant "YourName" --task-type "writing" --task-name "my_task"
# (Captures input for as long as you work, then shows TLX survey)

# 4. Train the model (after collecting sessions)
python ml/train.py --data data/session_dataset.jsonl

# 5. Launch dashboard
streamlit run dashboard/app.py
```

---

*End of Technical Specification*
*Document version: 1.0 | 2026-03-09*
