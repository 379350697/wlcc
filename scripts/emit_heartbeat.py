#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.supervision.heartbeat import emit_heartbeat_record


def main():
    parser = argparse.ArgumentParser(description='Emit structured heartbeat report for long-chain autonomy.')
    parser.add_argument('--stage', required=True)
    parser.add_argument('--current-task', required=True)
    parser.add_argument('--next-step', required=True)
    parser.add_argument('--trigger-reason', required=True)
    parser.add_argument('--requires-human', action='store_true')
    parser.add_argument('--completed-items', nargs='*', default=[])
    parser.add_argument('--risk-or-blocker', default='none')
    parser.add_argument('--throttle-seconds', type=int, default=60)
    args = parser.parse_args()

    emit_heartbeat_record(root, {
        'stage': args.stage,
        'completedItems': args.completed_items,
        'currentTask': args.current_task,
        'riskOrBlocker': args.risk_or_blocker,
        'nextStep': args.next_step,
        'requiresHuman': args.requires_human,
        'triggerReason': args.trigger_reason,
    }, throttle_seconds=args.throttle_seconds, write_markdown=True)
    print(f"OK: wrote {root / '.agent' / 'heartbeat' / 'latest-heartbeat.json'}")
    print(f"OK: wrote {root / '.agent' / 'heartbeat' / 'heartbeat-history.json'}")
    print(f"OK: wrote {root / 'tests' / 'HEARTBEAT_RESULT.md'}")


if __name__ == '__main__':
    main()
