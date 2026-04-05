#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Fallback wrapper for next-task decision. Prefer v2 state-based builder.')
    parser.add_argument('--project-root', required=True)
    args = parser.parse_args()

    root = Path(args.project_root)
    builder = root / 'scripts' / 'build_next_task_from_state.py'
    if builder.exists():
        result = subprocess.run(['python3', str(builder)], check=False)
        raise SystemExit(result.returncode)

    print('ERROR: next-task v2 builder missing; no fallback available')
    raise SystemExit(2)


if __name__ == '__main__':
    main()
