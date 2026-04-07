from runtime.decomposition.judge import judge_leaf_bundle
from runtime.decomposition.models import LeafBundle


def test_leaf_judge_accepts_simple_bounded_leaf():
    leaf = LeafBundle(
        taskId="leaf-ok",
        parentTaskId="task-1",
        goal="add bounded mechanized execution field",
        allowedPaths=["runtime/"],
        doneWhen=["final-result recorded", "gap-check recorded", "status-update recorded"],
        requiredEvidence=["final-result", "gap-check", "status-update"],
        requiredTests=["python3 -m pytest tests/runtime/test_leaf_judge.py -q"],
        estimatedTurns=4,
        estimatedMinutes=15,
    )

    verdict = judge_leaf_bundle(leaf)

    assert verdict.passed is True
    assert verdict.reason == "ok"


def test_leaf_judge_rejects_vague_bundled_work():
    leaf = LeafBundle(
        taskId="leaf-bad",
        parentTaskId="task-1",
        goal="顺便补齐剩余问题并推进到下一阶段",
        allowedPaths=["runtime/", "scripts/"],
        doneWhen=["somehow done"],
        requiredEvidence=["final-result"],
        estimatedTurns=10,
        estimatedMinutes=45,
    )

    verdict = judge_leaf_bundle(leaf)

    assert verdict.passed is False
    assert verdict.violations
    assert any("bundled" in item or "budget" in item or "goal" in item for item in verdict.violations)
