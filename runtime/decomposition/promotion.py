from __future__ import annotations

from dataclasses import dataclass, replace

from .judge import judge_leaf_bundle
from .models import LeafBundle


@dataclass
class LeafPromotionResult:
    promoted: bool
    reason: str
    leaf: LeafBundle


def promote_leaf_bundle(leaf: LeafBundle) -> LeafPromotionResult:
    verdict = judge_leaf_bundle(leaf)
    if not verdict.passed:
        return LeafPromotionResult(False, verdict.reason, replace(leaf, status="draft"))

    if leaf.status == "ready":
        return LeafPromotionResult(True, "ok", leaf)

    promoted_leaf = replace(leaf, status="ready")
    return LeafPromotionResult(True, "ok", promoted_leaf)
