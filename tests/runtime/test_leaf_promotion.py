from runtime.decomposition.models import LeafBundle
from runtime.decomposition.promotion import promote_leaf_bundle


def test_promote_leaf_bundle_promotes_simple_leaf_to_ready():
    leaf = LeafBundle(
        taskId="leaf-promote",
        parentTaskId="task-1",
        goal="promote a bounded leaf",
        allowedPaths=["runtime/"],
        doneWhen=["final-result recorded", "gap-check recorded", "status-update recorded"],
        requiredEvidence=["final-result", "gap-check", "status-update"],
        requiredTests=["python3 -m pytest tests/runtime/test_leaf_promotion.py -q"],
        status="draft",
        estimatedTurns=3,
        estimatedMinutes=12,
        splitConfidence=0.92,
    )

    result = promote_leaf_bundle(leaf)

    assert result.promoted is True
    assert result.leaf.status == "ready"
    assert result.reason == "ok"


def test_promote_leaf_bundle_keeps_ambiguous_leaf_in_draft():
    leaf = LeafBundle(
        taskId="leaf-stays-draft",
        parentTaskId="task-1",
        goal="补齐机制层剩余问题",
        allowedPaths=[],
        doneWhen=[],
        requiredEvidence=[],
        status="draft",
        estimatedTurns=9,
        estimatedMinutes=40,
        splitConfidence=0.3,
    )

    result = promote_leaf_bundle(leaf)

    assert result.promoted is False
    assert result.leaf.status == "draft"
    assert result.reason != "ok"


def test_promote_leaf_bundle_keeps_unbounded_leaf_in_draft():
    leaf = LeafBundle(
        taskId="leaf-unbounded",
        parentTaskId="task-1",
        goal="实现一个看起来明确但范围过宽的 leaf",
        allowedPaths=["."],
        doneWhen=["final-result recorded", "gap-check recorded", "status-update recorded"],
        requiredEvidence=["final-result", "gap-check", "status-update"],
        requiredTests=["python3 -m pytest tests/runtime/test_leaf_promotion.py -q"],
        status="draft",
        estimatedTurns=3,
        estimatedMinutes=12,
        splitConfidence=0.92,
    )

    result = promote_leaf_bundle(leaf)

    assert result.promoted is False
    assert result.leaf.status == "draft"
    assert "allowedPaths" in result.reason


def test_promote_leaf_bundle_requires_known_tests_or_explicit_no_test_clause():
    leaf = LeafBundle(
        taskId="leaf-missing-tests",
        parentTaskId="task-1",
        goal="实现一个没有测试声明的 leaf",
        allowedPaths=["runtime/"],
        doneWhen=["final-result recorded", "gap-check recorded", "status-update recorded"],
        requiredEvidence=["final-result", "gap-check", "status-update"],
        requiredTests=[],
        status="draft",
        estimatedTurns=2,
        estimatedMinutes=10,
        splitConfidence=0.9,
    )

    result = promote_leaf_bundle(leaf)

    assert result.promoted is False
    assert result.leaf.status == "draft"
    assert "requiredTests" in result.reason
