#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'HANDOFF_RESUME_CROSSCHECK_RESULT.md'
issues = []

subprocess.run([
    'python3', str(root / 'scripts' / 'resume_task.py'),
    '--project-root', str(root),
    '--task-id', 'demo-long-chain-autonomy',
], capture_output=True, text=True)

res = subprocess.run([
    'python3', str(root / 'scripts' / 'write_handoff_state.py'),
    '--task-id', 'demo-long-chain-autonomy',
    '--owner', 'ceo',
    '--executor', 'coder',
    '--reviewer', 'reviewer',
    '--from-agent', 'coder',
    '--to-agent', 'reviewer',
    '--reason', 'crosscheck-demo',
    '--summary', '验证 handoff 和 resume 是否能互相链接。',
    '--next-action', 'resume-after-handoff',
    '--requires-human',
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('write_handoff_state failed')

handoff_path = root / '.agent' / 'state' / 'handoffs' / 'demo-long-chain-autonomy.json'
if not handoff_path.exists():
    issues.append('handoff state missing')
else:
    data = json.loads(handoff_path.read_text(encoding='utf-8'))
    if data.get('linkedResumeState') == 'missing':
        issues.append('handoff missing linked resume state')
    if data.get('linkedNextTask') == 'missing':
        issues.append('handoff missing linked next-task')

lines = ['# HANDOFF_RESUME_CROSSCHECK_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
