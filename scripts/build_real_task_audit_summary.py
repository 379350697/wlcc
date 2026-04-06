#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out_md = root / '.agent' / 'audit' / 'AUDIT_SUMMARY.md'
out_json = root / '.agent' / 'audit' / 'audit-summary.json'

state_dir = root / '.agent' / 'state' / 'tasks'
supervision_dir = root / '.agent' / 'state' / 'supervision'
handoff_dir = root / '.agent' / 'state' / 'handoffs'

real_tasks = []
if state_dir.exists():
    for path in sorted(state_dir.glob('*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('kind') == 'real':
            real_tasks.append(data)

summary = {
    'defaultScope': 'real-task-first',
    'realTaskCount': len(real_tasks),
    'tasks': [],
}
for task in real_tasks:
    task_id = task['taskId']
    supervision_path = supervision_dir / f'{task_id}.json'
    handoff_path = handoff_dir / f'{task_id}.json'
    supervision = json.loads(supervision_path.read_text(encoding='utf-8')) if supervision_path.exists() else {}
    handoff = json.loads(handoff_path.read_text(encoding='utf-8')) if handoff_path.exists() else {}
    summary['tasks'].append({
        'taskId': task_id,
        'lifecycle': task.get('lifecycle', 'unknown'),
        'supervisionState': task.get('supervisionState', 'unknown'),
        'scope': supervision.get('scope', 'unknown'),
        'lastHeartbeatAt': supervision.get('lastHeartbeatAt'),
        'lastResumeAt': supervision.get('lastResumeAt'),
        'lastHandoffAt': supervision.get('lastHandoffAt'),
        'handoffReason': handoff.get('reason', 'none'),
    })

out_json.parent.mkdir(parents=True, exist_ok=True)
out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

lines = ['# AUDIT_SUMMARY', '', '## runtime_scope', '- defaultScope: real-task-first', f'- realTaskCount: {len(real_tasks)}', '', '## tasks']
if real_tasks:
    for item in summary['tasks']:
        lines.append(f"- taskId: {item['taskId']} | lifecycle: {item['lifecycle']} | supervisionState: {item['supervisionState']} | scope: {item['scope']} | handoffReason: {item['handoffReason']}")
else:
    lines.append('- none')
out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out_json}')
print(f'OK: wrote {out_md}')
