"""
logger — Data collection package.

Modules:
    event_logger        Raw keyboard and mouse event capture (pynput).
    privacy_filter      Maps raw keys to privacy-safe categories.
    deletion_estimator  Estimates deleted character counts with confidence weighting.
    window_aggregator   Aggregates raw events into 5-second feature windows.
    power_manager       Detects Windows sleep/wake events (pywin32).
    tray_app            System tray icon and background mode (pystray).
"""
