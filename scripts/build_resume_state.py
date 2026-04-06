#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.sidecar.reports import write_resume_state_output


def main():
    parser = argparse.ArgumentParser(description='Build multi-session resume state with conflict resolution.')
    parser.add_argument('--task-ids', nargs='+', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    _, output = write_resume_state_output(root, args.task_ids, Path(args.output))
    print(f'OK: wrote {output}')


if __name__ == '__main__':
    main()
