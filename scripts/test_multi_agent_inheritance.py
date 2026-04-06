#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
policy_path = root / '.agent' / 'state' / 'multi-agent-policy.json'
handoff_path = root / '.agent' / 'state' / 'handoffs' / 'task-phase2-demo.json'
resume_state_path = root / '.agent' / 'state' / 'task-phase2-demo-resume-state.json'
next_task_path = root / '.agent' / 'state' / 'next-task.json'
risk_policy_path = root / 'risk_policy.json'
out = root / 'tests' / 'MULTI_AGENT_INHERITANCE_RESULT.md'

issues = []
if not policy_path.exists():
    issues.append('missing multi-agent-policy.json')
else:
    policy = json.loads(policy_path.read_text(encoding='utf-8'))
    if policy.get('sharedStateSource') != 'canonical-state':
        issues.append('sharedStateSource mismatch')
    rules = policy.get('inheritanceRules', {})
    if rules.get('nextTaskReadPolicy') != 'all-agents-read-same-next-task':
        issues.append('nextTaskReadPolicy mismatch')
    if rules.get('stopHeartbeatRiskSemantics') != 'shared':
        issues.append('stopHeartbeatRiskSemantics mismatch')
    permissions = policy.get('writePermissions', {})
    if 'write-state' not in permissions.get('owner', []):
        issues.append('owner missing write-state')
    if 'write-state' not in permissions.get('executor', []):
        issues.append('executor missing write-state')
    if 'write-state' in permissions.get('reviewer', []):
        issues.append('reviewer should not write-state')

if not handoff_path.exists():
    issues.append('missing handoff state')
if not resume_state_path.exists():
    issues.append('missing resume state')
if not next_task_path.exists():
    issues.append('missing next-task state')
if not risk_policy_path.exists():
    issues.append('missing risk policy')

lines = ['# MULTI_AGENT_INHERITANCE_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
