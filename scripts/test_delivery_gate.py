#!/usr/bin/env python3
"""
test_delivery_gate.py — 交付物门禁测试

测试覆盖：
    1. 空话术拒绝（latest_result = "已完成"）
    2. 有效文件路径通过
    3. 多项 evidence 通过
    4. 真实任务 evidence 数量不足拒绝
    5. CLI 退出码检查
"""
import json
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
results = []


def run_gate(task_id, latest_result, task_kind='sample', project_root=None):
    """执行 delivery gate 脚本，返回 (exit_code, result_dict)。"""
    pr = project_root or str(root)
    cmd = [
        'python3', str(root / 'scripts' / 'delivery_gate.py'),
        '--task-id', task_id,
        '--latest-result', latest_result,
        '--project-root', pr,
        '--task-kind', task_kind,
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

print('=== test_delivery_gate.py ===')

# 1. 空话术拒绝
code, data = run_gate('T-test-1', '已完成')
test('空话术拒绝', code != 0, f'exit={code}')

# 2. 空话术拒绝（英文）
code, data = run_gate('T-test-2', 'done')
test('空话术拒绝(英文)', code != 0, f'exit={code}')

# 3. 太短的内容拒绝
code, data = run_gate('T-test-3', 'ok')
test('太短内容拒绝', code != 0, f'exit={code}')

# 4. 有实质内容的 latest_result（文件存在 + 内容非空话术）
#    使用项目中已知存在的文件
code, data = run_gate('T-test-4', '生成了 ARCHITECTURE_PLAN.md 架构文档并完成了核心审查')
test('有实质内容通过', code == 0, f'exit={code}, evidence={data.get("collected", "?")}')

# 5. 真实任务需要 2 项 evidence（仅 content 不够）
code, data = run_gate('T-test-5', '这是一段有实质内容的描述，但不是文件路径', task_kind='real')
test('真实任务单项evidence不足',
     code != 0 or data.get('collected', 0) < 2,
     f'exit={code}, evidence={data.get("collected", "?")}')

# 6. 指向存在的文件路径
code, data = run_gate('T-test-6', 'README.md')
test('文件路径存在通过', code == 0, f'evidence={data.get("collected", "?")}')

# ---------------------------------------------------------------------------
# 输出结果
# ---------------------------------------------------------------------------

out = root / 'tests' / 'DELIVERY_GATE_TEST_RESULT.md'
lines = ['# DELIVERY_GATE_TEST_RESULT', '']
lines.extend(results)
lines.append('')
all_pass = all('PASS' in r for r in results)
lines.append(f'## Overall: {"PASS" if all_pass else "FAIL"}')
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'\nOK: wrote {out}')
print(f'Overall: {"PASS" if all_pass else "FAIL"}')
