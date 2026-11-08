from pathlib import Path


def read_file(path: str, cwd: Path) -> str:
    """Read a file at `path` relative to `cwd`. Raises ValueError if path escapes cwd."""
    # TODO: resolve the full path as cwd / path
    resolved =  (cwd / path).resolve()
    # TODO: raise ValueError if resolved is not inside cwd
    if not resolved.is_relative_to(cwd.resolve()):
        raise ValueError

    # TODO: return the file contents as a string
    return resolved.read_text()
