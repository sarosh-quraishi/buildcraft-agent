"""Buildcraft adapter — wraps agent.__main__.run as a Target."""
from __future__ import annotations

from pathlib import Path

from agent.__main__ import run as _agent_run
from harness.target import RunResult, Target


class BuildcraftTarget:
    """Adapts buildcraft's run() to the Target protocol."""

    def __init__(self, workdir: Path):
        self.workdir = workdir
        self._planted: list[Path] = []

    async def run(self, prompt: str, history: list) -> RunResult:
        result = await _agent_run(prompt, history)
        return RunResult(
            output=result.output,
            bash_calls=result.bash_calls,
            history=result.history,
        )

    def plant_file(self, name: str, content: str) -> None:
        path = self.workdir / name
        path.write_text(content)
        self._planted.append(path)

    def cleanup(self) -> None:
        for path in self._planted:
            path.unlink(missing_ok=True)
        self._planted.clear()
