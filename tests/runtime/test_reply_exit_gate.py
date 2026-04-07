from runtime.reply.exit_gate import evaluate_reply_exit_gate


def test_reply_exit_gate_rejects_final_reply_for_open_leaf():
    task = {
        "taskId": "leaf-open",
        "kind": "real",
        "taskLevel": "leaf",
        "status": "running",
        "lifecycle": "running",
        "phase": "implement",
        "requiredEvidence": ["final-result", "gap-check", "status-update"],
        "evidenceIds": ["final-result", "gap-check", "status-update"],
    }

    result = evaluate_reply_exit_gate(
        task=task,
        flow=None,
        payload={"replyKind": "final"},
    )

    assert result["allowed"] is False
    assert result["decision"] == "reject-open-leaf"
    assert "open leaf" in result["reason"]


def test_reply_exit_gate_allows_blocked_reply_when_blocker_is_structured():
    task = {
        "taskId": "leaf-blocked",
        "kind": "real",
        "taskLevel": "leaf",
        "status": "blocked",
        "lifecycle": "blocked",
        "phase": "implement",
        "blocker": "need API key to continue",
    }
    flow = {
        "taskFlowId": "flow-1",
        "status": "blocked",
    }

    result = evaluate_reply_exit_gate(
        task=task,
        flow=flow,
        payload={
            "replyKind": "blocked",
            "structured": True,
            "requestedInput": "Provide the missing API key for the current flow.",
        },
    )

    assert result["allowed"] is True
    assert result["decision"] == "allow-blocked-reply"


def test_reply_exit_gate_allows_final_reply_for_closed_leaf_with_closure_artifacts():
    task = {
        "taskId": "leaf-closed",
        "kind": "real",
        "taskLevel": "leaf",
        "status": "closed",
        "lifecycle": "archived",
        "phase": "done",
        "requiredEvidence": ["final-result", "gap-check", "status-update"],
        "evidenceIds": ["final-result", "gap-check", "status-update"],
        "finalReplyEligible": True,
    }
    flow = {
        "taskFlowId": "flow-1",
        "status": "completed",
    }

    result = evaluate_reply_exit_gate(
        task=task,
        flow=flow,
        payload={"replyKind": "final"},
    )

    assert result["allowed"] is True
    assert result["decision"] == "allow-final-reply"


def test_reply_exit_gate_rejects_final_reply_without_closure_truth_even_if_flag_set():
    task = {
        "taskId": "leaf-closed-missing-artifacts",
        "kind": "real",
        "taskLevel": "leaf",
        "status": "closed",
        "lifecycle": "archived",
        "phase": "done",
        "requiredEvidence": ["final-result", "gap-check", "status-update"],
        "evidenceIds": ["final-result"],
        "finalReplyEligible": True,
    }

    result = evaluate_reply_exit_gate(
        task=task,
        flow={"taskFlowId": "flow-1", "status": "completed"},
        payload={"replyKind": "final"},
    )

    assert result["allowed"] is False
    assert result["decision"] == "reject-open-leaf"


def test_reply_exit_gate_allows_only_structured_status_reply_for_open_leaf():
    task = {
        "taskId": "leaf-open-status",
        "kind": "real",
        "taskLevel": "leaf",
        "status": "verify",
        "lifecycle": "verify",
        "phase": "verify",
        "evidenceIds": ["final-result"],
    }
    flow = {
        "taskFlowId": "flow-1",
        "status": "active",
    }

    accepted = evaluate_reply_exit_gate(
        task=task,
        flow=flow,
        payload={"replyKind": "status", "structured": True},
    )
    rejected = evaluate_reply_exit_gate(
        task=task,
        flow=flow,
        payload={"replyKind": "status", "structured": False},
    )

    assert accepted["allowed"] is True
    assert accepted["decision"] == "allow-status-reply"
    assert rejected["allowed"] is False
    assert rejected["decision"] == "reject-open-leaf"
