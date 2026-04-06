#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.sidecar.reports import render_state_views_for_root


def main():
    parser = argparse.ArgumentParser(description='Render markdown views from canonical state store.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id')
    args = parser.parse_args()
    for path in render_state_views_for_root(Path(args.project_root), args.task_id):
        print(f'OK: wrote {path}')


if __name__ == '__main__':
    main()
