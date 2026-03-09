# Workload Logger

A privacy-preserving system that measures cognitive workload from keyboard
and mouse dynamics — without recording any typed content.

**Based on:** Hamidov, Z. (2026). *A Privacy-Preserving Workload Logger
Using Keyboard and Mouse Dynamics: System Design, Feature Engineering,
and a Pilot Study.*

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. First-time setup (registers auto-start)
python main.py --setup

# 4. Start a session manually
python main.py --participant "YourName" --task-type "writing"

# 5. Train model (after collecting sessions)
python ml/train.py

# 6. Launch dashboard
streamlit run dashboard/app.py
```

---

## Project Structure

```
workload_logger/
├── main.py                    # Entry point
├── config.yaml                # All tunable parameters
├── requirements.txt
│
├── logger/                    # Data collection
│   ├── event_logger.py        # pynput keyboard + mouse listeners
│   ├── privacy_filter.py      # Key → category mapping (no raw text)
│   ├── deletion_estimator.py  # Confidence-weighted deletion counts
│   ├── window_aggregator.py   # 5-second feature windows
│   ├── power_manager.py       # Sleep/wake events (pywin32)
│   └── tray_app.py            # System tray icon (pystray)
│
├── features/                  # Feature engineering
│   ├── mouse_features.py      # Distance, speed, idle, clicks
│   ├── trajectory_features.py # Efficiency, curvature, SAT
│   ├── keyboard_features.py   # Typing rate, hold times, pauses
│   └── session_aggregator.py  # mean/std/min/max → session row
│
├── survey/                    # NASA-TLX UI
│   ├── nasa_tlx_ui.py         # Full post-session survey (tkinter)
│   └── mini_tlx_ui.py         # 2-min micro-survey popup
│
├── ml/                        # Machine learning
│   ├── pipeline.py            # Impute → Scale → Ridge
│   ├── train.py               # LOO CV + hyperparameter tuning
│   └── evaluate.py            # MAE, RMSE, R² reporting
│
├── dashboard/                 # Streamlit interactive dashboard
│   ├── app.py                 # Main entry point (4 tabs)
│   ├── realtime_panel.py      # Live workload monitor
│   ├── session_analysis.py    # Per-session charts + heatmaps
│   └── model_analysis.py      # Feature importance, PCA
│
├── tasks/                     # Structured task protocol
│   └── task_protocol.py       # 4-level gamified tasks
│
├── tests/                     # Unit + integration tests
│   ├── test_privacy_filter.py
│   ├── test_mouse_features.py
│   ├── test_trajectory.py
│   ├── test_keyboard_features.py
│   ├── test_deletion_estimator.py
│   ├── test_session_aggregator.py
│   └── test_ml_pipeline.py
│
├── data/                      # Auto-generated (gitignored)
│   ├── input_events.jsonl
│   ├── session_dataset.jsonl
│   └── mini_tlx_labels.jsonl
│
├── models/                    # Auto-generated (gitignored)
│   ├── ridge_model_*.pkl
│   └── feature_importance_*.csv
│
└── assets/
    └── icon.png               # System tray icon
```

---

## Privacy

- No keystrokes stored — only key *categories* (CHAR, BACKSPACE, etc.)
- No screenshots, no audio
- All data stored locally — no network connections
- Consent dialog shown before every session

## Tech Stack

| Layer | Library |
|---|---|
| Event capture | `pynput` |
| Power events | `pywin32` |
| System tray | `pystray` + `Pillow` |
| Data storage | `jsonlines` |
| ML pipeline | `scikit-learn` |
| Dashboard | `streamlit` + `plotly` |
| Survey UI | `tkinter` (built-in) |
