from runtime.common.models import TaskState
from runtime.contracts.task_contract import (
    TaskContract,
    normalize_contract_dict,
    validate_contract_dict,
)


def test_leaf_contract_defaults_are_strict():
    contract = TaskContract()

    assert contract.taskLevel == "leaf"
    assert contract.phase == "analyze"
    assert contract.requiredEvidence == ["state-update"]
    assert contract.allowedPaths == ["."]
    assert contract.maxTurns == 8
    assert contract.maxMinutes == 20


def test_validate_contract_rejects_unknown_phase():
    verdict = validate_contract_dict({"phase": "ship-it"})

    assert verdict.passed is False
    assert "phase" in verdict.reason


def test_leaf_contract_requires_allowed_paths():
    contract = TaskContract(taskLevel="leaf", allowedPaths=[], doneWhen=["state updated"])

    verdict = contract.validate()

    assert verdict.passed is False
    assert "allowedPaths" in verdict.reason


def test_normalize_contract_from_task_state_round_trip():
    task = TaskState(
        taskId="real-contract",
        project="wlcc",
        goal="verify contract persistence",
        status="doing",
        kind="real",
        taskLevel="leaf",
        parentTaskId="",
        phase="analyze",
        doneWhen=["required evidence recorded"],
        requiredEvidence=["state-update"],
        requiredTests=["python3 -m pytest tests/runtime/test_task_contract.py -q"],
        allowedPaths=["runtime/"],
        forbiddenPaths=["secrets/"],
        maxTurns=5,
        maxMinutes=12,
        turnCount=1,
    )

    normalized = normalize_contract_dict(task.to_dict())

    assert normalized["taskLevel"] == "leaf"
    assert normalized["allowedPaths"] == ["runtime/"]
    assert normalized["requiredTests"] == ["python3 -m pytest tests/runtime/test_task_contract.py -q"]
    assert normalized["maxTurns"] == 5
    assert normalized["turnCount"] == 1
