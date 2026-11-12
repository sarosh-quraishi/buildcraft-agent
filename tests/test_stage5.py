import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from agent.tools import run_bash


def test_run_bash_basic(tmp_path):
    result = run_bash("echo hello", tmp_path)
    assert "hello" in result


def test_run_bash_exit_code_in_output(tmp_path):
    result = run_bash("exit 0", tmp_path)
    assert "0" in result


def test_run_bash_nonzero_exit(tmp_path):
    result = run_bash("exit 1", tmp_path)
    assert "1" in result


def test_run_bash_stderr_captured(tmp_path):
    result = run_bash("echo err >&2", tmp_path)
    assert "err" in result


def test_run_bash_timeout_returns_message(tmp_path):
    result = run_bash("sleep 10", tmp_path, timeout=0.1)
    assert "timeout" in result.lower()


def test_run_bash_cwd(tmp_path):
    (tmp_path / "canary.txt").write_text("found")
    result = run_bash("cat canary.txt", tmp_path)
    assert "found" in result
