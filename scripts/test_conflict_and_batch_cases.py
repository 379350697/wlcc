#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'CONFLICT_AND_BATCH_CASES_RESULT.md'
issues = []

# Prepare conflict candidates in isolated output only
res = subprocess.run([
    'python3', str(root / 'scripts' / 'build_resume_state.py'),
    '--task-ids', 'demo-long-chain-autonomy', 'local-task-001',
    '--output', str(root / 'tests' / 'TMP_CONFLICT_RESUME_STATE.json')
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('build_resume_state conflict case failed')
else:
    data = json.loads((root / 'tests' / 'TMP_CONFLICT_RESUME_STATE.json').read_text(encoding='utf-8'))
    if data.get('selectedTaskId') not in {'demo-long-chain-autonomy', 'local-task-001'}:
        issues.append('unexpected selected task in batch conflict case')
    if data.get('candidateCount', 0) < 2:
        issues.append('candidateCount too small for conflict case')

# force-hold and force-run collision in scheduler
input_path = root / 'tests' / 'TMP_COLLISION_INPUT.json'
output_path = root / 'tests' / 'TMP_COLLISION_OUTPUT.json'
input_path.write_text(json.dumps({'tasks': [
    {'taskId': 'hold-task', 'status': 'todo', 'priority': 'P0', 'dependencies': [], 'override': 'force-hold', 'updatedAt': '2026-04-06 14:10 Asia/Shanghai'},
    {'taskId': 'run-task', 'status': 'todo', 'priority': 'P3', 'dependencies': [], 'override': 'force-run', 'updatedAt': '2026-04-06 14:11 Asia/Shanghai'}
]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
res = subprocess.run(['python3', str(root / 'scripts' / 'decide_next_task_v2.py'), '--input', str(input_path), '--output', str(output_path)], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('override collision decision failed')
else:
    data = json.loads(output_path.read_text(encoding='utf-8'))
    if data.get('nextTaskId') != 'run-task':
        issues.append('force-run did not win over force-hold collision')

lines = ['# CONFLICT_AND_BATCH_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
