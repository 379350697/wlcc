#!/usr/bin/env python3
import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'MISSING_DIRTY_FIELD_CASES_RESULT.md'
issues = []

# Missing required field inside task json should break state-view consistency
task_id = 'real-task-runtime-mainline' if (root / '.agent' / 'state' / 'tasks' / 'real-task-runtime-mainline.json').exists() else 'task-phase2-demo'
path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
backup = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json.bak-missing'
if path.exists():
    shutil.copy2(path, backup)
    data = json.loads(path.read_text(encoding='utf-8'))
    data.pop('goal', None)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    res = subprocess.run(['python3', str(root / 'scripts' / 'check_state_view_consistency.py')], capture_output=True, text=True)
    if res.returncode == 0:
        issues.append('missing goal unexpectedly passed consistency check')
    shutil.copy2(backup, path)
    backup.unlink(missing_ok=True)
else:
    issues.append('missing demo task json for missing-field case')

# Dirty handoff field should still be stored but detectable by explicit read
handoff = root / '.agent' / 'state' / 'handoffs' / f'{task_id}.json'
backup2 = root / '.agent' / 'state' / 'handoffs' / f'{task_id}.json.bak-dirty'
if handoff.exists():
    shutil.copy2(handoff, backup2)
    data = json.loads(handoff.read_text(encoding='utf-8'))
    data['toAgent'] = ''
    handoff.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    reread = json.loads(handoff.read_text(encoding='utf-8'))
    if reread.get('toAgent') != '':
        issues.append('dirty handoff field mutation not persisted for explicit check')
    shutil.copy2(backup2, handoff)
    backup2.unlink(missing_ok=True)
else:
    issues.append('missing handoff state for dirty-field case')

lines = ['# MISSING_DIRTY_FIELD_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
