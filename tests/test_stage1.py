"""Stage 1 tests — CLI skeleton + message protocol.

These tests specify behaviour from the OUTSIDE (what the CLI prints, what the
dataclass enforces).  They do NOT import any implementation yet — they will
fail until you build src/agent/__main__.py and src/agent/protocol.py.
"""

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))


# ---------------------------------------------------------------------------
# 1. Message dataclass
# ---------------------------------------------------------------------------

class TestMessageProtocol:
    """The Message type must enforce role + content and be dict-exportable."""

    def _import(self):
        return importlib.import_module("agent.protocol")

    def test_message_has_role_and_content(self):
        m = self._import()
        msg = m.Message(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"

    def test_message_invalid_role_raises(self):
        """Only 'user', 'assistant', 'tool' are valid roles."""
        m = self._import()
        with pytest.raises((ValueError, TypeError)):
            m.Message(role="robot", content="hi")

    def test_message_to_dict(self):
        """to_dict() must return {'role': ..., 'content': ...}."""
        m = self._import()
        msg = m.Message(role="assistant", content="pong")
        d = msg.to_dict()
        assert d == {"role": "assistant", "content": "pong"}


# ---------------------------------------------------------------------------
# 2. CLI entry point
# ---------------------------------------------------------------------------

class TestCLI:
    """python -m agent must be runnable and produce sensible output."""

    def _run(self, *args, input_text=None):
        return subprocess.run(
            [sys.executable, "-m", "agent", *args],
            capture_output=True,
            text=True,
            input=input_text,
            cwd=SRC,
        )

    def test_help_exits_zero(self):
        result = self._run("--help")
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower()

    def test_single_prompt_prints_reply(self):
        """'python -m agent "hello"' must print something to stdout and exit 0."""
        result = self._run("hello")
        assert result.returncode == 0
        assert result.stdout.strip() != ""

    def test_reply_is_non_empty(self):
        """Agent must print something to stdout and exit 0."""
        result = self._run("ping")
        assert result.returncode == 0
        assert result.stdout.strip() != ""
