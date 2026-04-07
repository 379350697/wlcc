from __future__ import annotations

from dataclasses import dataclass, field

from .models import LeafBundle


BUNDLED_WORK_PHRASES = (
    "顺便",
    "同时",
    "顺手",
    "以及其他",
    "以及相关",
    "其他相关",
    "剩余",
    "补齐剩余问题",
    "推进到下一阶段",
    "完成相关工作",
)
MAX_ESTIMATED_TURNS = 8
MAX_ESTIMATED_MINUTES = 30


def _has_explicit_no_test_clause(done_when: list[str]) -> bool:
    for item in done_when:
        lowered = item.strip().lower()
        if "无需测试" in item or "免测" in item or "no test" in lowered or "no-test" in lowered:
            return True
    return False


@dataclass
class LeafJudgeVerdict:
    passed: bool
    reason: str = "ok"
    violations: list[str] = field(default_factory=list)


def judge_leaf_bundle(leaf: LeafBundle) -> LeafJudgeVerdict:
    violations = []
    goal = leaf.goal.strip()
    lowered = goal.lower()

    if not goal:
        violations.append("goal is required")
    if any(phrase in goal for phrase in BUNDLED_WORK_PHRASES):
        violations.append("goal describes bundled work instead of one leaf")
    if not leaf.parentTaskId:
        violations.append("parentTaskId is required")
    if not leaf.allowedPaths:
        violations.append("allowedPaths are required for a leaf")
    if any(path.strip() in {"", "."} for path in leaf.allowedPaths):
        violations.append("allowedPaths must be bounded for auto-promotion")
    if not leaf.doneWhen:
        violations.append("doneWhen is required for closure readiness")
    if not leaf.requiredEvidence:
        violations.append("requiredEvidence is required for closure readiness")
    if not leaf.requiredTests and not _has_explicit_no_test_clause(leaf.doneWhen):
        violations.append("requiredTests or an explicit no-test clause is required")
    if leaf.estimatedTurns > MAX_ESTIMATED_TURNS:
        violations.append(f"budget too large: estimatedTurns exceeds {MAX_ESTIMATED_TURNS}")
    if leaf.estimatedMinutes > MAX_ESTIMATED_MINUTES:
        violations.append(f"budget too large: estimatedMinutes exceeds {MAX_ESTIMATED_MINUTES}")
    if "相关工作" in lowered:
        violations.append("goal is too vague for one leaf")

    if violations:
        return LeafJudgeVerdict(False, violations[0], violations)
    return LeafJudgeVerdict(True)
