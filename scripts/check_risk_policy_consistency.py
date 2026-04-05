#!/usr/bin/env python3
import json
from pathlib import Path


root = Path(__file__).resolve().parent.parent
issues = []

policy_path = root / 'risk_policy.json'
matrix_path = root / 'tests' / 'RISK_POLICY_MATRIX_RESULT.md'
granularity_path = root / 'tests' / 'RISK_POLICY_GRANULARITY_RESULT.md'
integration_path = root / 'tests' / 'RISK_POLICY_INTEGRATION_RESULT.md'
risk_log_path = root / '.agent' / 'audit' / 'RISK_CHECK_LOG.md'

if not policy_path.exists():
    issues.append('missing risk_policy.json')
else:
    policy = json.loads(policy_path.read_text(encoding='utf-8'))
    if policy.get('version') != 'phase2-v2':
        issues.append('unexpected risk policy version')
    actions = [rule.get('action') for rule in policy.get('rules', [])]
    if 'modify-script' not in actions:
        issues.append('missing modify-script rule')
    if 'delete-state' not in actions:
        issues.append('missing delete-state rule')
    if not any(rule.get('matchContext', {}).get('touchesCanonicalState') is True for rule in policy.get('rules', [])):
        issues.append('missing canonical-state granular rule')
    if not any(rule.get('matchContext', {}).get('touchesReleaseRepo') is True for rule in policy.get('rules', [])):
        issues.append('missing release-repo granular rule')

for path, label in [
    (matrix_path, 'matrix'),
    (granularity_path, 'granularity'),
    (integration_path, 'integration'),
    (risk_log_path, 'risk-log'),
]:
    if not path.exists():
        issues.append(f'missing {label} artifact')

if matrix_path.exists() and '- PASS' not in matrix_path.read_text(encoding='utf-8'):
    issues.append('risk matrix result not pass')
if granularity_path.exists() and '- PASS' not in granularity_path.read_text(encoding='utf-8'):
    issues.append('risk granularity result not pass')
if integration_path.exists():
    integration_text = integration_path.read_text(encoding='utf-8')
    if 'risk_policy.json' not in integration_text:
        issues.append('integration result missing configized policy note')
    if 'RISK_POLICY_GRANULARITY_RESULT.md' not in integration_text:
        issues.append('integration result missing granularity note')
if risk_log_path.exists():
    risk_log = risk_log_path.read_text(encoding='utf-8')
    if 'check_risk_level.py --action write-state' not in risk_log:
        issues.append('risk log missing write-state record')
    if 'check_risk_level.py --action delete-state' not in risk_log:
        issues.append('risk log missing delete-state record')

lines = ['# RISK_POLICY_CONSISTENCY', '']
if policy_path.exists():
    lines.append('## summary')
    lines.append(f"- policy_version: {policy.get('version', 'unknown')}")
    lines.append(f"- matrix_artifact: {'yes' if matrix_path.exists() else 'no'}")
    lines.append(f"- granularity_artifact: {'yes' if granularity_path.exists() else 'no'}")
    lines.append(f"- integration_artifact: {'yes' if integration_path.exists() else 'no'}")
    lines.append(f"- risk_log_artifact: {'yes' if risk_log_path.exists() else 'no'}")
    lines.append('')
lines.append('## issues')
if issues:
    lines.extend(f'- {issue}' for issue in issues)
    code = 1
else:
    lines.append('- none')
    code = 0

out = root / 'tests' / 'RISK_POLICY_CONSISTENCY_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
