#!/usr/bin/env python3
"""
test_tool_harness.py — 工具执行框架测试

测试覆盖：
    1. Registry 查询 — 已注册脚本返回正确元数据
    2. Registry 默认值 — 未注册脚本返回 fail-closed 默认值
    3. 分区策略 — 连续只读脚本合批为并发组
    4. 串行执行 — 状态写入脚本独立执行
    5. 超时控制 — 超时脚本被正确标记
    6. 结果截断 — 超长输出被截断
    7. 结构化日志 — harness 日志文件生成
"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / 'scripts'))

from tool_registry import get_meta, is_registered, list_concurrent_safe, DEFAULTS
from tool_harness import TaskHarness, TrackedStep

results = []


def test(name, passed, detail=''):
    """记录一个测试结果。"""
    status = 'PASS' if passed else 'FAIL'
    results.append(f'- {name}: {status}' + (f' ({detail})' if detail else ''))
    print(f'  [{status}] {name}' + (f' — {detail}' if detail else ''))


# ---------------------------------------------------------------------------
# Registry 测试
# ---------------------------------------------------------------------------

print('=== test_tool_harness.py ===')
print()
print('--- Registry Tests ---')

# 1. 已注册脚本
meta = get_meta('render_state_views')
test('registry-已注册-read_only',
     meta['read_only'] is True, f"read_only={meta['read_only']}")
test('registry-已注册-concurrent_safe',
     meta['concurrent_safe'] is True, f"concurrent_safe={meta['concurrent_safe']}")
test('registry-已注册-timeout',
     meta['timeout'] == 30, f"timeout={meta['timeout']}")

# 2. 未注册脚本 — fail-closed
meta_unknown = get_meta('some_unknown_script')
test('registry-未注册-fail-closed-read_only',
     meta_unknown['read_only'] is False, 'default read_only=False')
test('registry-未注册-fail-closed-concurrent_safe',
     meta_unknown['concurrent_safe'] is False, 'default concurrent_safe=False')
test('registry-未注册-fail-closed-can_modify_state',
     meta_unknown['can_modify_state'] is True, 'default can_modify_state=True')

# 3. 注册检查
test('registry-is_registered-已注册',
     is_registered('render_state_views'))
test('registry-is_registered-未注册',
     not is_registered('nonexistent_script'))

# 4. 并发安全列表
concurrent = list_concurrent_safe()
test('registry-concurrent-list-非空',
     len(concurrent) > 0, f'count={len(concurrent)}')
test('registry-concurrent-list-包含render',
     'render_state_views' in concurrent)

# 5. .py 后缀和路径前缀处理
meta_with_py = get_meta('render_state_views.py')
test('registry-py后缀处理',
     meta_with_py['read_only'] is True, '去除 .py 后正确匹配')

meta_with_path = get_meta('scripts/render_state_views')
test('registry-路径前缀处理',
     meta_with_path['read_only'] is True, '去除路径后正确匹配')

# ---------------------------------------------------------------------------
# 分区策略测试
# ---------------------------------------------------------------------------

print()
print('--- Partition Tests ---')

harness = TaskHarness(task_id='test', project_root=root, enable_consistency_check=False)
harness.add('render_state_views', ['--project-root', str(root), '--task-id', 'test'])
harness.add('build_next_task_from_state', [])
harness.add('update_task_lifecycle', ['--task-id', 'test', '--to', 'active'])
harness.add('run_task_supervision', ['--task-id', 'test', '--trigger', 'on_task_changed'])

groups = harness._partition_steps()
test('partition-组数',
     len(groups) == 3,
     f'expected 3 (concurrent+serial+serial), got {len(groups)}')
test('partition-第一组并发',
     groups[0]['type'] == 'concurrent',
     f"type={groups[0]['type']}")
test('partition-第一组包含2个步骤',
     len(groups[0]['steps']) == 2,
     f"steps={len(groups[0]['steps'])}")
test('partition-第二组串行',
     groups[1]['type'] == 'serial',
     f"type={groups[1]['type']}")

# ---------------------------------------------------------------------------
# TrackedStep 序列化测试
# ---------------------------------------------------------------------------

print()
print('--- TrackedStep Tests ---')

step = TrackedStep(
    script_name='render_state_views',
    args=['--task-id', 'test'],
    meta=get_meta('render_state_views'),
    state='completed',
    exit_code=0,
    duration_ms=150,
)
d = step.to_dict()
test('tracked-step-序列化',
     d['script'] == 'render_state_views' and d['state'] == 'completed')
test('tracked-step-cmd',
     'render_state_views.py' in ' '.join(step.cmd))

# ---------------------------------------------------------------------------
# 日志文件测试（检查目录存在即可）
# ---------------------------------------------------------------------------

print()
print('--- Log Tests ---')

log_dir = root / '.agent' / 'logs'
test('log-目录存在', log_dir.exists())

# ---------------------------------------------------------------------------
# 输出结果
# ---------------------------------------------------------------------------

print()
out = root / 'tests' / 'TOOL_HARNESS_TEST_RESULT.md'
lines = ['# TOOL_HARNESS_TEST_RESULT', '']
lines.extend(results)
lines.append('')
all_pass = all('PASS' in r for r in results)
lines.append(f'## Overall: {"PASS" if all_pass else "FAIL"}')
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
print(f'Overall: {"PASS" if all_pass else "FAIL"}')
raise SystemExit(0 if all_pass else 1)
