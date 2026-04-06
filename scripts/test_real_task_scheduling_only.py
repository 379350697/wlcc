#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'REAL_TASK_SCHEDULING_ONLY_RESULT.md'
issues = []

input_path = root / 'tests' / 'TMP_REAL_ONLY_SCHED_INPUT.json'
output_path = root / 'tests' / 'TMP_REAL_ONLY_SCHED_OUTPUT.json'
input_path.write_text(json.dumps({'tasks': [
    {
        'taskId': 'real-primary',
        'status': 'todo',
        'priority': 'P1',
        'dependencies': [],
        'override': 'none',
        'updatedAt': '2026-04-06 16:15 Asia/Shanghai',
        'kind': 'real',
        'executionMode': 'live',
        'eligibleForScheduling': True,
        'isPrimaryTrack': True,
    },
    {
        'taskId': 'demo-high-priority',
        'status': 'todo',
        'priority': 'P0',
        'dependencies': [],
        'override': 'none',
        'updatedAt': '2026-04-06 16:16 Asia/Shanghai',
        'kind': 'demo',
        'executionMode': 'sample-only',
        'eligibleForScheduling': False,
        'isPrimaryTrack': False,
    }
]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
res = subprocess.run(['python3', str(root / 'scripts' / 'decide_next_task_v2.py'), '--input', str(input_path), '--output', str(output_path)], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('decide_next_task_v2 failed')
else:
    data = json.loads(output_path.read_text(encoding='utf-8'))
    if data.get('nextTaskId') != 'real-primary':
        issues.append('scheduler did not restrict to real primary task')

lines = ['# REAL_TASK_SCHEDULING_ONLY_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
