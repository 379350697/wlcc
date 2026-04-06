#!/usr/bin/env python3
import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'RESUME_STATE_CONFLICT_CASES_RESULT.md'
issues = []

resume_state = root / '.agent' / 'state' / 'demo-long-chain-autonomy-resume-state.json'
backup = root / '.agent' / 'state' / 'demo-long-chain-autonomy-resume-state.json.bak-conflict'
if resume_state.exists():
    shutil.copy2(resume_state, backup)
    data = json.loads(resume_state.read_text(encoding='utf-8'))
    data['selectedTaskId'] = 'local-task-001'
    resume_state.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    res = subprocess.run(['python3', str(root / 'scripts' / 'resume_task.py'), '--project-root', str(root), '--task-id', 'demo-long-chain-autonomy'], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append('resume_task failed during conflict case')
    output = root / 'tests' / 'demo-long-chain-autonomy-resume-output.md'
    if output.exists():
        text = output.read_text(encoding='utf-8')
        if 'demo-long-chain-autonomy' not in text:
            issues.append('resume output lost primary task identity under conflict')
    else:
        issues.append('missing resume output for conflict case')
    shutil.copy2(backup, resume_state)
    backup.unlink(missing_ok=True)
else:
    issues.append('missing resume-state for conflict case')

lines = ['# RESUME_STATE_CONFLICT_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
