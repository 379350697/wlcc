#!/usr/bin/env python3
import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Safely write content to a file using temp file + atomic replace + backup.")
    parser.add_argument("target", help="Target file path")
    parser.add_argument("--input", help="Input content file path")
    parser.add_argument("--backup-dir", help="Directory for backups")
    parser.add_argument("--ensure-parent", action="store_true", help="Create parent directories if missing")
    args = parser.parse_args()

    target = Path(args.target)
    if args.ensure_parent:
        target.parent.mkdir(parents=True, exist_ok=True)

    if not args.input:
        print("ERROR: --input is required", file=sys.stderr)
        return 2

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 2

    content = input_path.read_text(encoding="utf-8")
    if content == "":
        print("ERROR: refusing to write empty content", file=sys.stderr)
        return 2

    if target.exists() and args.backup_dir:
        backup_dir = Path(args.backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{target.name}.bak"
        shutil.copy2(target, backup_path)

    temp_dir = target.parent if str(target.parent) not in ("", ".") else Path.cwd()
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_path_str = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(temp_dir))
    temp_path = Path(temp_path_str)

    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        if temp_path.read_text(encoding="utf-8") != content:
            raise RuntimeError("temporary file content verification failed")

        os.replace(str(temp_path), str(target))

        if target.read_text(encoding="utf-8") != content:
            raise RuntimeError("post-replace verification failed")

        print(f"OK: wrote {target}")
        return 0
    except Exception as e:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
