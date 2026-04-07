from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from runtime.common.io import read_json, write_json
from runtime.common.models import EvidenceRecord

from .models import EvidenceLedger


LEDGER_VERSION = 1
MAX_SUMMARY_CHARS = 240
MAX_DETAIL_STRING_CHARS = 120
MAX_DETAIL_LIST_ITEMS = 8
MAX_DETAIL_DICT_ITEMS = 12


def now_text() -> str:
    return datetime.now().isoformat(timespec='seconds')


def evidence_ledger_path(root: Path, task_id: str) -> Path:
    return root / '.agent' / 'state' / 'evidence' / f'{task_id}.json'


def _clip_text(value: str, limit: int) -> str:
    normalized = value.strip()
    if len(normalized) <= limit:
        return normalized
    if limit <= 3:
        return normalized[:limit]
    return normalized[: limit - 3] + '...'


def _normalize_value(value: Any, depth: int = 0) -> Any:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _clip_text(value, MAX_DETAIL_STRING_CHARS)
    if depth >= 2:
        return _clip_text(str(value), MAX_DETAIL_STRING_CHARS)
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= MAX_DETAIL_DICT_ITEMS:
                normalized['_truncated'] = True
                break
            normalized[str(key)] = _normalize_value(item, depth + 1)
        return normalized
    if isinstance(value, (list, tuple, set)):
        normalized_list = [_normalize_value(item, depth + 1) for item in list(value)[:MAX_DETAIL_LIST_ITEMS]]
        if len(value) > MAX_DETAIL_LIST_ITEMS:
            normalized_list.append('... [truncated]')
        return normalized_list
    return _clip_text(str(value), MAX_DETAIL_STRING_CHARS)


def _normalize_details(details: dict[str, Any] | None) -> dict[str, Any]:
    if not details:
        return {}
    return {str(key): _normalize_value(value) for key, value in details.items()}


def _normalize_summary(summary: str) -> str:
    return _clip_text(summary, MAX_SUMMARY_CHARS)


def _normalize_record(
    evidence_type: str,
    source: str,
    summary: str,
    details: dict[str, Any] | None = None,
    recorded_at: str | None = None,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidenceType=evidence_type,
        source=source,
        summary=_normalize_summary(summary),
        details=_normalize_details(details),
        recordedAt=recorded_at or now_text(),
    )


def load_evidence_ledger(root: Path, task_id: str) -> EvidenceLedger | None:
    payload = read_json(evidence_ledger_path(root, task_id), None)
    if not isinstance(payload, dict):
        return None
    try:
        return EvidenceLedger.from_dict(payload)
    except Exception:
        return None


def save_evidence_ledger(root: Path, ledger: EvidenceLedger) -> Path:
    path = evidence_ledger_path(root, ledger.taskId)
    write_json(path, ledger.to_dict())
    return path


def append_evidence_record(
    root: Path,
    task_id: str,
    record: EvidenceRecord | dict[str, Any],
) -> EvidenceLedger:
    ledger = load_evidence_ledger(root, task_id)
    if ledger is None:
        ledger = EvidenceLedger(taskId=task_id, version=LEDGER_VERSION, updatedAt=now_text())
    if isinstance(record, EvidenceRecord):
        normalized = _normalize_record(
            record.evidenceType,
            record.source,
            record.summary,
            record.details,
            record.recordedAt or None,
        )
    else:
        normalized = _normalize_record(
            str(record.get('evidenceType', record.get('type', 'unknown'))),
            str(record.get('source', 'unknown')),
            str(record.get('summary', record.get('reason', ''))),
            record.get('details') if isinstance(record.get('details'), dict) else None,
            str(record.get('recordedAt', '')) or None,
        )
    for existing in ledger.entries:
        if (
            existing.evidenceType == normalized.evidenceType
            and existing.source == normalized.source
            and existing.summary == normalized.summary
            and existing.details == normalized.details
        ):
            ledger.updatedAt = normalized.recordedAt
            save_evidence_ledger(root, ledger)
            return ledger
    ledger.entries.append(normalized)
    ledger.updatedAt = normalized.recordedAt
    save_evidence_ledger(root, ledger)
    return ledger


def record_task_evidence(
    root: Path,
    task_id: str,
    evidence_type: str,
    source: str,
    summary: str,
    details: dict[str, Any] | None = None,
) -> EvidenceLedger:
    return append_evidence_record(
        root,
        task_id,
        EvidenceRecord(
            evidenceType=evidence_type,
            source=source,
            summary=summary,
            details=details or {},
        ),
    )


def load_evidence_entries(
    root: Path,
    task_id: str,
    evidence_types: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    ledger = load_evidence_ledger(root, task_id)
    if ledger is None:
        return []
    allowed = set(evidence_types) if evidence_types is not None else None
    entries: list[dict[str, Any]] = []
    for entry in ledger.entries:
        if allowed is not None and entry.evidenceType not in allowed:
            continue
        entries.append(
            {
                'type': entry.evidenceType,
                'source': entry.source,
                'summary': entry.summary,
                'details': dict(entry.details),
                'recordedAt': entry.recordedAt,
            }
        )
    return entries


def record_progress_entries(
    root: Path,
    task_id: str,
    *,
    latest_result: str,
    next_step: str,
    changed_files: list[str],
    tests_run: list[str],
    evidence_ids: list[str],
    phase: str,
    status: str,
    lifecycle: str,
    turn_count: int,
) -> EvidenceLedger:
    ledger = append_evidence_record(
        root,
        task_id,
        {
            "evidenceType": "progress-update",
            "source": "runtime.progress_runtime.apply_progress_update",
            "summary": latest_result,
            "details": {
                "nextStep": next_step,
                "phase": phase,
                "status": status,
                "lifecycle": lifecycle,
                "turnCount": turn_count,
                "changedFiles": list(changed_files),
                "testsRun": list(tests_run),
                "evidenceIds": list(evidence_ids),
            },
        },
    )
    for path in changed_files:
        ledger = append_evidence_record(
            root,
            task_id,
            {
                "evidenceType": "file-change",
                "source": "runtime.progress_runtime.apply_progress_update",
                "summary": path,
                "details": {"path": path},
            },
        )
    for test in tests_run:
        ledger = append_evidence_record(
            root,
            task_id,
            {
                "evidenceType": "test-run",
                "source": "runtime.progress_runtime.apply_progress_update",
                "summary": test,
                "details": {"command": test},
            },
        )
    for artifact in evidence_ids:
        ledger = append_evidence_record(
            root,
            task_id,
            {
                "evidenceType": "artifact-emitted",
                "source": "runtime.progress_runtime.apply_progress_update",
                "summary": artifact,
                "details": {"artifactId": artifact},
            },
        )
    return ledger
