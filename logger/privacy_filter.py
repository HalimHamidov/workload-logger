"""
privacy_filter.py — Maps raw pynput key objects to privacy-safe string categories.

No actual key values are ever stored or logged.
Every key pressed by the user is reduced to one of the categories below
before any further processing.

Categories
----------
CHAR        Alphanumeric characters and punctuation (a-z, A-Z, 0-9, .,!? etc.)
BACKSPACE   Backspace key
DELETE      Delete key
SPACE       Space bar
ENTER       Enter / Return
TAB         Tab key
CTRL        Left or right Control
SHIFT       Left or right Shift
ALT         Left or right Alt
ARROW       Arrow keys (Left, Right, Up, Down)
FUNCTION    Function keys F1–F12
OTHER       Any key not matched above
"""

from pynput import keyboard
from typing import Optional


# Ordered from most specific to most general
_SPECIAL_KEY_MAP: dict[keyboard.Key, str] = {
    keyboard.Key.backspace: "BACKSPACE",
    keyboard.Key.delete:    "DELETE",
    keyboard.Key.space:     "SPACE",
    keyboard.Key.enter:     "ENTER",
    keyboard.Key.tab:       "TAB",
    keyboard.Key.ctrl_l:    "CTRL",
    keyboard.Key.ctrl_r:    "CTRL",
    keyboard.Key.shift:     "SHIFT",
    keyboard.Key.shift_r:   "SHIFT",
    keyboard.Key.alt_l:     "ALT",
    keyboard.Key.alt_r:     "ALT",
    keyboard.Key.alt_gr:    "ALT",
    keyboard.Key.left:      "ARROW",
    keyboard.Key.right:     "ARROW",
    keyboard.Key.up:        "ARROW",
    keyboard.Key.down:      "ARROW",
}

_FUNCTION_KEYS = {
    keyboard.Key.f1,  keyboard.Key.f2,  keyboard.Key.f3,  keyboard.Key.f4,
    keyboard.Key.f5,  keyboard.Key.f6,  keyboard.Key.f7,  keyboard.Key.f8,
    keyboard.Key.f9,  keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12,
}


def categorize(key) -> str:
    """Return the privacy-safe category string for a pynput key object.

    Parameters
    ----------
    key : pynput.keyboard.Key or pynput.keyboard.KeyCode

    Returns
    -------
    str
        One of: CHAR, BACKSPACE, DELETE, SPACE, ENTER, TAB,
                CTRL, SHIFT, ALT, ARROW, FUNCTION, OTHER
    """
    # Special keys with direct mapping
    if key in _SPECIAL_KEY_MAP:
        return _SPECIAL_KEY_MAP[key]

    # Function keys
    if key in _FUNCTION_KEYS:
        return "FUNCTION"

    # KeyCode objects (regular character keys) — log as CHAR, never the value
    if hasattr(key, "char") and key.char is not None:
        return "CHAR"

    return "OTHER"


def is_deletion_key(key) -> bool:
    """Return True if the key is a deletion action (Backspace or Delete)."""
    return categorize(key) in ("BACKSPACE", "DELETE")


def is_char_key(key) -> bool:
    """Return True if the key is a printable character key."""
    return categorize(key) == "CHAR"
