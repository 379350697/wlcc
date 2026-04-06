from __future__ import annotations

from typing import Any

from .classifier import classify_failure
from .models import FailureVerdict


FAILURE_DECISIONS = {
    'none': ('accept', False, False),
    'content_weak': ('retry_same_step', True, False),
    'evidence_insufficient': ('degrade_continue', True, False),
    'risk_blocked': ('freeze_task', False, True),
    'manual_intervention_required': ('escalate_human', False, True),
    'resume_required': ('prepare_resume', False, True),
    'heartbeat_stale': ('prepare_resume', False, True),
    'state_inconsistent': ('freeze_task', False, True),
}


def build_failure_verdict(failure_class: str, source: str, reason: str, details: dict[str, Any] | None = None) -> FailureVerdict:
    decision, retryable, requires_human = FAILURE_DECISIONS.get(
        failure_class,
        ('freeze_task', False, True),
    )
    return FailureVerdict(
        failure_class=failure_class,
        decision=decision,
        next_action=decision,
        retryable=retryable,
        requires_human=requires_human,
        source=source,
        reason=reason,
        details=details or {},
    )


def route_failure(source: str, verdict: dict[str, Any]) -> FailureVerdict:
    failure_class = classify_failure(source, verdict)
    reason = verdict.get('reason', 'unknown')
    return build_failure_verdict(failure_class, source, reason, verdict)
