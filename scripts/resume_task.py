#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.resume.service import write_resume_output


def main():
    parser = argparse.ArgumentParser(description='Resume a task from canonical state first, markdown views second.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root)
    result_path = write_resume_output(project_root, args.task_id)
    print(f'OK: wrote {result_path}')


if __name__ == '__main__':
    main()
