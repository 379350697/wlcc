#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.gates.risk import evaluate_risk, load_policy


def main():
    parser = argparse.ArgumentParser(description='Evaluate policy-based risk decision.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding='utf-8'))
    result = evaluate_risk(payload['action'], payload['scope'], payload.get('context', {}), payload.get('target'))
    result['action'] = payload['action']
    result['scope'] = payload['scope']
    result['policyVersion'] = load_policy().get('version', 'unknown')
    if 'target' in payload:
        result['target'] = payload['target']
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('OK')


if __name__ == '__main__':
    main()
