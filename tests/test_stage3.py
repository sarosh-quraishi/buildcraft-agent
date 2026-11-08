"""Stage 3 tests — read_file tool.

Tests the path validation and file reading logic in isolation.
No LLM calls needed.
"""

import sys
import tempfile
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))

from agent.tools import read_file


class TestReadFile:
    def test_reads_file_contents(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("hello world")
        assert read_file("hello.txt", tmp_path) == "hello world"

    def test_rejects_path_traversal(self, tmp_path):
        with pytest.raises(ValueError):
            read_file("../../etc/passwd", tmp_path)

    def test_rejects_absolute_path_outside_cwd(self, tmp_path):
        with pytest.raises((ValueError, Exception)):
            read_file("/etc/passwd", tmp_path)

    def test_reads_file_in_subdirectory(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "data.txt").write_text("nested")
        assert read_file("sub/data.txt", tmp_path) == "nested"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises((FileNotFoundError, OSError)):
            read_file("nonexistent.txt", tmp_path)
