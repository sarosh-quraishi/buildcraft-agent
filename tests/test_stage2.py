"""Stage 2 tests — bare-bones agent loop with real LLM.

These tests run against the real OpenRouter API. They require OPENROUTER_API_KEY
in the environment or .env file.
"""

import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent / "src"
ENV = Path(__file__).parent.parent / ".env"


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "agent", *args],
        capture_output=True,
        text=True,
        cwd=SRC,
        env={
            **__import__("os").environ,
            "PYDANTIC_AI_NO_BANNER": "1",
            **_load_dotenv(),
        },
    )


def _load_dotenv() -> dict:
    result = {}
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                result[k.strip()] = v.strip()
    return result


class TestAgentLoop:
    def test_exits_zero(self):
        result = _run("say only the word: pong")
        assert result.returncode == 0, result.stderr

    def test_prints_to_stdout(self):
        result = _run("say only the word: pong")
        assert result.stdout.strip() != ""

    def test_response_is_not_stub(self):
        """Real LLM replies must not contain the stage-1 stub prefix."""
        result = _run("say only the word: pong")
        assert "[stub]" not in result.stdout

    def test_no_crash_on_longer_prompt(self):
        result = _run("what is 2 + 2? reply with just the number")
        assert result.returncode == 0
        assert "4" in result.stdout
