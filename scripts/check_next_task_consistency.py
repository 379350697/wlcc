#!/usr/bin/env python3
import json
from pathlib import Path


root = Path(__file__).resolve().parent.parent
state_file = root / '.agent' / 'state' / 'next-task.json'
view_file = root / '.agent' / 'NEXT_TASK.md'
issues = []

if not state_file.exists():
    issues.append('missing next-task state json')
else:
    state = json.loads(state_file.read_text(encoding='utf-8'))

if not view_file.exists():
    issues.append('missing NEXT_TASK markdown view')
else:
    view = view_file.read_text(encoding='utf-8')

if not issues:
    mapping = {
        'currentTask': 'currentTask',
        'currentStatus': 'currentStatus',
        'decisionType': 'decisionType',
        'nextTaskId': 'nextTaskId',
        'selectedPriority': 'selectedPriority',
        'dependencyStatus': 'dependencyStatus',
        'overrideStatus': 'overrideStatus',
    }
    for json_key, md_key in mapping.items():
        value = state.get(json_key, 'MISSING')
        expected = f'- {md_key}: {value}'
        if expected not in view:
            issues.append(f'mismatch: {json_key}')

lines = ['# NEXT_TASK_CONSISTENCY', '']
if not issues:
    lines.append('## summary')
    lines.append(f"- currentTask: {state.get('currentTask', 'MISSING')}")
    lines.append(f"- nextTaskId: {state.get('nextTaskId', 'MISSING')}")
    lines.append(f"- decisionType: {state.get('decisionType', 'MISSING')}")
    lines.append(f"- selectedPriority: {state.get('selectedPriority', 'MISSING')}")
    lines.append('')
lines.append('## issues')
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0

out = root / 'tests' / 'NEXT_TASK_CONSISTENCY_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
