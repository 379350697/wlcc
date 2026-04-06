import json
from datetime import datetime
from pathlib import Path

from runtime.sidecar.tasks_view import write_state_views

PRIORITY_ORDER = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
STATUS_ORDER = {'doing': 0, 'todo': 1, 'blocked': 2, 'done': 3}


def parse_time(text: str) -> datetime:
    """Parse timestamps produced by the task runtime.

    Supports legacy spaced timestamps and newer ISO timestamps so the
    scheduler keeps working as the runtime migrates.
    """
    if text is None:
        raise ValueError('missing time text')

    cleaned = str(text).strip()
    if cleaned.endswith(' Asia/Shanghai'):
        cleaned = cleaned.removesuffix(' Asia/Shanghai')

    candidates = (
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
    )
    for fmt in candidates:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError(f'unsupported timestamp format: {text!r}') from exc


def _sort_time_value(text: str) -> datetime:
    try:
        return parse_time(text)
    except ValueError:
        return datetime.min


def _sort_time_rank(text: str) -> float:
    try:
        return parse_time(text).timestamp()
    except ValueError:
        return float('-inf')


def load_tasks_from_state_dir(state_dir: Path) -> list[dict]:
    tasks = []
    for path in sorted(state_dir.glob('*.json')):
        tasks.append(json.loads(path.read_text(encoding='utf-8')))
    return tasks


def normalize_task(task: dict, done_ids: set[str]) -> dict:
    priority = task.get('priority', 'P2')
    dependencies = task.get('dependencies', [])
    override = task.get('override', 'none')
    kind = task.get('kind', 'sample')
    execution_mode = task.get('executionMode', 'live')
    eligible = task.get('eligibleForScheduling', True)
    primary = task.get('isPrimaryTrack', False)
    dependency_satisfied = all(dep in done_ids for dep in dependencies)
    runnable = (
        task.get('status') in {'doing', 'todo'}
        and dependency_satisfied
        and override != 'force-hold'
        and eligible
    )
    forced = override == 'force-run'
    return {
        **task,
        'priority': priority,
        'dependencies': dependencies,
        'override': override,
        'kind': kind,
        'executionMode': execution_mode,
        'eligibleForScheduling': eligible,
        'isPrimaryTrack': primary,
        'dependencySatisfied': dependency_satisfied,
        'isRunnable': runnable,
        'isForced': forced,
    }


def build_next_task_payload(tasks: list[dict]) -> dict:
    return {'tasks': tasks}


def choose_next_task(tasks: list[dict]) -> dict:
    done_ids = {t['taskId'] for t in tasks if t.get('status') == 'done'}
    normalized = [normalize_task(t, done_ids) for t in tasks]

    force_run = [t for t in normalized if t['override'] == 'force-run']
    if force_run:
        selected = sorted(
            force_run,
            key=lambda t: (
                PRIORITY_ORDER.get(t['priority'], 99),
                _sort_time_rank(t.get('updatedAt', '')),
            ),
        )[0]
        return {
            'decisionType': 'force-override',
            'nextTaskId': selected['taskId'],
            'selectedPriority': selected['priority'],
            'dependencyStatus': 'satisfied' if selected['dependencySatisfied'] else 'unsatisfied',
            'overrideStatus': 'force-run',
            'reason': '存在 force-run 覆盖任务。',
            'nextAction': '直接执行覆盖任务。',
            'currentTask': selected['taskId'],
            'currentStatus': selected['status'],
        }

    active = [
        t for t in normalized
        if t['status'] != 'done'
        and t['override'] != 'force-hold'
        and t.get('eligibleForScheduling', False)
        and t.get('executionMode', 'sample-only') != 'sample-only'
    ]
    if not active:
        return {
            'decisionType': 'done-no-next',
            'nextTaskId': 'none',
            'selectedPriority': 'none',
            'dependencyStatus': 'none',
            'overrideStatus': 'none',
            'reason': '无可选任务。',
            'nextAction': '当前阶段完成。',
            'currentTask': 'none',
            'currentStatus': 'done',
        }

    sorted_active = sorted(
        active,
        key=lambda t: (
            0 if t.get('kind') == 'real' else 1,
            0 if t.get('isPrimaryTrack') else 1,
            PRIORITY_ORDER.get(t['priority'], 99),
            STATUS_ORDER.get(t['status'], 99),
            -_sort_time_rank(t.get('updatedAt', '')),
        ),
    )
    top = sorted_active[0]

    if not top['dependencySatisfied']:
        return {
            'decisionType': 'wait-dependency',
            'nextTaskId': top['taskId'],
            'selectedPriority': top['priority'],
            'dependencyStatus': 'unsatisfied',
            'overrideStatus': top['override'],
            'reason': '最高优先任务依赖未满足。',
            'nextAction': '先满足依赖任务。',
            'currentTask': top['taskId'],
            'currentStatus': top['status'],
        }

    if top['status'] == 'doing':
        decision = 'continue-current'
        action = '继续执行当前优先任务。'
    elif top['status'] == 'todo':
        decision = 'switch-next'
        action = '切换到下一优先任务。'
    else:
        decision = 'blocked'
        action = '等待阻塞解除。'

    return {
        'decisionType': decision,
        'nextTaskId': top['taskId'],
        'selectedPriority': top['priority'],
        'dependencyStatus': 'satisfied',
        'overrideStatus': top['override'],
        'reason': '按 priority/status/updatedAt 选出最高优先任务。',
        'nextAction': action,
        'currentTask': top['taskId'],
        'currentStatus': top['status'],
    }


def write_next_task_state(output_path: Path, result: dict) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return output_path


def render_next_task_view(result: dict) -> str:
    lines = [
        '# NEXT_TASK',
        '',
        f"- currentTask: {result['currentTask']}",
        f"- currentStatus: {result['currentStatus']}",
        f"- decisionType: {result['decisionType']}",
        f"- nextTaskId: {result['nextTaskId']}",
        f"- selectedPriority: {result['selectedPriority']}",
        f"- dependencyStatus: {result['dependencyStatus']}",
        f"- overrideStatus: {result['overrideStatus']}",
        f"- reason: {result['reason']}",
        f"- nextAction: {result['nextAction']}",
    ]
    return '\n'.join(lines) + '\n'


def write_next_task_view(output_path: Path, result: dict) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_next_task_view(result), encoding='utf-8')
    return output_path

def build_next_task_from_state_dir(state_dir: Path, next_state_path: Path, next_view_path: Path, input_path: Path | None = None) -> dict:
    tasks = load_tasks_from_state_dir(state_dir)
    payload = build_next_task_payload(tasks)
    if input_path is not None:
        input_path.parent.mkdir(parents=True, exist_ok=True)
        input_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result = choose_next_task(tasks)
    write_next_task_state(next_state_path, result)
    write_next_task_view(next_view_path, result)
    return result
