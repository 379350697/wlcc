#!/usr/bin/env python3
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Append a normalized event to EVENT_LOG.md')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--time', required=True)
    parser.add_argument('--type', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--result', required=True)
    parser.add_argument('--note', required=True)
    args = parser.parse_args()

    root = Path(args.project_root)
    path = root / '.agent' / 'logs' / 'EVENT_LOG.md'
    if path.exists():
        old = path.read_text(encoding='utf-8').rstrip() + '\n'
    else:
        old = '# EVENT_LOG\n\n'

    block = (
        '## Event\n'
        f'- time: {args.time}\n'
        f'- type: {args.type}\n'
        f'- target: {args.target}\n'
        f'- result: {args.result}\n'
        f'- note: {args.note}\n\n'
    )
    path.write_text(old + block, encoding='utf-8')
    print(f'OK: wrote {path}')


if __name__ == '__main__':
    main()
