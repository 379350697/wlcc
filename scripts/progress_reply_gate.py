#!/usr/bin/env python3
"""
progress_reply_gate.py — 汇报门禁（Progress Reply Gate）

职责：
    防止 agent 以空话术或循环推进的方式通过 progress 汇报。
    确保每次推进的 next_step 是具体、可操作的。

门禁规则：
    1. next_step 最少 10 个字符（强制具体化）
    2. next_step 不能和 latest_result 完全相同（防循环推进）
    3. next_step 不能是已知的空话术
    4. latest_result 最少 5 个字符

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

from runtime.gates.progress import evaluate_progress_gate


def evaluate_gate(latest_result: str, next_step: str) -> dict:
    return evaluate_progress_gate(latest_result, next_step)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description='汇报门禁：防止空话术和循环推进。'
    )
    parser.add_argument('--latest-result', required=True,
                        help='agent 提交的最新结果描述')
    parser.add_argument('--next-step', required=True,
                        help='agent 声明的下一步动作')
    args = parser.parse_args()

    result = evaluate_gate(
        latest_result=args.latest_result,
        next_step=args.next_step,
    )

    # 输出结果 JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
