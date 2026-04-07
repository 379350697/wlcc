from __future__ import annotations

from dataclasses import dataclass, field


ALLOWED_TASK_LEVELS = frozenset({"epic", "task", "leaf"})
ALLOWED_PHASES = frozenset({"analyze", "plan", "implement", "verify", "done"})


@dataclass
class ContractValidationResult:
    passed: bool
    reason: str = "ok"
    violations: list[str] = field(default_factory=list)


@dataclass
class TaskContract:
    taskLevel: str = "leaf"
    parentTaskId: str = ""
    phase: str = "analyze"
    doneWhen: list[str] = field(default_factory=list)
    requiredEvidence: list[str] = field(default_factory=lambda: ["state-update"])
    requiredTests: list[str] = field(default_factory=list)
    allowedPaths: list[str] = field(default_factory=lambda: ["."])
    forbiddenPaths: list[str] = field(default_factory=list)
    maxTurns: int = 8
    maxMinutes: int = 20
    turnCount: int = 0

    def to_dict(self) -> dict:
        return {
            "taskLevel": self.taskLevel,
            "parentTaskId": self.parentTaskId,
            "phase": self.phase,
            "doneWhen": list(self.doneWhen),
            "requiredEvidence": list(self.requiredEvidence),
            "requiredTests": list(self.requiredTests),
            "allowedPaths": list(self.allowedPaths),
            "forbiddenPaths": list(self.forbiddenPaths),
            "maxTurns": self.maxTurns,
            "maxMinutes": self.maxMinutes,
            "turnCount": self.turnCount,
        }

    def validate(self) -> ContractValidationResult:
        return validate_contract_dict(self.to_dict())


def _string_list(values, *, default: list[str] | None = None) -> list[str]:
    if values is None:
        return list(default or [])
    cleaned = []
    for value in values or []:
        text = str(value).strip()
        if text:
            cleaned.append(text)
    if cleaned:
        return cleaned
    return []


def _int_value(value, *, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def normalize_contract_dict(payload: dict | None) -> dict:
    payload = dict(payload or {})
    normalized = TaskContract(
        taskLevel=str(payload.get("taskLevel", "leaf") or "leaf"),
        parentTaskId=str(payload.get("parentTaskId", "") or ""),
        phase=str(payload.get("phase", "analyze") or "analyze"),
        doneWhen=_string_list(payload.get("doneWhen"), default=[]),
        requiredEvidence=_string_list(payload.get("requiredEvidence"), default=["state-update"]),
        requiredTests=_string_list(payload.get("requiredTests"), default=[]),
        allowedPaths=_string_list(payload.get("allowedPaths"), default=["."]),
        forbiddenPaths=_string_list(payload.get("forbiddenPaths"), default=[]),
        maxTurns=_int_value(payload.get("maxTurns"), default=8),
        maxMinutes=_int_value(payload.get("maxMinutes"), default=20),
        turnCount=_int_value(payload.get("turnCount"), default=0),
    ).to_dict()
    return normalized


def validate_contract_dict(payload: dict | None) -> ContractValidationResult:
    contract = normalize_contract_dict(payload)
    violations = []

    if contract["taskLevel"] not in ALLOWED_TASK_LEVELS:
        violations.append(f"invalid taskLevel: {contract['taskLevel']}")
    if contract["phase"] not in ALLOWED_PHASES:
        violations.append(f"invalid phase: {contract['phase']}")
    if contract["taskLevel"] == "leaf" and not contract["allowedPaths"]:
        violations.append("allowedPaths required for leaf task")
    if contract["maxTurns"] <= 0:
        violations.append("maxTurns must be positive")
    if contract["maxMinutes"] <= 0:
        violations.append("maxMinutes must be positive")

    if violations:
        return ContractValidationResult(
            passed=False,
            reason=violations[0],
            violations=violations,
        )
    return ContractValidationResult(passed=True)
