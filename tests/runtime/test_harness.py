from pathlib import Path

from runtime.actions.registry import get_action_meta
from runtime.events.bus import clear_runtime_event_bus, get_runtime_events, subscribe_runtime_events
from runtime.harness.registry import DEFAULTS, get_meta, is_registered, list_concurrent_safe
from runtime.harness.task_harness import TaskHarness, TrackedStep


def setup_function():
    clear_runtime_event_bus()


def teardown_function():
    clear_runtime_event_bus()


def test_registry_lookup_handles_suffix_and_paths():
    assert get_meta('render_state_views.py')['read_only'] is True
    assert get_meta('scripts/render_state_views')['read_only'] is True
    assert is_registered('render_state_views') is True
    assert is_registered('nonexistent_script') is False


def test_registry_unknown_is_fail_closed():
    meta = get_meta('unknown-script')
    assert meta['read_only'] is DEFAULTS['read_only']
    assert meta['concurrent_safe'] is DEFAULTS['concurrent_safe']
    assert meta['risk_action'] == DEFAULTS['risk_action']


def test_action_registry_bridge_exposes_same_metadata():
    meta = get_action_meta('render_state_views')
    assert meta['name'] == 'render_state_views'
    assert meta['read_only'] is True
    assert meta['concurrent_safe'] is True
    assert meta['evidence_policy'] == 'none'


def test_harness_partition_groups_read_only_steps(repo_root=Path('.').resolve()):
    harness = TaskHarness(task_id='test', project_root=repo_root, enable_consistency_check=False)
    harness.add('render_state_views', ['--project-root', str(repo_root), '--task-id', 'test'])
    harness.add('build_next_task_from_state', [])
    harness.add('run_task_supervision', ['--task-id', 'test', '--trigger', 'on_task_changed'])
    groups = harness._partition_steps()
    assert groups[0]['type'] == 'concurrent'
    assert len(groups[0]['steps']) == 2
    assert groups[1]['type'] == 'serial'


def test_tracked_step_cmd_points_to_scripts_dir():
    step = TrackedStep('render_state_views', ['--task-id', 'x'], get_meta('render_state_views'))
    assert 'scripts/render_state_views.py' in ' '.join(step.cmd)


def test_concurrent_list_not_empty():
    assert 'render_state_views' in list_concurrent_safe()


def test_task_harness_emits_step_events(tmp_path: Path, monkeypatch):
    seen = []
    subscribe_runtime_events(lambda event: seen.append(event.event_type))

    harness = TaskHarness(task_id='task-evt', project_root=tmp_path, enable_consistency_check=False)
    harness.add('run_task_supervision', ['--task-id', 'task-evt', '--trigger', 'on_interval'])

    def fake_execute(cmd, timeout, max_chars, cwd):
        return {
            'state': 'completed',
            'output': 'ok',
            'error': None,
            'exit_code': 0,
            'duration_ms': 1,
            'truncated': False,
        }

    monkeypatch.setattr('runtime.harness.task_harness._execute_step_standalone', fake_execute)

    result = harness.execute_all()

    assert result.success is True
    assert 'task_harness.step_queued' in seen
    assert 'task_harness.step_started' in seen
    assert 'task_harness.step_completed' in seen
    assert any(event.event_type == 'task_harness.step_completed' for event in get_runtime_events())
