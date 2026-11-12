import subprocess
from pathlib import Path

from pydantic_ai import ModelRetry

BASH_TIMEOUT_S = 30  # default timeout in seconds


def run_bash(command: str, cwd: Path, timeout: float = BASH_TIMEOUT_S) -> str:
    """Run a shell command in cwd with a timeout. Returns stdout+stderr combined.

    TODO: use subprocess.run with shell=True, cwd=cwd, timeout=timeout
    TODO: capture stdout and stderr (both as text)
    TODO: on TimeoutExpired, kill the process and return a timeout message
    TODO: return a string with exit code + output, e.g. "Exit code: 0.\n\nstdout:\n..."

    """
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
        command,           # string (with shell=True) or list of args
        shell=True,        # lets you pass a string with pipes, &&, etc.
        cwd=cwd,           # working directory
        capture_output=True,  # captures stdout and stderr (shorthand for stdout=PIPE, stderr=PIPE)
        text=True,         # returns strings instead of bytes
        timeout=timeout,   # raises subprocess.TimeoutExpired if exceeded
        )
    except subprocess.TimeoutExpired:
        return f"Command timeout after {timeout}s."

    #raise NotImplementedError
    return f"Exit code: {result.returncode}.\n\n stdout:{result.stdout}.\n\n stderr:{result.stderr}."


def read_file(path: str, cwd: Path) -> str:
    """Read a file at `path` relative to `cwd`. Raises ValueError if path escapes cwd."""
    # TODO: resolve the full path as cwd / path
    resolved =  (cwd / path).resolve()
    BLOCKED = {".env", ".env.local", ".env.production"}
    if resolved.name in BLOCKED:
        raise ModelRetry("reading sensitive files is not allowed")
    # TODO: raise ValueError if resolved is not inside cwd
    if not resolved.is_relative_to(cwd.resolve()):
        raise ValueError

    # TODO: return the file contents as a string
    return resolved.read_text()
