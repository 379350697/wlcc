#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'DEADLOOP_AND_ROLLBACK_CASES_RESULT.md'
issues = []

cases = [
    ({'taskId': 'demo-long-chain-autonomy', 'repeatedTask': True, 'repeatedFailures': 3, 'noProgressCount': 3}, 'dead-loop-stop'),
    ({'taskId': 'demo-long-chain-autonomy', 'reason': 'need rollback now', 'stopType': 'anomaly-stop', 'retries': 2, 'maxRetries': 2}, 'rollback'),
]
input_path = root / 'tests' / 'TMP_FAILURE_CONTROL_INPUT.json'
for payload, expected in cases:
    input_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    res = subprocess.run(['python3', str(root / 'scripts' / 'evaluate_failure_control.py'), '--input', str(input_path)], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append(f'evaluate_failure_control failed for {expected}')
        continue
    data = json.loads((root / '.agent' / 'loop' / 'failure-control.json').read_text(encoding='utf-8'))
    if data.get('decision') != expected:
        issues.append(f'expected {expected}, got {data.get("decision")}')

lines = ['# DEADLOOP_AND_ROLLBACK_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
