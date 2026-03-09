"""Tests for logger/privacy_filter.py — key categorization."""
import pytest
from unittest.mock import MagicMock
from pynput import keyboard
from logger.privacy_filter import categorize, is_deletion_key, is_char_key


class TestCategorize:
    def test_backspace_is_backspace(self):
        assert categorize(keyboard.Key.backspace) == "BACKSPACE"

    def test_delete_is_delete(self):
        assert categorize(keyboard.Key.delete) == "DELETE"

    def test_space_is_space(self):
        assert categorize(keyboard.Key.space) == "SPACE"

    def test_enter_is_enter(self):
        assert categorize(keyboard.Key.enter) == "ENTER"

    def test_ctrl_left_is_ctrl(self):
        assert categorize(keyboard.Key.ctrl_l) == "CTRL"

    def test_ctrl_right_is_ctrl(self):
        assert categorize(keyboard.Key.ctrl_r) == "CTRL"

    def test_shift_is_shift(self):
        assert categorize(keyboard.Key.shift) == "SHIFT"

    def test_arrow_is_arrow(self):
        assert categorize(keyboard.Key.left) == "ARROW"
        assert categorize(keyboard.Key.right) == "ARROW"

    def test_function_key(self):
        assert categorize(keyboard.Key.f1) == "FUNCTION"
        assert categorize(keyboard.Key.f12) == "FUNCTION"

    def test_char_key_returns_char_not_value(self):
        key = MagicMock()
        key.char = "a"
        assert categorize(key) == "CHAR"

    def test_char_key_does_not_leak_value(self):
        key = MagicMock()
        key.char = "s"   # 's' for secret
        result = categorize(key)
        assert result == "CHAR"
        assert "s" not in result   # value must not appear in result


class TestHelpers:
    def test_is_deletion_key_backspace(self):
        assert is_deletion_key(keyboard.Key.backspace) is True

    def test_is_deletion_key_delete(self):
        assert is_deletion_key(keyboard.Key.delete) is True

    def test_is_deletion_key_char(self):
        key = MagicMock()
        key.char = "x"
        assert is_deletion_key(key) is False

    def test_is_char_key(self):
        key = MagicMock()
        key.char = "z"
        assert is_char_key(key) is True

    def test_is_char_key_enter(self):
        assert is_char_key(keyboard.Key.enter) is False
