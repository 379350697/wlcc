from __future__ import annotations


def _normalize_list(values) -> list[str]:
    normalized = []
    for value in values or []:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return normalized


def _path_allowed(path: str, allowed_paths: list[str]) -> bool:
    candidate = path.strip().strip("/")
    for allowed in allowed_paths:
        scope = allowed.strip().strip("/")
        if not scope or scope == ".":
            return True
        if candidate == scope or candidate.startswith(f"{scope}/"):
            return True
    return False


def evaluate_completion_gate(task: dict, payload: dict) -> dict:
    phase = str(task.get("phase", "")).strip()
    required_evidence = set(_normalize_list(task.get("requiredEvidence")))
    required_tests = set(_normalize_list(task.get("requiredTests")))
    allowed_paths = _normalize_list(task.get("allowedPaths")) or ["."]
    evidence_ids = set(_normalize_list(payload.get("evidenceIds")))
    tests_run = set(_normalize_list(payload.get("testsRun")))
    changed_files = _normalize_list(payload.get("changedFiles"))

    violations = []
    if phase != "verify":
        violations.append("task phase must be verify before completion")

    missing_evidence = sorted(required_evidence - evidence_ids)
    if missing_evidence:
        violations.append(f"missing required evidence: {', '.join(missing_evidence)}")

    missing_tests = sorted(required_tests - tests_run)
    if missing_tests:
        violations.append(f"missing required tests: {', '.join(missing_tests)}")

    disallowed = sorted(path for path in changed_files if not _path_allowed(path, allowed_paths))
    if disallowed:
        violations.append(f"changed files outside allowed paths: {', '.join(disallowed)}")

    return {
        "passed": len(violations) == 0,
        "reason": "ok" if not violations else violations[0],
        "violations": violations,
    }
