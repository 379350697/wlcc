from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FailureVerdict:
    failure_class: str
    decision: str
    next_action: str
    retryable: bool
    requires_human: bool
    source: str
    reason: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'failure_class': self.failure_class,
            'decision': self.decision,
            'next_action': self.next_action,
            'retryable': self.retryable,
            'requires_human': self.requires_human,
            'source': self.source,
            'reason': self.reason,
            'details': dict(self.details),
        }
