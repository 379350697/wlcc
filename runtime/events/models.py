from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RuntimeEvent:
    event_type: str
    task_id: str
    stage: str
    payload: dict[str, Any] = field(default_factory=dict)
    emitted_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec='seconds'))

    def to_dict(self) -> dict[str, Any]:
        return {
            'event_type': self.event_type,
            'task_id': self.task_id,
            'stage': self.stage,
            'payload': dict(self.payload),
            'emitted_at': self.emitted_at,
        }
