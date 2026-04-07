from __future__ import annotations

from dataclasses import dataclass, field


ALLOWED_TASK_LEVELS = frozenset({"epic", "task", "leaf"})
ALLOWED_PHASES = frozenset({"analyze", "plan", "implement", "verify", "done"})
ALLOWED_STATUSES = frozenset({
    "draft",
    "ready",
    "running",
    "verify",
    "closed",
    "blocked",
    "waiting-human",
    "todo",
    "doing",
    "done",
})
ALLOWED_RISK_LEVELS = frozenset({"low", "medium", "high"})
CLOSURE_READY_STATUSES = frozenset({"ready", "running", "verify", "closed"})


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
    status: str = "draft"
    doneWhen: list[str] = field(default_factory=list)
    requiredEvidence: list[str] = field(default_factory=lambda: ["state-update"])
    requiredTests: list[str] = field(default_factory=list)
    allowedPaths: list[str] = field(default_factory=lambda: ["."])
    forbiddenPaths: list[str] = field(default_factory=list)
    maxTurns: int = 8
    maxMinutes: int = 20
    turnCount: int = 0
    riskLevel: str = "medium"
    estimatedTurns: int = 0
    estimatedMinutes: int = 0
    splitConfidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "taskLevel": self.taskLevel,
            "parentTaskId": self.parentTaskId,
            "phase": self.phase,
            "status": self.status,
            "doneWhen": list(self.doneWhen),
            "requiredEvidence": list(self.requiredEvidence),
            "requiredTests": list(self.requiredTests),
            "allowedPaths": list(self.allowedPaths),
            "forbiddenPaths": list(self.forbiddenPaths),
            "maxTurns": self.maxTurns,
            "maxMinutes": self.maxMinutes,
            "turnCount": self.turnCount,
            "riskLevel": self.riskLevel,
            "estimatedTurns": self.estimatedTurns,
            "estimatedMinutes": self.estimatedMinutes,
            "splitConfidence": self.splitConfidence,
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


def _float_value(value, *, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed


def normalize_contract_dict(payload: dict | None) -> dict:
    payload = dict(payload or {})
    normalized = TaskContract(
        taskLevel=str(payload.get("taskLevel", "leaf") or "leaf"),
        parentTaskId=str(payload.get("parentTaskId", "") or ""),
        phase=str(payload.get("phase", "analyze") or "analyze"),
        status=str(payload.get("status", "draft") or "draft"),
        doneWhen=_string_list(payload.get("doneWhen"), default=[]),
        requiredEvidence=_string_list(payload.get("requiredEvidence"), default=["state-update"]),
        requiredTests=_string_list(payload.get("requiredTests"), default=[]),
        allowedPaths=_string_list(payload.get("allowedPaths"), default=["."]),
        forbiddenPaths=_string_list(payload.get("forbiddenPaths"), default=[]),
        maxTurns=_int_value(payload.get("maxTurns"), default=8),
        maxMinutes=_int_value(payload.get("maxMinutes"), default=20),
        turnCount=_int_value(payload.get("turnCount"), default=0),
        riskLevel=str(payload.get("riskLevel", "medium") or "medium"),
        estimatedTurns=_int_value(payload.get("estimatedTurns"), default=0),
        estimatedMinutes=_int_value(payload.get("estimatedMinutes"), default=0),
        splitConfidence=_float_value(payload.get("splitConfidence"), default=0.0),
    ).to_dict()
    return normalized


def validate_contract_dict(payload: dict | None) -> ContractValidationResult:
    contract = normalize_contract_dict(payload)
    violations = []

    if contract["taskLevel"] not in ALLOWED_TASK_LEVELS:
        violations.append(f"invalid taskLevel: {contract['taskLevel']}")
    if contract["phase"] not in ALLOWED_PHASES:
        violations.append(f"invalid phase: {contract['phase']}")
    if contract["status"] not in ALLOWED_STATUSES:
        violations.append(f"invalid status: {contract['status']}")
    if contract["taskLevel"] == "leaf" and not contract["allowedPaths"]:
        violations.append("allowedPaths required for leaf task")
    if contract["taskLevel"] == "leaf" and contract["status"] in CLOSURE_READY_STATUSES:
        if not contract["doneWhen"]:
            violations.append("doneWhen required for closure-ready leaf task")
        if not contract["requiredEvidence"]:
            violations.append("requiredEvidence required for closure-ready leaf task")
    if contract["maxTurns"] <= 0:
        violations.append("maxTurns must be positive")
    if contract["maxMinutes"] <= 0:
        violations.append("maxMinutes must be positive")
    if contract["riskLevel"] not in ALLOWED_RISK_LEVELS:
        violations.append(f"invalid riskLevel: {contract['riskLevel']}")
    if contract["estimatedTurns"] < 0:
        violations.append("estimatedTurns must be non-negative")
    if contract["estimatedMinutes"] < 0:
        violations.append("estimatedMinutes must be non-negative")
    if not 0.0 <= contract["splitConfidence"] <= 1.0:
        violations.append("splitConfidence must be between 0 and 1")

    if violations:
        return ContractValidationResult(
            passed=False,
            reason=violations[0],
            violations=violations,
        )
    return ContractValidationResult(passed=True)
