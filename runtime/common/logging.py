from pathlib import Path

from runtime.common.io import append_line


def append_log(path: Path, line: str) -> None:
    append_line(path, line)

