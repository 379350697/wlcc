"""Resume and retrieval services for runtime execution."""
import json
from datetime import datetime
from pathlib import Path

from runtime.context.package import package_context_payload
from runtime.resume.context import collect_context_payload
from runtime.resume.resume_state import build_resume_state_payload
from runtime.common.paths import RuntimePaths
from runtime.state.store import resolve_task_id
from runtime.supervision.core import handle_supervision_trigger, load_json, save_json


def read_if_exists(path: Path):
    if path.exists():
        return path.read_text(encoding='utf-8').strip()
    return 'MISSING'


def extract_field(text: str, prefix: str):
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.replace(prefix, '').strip()
    return 'MISSING'


def tail_lines(text: str, count: int = 12):
    lines = text.splitlines()
    return '\n'.join(lines[-count:]) if lines else 'MISSING'


def resume_task_payload(root: Path, task_id: str) -> dict:
    context = collect_context_payload(root, task_id)
    context_package = package_context_payload(context)
    task_view = read_if_exists(root / '.agent' / 'tasks' / f'{task_id}.md')
    resume_view = read_if_exists(root / '.agent' / 'resume' / f'{task_id}-resume.md')
    tasks_view = read_if_exists(root / 'TASKS.md')
    next_task_state = read_if_exists(root / '.agent' / 'state' / 'next-task.json')
    next_task_view = read_if_exists(root / '.agent' / 'NEXT_TASK.md')
    changelog = read_if_exists(root / '.agent' / 'logs' / 'CHANGELOG.md')
    event_log = read_if_exists(root / '.agent' / 'logs' / 'EVENT_LOG.md')
    task_state_json = read_if_exists(root / '.agent' / 'state' / 'tasks' / f'{task_id}.json')
    resume_state = build_resume_state_payload(root, [task_id])
    task_kind = 'unknown'
    summary_source = 'state-json'
    if task_state_json != 'MISSING':
        parsed = json.loads(task_state_json)
        task_kind = parsed.get('kind', 'unknown')
        goal = parsed.get('goal', 'MISSING')
        status = parsed.get('status', 'MISSING')
        blocker = parsed.get('blocker', 'MISSING')
        next_step = parsed.get('nextStep', 'MISSING')
        last_success = parsed.get('lastSuccess', 'MISSING')
        last_failure = parsed.get('lastFailure', 'MISSING')
    else:
        summary_source = 'markdown-view-fallback'
        goal = extract_field(task_view, '- goal: ')
        status = extract_field(task_view, '- status: ')
        blocker = extract_field(task_view, '- blocker: ')
        next_step = extract_field(task_view, '- nextStep: ')
        last_success = extract_field(resume_view, '- 最后成功动作：')
        last_failure = extract_field(resume_view, '- 最后失败动作：')
    return {
        'structured_summary': {
            'summary_source': summary_source,
            'goal': goal,
            'status': status,
            'blocker': blocker,
            'next_step': next_step,
            'last_success': last_success,
            'last_failure': last_failure,
        },
        'recent_events': {
            'changelog_tail': tail_lines(changelog),
            'event_log_tail': tail_lines(event_log),
        },
        'retrieved_context': context,
        'runtime_meta': {
            'taskKind': task_kind,
            'contextBudgetChars': context_package.meta.get('contextBudgetChars', 0),
            'contextPackagedChars': context_package.meta.get('packagedChars', 0),
            'contextBudgetExceeded': context_package.meta.get('contextBudgetExceeded', False),
            'contextTrimmed': context_package.meta.get('contextTrimmed', False),
        },
        'resume_state': resume_state,
        'task_state_json': task_state_json,
        'task_view': task_view,
        'resume_view': resume_view,
        'tasks_view': tasks_view,
        'next_task_state': next_task_state,
        'next_task_view': next_task_view,
    }


def write_resume_output(root: Path, task_id: str) -> Path:
    payload = resume_task_payload(root, task_id)
    result_path = root / 'tests' / f'{task_id}-resume-output.md'
    result_path.parent.mkdir(parents=True, exist_ok=True)
    out = [
        '# RESUME_OUTPUT', '', '## structured_summary',
        f"- summary_source: {payload['structured_summary']['summary_source']}",
        f"- goal: {payload['structured_summary']['goal']}",
        f"- status: {payload['structured_summary']['status']}",
        f"- blocker: {payload['structured_summary']['blocker']}",
        f"- next_step: {payload['structured_summary']['next_step']}",
        f"- last_success: {payload['structured_summary']['last_success']}",
        f"- last_failure: {payload['structured_summary']['last_failure']}",
        '', '## recent_events', '### changelog_tail', payload['recent_events']['changelog_tail'], '', '### event_log_tail', payload['recent_events']['event_log_tail'], '', '## retrieved_context', json.dumps(payload['retrieved_context'], ensure_ascii=False, indent=2), '', '## runtime_meta', json.dumps(payload['runtime_meta'], ensure_ascii=False, indent=2), '', '## resume_state', json.dumps(payload['resume_state'], ensure_ascii=False, indent=2), '', '## task_state_json', payload['task_state_json'], '', '## task_view', payload['task_view'], '', '## resume_view', payload['resume_view'], '', '## tasks_view', payload['tasks_view'], '', '## next_task_state', payload['next_task_state'], '', '## next_task_view', payload['next_task_view'],
    ]
    result_path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return result_path


def resume_real_task_flow(root: Path, task_id: str) -> dict:
    paths = RuntimePaths(root)
    resolved_task_id = resolve_task_id(paths, task_id)
    task_path = root / '.agent' / 'state' / 'tasks' / f'{resolved_task_id}.json'
    task = load_json(task_path, {})
    if task.get('kind') != 'real':
        raise SystemExit('resume_real_task only supports kind=real')
    write_resume_output(root, resolved_task_id)
    task['lifecycle'] = 'active'
    task['supervisionState'] = 'active'
    task['updatedAt'] = datetime.now().isoformat(timespec='seconds')
    save_json(task_path, task)
    supervision = handle_supervision_trigger(root, resolved_task_id, 'on_interruption_detected')
    return {
        'task': task,
        'supervision': supervision,
    }
