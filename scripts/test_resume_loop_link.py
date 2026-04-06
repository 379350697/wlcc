#!/usr/bin/env python3
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
single_out = root / 'tests' / 'task-phase2-demo-resume-output.md'
bulk_out = root / 'tests' / 'BULK_RESUME_OUTPUT.md'
out = root / 'tests' / 'RESUME_LOOP_LINK_RESULT.md'

issues = []
res1 = subprocess.run([
    'python3', str(root / 'scripts' / 'resume_task.py'),
    '--project-root', str(root),
    '--task-id', 'task-phase2-demo',
], capture_output=True, text=True)
if res1.returncode != 0:
    issues.append('resume_task failed')

res2 = subprocess.run([
    'python3', str(root / 'scripts' / 'resume_many_tasks.py'),
    '--project-root', str(root),
    '--task-ids', 'task-phase2-demo', 'task-bulk-b', 'task-phase2-e2e-single',
], capture_output=True, text=True)
if res2.returncode != 0:
    issues.append('resume_many_tasks failed')

if single_out.exists():
    text = single_out.read_text(encoding='utf-8')
    if '## resume_state' not in text:
        issues.append('single resume missing resume_state section')
    if '"loopResume"' not in text:
        issues.append('single resume missing loopResume payload')
else:
    issues.append('missing single resume output')

if bulk_out.exists():
    text = bulk_out.read_text(encoding='utf-8')
    if '## bulk_resume_state' not in text:
        issues.append('bulk resume missing bulk_resume_state section')
    if '"selectedTaskId"' not in text:
        issues.append('bulk resume missing selectedTaskId payload')
else:
    issues.append('missing bulk resume output')

lines = ['# RESUME_LOOP_LINK_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
