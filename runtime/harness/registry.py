"""Compatibility wrapper for executable script metadata."""

from runtime.actions.registry import (
    ACTION_SPECS,
    DEFAULT_ACTION_SPEC,
    get_action_meta,
    get_action_spec,
    is_registered_action,
    list_concurrent_safe_actions,
    list_state_modifying_actions,
    normalize_action_name,
)

DEFAULTS = {
    'read_only': DEFAULT_ACTION_SPEC.read_only,
    'concurrent_safe': DEFAULT_ACTION_SPEC.concurrent_safe,
    'timeout': DEFAULT_ACTION_SPEC.timeout_s,
    'risk_action': DEFAULT_ACTION_SPEC.risk_action,
    'max_result_chars': DEFAULT_ACTION_SPEC.max_output_chars,
    'needs_validation': DEFAULT_ACTION_SPEC.needs_validation,
    'can_modify_state': DEFAULT_ACTION_SPEC.can_modify_state,
}

REGISTRY = {
    name: get_action_meta(name)
    for name in ACTION_SPECS
}


def _normalize_name(script_name: str) -> str:
    return normalize_action_name(script_name)


def get_meta(script_name: str) -> dict:
    return get_action_meta(script_name)


def is_registered(script_name: str) -> bool:
    return is_registered_action(script_name)


def list_concurrent_safe() -> list[str]:
    return list_concurrent_safe_actions()


def list_state_modifiers() -> list[str]:
    return list_state_modifying_actions()
