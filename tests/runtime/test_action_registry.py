from runtime.actions.registry import (
    ActionSpec,
    DEFAULT_ACTION_SPEC,
    get_action_meta,
    get_action_spec,
    is_registered_action,
    list_concurrent_safe_actions,
    list_state_modifying_actions,
    normalize_action_name,
)


def test_action_registry_normalizes_names():
    assert normalize_action_name('scripts/render_state_views.py') == 'render_state_views'
    assert normalize_action_name('render_state_views.py') == 'render_state_views'


def test_action_registry_returns_structured_specs():
    spec = get_action_spec('render_state_views')
    assert isinstance(spec, ActionSpec)
    assert spec.read_only is True
    assert spec.concurrent_safe is True
    assert spec.risk_action == 'read'
    assert spec.evidence_policy == 'none'


def test_action_registry_fail_closed_for_unknown_actions():
    spec = get_action_spec('unknown-script')
    assert spec.name == 'unknown-script'
    assert spec.read_only is DEFAULT_ACTION_SPEC.read_only
    assert spec.concurrent_safe is DEFAULT_ACTION_SPEC.concurrent_safe
    assert spec.risk_action == DEFAULT_ACTION_SPEC.risk_action


def test_action_registry_meta_shape_remains_compatible():
    meta = get_action_meta('render_state_views')
    assert meta['read_only'] is True
    assert meta['concurrent_safe'] is True
    assert meta['timeout'] == 30
    assert meta['max_result_chars'] == 10000
    assert meta['risk_action'] == 'read'


def test_action_registry_helpers_cover_existing_actions():
    assert is_registered_action('render_state_views') is True
    assert 'render_state_views' in list_concurrent_safe_actions()
    assert 'run_task_supervision' in list_state_modifying_actions()
