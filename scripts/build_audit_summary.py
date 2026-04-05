#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
audit_dir = root / '.agent' / 'audit'
logs_dir = root / '.agent' / 'logs'
out_path = root / '.agent' / 'audit' / 'AUDIT_SUMMARY.md'

sources = [
    logs_dir / 'CHANGELOG.md',
    logs_dir / 'FAILURE_LOG.md',
    logs_dir / 'HEALTHCHECK_LOG.md',
    audit_dir / 'RECOVERY_LOG.md',
    audit_dir / 'ROLLBACK_LOG.md',
    audit_dir / 'RISK_CHECK_LOG.md',
    audit_dir / 'COMPATIBILITY_AUDIT.md',
]

parts = ['# AUDIT_SUMMARY', '']
for src in sources:
    parts.append(f'## {src.name}')
    if src.exists():
        parts.append(src.read_text(encoding='utf-8').strip())
    else:
        parts.append('MISSING')
    parts.append('')

out_path.write_text('\n'.join(parts).rstrip() + '\n', encoding='utf-8')
print(f'OK: wrote {out_path}')
