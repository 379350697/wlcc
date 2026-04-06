#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description='Evaluate unified retry/reorder/rollback/dead-loop control.')
    parser.add_argument('--input', required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding='utf-8'))
    task_id = payload['taskId']
    stop_type = payload.get('stopType', 'none')
    reason = payload.get('reason', '')
    retries = payload.get('retries', 0)
    max_retries = payload.get('maxRetries', 0)
    repeated_task = payload.get('repeatedTask', False)
    repeated_failures = payload.get('repeatedFailures', 0)
    no_progress = payload.get('noProgressCount', 0)

    result = {
        'taskId': task_id,
        'decision': 'continue',
        'reason': 'continue',
        'nextAction': 'continue-loop',
        'requiresHuman': False,
    }

    if repeated_task or repeated_failures >= 3 or no_progress >= 3:
        result.update({
            'decision': 'dead-loop-stop',
            'reason': 'dead loop guard triggered',
            'nextAction': 'inspect-loop',
            'requiresHuman': True,
        })
    elif 'rollback' in reason.lower():
        result.update({
            'decision': 'rollback',
            'reason': reason,
            'nextAction': 'rollback',
            'requiresHuman': True,
        })
    elif stop_type == 'anomaly-stop' and retries < max_retries:
        result.update({
            'decision': 'retry',
            'reason': 'retry budget available',
            'nextAction': 'retry-same-task',
            'requiresHuman': False,
        })
    elif stop_type == 'anomaly-stop' and retries >= max_retries:
        result.update({
            'decision': 'reorder',
            'reason': 'retry budget exhausted',
            'nextAction': 'reorder-next-task',
            'requiresHuman': False,
        })
    elif stop_type == 'risk-stop':
        result.update({
            'decision': 'wait-confirmation',
            'reason': reason or 'risk stop',
            'nextAction': 'wait-human',
            'requiresHuman': True,
        })

    out_json = root / '.agent' / 'loop' / 'failure-control.json'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = ['# FAILURE_CONTROL_RESULT', '', '## summary']
    lines.append(f"- taskId: {task_id}")
    lines.append(f"- decision: {result['decision']}")
    lines.append(f"- reason: {result['reason']}")
    lines.append(f"- nextAction: {result['nextAction']}")
    lines.append(f"- requiresHuman: {str(result['requiresHuman']).lower()}")
    out_md = root / 'tests' / 'FAILURE_CONTROL_RESULT.md'
    out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out_json}')
    print(f'OK: wrote {out_md}')

if __name__ == '__main__':
    main()
