#!/usr/bin/env python3
"""
evaluate_failure_control.py — 失败控制与恢复级联

职责：
    评估任务失败后的恢复策略，按 4 级恢复级联逐级尝试。
    包含熔断器机制，防止连续失败导致无限重试。
    这是四层架构中 L4 Recovery 层的核心。

恢复级联（4 级，从轻到重）：
    Level 1: retry-same        — 原样重试（守卫：retryCount < maxRetries）
    Level 2: retry-reduced     — 缩小范围重试（守卫：scopeReductionAvailable）
    Level 3: fallback-simpler  — 降级到更简单的任务（守卫：simplifiedTaskExists）
    Level 4: handoff-to-human  — 交给人类（守卫：always）

熔断器：
    - 连续失败 >= 3 次 → 进入 OPEN 状态，拒绝执行
    - OPEN 状态持续 300 秒后 → HALF-OPEN，允许 1 次试探
    - 试探成功 → CLOSED，试探失败 → 重新 OPEN

设计原则（借鉴 Claude Code）：
    - 每种恢复只尝试一次（通过守卫标志防止重复）
    - 从轻到重，不跳级
    - 无交叉影响：某级恢复失败不影响下一级的判断

退出码：
    0 = 正常决策
    1 = 熔断器触发
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 恢复级联定义
# ---------------------------------------------------------------------------

RECOVERY_CASCADE = [
    {
        'level': 1,
        'action': 'retry-same',
        'description': '原样重试当前任务',
        'requires_human': False,
        'next_action': 'retry-same-task',
    },
    {
        'level': 2,
        'action': 'retry-reduced-scope',
        'description': '缩小范围后重试（降低复杂度）',
        'requires_human': False,
        'next_action': 'retry-reduced-scope',
    },
    {
        'level': 3,
        'action': 'fallback-to-simpler-task',
        'description': '降级到更简单的替代任务',
        'requires_human': False,
        'next_action': 'fallback-simpler-task',
    },
    {
        'level': 4,
        'action': 'handoff-to-human',
        'description': '所有自动恢复手段已用尽，交给人类处理',
        'requires_human': True,
        'next_action': 'wait-human',
    },
]


# ---------------------------------------------------------------------------
# 熔断器
# ---------------------------------------------------------------------------

CIRCUIT_BREAKER = {
    'maxConsecutiveFailures': 3,   # 连续失败阈值
    'cooldownSeconds': 300,        # OPEN → HALF-OPEN 冷却时间
    'halfOpenRetries': 1,          # HALF-OPEN 允许的试探次数
}


def load_circuit_state(task_id: str) -> dict:
    """加载任务的熔断器状态。"""
    path = root / '.agent' / 'loop' / f'circuit-{task_id}.json'
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        'taskId': task_id,
        'state': 'CLOSED',           # CLOSED / OPEN / HALF-OPEN
        'consecutiveFailures': 0,
        'lastFailureAt': None,
        'halfOpenAttempts': 0,
    }


def save_circuit_state(task_id: str, state: dict):
    """保存任务的熔断器状态。"""
    path = root / '.agent' / 'loop' / f'circuit-{task_id}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def check_circuit_breaker(task_id: str) -> tuple[bool, dict]:
    """检查熔断器是否允许执行。
    
    Returns:
        (allowed: bool, circuit_state: dict)
    """
    cs = load_circuit_state(task_id)

    if cs['state'] == 'CLOSED':
        return True, cs

    if cs['state'] == 'OPEN':
        # 检查冷却时间是否已过
        if cs['lastFailureAt']:
            try:
                last = datetime.fromisoformat(cs['lastFailureAt'])
                age = (datetime.now() - last).total_seconds()
                if age >= CIRCUIT_BREAKER['cooldownSeconds']:
                    # 进入 HALF-OPEN
                    cs['state'] = 'HALF-OPEN'
                    cs['halfOpenAttempts'] = 0
                    save_circuit_state(task_id, cs)
                    return True, cs
            except (ValueError, TypeError):
                pass
        return False, cs

    if cs['state'] == 'HALF-OPEN':
        if cs['halfOpenAttempts'] < CIRCUIT_BREAKER['halfOpenRetries']:
            return True, cs
        # 试探次数用尽 → 重新 OPEN
        cs['state'] = 'OPEN'
        cs['lastFailureAt'] = datetime.now().isoformat(timespec='seconds')
        save_circuit_state(task_id, cs)
        return False, cs

    return True, cs


def record_failure(task_id: str):
    """记录一次失败，更新熔断器状态。"""
    cs = load_circuit_state(task_id)
    cs['consecutiveFailures'] += 1
    cs['lastFailureAt'] = datetime.now().isoformat(timespec='seconds')

    if cs['state'] == 'HALF-OPEN':
        cs['halfOpenAttempts'] += 1
        if cs['halfOpenAttempts'] >= CIRCUIT_BREAKER['halfOpenRetries']:
            cs['state'] = 'OPEN'

    if cs['consecutiveFailures'] >= CIRCUIT_BREAKER['maxConsecutiveFailures']:
        cs['state'] = 'OPEN'

    save_circuit_state(task_id, cs)
    return cs


def record_success(task_id: str):
    """记录一次成功，重置熔断器。"""
    cs = load_circuit_state(task_id)
    cs['state'] = 'CLOSED'
    cs['consecutiveFailures'] = 0
    cs['halfOpenAttempts'] = 0
    save_circuit_state(task_id, cs)
    return cs


# ---------------------------------------------------------------------------
# 恢复级联评估
# ---------------------------------------------------------------------------


def evaluate_cascade(payload: dict) -> dict:
    """评估恢复级联，返回决策结果。
    
    Args:
        payload: {
            taskId, stopType, reason, retries, maxRetries,
            repeatedTask, repeatedFailures, noProgressCount,
            scopeReductionAvailable, simplifiedTaskExists,
        }
    
    Returns:
        dict: {
            taskId, decision, reason, nextAction, requiresHuman,
            recoveryLevel, circuitState,
        }
    """
    task_id = payload['taskId']
    retries = payload.get('retries', 0)
    max_retries = payload.get('maxRetries', 2)
    repeated_task = payload.get('repeatedTask', False)
    repeated_failures = payload.get('repeatedFailures', 0)
    no_progress = payload.get('noProgressCount', 0)
    stop_type = payload.get('stopType', 'none')
    reason = payload.get('reason', '')
    scope_reduction = payload.get('scopeReductionAvailable', False)
    simplified_task = payload.get('simplifiedTaskExists', False)

    # ── 熔断器检查 ────────────────────────────────────────────────
    allowed, circuit_state = check_circuit_breaker(task_id)
    if not allowed:
        return {
            'taskId': task_id,
            'decision': 'circuit-breaker-open',
            'reason': f'circuit breaker OPEN: {circuit_state["consecutiveFailures"]} consecutive failures',
            'nextAction': 'wait-cooldown',
            'requiresHuman': True,
            'recoveryLevel': 0,
            'circuitState': circuit_state['state'],
        }

    # ── 死循环检测（优先于恢复级联） ──────────────────────────────
    if repeated_task or repeated_failures >= 3 or no_progress >= 3:
        record_failure(task_id)
        return {
            'taskId': task_id,
            'decision': 'dead-loop-stop',
            'reason': 'dead loop guard triggered',
            'nextAction': 'inspect-loop',
            'requiresHuman': True,
            'recoveryLevel': 0,
            'circuitState': circuit_state['state'],
        }

    # ── 风险停止 ──────────────────────────────────────────────────
    if stop_type == 'risk-stop':
        return {
            'taskId': task_id,
            'decision': 'wait-confirmation',
            'reason': reason or 'risk stop',
            'nextAction': 'wait-human',
            'requiresHuman': True,
            'recoveryLevel': 0,
            'circuitState': circuit_state['state'],
        }

    # ── 4 级恢复级联 ──────────────────────────────────────────────
    # 按级别从轻到重尝试，第一个满足守卫条件的即为决策。
    guards = [
        lambda: retries < max_retries,                # L1: retry 预算未用尽
        lambda: scope_reduction,                       # L2: 有范围缩小方案
        lambda: simplified_task,                       # L3: 有简化替代任务
        lambda: True,                                  # L4: 总是可以交人类
    ]

    for cascade_entry, guard in zip(RECOVERY_CASCADE, guards):
        if guard():
            # 记录失败（更新熔断器）
            if cascade_entry['level'] <= 3:
                record_failure(task_id)
            return {
                'taskId': task_id,
                'decision': cascade_entry['action'],
                'reason': cascade_entry['description'],
                'nextAction': cascade_entry['next_action'],
                'requiresHuman': cascade_entry['requires_human'],
                'recoveryLevel': cascade_entry['level'],
                'circuitState': circuit_state['state'],
            }

    # 兜底（不应到达）
    return {
        'taskId': task_id,
        'decision': 'handoff-to-human',
        'reason': 'no recovery option matched (fallthrough)',
        'nextAction': 'wait-human',
        'requiresHuman': True,
        'recoveryLevel': 4,
        'circuitState': circuit_state['state'],
    }


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description='评估失败恢复策略：4 级恢复级联 + 熔断器。'
    )
    parser.add_argument('--input', required=True,
                        help='输入 JSON 文件路径')
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding='utf-8'))
    result = evaluate_cascade(payload)

    # 写入结果 JSON
    out_json = root / '.agent' / 'loop' / 'failure-control.json'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 写入测试结果 MD
    lines = ['# FAILURE_CONTROL_RESULT', '', '## summary']
    lines.append(f"- taskId: {result['taskId']}")
    lines.append(f"- decision: {result['decision']}")
    lines.append(f"- reason: {result['reason']}")
    lines.append(f"- nextAction: {result['nextAction']}")
    lines.append(f"- requiresHuman: {str(result['requiresHuman']).lower()}")
    lines.append(f"- recoveryLevel: {result['recoveryLevel']}")
    lines.append(f"- circuitState: {result['circuitState']}")
    out_md = root / 'tests' / 'FAILURE_CONTROL_RESULT.md'
    out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out_json}')
    print(f'OK: wrote {out_md}')

    if result['decision'] == 'circuit-breaker-open':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
