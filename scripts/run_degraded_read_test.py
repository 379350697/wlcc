#!/usr/bin/env python3
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent.parent
session_file = root / 'memory' / 'session' / 'SESSION_SUMMARY.md'
backup_file = root / 'memory' / 'session' / 'SESSION_SUMMARY.md.bak'
out_file = root / 'tests' / 'COMPATIBILITY_DEGRADED_OUTPUT.md'

if session_file.exists():
    session_file.rename(backup_file)

try:
    result = subprocess.run(
        ['python3', str(root / 'scripts' / 'read_project_context.py'), '--project-root', str(root), '--task-id', 'task-001'],
        capture_output=True,
        text=True,
        check=False,
    )
    out_file.write_text(result.stdout, encoding='utf-8')
finally:
    if backup_file.exists():
        backup_file.rename(session_file)

print('OK: degraded read test finished')
