from __future__ import annotations

from collections import deque
from dataclasses import replace
from typing import Callable

from .models import RuntimeEvent


Subscriber = Callable[[RuntimeEvent], None]
MAX_EVENT_HISTORY = 256


class RuntimeEventBus:
    def __init__(self):
        self._subscribers: list[Subscriber] = []
        self._events: deque[RuntimeEvent] = deque(maxlen=MAX_EVENT_HISTORY)

    def subscribe(self, subscriber: Subscriber) -> Callable[[], None]:
        self._subscribers.append(subscriber)

        def unsubscribe() -> None:
            try:
                self._subscribers.remove(subscriber)
            except ValueError:
                pass

        return unsubscribe

    def publish(self, event: RuntimeEvent) -> RuntimeEvent:
        stored = replace(event, payload=dict(event.payload))
        self._events.append(stored)
        for subscriber in list(self._subscribers):
            try:
                subscriber(stored)
            except Exception:
                continue
        return stored

    def clear(self) -> None:
        self._subscribers.clear()
        self._events.clear()

    def clear_events(self) -> None:
        self._events.clear()

    def get_events(self) -> list[RuntimeEvent]:
        return list(self._events)


EVENT_BUS = RuntimeEventBus()


def subscribe_runtime_events(subscriber: Subscriber) -> Callable[[], None]:
    return EVENT_BUS.subscribe(subscriber)


def publish_runtime_event(event_type: str, task_id: str, stage: str, payload: dict | None = None) -> RuntimeEvent:
    event = RuntimeEvent(
        event_type=event_type,
        task_id=task_id,
        stage=stage,
        payload=payload or {},
    )
    return EVENT_BUS.publish(event)


def clear_runtime_event_bus() -> None:
    EVENT_BUS.clear()


def get_runtime_events() -> list[RuntimeEvent]:
    return EVENT_BUS.get_events()
