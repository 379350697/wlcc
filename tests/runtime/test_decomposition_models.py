from runtime.common.models import TaskState
from runtime.contracts.task_contract import normalize_contract_dict, validate_contract_dict
from runtime.decomposition.models import LeafBundle


def test_mechanized_leaf_fields_round_trip_from_task_state():
    task = TaskState(
        taskId="real-decomposed-leaf",
        project="wlcc",
        goal="prove mechanized leaf persistence",
        status="ready",
        kind="real",
        taskLevel="leaf",
        parentTaskId="task-parent",
        phase="analyze",
        doneWhen=["final-result recorded", "gap-check recorded", "status-update recorded"],
        requiredEvidence=["final-result", "gap-check", "status-update"],
        requiredTests=["python3 -m pytest tests/runtime/test_decomposition_models.py -q"],
        allowedPaths=["runtime/"],
        forbiddenPaths=["secrets/"],
        maxTurns=8,
        maxMinutes=20,
        turnCount=0,
        riskLevel="medium",
        estimatedTurns=4,
        estimatedMinutes=15,
        splitConfidence=0.85,
    )

    normalized = normalize_contract_dict(task.to_dict())

    assert normalized["status"] == "ready"
    assert normalized["parentTaskId"] == "task-parent"
    assert normalized["riskLevel"] == "medium"
    assert normalized["estimatedTurns"] == 4
    assert normalized["estimatedMinutes"] == 15
    assert normalized["splitConfidence"] == 0.85


def test_mechanized_leaf_status_accepts_ready_and_rejects_unknown():
    ready_verdict = validate_contract_dict(
        {
            "taskLevel": "leaf",
            "status": "ready",
            "allowedPaths": ["runtime/"],
            "doneWhen": ["final-result recorded"],
            "requiredEvidence": ["final-result"],
        }
    )
    invalid_verdict = validate_contract_dict({"taskLevel": "leaf", "status": "ship-next", "allowedPaths": ["runtime/"]})

    assert ready_verdict.passed is True
    assert invalid_verdict.passed is False
    assert "status" in invalid_verdict.reason


def test_leaf_bundle_maps_to_wlcc_contract_shape():
    leaf = LeafBundle(
        taskId="leaf-1",
        parentTaskId="task-1",
        goal="implement bounded leaf",
        allowedPaths=["runtime/"],
        doneWhen=["final-result recorded"],
        requiredEvidence=["final-result"],
        requiredTests=["python3 -m pytest tests/runtime/test_decomposition_models.py -q"],
        status="draft",
        riskLevel="low",
        estimatedTurns=3,
        estimatedMinutes=10,
        splitConfidence=0.9,
    )

    contract = leaf.to_task_contract()

    assert contract["taskLevel"] == "leaf"
    assert contract["status"] == "draft"
    assert contract["parentTaskId"] == "task-1"
    assert contract["allowedPaths"] == ["runtime/"]
    assert contract["riskLevel"] == "low"
    assert contract["estimatedTurns"] == 3
    assert contract["estimatedMinutes"] == 10
    assert contract["splitConfidence"] == 0.9


def test_draft_leaf_bundle_is_not_schedulable():
    draft_leaf = LeafBundle(
        taskId="leaf-draft",
        parentTaskId="task-1",
        goal="stay draft until promoted",
        allowedPaths=["runtime/"],
        doneWhen=["gap-check recorded"],
        requiredEvidence=["gap-check"],
        status="draft",
    )
    ready_leaf = LeafBundle(
        taskId="leaf-ready",
        parentTaskId="task-1",
        goal="ready leaf can enter wlcc",
        allowedPaths=["runtime/"],
        doneWhen=["status-update recorded"],
        requiredEvidence=["status-update"],
        status="ready",
    )

    assert draft_leaf.is_schedulable is False
    assert ready_leaf.is_schedulable is True
