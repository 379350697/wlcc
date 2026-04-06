from __future__ import annotations

from typing import Any


CONTENT_WEAK_REASONS = {
    'empty-latest-result',
    'latest_result_length',
    'latest_result_phrase',
    'next_step_length',
    'next_step_phrase',
    'circular',
}


def classify_progress_failure(verdict: dict[str, Any]) -> str:
    if verdict.get('passed', True):
        return 'none'
    violations = verdict.get('violations', [])
    for item in violations:
        if item.get('check') in CONTENT_WEAK_REASONS:
            return 'content_weak'
    return 'state_inconsistent'


def classify_delivery_failure(verdict: dict[str, Any]) -> str:
    if verdict.get('passed', True):
        return 'none'
    if verdict.get('collected', 0) < verdict.get('required', 1):
        return 'evidence_insufficient'
    return 'state_inconsistent'


def classify_risk_failure(verdict: dict[str, Any]) -> str:
    decision = verdict.get('decision')
    if decision == 'reject':
        return 'risk_blocked'
    if decision == 'require-confirmation':
        return 'manual_intervention_required'
    return 'none'


def classify_supervision_failure(verdict: dict[str, Any]) -> str:
    if verdict.get('allowed', True):
        return 'none'
    reason = verdict.get('reason', '')
    checks = set(verdict.get('checks', []))
    if reason == 'interruption-detected' or 'interruption-detected' in checks:
        return 'resume_required'
    if reason == 'stale-heartbeat' or 'stale-heartbeat' in checks:
        return 'heartbeat_stale'
    if reason == 'empty-latest-result' or 'empty-latest-result' in checks:
        return 'content_weak'
    return 'state_inconsistent'


def classify_failure(source: str, verdict: dict[str, Any]) -> str:
    if source == 'progress':
        return classify_progress_failure(verdict)
    if source == 'delivery':
        return classify_delivery_failure(verdict)
    if source == 'risk':
        return classify_risk_failure(verdict)
    if source == 'supervision':
        return classify_supervision_failure(verdict)
    return 'state_inconsistent'
