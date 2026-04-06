from runtime.events.bus import (
    MAX_EVENT_HISTORY,
    clear_runtime_event_bus,
    get_runtime_events,
    publish_runtime_event,
    subscribe_runtime_events,
)


def setup_function():
    clear_runtime_event_bus()


def teardown_function():
    clear_runtime_event_bus()


def test_event_bus_publishes_synchronously_and_preserves_payload():
    seen = []

    def subscriber(event):
        seen.append(event)

    unsubscribe = subscribe_runtime_events(subscriber)
    event = publish_runtime_event('task.test', 'task-1', 'stage-1', {'answer': 42})
    unsubscribe()

    assert seen == [event]
    assert event.event_type == 'task.test'
    assert event.task_id == 'task-1'
    assert event.stage == 'stage-1'
    assert event.payload == {'answer': 42}
    assert get_runtime_events() == [event]


def test_event_bus_preserves_order_across_multiple_subscribers():
    seen_a = []
    seen_b = []

    subscribe_runtime_events(lambda event: seen_a.append(event.event_type))
    subscribe_runtime_events(lambda event: seen_b.append(event.task_id))

    publish_runtime_event('one', 'task-a', 'stage-a')
    publish_runtime_event('two', 'task-b', 'stage-b')

    assert seen_a == ['one', 'two']
    assert seen_b == ['task-a', 'task-b']


def test_event_bus_is_noop_without_subscribers():
    event = publish_runtime_event('noop', 'task-z', 'stage-z')
    assert event.event_type == 'noop'
    assert get_runtime_events() == [event]


def test_event_bus_caps_history_without_dropping_delivery():
    seen = []

    subscribe_runtime_events(lambda event: seen.append(event.event_type))

    total = MAX_EVENT_HISTORY + 7
    for index in range(total):
        publish_runtime_event(f'event-{index}', f'task-{index}', 'stage')

    events = get_runtime_events()

    assert len(seen) == total
    assert len(events) == MAX_EVENT_HISTORY
    assert [event.event_type for event in events] == [f'event-{index}' for index in range(7, total)]
