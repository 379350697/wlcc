#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.sidecar.reports import write_retrieve_context_output


def main():
    parser = argparse.ArgumentParser(description='Retrieve context with explicit source priority.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()
    payload_root = Path(args.project_root)
    _, output = write_retrieve_context_output(payload_root, args.task_id)
    print(f'OK: wrote {output}')


if __name__ == '__main__':
    main()
