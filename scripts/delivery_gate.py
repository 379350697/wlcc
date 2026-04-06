#!/usr/bin/env python3
"""
delivery_gate.py — 交付物门禁（Delivery Gate）

职责：
    检查一次 progress 推进是否有真实交付物支撑。
    防止 agent 用空话术（如"已完成"、"推进中"）通过状态推进。

门禁策略：
    - 真实任务（kind=real）：至少 2 项 evidence
    - 样例任务（kind=sample）：至少 1 项 evidence
    - 迁移到 done 时：额外要求 check_delivery_completeness 通过

evidence 来源（4 种）：
    1. latest_result 内容不是空话术
    2. latest_result 指向的文件路径存在
    3. heartbeat 在阈值内（默认 300 秒）
    4. 自上次推进以来有项目文件变化

退出码：
    0 = 通过
    1 = 拒绝（输出拒绝原因 JSON）
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.gates.delivery import evaluate_delivery_gate


def evaluate_gate(task_id: str, latest_result: str, project_root: Path,
                  task_kind: str = 'sample') -> dict:
    return evaluate_delivery_gate(task_id, latest_result, project_root, task_kind)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description='交付物门禁：检查 progress 推进是否有真实交付物支撑。'
    )
    parser.add_argument('--task-id', required=True,
                        help='任务 ID')
    parser.add_argument('--latest-result', required=True,
                        help='agent 提交的最新结果描述')
    parser.add_argument('--project-root', required=True,
                        help='项目根目录路径')
    parser.add_argument('--task-kind', default='sample', choices=['real', 'sample'],
                        help='任务类型：real 需要更严格的 evidence（默认 sample）')
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result = evaluate_gate(
        task_id=args.task_id,
        latest_result=args.latest_result,
        project_root=project_root,
        task_kind=args.task_kind,
    )

    # 输出结果 JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
