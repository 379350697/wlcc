#!/usr/bin/env python3
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent.parent
results = []

# 1. retrieval-based read
read_cmd = ['python3', str(root / 'scripts' / 'retrieve_context.py'), '--project-root', str(root), '--task-id', 'task-phase2-demo']
read_res = subprocess.run(read_cmd, capture_output=True, text=True)
results.append(('retrieval_read', read_res.returncode == 0))

# 2. risk check
risk_cmd = ['python3', str(root / 'scripts' / 'check_risk_level.py'), '--action', 'write-state']
risk_res = subprocess.run(risk_cmd, capture_output=True, text=True)
results.append(('risk_check', risk_res.returncode == 0 and risk_res.stdout.strip() == 'L1'))

# 3. audit summary exists
summary_path = root / '.agent' / 'audit' / 'AUDIT_SUMMARY.md'
results.append(('audit_summary', summary_path.exists()))

out = ['# SYSTEM_HEALTHCHECK', '']
for name, ok in results:
    out.append(f'- {name}: {"PASS" if ok else "FAIL"}')

status = 'PASS' if all(ok for _, ok in results) else 'FAIL'
out.append('')
out.append(f'## Overall\n- {status}')

result_path = root / 'tests' / 'SYSTEM_HEALTHCHECK_RESULT.md'
result_path.write_text('\n'.join(out) + '\n', encoding='utf-8')

log_script = root / 'scripts' / 'log_event.py'
if log_script.exists():
    subprocess.run([
        'python3', str(log_script),
        '--project-root', str(root),
        '--time', '2026-04-05 19:31 Asia/Shanghai',
        '--type', 'system-healthcheck',
        '--target', 'system',
        '--result', status.lower(),
        '--note', 'system healthcheck executed',
    ], check=False)

print(status)
