#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
script = root / 'scripts' / 'build_resume_state.py'
out_json = root / '.agent' / 'state' / 'bulk-resume-state.json'
out_md = root / 'tests' / 'RESUME_CONFLICT_RESOLUTION_RESULT.md'

task_dir = root / '.agent' / 'state' / 'tasks'
task_ids = ['task-phase2-demo', 'task-bulk-b', 'task-phase2-e2e-single']
if task_dir.exists():
    available = [p.stem for p in sorted(task_dir.glob('*.json'))]
    if len(available) >= 3:
        task_ids = available[:3]
    elif available:
        task_ids = available

res = subprocess.run([
    'python3', str(script),
    '--task-ids', *task_ids,
    '--output', str(out_json),
], capture_output=True, text=True)

issues = []
if res.returncode != 0:
    issues.append('build_resume_state failed')
if not out_json.exists():
    issues.append('missing bulk-resume-state.json')
else:
    data = json.loads(out_json.read_text(encoding='utf-8'))
    if data.get('selectedTaskId') == 'none':
        issues.append('unexpected selectedTaskId')
    if not data.get('selectionReasons', []):
        issues.append('missing next-task priority reason')
    if 'loopResume' not in data:
        issues.append('missing loopResume')
    if data.get('loopResume', {}).get('lastTaskId') in {None, 'none'}:
        issues.append('missing loop task linkage')
    if not data.get('conflictPolicy', {}).get('priority'):
        issues.append('missing conflictPolicy priority')

lines = ['# RESUME_CONFLICT_RESOLUTION_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out_md}')
raise SystemExit(code)
