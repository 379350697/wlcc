#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


root = Path(__file__).resolve().parent.parent
state_dir = root / '.agent' / 'state' / 'tasks'
next_state = root / '.agent' / 'state' / 'next-task.json'
next_view = root / '.agent' / 'NEXT_TASK.md'
input_file = root / '.agent' / 'state' / 'next-task-input.json'


tasks = []
for path in sorted(state_dir.glob('*.json')):
    tasks.append(json.loads(path.read_text(encoding='utf-8')))

payload = {'tasks': tasks}
input_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

subprocess.run([
    'python3', str(root / 'scripts' / 'decide_next_task_v2.py'),
    '--input', str(input_file),
    '--output', str(next_state),
], check=True)

result = json.loads(next_state.read_text(encoding='utf-8'))
lines = [
    '# NEXT_TASK',
    '',
    f"- currentTask: {result['currentTask']}",
    f"- currentStatus: {result['currentStatus']}",
    f"- decisionType: {result['decisionType']}",
    f"- nextTaskId: {result['nextTaskId']}",
    f"- selectedPriority: {result['selectedPriority']}",
    f"- dependencyStatus: {result['dependencyStatus']}",
    f"- overrideStatus: {result['overrideStatus']}",
    f"- reason: {result['reason']}",
    f"- nextAction: {result['nextAction']}",
]
next_view.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {next_state}')
print(f'OK: wrote {next_view}')
