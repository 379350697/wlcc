from runtime.scheduling.next_task import choose_next_task


def test_choose_next_task_stays_on_open_leaf():
    tasks = [
        {
            "taskId": "0.1",
            "status": "doing",
            "taskLevel": "leaf",
            "phase": "implement",
            "priority": "P0",
            "dependencies": [],
            "override": "none",
            "kind": "real",
            "executionMode": "live",
            "eligibleForScheduling": True,
            "isPrimaryTrack": True,
            "updatedAt": "2026-04-07T10:00:00",
        },
        {
            "taskId": "0.2",
            "status": "todo",
            "taskLevel": "leaf",
            "phase": "analyze",
            "priority": "P0",
            "dependencies": [],
            "override": "none",
            "kind": "real",
            "executionMode": "live",
            "eligibleForScheduling": True,
            "isPrimaryTrack": True,
            "updatedAt": "2026-04-07T10:01:00",
        },
    ]

    result = choose_next_task(tasks)

    assert result["nextTaskId"] == "0.1"
    assert result["decisionType"] == "continue-current-leaf"


def test_choose_next_task_keeps_blocked_leaf_in_focus():
    tasks = [
        {
            "taskId": "0.1",
            "status": "blocked",
            "taskLevel": "leaf",
            "phase": "implement",
            "priority": "P0",
            "dependencies": [],
            "override": "none",
            "kind": "real",
            "executionMode": "live",
            "eligibleForScheduling": True,
            "isPrimaryTrack": True,
            "updatedAt": "2026-04-07T10:00:00",
        },
        {
            "taskId": "0.2",
            "status": "todo",
            "taskLevel": "leaf",
            "phase": "analyze",
            "priority": "P0",
            "dependencies": [],
            "override": "none",
            "kind": "real",
            "executionMode": "live",
            "eligibleForScheduling": True,
            "isPrimaryTrack": True,
            "updatedAt": "2026-04-07T10:01:00",
        },
    ]

    result = choose_next_task(tasks)

    assert result["nextTaskId"] == "0.1"
    assert result["decisionType"] == "blocked-current-leaf"


def test_choose_next_task_does_not_jump_to_parent_task_while_leaf_open():
    tasks = [
        {
            "taskId": "0",
            "status": "todo",
            "taskLevel": "task",
            "phase": "analyze",
            "priority": "P0",
            "dependencies": [],
            "override": "none",
            "kind": "real",
            "executionMode": "live",
            "eligibleForScheduling": True,
            "isPrimaryTrack": True,
            "updatedAt": "2026-04-07T10:02:00",
        },
        {
            "taskId": "0.1",
            "status": "doing",
            "taskLevel": "leaf",
            "phase": "implement",
            "priority": "P0",
            "dependencies": [],
            "override": "none",
            "kind": "real",
            "executionMode": "live",
            "eligibleForScheduling": True,
            "isPrimaryTrack": True,
            "updatedAt": "2026-04-07T10:00:00",
        },
    ]

    result = choose_next_task(tasks)

    assert result["nextTaskId"] == "0.1"
    assert result["decisionType"] == "continue-current-leaf"
