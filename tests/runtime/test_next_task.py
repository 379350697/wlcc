from pathlib import Path

from runtime.scheduling.next_task import (
    build_next_task_from_state_dir,
    choose_next_task,
    parse_time,
    render_next_task_view,
)


def test_parse_time_supports_legacy_and_iso():
    legacy = parse_time('2026-04-06 21:17')
    iso = parse_time('2026-04-06T21:17:52')

    assert legacy.year == 2026
    assert iso.second == 52


def test_choose_next_task_accepts_iso_updated_at():
    tasks = [
        {
            'taskId': 'real-task',
            'status': 'doing',
            'priority': 'P0',
            'dependencies': [],
            'override': 'none',
            'kind': 'real',
            'taskLevel': 'leaf',
            'phase': 'implement',
            'executionMode': 'live',
            'eligibleForScheduling': True,
            'isPrimaryTrack': True,
            'updatedAt': '2026-04-06T21:17:52',
        },
        {
            'taskId': 'sample-task',
            'status': 'todo',
            'priority': 'P1',
            'dependencies': [],
            'override': 'none',
            'kind': 'sample',
            'taskLevel': 'leaf',
            'phase': 'analyze',
            'executionMode': 'sample-only',
            'eligibleForScheduling': False,
            'isPrimaryTrack': False,
            'updatedAt': '2026-04-06 21:10',
        },
    ]

    result = choose_next_task(tasks)

    assert result['nextTaskId'] == 'real-task'
    assert result['decisionType'] == 'continue-current-leaf'


def test_build_next_task_from_state_dir_writes_state_and_view(tmp_path: Path):
    state_dir = tmp_path / '.agent' / 'state' / 'tasks'
    next_state = tmp_path / '.agent' / 'state' / 'next-task.json'
    next_view = tmp_path / '.agent' / 'NEXT_TASK.md'
    input_file = tmp_path / '.agent' / 'state' / 'next-task-input.json'
    state_dir.mkdir(parents=True, exist_ok=True)

    (state_dir / 'task-a.json').write_text(
        '\n'.join([
            '{',
            '  "taskId": "task-a",',
            '  "status": "doing",',
            '  "priority": "P0",',
            '  "dependencies": [],',
            '  "override": "none",',
            '  "kind": "real",',
            '  "taskLevel": "leaf",',
            '  "phase": "implement",',
            '  "executionMode": "live",',
            '  "eligibleForScheduling": true,',
            '  "isPrimaryTrack": true,',
            '  "updatedAt": "2026-04-06T21:17:52"',
            '}',
        ]) + '\n',
        encoding='utf-8',
    )

    result = build_next_task_from_state_dir(state_dir, next_state, next_view, input_file)

    assert result['nextTaskId'] == 'task-a'
    assert next_state.exists()
    assert next_view.exists()
    assert input_file.exists()
    assert '"nextTaskId": "task-a"' in next_state.read_text(encoding='utf-8')
    assert '- nextTaskId: task-a' in render_next_task_view(result) or '- nextTaskId: task-a' in next_view.read_text(encoding='utf-8')
