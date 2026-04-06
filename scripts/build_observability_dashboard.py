#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent.parent
audit_dir = root / '.agent' / 'audit'
loop_dir = root / '.agent' / 'loop'
heartbeat_dir = root / '.agent' / 'heartbeat'
logs_dir = root / '.agent' / 'logs'

dashboard_md = audit_dir / 'OBSERVABILITY_DASHBOARD.md'
dashboard_json = audit_dir / 'observability-dashboard.json'


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def read_text(path: Path):
    if not path.exists():
        return 'MISSING'
    return path.read_text(encoding='utf-8').strip()


def parse_event_blocks(path: Path):
    if not path.exists():
        return []
    raw = path.read_text(encoding='utf-8').strip().split('## Event')
    blocks = []
    for block in raw:
        block = block.strip()
        if not block:
            continue
        item = {}
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith('- '):
                continue
            if ': ' not in line:
                continue
            key, value = line[2:].split(': ', 1)
            item[key] = value
        blocks.append(item)
    return blocks


def main():
    audit_dir.mkdir(parents=True, exist_ok=True)

    loop_last_run = load_json(loop_dir / 'last-run.json', {})
    check_summary = load_json(loop_dir / 'check-summary.json', {})
    retry_state = load_json(loop_dir / 'retry-state.json', {})
    failure_control = load_json(loop_dir / 'failure-control.json', {})
    heartbeat_summary = load_json(heartbeat_dir / 'heartbeat-summary.json', {})
    system_healthcheck = read_text(root / 'tests' / 'SYSTEM_HEALTHCHECK_RESULT.md')
    event_blocks = parse_event_blocks(logs_dir / 'EVENT_LOG.md')

    failure_counter = Counter()
    rollback_events = []
    retry_reorder_events = []
    check_failures = []
    for event in event_blocks:
        event_type = event.get('type', 'unknown')
        result = event.get('result', 'unknown')
        note = event.get('note', '')
        target = event.get('target', 'unknown')
        if result == 'failure' or 'failure' in note or 'rollback' in note or 'risk' in note:
            failure_counter[target] += 1
        if 'rollback' in note.lower() or event_type == 'rollback':
            rollback_events.append(event)
        if event_type in {'task-loop-step', 'task-update'} and any(token in note.lower() for token in ['retry', 'reorder', 'rollback']):
            retry_reorder_events.append(event)

    for item in check_summary.get('checks', []):
        if item.get('status') != 'continue':
            check_failures.append({'name': item.get('name', 'unknown'), 'status': item.get('status', 'unknown')})

    failure_clusters = [
        {'target': target, 'count': count}
        for target, count in failure_counter.most_common()
    ]

    loop_history = [step for step in loop_last_run.get('steps', []) if step.get('taskId', '').startswith('real-') or step.get('taskId') == 'real-task-runtime-mainline']
    dashboard = {
        'loopHistory': loop_history,
        'checkHistory': check_summary.get('checks', []),
        'failureClusters': failure_clusters,
        'retryReorderRollbackHistory': {
            'retryState': retry_state,
            'latestFailureControl': failure_control,
            'matchedEvents': retry_reorder_events,
            'rollbackEvents': rollback_events,
        },
        'systemHealthSummary': {
            'heartbeatSummary': heartbeat_summary,
            'systemHealthcheck': system_healthcheck,
            'eventCount': len(event_blocks),
            'checkFailures': check_failures,
        },
    }
    dashboard_json.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = ['# OBSERVABILITY_DASHBOARD', '']
    lines.append('## loop_history')
    steps = dashboard['loopHistory']
    if steps:
        lines.append(f'- steps: {len(steps)}')
        last = steps[-1]
        lines.append(f"- lastTask: {last.get('taskId', 'unknown')}")
        lines.append(f"- lastFailureControl: {last.get('failureControl', 'unknown')}")
        lines.append(f"- lastRiskEscalation: {last.get('riskEscalation', 'unknown')}")
    else:
        lines.append('- none')

    lines.append('')
    lines.append('## check_history')
    checks = dashboard['checkHistory']
    if checks:
        for item in checks:
            lines.append(f"- {item.get('name', 'unknown')}: {item.get('status', 'unknown')}")
    else:
        lines.append('- none')

    lines.append('')
    lines.append('## failure_clusters')
    if failure_clusters:
        for item in failure_clusters[:10]:
            lines.append(f"- {item['target']}: {item['count']}")
    else:
        lines.append('- none')

    lines.append('')
    lines.append('## retry_reorder_rollback_history')
    lines.append(f"- retryStateTasks: {len(retry_state)}")
    lines.append(f"- latestFailureDecision: {failure_control.get('decision', 'none')}")
    lines.append(f"- matchedEvents: {len(retry_reorder_events)}")
    lines.append(f"- rollbackEvents: {len(rollback_events)}")

    lines.append('')
    lines.append('## runtime_scope')
    lines.append('- defaultScope: real-task-first')
    real_failure_clusters = [item for item in failure_clusters if str(item.get('target', '')).startswith('real-')]
    lines.append(f'- realFailureClusterCount: {len(real_failure_clusters)}')
    lines.append('')
    lines.append('## system_health_summary')
    heartbeat_count = heartbeat_summary.get('historyCount', 0)
    requires_human_count = heartbeat_summary.get('requiresHumanCount', 0)
    lines.append(f'- heartbeatHistoryCount: {heartbeat_count}')
    lines.append(f'- heartbeatRequiresHumanCount: {requires_human_count}')
    lines.append(f'- eventCount: {len(event_blocks)}')
    lines.append(f"- checkFailureCount: {len(check_failures)}")
    if '## Overall' in system_healthcheck:
        overall_line = system_healthcheck.split('## Overall', 1)[1].strip().splitlines()[0].strip()
        lines.append(f'- systemHealthcheck: {overall_line}')

    dashboard_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {dashboard_json}')
    print(f'OK: wrote {dashboard_md}')


if __name__ == '__main__':
    main()
