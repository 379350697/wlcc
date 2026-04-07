from __future__ import annotations


DEFAULT_CLOSURE_ARTIFACTS = ("final-result", "gap-check", "status-update")


def _normalize_list(values) -> list[str]:
    normalized = []
    for value in values or []:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return normalized


def evaluate_closure_artifacts(task: dict, payload: dict) -> dict:
    if task.get("kind") != "real":
        return {"passed": True, "reason": "ok", "violations": []}

    evidence_ids = set(_normalize_list(payload.get("evidenceIds")))
    missing = [artifact for artifact in DEFAULT_CLOSURE_ARTIFACTS if artifact not in evidence_ids]
    violations = [f"missing closure artifact: {artifact}" for artifact in missing]
    return {
        "passed": len(violations) == 0,
        "reason": "ok" if not violations else violations[0],
        "violations": violations,
    }
