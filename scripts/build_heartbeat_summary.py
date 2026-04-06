#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.sidecar.reports import build_heartbeat_summary


def main():
    _, outputs = build_heartbeat_summary(root)
    for path in outputs:
        print(f'OK: wrote {path}')


if __name__ == '__main__':
    main()
