from pathlib import Path

from runtime.harness.registry import DEFAULTS, get_meta, is_registered, list_concurrent_safe
from runtime.harness.task_harness import TaskHarness, TrackedStep


def test_registry_lookup_handles_suffix_and_paths():
    assert get_meta('render_state_views.py')['read_only'] is True
    assert get_meta('scripts/render_state_views')['read_only'] is True
    assert is_registered('render_state_views') is True
    assert is_registered('nonexistent_script') is False


def test_registry_unknown_is_fail_closed():
    meta = get_meta('unknown-script')
    assert meta['read_only'] is DEFAULTS['read_only']
    assert meta['concurrent_safe'] is DEFAULTS['concurrent_safe']


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
