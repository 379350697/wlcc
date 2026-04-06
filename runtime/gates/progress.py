from __future__ import annotations

EMPTY_PHRASES = frozenset({
    '已完成', '完成', '推进中', '继续', '进行中', '正在处理',
    'done', 'completed', 'in progress', 'continue', 'ok', 'wip',
    '无', 'none', 'n/a', 'tbd',
})

MIN_NEXT_STEP_LENGTH = 10
MIN_LATEST_RESULT_LENGTH = 5


def check_latest_result_substantive(latest_result: str) -> dict | None:
    stripped = latest_result.strip()
    if len(stripped) < MIN_LATEST_RESULT_LENGTH:
        return {
            'check': 'latest_result_length',
            'passed': False,
            'reason': f'latest_result 太短（{len(stripped)} 字符，最少 {MIN_LATEST_RESULT_LENGTH}）',
        }
    if stripped.lower() in EMPTY_PHRASES:
        return {
            'check': 'latest_result_phrase',
            'passed': False,
            'reason': f'latest_result 是空话术："{stripped}"',
        }
    return None


def check_next_step_length(next_step: str) -> dict | None:
    stripped = next_step.strip()
    if len(stripped) < MIN_NEXT_STEP_LENGTH:
        return {
            'check': 'next_step_length',
            'passed': False,
            'reason': f'next_step 太短（{len(stripped)} 字符，最少 {MIN_NEXT_STEP_LENGTH}）',
        }
    return None


def check_next_step_not_phrase(next_step: str) -> dict | None:
    normalized = next_step.strip().lower()
    if normalized in EMPTY_PHRASES:
        return {
            'check': 'next_step_phrase',
            'passed': False,
            'reason': f'next_step 是空话术："{next_step.strip()}"',
        }
    return None


def check_not_circular(latest_result: str, next_step: str) -> dict | None:
    if latest_result.strip() == next_step.strip():
        return {
            'check': 'circular',
            'passed': False,
            'reason': 'next_step 与 latest_result 完全相同（循环推进）',
        }
    return None


def evaluate_progress_gate(latest_result: str, next_step: str) -> dict:
    checks = [
        lambda: check_latest_result_substantive(latest_result),
        lambda: check_next_step_length(next_step),
        lambda: check_next_step_not_phrase(next_step),
        lambda: check_not_circular(latest_result, next_step),
    ]

    violations = []
    for check in checks:
        result = check()
        if result is not None:
            violations.append(result)

    passed = len(violations) == 0
    reason = 'ok' if passed else violations[0]['reason']
    return {
        'passed': passed,
        'reason': reason,
        'violations': violations,
    }

