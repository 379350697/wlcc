"""Runtime registry for executable script metadata."""

DEFAULTS = {
    'read_only': False,
    'concurrent_safe': False,
    'timeout': 15,
    'risk_action': 'write-state',
    'max_result_chars': 5000,
    'needs_validation': True,
    'can_modify_state': True,
}

REGISTRY = {
    'render_state_views': {'read_only': True, 'concurrent_safe': True, 'timeout': 30, 'risk_action': 'read', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': False},
    'build_next_task_from_state': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'build_heartbeat_summary': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'build_resume_state': {'read_only': True, 'concurrent_safe': True, 'timeout': 30, 'risk_action': 'read', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': False},
    'build_observability_dashboard': {'read_only': True, 'concurrent_safe': True, 'timeout': 30, 'risk_action': 'read', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': False},
    'build_audit_summary': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'build_real_task_audit_summary': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'read_project_context': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': False},
    'retrieve_context': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': False},
    'decide_next_task_v2': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'update_task_lifecycle': {'read_only': False, 'concurrent_safe': False, 'timeout': 15, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': True, 'can_modify_state': True},
    'update_task_state': {'read_only': False, 'concurrent_safe': False, 'timeout': 15, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': True, 'can_modify_state': True},
    'write_state_store': {'read_only': False, 'concurrent_safe': False, 'timeout': 15, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': True, 'can_modify_state': True},
    'run_task_supervision': {'read_only': False, 'concurrent_safe': False, 'timeout': 30, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': True},
    'emit_heartbeat': {'read_only': False, 'concurrent_safe': False, 'timeout': 15, 'risk_action': 'write-state', 'max_result_chars': 3000, 'needs_validation': False, 'can_modify_state': True},
    'write_handoff_state': {'read_only': False, 'concurrent_safe': False, 'timeout': 15, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': True},
    'ingest_real_task': {'read_only': False, 'concurrent_safe': False, 'timeout': 30, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': True, 'can_modify_state': True},
    'close_task_runtime': {'read_only': False, 'concurrent_safe': False, 'timeout': 30, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': True, 'can_modify_state': True},
    'progress_task_runtime': {'read_only': False, 'concurrent_safe': False, 'timeout': 60, 'risk_action': 'write-state', 'max_result_chars': 5000, 'needs_validation': True, 'can_modify_state': True},
    'safe_write': {'read_only': False, 'concurrent_safe': False, 'timeout': 10, 'risk_action': 'write-doc', 'max_result_chars': 3000, 'needs_validation': False, 'can_modify_state': False},
    'log_event': {'read_only': False, 'concurrent_safe': True, 'timeout': 5, 'risk_action': 'write-doc', 'max_result_chars': 1000, 'needs_validation': False, 'can_modify_state': False},
    'check_delivery_completeness': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'check_state_view_consistency': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'check_risk_level': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 3000, 'needs_validation': False, 'can_modify_state': False},
    'check_risk_policy_consistency': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'check_next_task_consistency': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'check_retrieval_priority': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'system_healthcheck': {'read_only': True, 'concurrent_safe': True, 'timeout': 30, 'risk_action': 'read', 'max_result_chars': 5000, 'needs_validation': False, 'can_modify_state': False},
    'delivery_gate': {'read_only': True, 'concurrent_safe': True, 'timeout': 15, 'risk_action': 'read', 'max_result_chars': 3000, 'needs_validation': False, 'can_modify_state': False},
    'progress_reply_gate': {'read_only': True, 'concurrent_safe': True, 'timeout': 5, 'risk_action': 'read', 'max_result_chars': 2000, 'needs_validation': False, 'can_modify_state': False},
    'resume_task': {'read_only': False, 'concurrent_safe': False, 'timeout': 30, 'risk_action': 'write-state', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': True},
    'resume_real_task': {'read_only': False, 'concurrent_safe': False, 'timeout': 30, 'risk_action': 'write-state', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': True},
    'resume_many_tasks': {'read_only': False, 'concurrent_safe': False, 'timeout': 60, 'risk_action': 'write-state', 'max_result_chars': 10000, 'needs_validation': False, 'can_modify_state': True},
    'evaluate_failure_control': {'read_only': False, 'concurrent_safe': False, 'timeout': 10, 'risk_action': 'write-state', 'max_result_chars': 3000, 'needs_validation': False, 'can_modify_state': True},
    'evaluate_risk_policy': {'read_only': True, 'concurrent_safe': True, 'timeout': 10, 'risk_action': 'read', 'max_result_chars': 3000, 'needs_validation': False, 'can_modify_state': False},
    'evaluate_retry_reorder': {'read_only': False, 'concurrent_safe': False, 'timeout': 10, 'risk_action': 'write-state', 'max_result_chars': 3000, 'needs_validation': False, 'can_modify_state': True},
}


def _normalize_name(script_name: str) -> str:
    return script_name.replace('.py', '').split('/')[-1].split('\\')[-1]


def get_meta(script_name: str) -> dict:
    name = _normalize_name(script_name)
    entry = REGISTRY.get(name, {})
    return {**DEFAULTS, 'name': name, **entry}


def is_registered(script_name: str) -> bool:
    return _normalize_name(script_name) in REGISTRY


def list_concurrent_safe() -> list[str]:
    return [name for name, meta in REGISTRY.items() if meta.get('read_only', False) and meta.get('concurrent_safe', False)]


def list_state_modifiers() -> list[str]:
    return [name for name, meta in REGISTRY.items() if meta.get('can_modify_state', DEFAULTS['can_modify_state'])]
