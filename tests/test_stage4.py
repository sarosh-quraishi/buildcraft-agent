"""Stage 4 tests — permission gate.

Tests gate_check and ask_user in isolation. No LLM calls.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))

from agent.__main__ import Decision, gate_check, ask_user


class TestGateCheck:
    def test_listed_allow_tool_returns_allow(self):
        assert gate_check("read") is Decision.ALLOW

    def test_unknown_tool_defaults_to_allow(self):
        assert gate_check("unknown_tool") is Decision.ALLOW

    def test_returns_decision_enum(self):
        result = gate_check("read")
        assert isinstance(result, Decision)


class TestAskUser:
    def test_y_returns_true(self):
        with patch("builtins.input", return_value="y"):
            assert ask_user("bash", "ls") is True

    def test_n_returns_false(self):
        with patch("builtins.input", return_value="n"):
            assert ask_user("bash", "ls") is False

    def test_other_input_returns_false(self):
        with patch("builtins.input", return_value="yes"):
            assert ask_user("bash", "ls") is False

    def test_prompt_contains_tool_name_and_args(self):
        with patch("builtins.input", return_value="n") as mock_input:
            ask_user("bash", "rm -rf /")
            prompt = mock_input.call_args[0][0]
            assert "bash" in prompt
            assert "rm -rf /" in prompt
