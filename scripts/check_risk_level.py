#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.gates.risk import ACTION_SCOPE, ORDERED, evaluate_risk


def main():
    parser = argparse.ArgumentParser(description='Classify operation risk level using policy evaluation.')
    parser.add_argument('--action', required=True)
    parser.add_argument('--require-max')
    parser.add_argument('--user-approved', action='store_true')
    parser.add_argument('--requires-confirmation', action='store_true')
    args = parser.parse_args()

    payload = {
        'action': args.action,
        'scope': ACTION_SCOPE.get(args.action, 'project'),
        'context': {
            'userApproved': args.user_approved,
            'requiresConfirmation': args.requires_confirmation,
        },
    }
    try:
        policy = evaluate_risk(payload['action'], payload['scope'], payload['context'])
    except Exception:
        print('UNKNOWN')
        raise SystemExit(2)
    level = policy['riskLevel']
    decision = policy['decision']

    if args.require_max and ORDERED[level] > ORDERED[args.require_max]:
        print(f'REJECT:{level}')
        raise SystemExit(3)

    print(level)
    if decision == 'reject':
        raise SystemExit(3)
    if decision == 'require-confirmation' and not args.user_approved:
        raise SystemExit(4)


if __name__ == '__main__':
    main()
