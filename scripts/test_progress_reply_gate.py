#!/usr/bin/env python3
"""
test_progress_reply_gate.py — 汇报门禁测试

测试覆盖：
    1. 正常通过
    2. next_step 太短拒绝
    3. next_step 是空话术拒绝
    4. 循环推进拒绝（latest_result == next_step）
    5. latest_result 太短拒绝
"""
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
results = []


def run_gate(latest_result, next_step):
    """执行 progress reply gate 脚本，返回 (exit_code, result_dict)。"""
    cmd = [
        'python3', str(root / 'scripts' / 'progress_reply_gate.py'),
        '--latest-result', latest_result,
        '--next-step', next_step,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {}
    return result.returncode, data


def test(name, passed, detail=''):
    """记录一个测试结果。"""
    status = 'PASS' if passed else 'FAIL'
    results.append(f'- {name}: {status}' + (f' ({detail})' if detail else ''))
    print(f'  [{status}] {name}' + (f' — {detail}' if detail else ''))


# ---------------------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------------------

print('=== test_progress_reply_gate.py ===')

# 1. 正常通过
code, data = run_gate(
    '完成了 ARCHITECTURE_PLAN.md 的写入',
    '下一步开始编写 MIGRATION_PLAN.md 并验证迁移路径',
)
test('正常通过', code == 0, f'exit={code}')

# 2. next_step 太短拒绝
code, data = run_gate(
    '完成了 ARCHITECTURE_PLAN.md 的写入',
    '继续',
)
test('next_step太短拒绝', code != 0, f'exit={code}, reason={data.get("reason", "?")}')

# 3. next_step 是空话术拒绝
code, data = run_gate(
    '完成了 ARCHITECTURE_PLAN.md 的写入',
    'in progress',
)
test('next_step空话术拒绝', code != 0, f'exit={code}')

# 4. 循环推进拒绝
code, data = run_gate(
    '完成了 ARCHITECTURE_PLAN.md 的写入',
    '完成了 ARCHITECTURE_PLAN.md 的写入',
)
test('循环推进拒绝', code != 0, f'exit={code}, reason={data.get("reason", "?")}')

# 5. latest_result 太短拒绝
code, data = run_gate(
    'ok',
    '下一步开始编写 MIGRATION_PLAN.md 并验证迁移路径',
)
test('latest_result太短拒绝', code != 0, f'exit={code}')

# 6. latest_result 空话术拒绝
code, data = run_gate(
    '已完成',
    '下一步开始编写 MIGRATION_PLAN.md 并验证迁移路径',
)
test('latest_result空话术拒绝', code != 0, f'exit={code}')

# ---------------------------------------------------------------------------
# 输出结果
# ---------------------------------------------------------------------------

out = root / 'tests' / 'PROGRESS_REPLY_GATE_TEST_RESULT.md'
lines = ['# PROGRESS_REPLY_GATE_TEST_RESULT', '']
lines.extend(results)
lines.append('')
all_pass = all('PASS' in r for r in results)
lines.append(f'## Overall: {"PASS" if all_pass else "FAIL"}')
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'\nOK: wrote {out}')
print(f'Overall: {"PASS" if all_pass else "FAIL"}')
