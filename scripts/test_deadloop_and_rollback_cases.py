#!/usr/bin/env python3
"""
test_deadloop_and_rollback_cases.py — 失败控制与恢复级联测试

测试覆盖（基于 4 级恢复级联 + 熔断器）：
    1. 死循环检测 → dead-loop-stop
    2. 重试预算未用尽 → retry-same（L1）
    3. 重试预算用尽 + 有范围缩小 → retry-reduced-scope（L2）
    4. 重试预算用尽 + 无范围缩小 + 有简化任务 → fallback-to-simpler-task（L3）
    5. 所有自动恢复手段用尽 → handoff-to-human（L4）
    6. 风险停止 → wait-confirmation
"""
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'DEADLOOP_AND_ROLLBACK_CASES_RESULT.md'
issues = []

# 清理可能残留的熔断器状态
circuit_dir = root / '.agent' / 'loop'
for f in circuit_dir.glob('circuit-*.json'):
    f.unlink()

cases = [
    # 1. 死循环检测
    (
        {'taskId': 'test-deadloop', 'repeatedTask': True,
         'repeatedFailures': 3, 'noProgressCount': 3},
        'dead-loop-stop',
    ),
    # 2. L1: 重试预算未用尽
    (
        {'taskId': 'test-retry-l1', 'stopType': 'anomaly-stop',
         'retries': 0, 'maxRetries': 2},
        'retry-same',
    ),
    # 3. L2: 重试预算用尽 + 有范围缩小
    (
        {'taskId': 'test-retry-l2', 'stopType': 'anomaly-stop',
         'retries': 2, 'maxRetries': 2, 'scopeReductionAvailable': True},
        'retry-reduced-scope',
    ),
    # 4. L3: 重试预算用尽 + 无范围缩小 + 有简化任务
    (
        {'taskId': 'test-fallback-l3', 'stopType': 'anomaly-stop',
         'retries': 2, 'maxRetries': 2, 'simplifiedTaskExists': True},
        'fallback-to-simpler-task',
    ),
    # 5. L4: 所有自动恢复手段用尽
    (
        {'taskId': 'test-handoff-l4', 'stopType': 'anomaly-stop',
         'retries': 2, 'maxRetries': 2},
        'handoff-to-human',
    ),
    # 6. 风险停止
    (
        {'taskId': 'test-risk', 'stopType': 'risk-stop',
         'reason': 'high risk operation'},
        'wait-confirmation',
    ),
]

input_path = root / 'tests' / 'TMP_FAILURE_CONTROL_INPUT.json'
for payload, expected in cases:
    input_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    res = subprocess.run([
        'python3', str(root / 'scripts' / 'evaluate_failure_control.py'),
        '--input', str(input_path),
    ], capture_output=True, text=True)
    if res.returncode != 0 and expected != 'circuit-breaker-open':
        issues.append(f'evaluate_failure_control failed for {expected}: {res.stderr.strip()[:100]}')
        continue
    data = json.loads((root / '.agent' / 'loop' / 'failure-control.json').read_text(encoding='utf-8'))
    if data.get('decision') != expected:
        issues.append(f'expected {expected}, got {data.get("decision")} (level={data.get("recoveryLevel")})')

# 清理临时文件
if input_path.exists():
    input_path.unlink()

lines = ['# DEADLOOP_AND_ROLLBACK_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
