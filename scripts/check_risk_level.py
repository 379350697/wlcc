#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

ACTION_SCOPE = {
    'read': 'project',
    'summary': 'project',
    'write-doc': 'project',
    'write-state': 'project',
    'modify-script': 'project',
    'modify-config': 'project',
    'delete-state': 'project',
    'overwrite-facts': 'project',
}

ORDERED = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3}


def main():
    parser = argparse.ArgumentParser(description='Classify operation risk level using policy evaluation.')
    parser.add_argument('--action', required=True)
    parser.add_argument('--require-max')
    parser.add_argument('--user-approved', action='store_true')
    parser.add_argument('--requires-confirmation', action='store_true')
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    evaluator = root / 'scripts' / 'evaluate_risk_policy.py'

    payload = {
        'action': args.action,
        'scope': ACTION_SCOPE.get(args.action, 'project'),
        'context': {
            'userApproved': args.user_approved,
            'requiresConfirmation': args.requires_confirmation,
        },
    }
    tmp = root / '.agent' / 'tmp-risk-policy.json'
    out = root / '.agent' / 'tmp-risk-policy-output.json'
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    result = subprocess.run([
        'python3', str(evaluator),
        '--input', str(tmp),
        '--output', str(out),
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print('UNKNOWN')
        raise SystemExit(2)

    policy = json.loads(out.read_text(encoding='utf-8'))
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
