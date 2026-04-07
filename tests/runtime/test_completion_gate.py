from runtime.gates.completion import evaluate_completion_gate


def test_completion_gate_rejects_missing_required_evidence():
    task = {
        "kind": "real",
        "phase": "verify",
        "requiredEvidence": ["state-update"],
        "requiredTests": [],
        "allowedPaths": ["runtime/"],
    }
    payload = {
        "evidenceIds": ["final-result", "gap-check", "status-update"],
        "testsRun": [],
        "changedFiles": ["runtime/common/models.py"],
    }

    result = evaluate_completion_gate(task, payload)

    assert result["passed"] is False
    assert "required evidence" in result["reason"]


def test_completion_gate_rejects_missing_tests():
    task = {
        "kind": "real",
        "phase": "verify",
        "requiredEvidence": ["state-update"],
        "requiredTests": ["python3 -m pytest tests/runtime/test_task_contract.py -q"],
        "allowedPaths": ["runtime/"],
    }
    payload = {
        "evidenceIds": ["state-update", "final-result", "gap-check", "status-update"],
        "testsRun": [],
        "changedFiles": ["runtime/common/models.py"],
    }

    result = evaluate_completion_gate(task, payload)

    assert result["passed"] is False
    assert "required tests" in result["reason"]


def test_completion_gate_rejects_non_verify_phase():
    task = {
        "kind": "real",
        "phase": "implement",
        "requiredEvidence": ["state-update"],
        "requiredTests": [],
        "allowedPaths": ["runtime/"],
    }
    payload = {
        "evidenceIds": ["state-update"],
        "testsRun": [],
        "changedFiles": ["runtime/common/models.py"],
    }

    result = evaluate_completion_gate(task, payload)

    assert result["passed"] is False
    assert "verify" in result["reason"]


def test_completion_gate_rejects_changed_file_outside_allowed_paths():
    task = {
        "kind": "real",
        "phase": "verify",
        "requiredEvidence": ["state-update"],
        "requiredTests": [],
        "allowedPaths": ["runtime/"],
    }
    payload = {
        "evidenceIds": ["state-update", "final-result", "gap-check", "status-update"],
        "testsRun": [],
        "changedFiles": ["scripts/close_task_runtime.py"],
    }

    result = evaluate_completion_gate(task, payload)

    assert result["passed"] is False
    assert "allowed paths" in result["reason"]


def test_completion_gate_accepts_valid_payload():
    task = {
        "kind": "real",
        "phase": "verify",
        "requiredEvidence": ["state-update"],
        "requiredTests": ["python3 -m pytest tests/runtime/test_task_contract.py -q"],
        "allowedPaths": ["runtime/"],
    }
    payload = {
        "evidenceIds": ["state-update", "final-result", "gap-check", "status-update"],
        "testsRun": ["python3 -m pytest tests/runtime/test_task_contract.py -q"],
        "changedFiles": ["runtime/common/models.py"],
    }

    result = evaluate_completion_gate(task, payload)

    assert result["passed"] is True
    assert result["reason"] == "ok"
