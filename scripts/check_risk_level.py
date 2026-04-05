#!/usr/bin/env python3
import argparse

RULES = {
    'read': 'L0',
    'summary': 'L0',
    'write-doc': 'L1',
    'write-state': 'L1',
    'modify-script': 'L2',
    'modify-config': 'L2',
    'delete-state': 'L3',
    'overwrite-facts': 'L3',
}


def main():
    parser = argparse.ArgumentParser(description='Classify operation risk level for current project rules.')
    parser.add_argument('--action', required=True)
    parser.add_argument('--require-max')
    args = parser.parse_args()

    level = RULES.get(args.action)
    if not level:
        print('UNKNOWN')
        raise SystemExit(2)

    if args.require_max:
        ordered = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3}
        if ordered[level] > ordered[args.require_max]:
            print(f'REJECT:{level}')
            raise SystemExit(3)

    print(level)


if __name__ == '__main__':
    main()
