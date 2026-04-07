from runtime.gates.closure_artifacts import evaluate_closure_artifacts


def test_closure_artifacts_reject_missing_final_result():
    task = {"kind": "real"}
    payload = {"evidenceIds": ["gap-check", "status-update"]}

    result = evaluate_closure_artifacts(task, payload)

    assert result["passed"] is False
    assert "final-result" in result["reason"]


def test_closure_artifacts_reject_missing_gap_check():
    task = {"kind": "real"}
    payload = {"evidenceIds": ["final-result", "status-update"]}

    result = evaluate_closure_artifacts(task, payload)

    assert result["passed"] is False
    assert "gap-check" in result["reason"]


def test_closure_artifacts_reject_missing_status_update():
    task = {"kind": "real"}
    payload = {"evidenceIds": ["final-result", "gap-check"]}

    result = evaluate_closure_artifacts(task, payload)

    assert result["passed"] is False
    assert "status-update" in result["reason"]


def test_closure_artifacts_accept_complete_three_piece_payload():
    task = {"kind": "real"}
    payload = {"evidenceIds": ["final-result", "gap-check", "status-update", "state-update"]}

    result = evaluate_closure_artifacts(task, payload)

    assert result["passed"] is True
    assert result["reason"] == "ok"
