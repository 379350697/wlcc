#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from runtime.scheduling.next_task import choose_next_task


def main():
    parser = argparse.ArgumentParser(description='Decide next task with priority/dependency/override support.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    tasks = json.loads(Path(args.input).read_text(encoding='utf-8'))['tasks']
    result = choose_next_task(tasks)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('OK')


if __name__ == '__main__':
    main()
