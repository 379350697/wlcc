#!/usr/bin/env python3
"""
rejection_log.py — 结构化拒绝日志

职责：
    集中记录所有门禁拒绝事件（delivery gate / progress reply gate /
    lifecycle gate / supervisor judge / circuit breaker）。
    以 JSON Lines 格式追加写入，便于后续统计分析。

日志格式（每行一个 JSON 对象）：
    {
        "timestamp": "2026-04-06T20:00:00",
        "taskId": "T001",
        "gate": "delivery_gate",
        "reason": "insufficient evidence: 1/2",
        "detail": { ... },       # 门禁返回的完整 JSON（可选）
        "source": "progress_task_runtime"  # 调用来源
    }

使用方式：
    # 作为模块导入
    from rejection_log import log_rejection
    log_rejection('T001', 'delivery_gate', 'insufficient evidence', detail={...})
    
    # 作为 CLI 工具
    python3 scripts/rejection_log.py --task-id T001 --gate delivery_gate --reason "..."
    
    # 查询统计
    python3 scripts/rejection_log.py --stats
"""
import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent
LOG_PATH = root / '.agent' / 'logs' / 'rejection_log.jsonl'


# ---------------------------------------------------------------------------
# 核心 API
# ---------------------------------------------------------------------------


def log_rejection(task_id: str, gate: str, reason: str,
                  detail: dict = None, source: str = '') -> dict:
    """记录一次门禁拒绝事件。
    
    Args:
        task_id: 任务 ID
        gate: 门禁名称（delivery_gate / progress_reply_gate / 
              lifecycle_gate / supervisor_judge / circuit_breaker）
        reason: 拒绝原因（人类可读）
        detail: 门禁返回的完整 JSON（可选）
        source: 调用来源脚本名（可选）
    
    Returns:
        dict: 写入的日志条目
    """
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'taskId': task_id,
        'gate': gate,
        'reason': reason,
        'source': source,
    }
    if detail:
        entry['detail'] = detail

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    return entry


def read_rejections(limit: int = 100) -> list[dict]:
    """读取最近的拒绝记录。
    
    Args:
        limit: 最多返回的记录数
    
    Returns:
        list[dict]: 拒绝记录列表（最新在前）
    """
    if not LOG_PATH.exists():
        return []

    entries = []
    for line in LOG_PATH.read_text(encoding='utf-8').strip().split('\n'):
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return list(reversed(entries[-limit:]))


def get_stats() -> dict:
    """统计拒绝记录。
    
    Returns:
        dict: {
            total: int,
            by_gate: {gate: count},
            by_task: {taskId: count},
            by_reason: {reason: count},
            recent: list[dict],  # 最近 5 条
        }
    """
    entries = read_rejections(limit=10000)
    if not entries:
        return {'total': 0, 'by_gate': {}, 'by_task': {},
                'by_reason': {}, 'recent': []}

    by_gate = Counter(e.get('gate', 'unknown') for e in entries)
    by_task = Counter(e.get('taskId', 'unknown') for e in entries)
    by_reason = Counter(e.get('reason', 'unknown') for e in entries)

    return {
        'total': len(entries),
        'by_gate': dict(by_gate.most_common()),
        'by_task': dict(by_task.most_common(10)),
        'by_reason': dict(by_reason.most_common(10)),
        'recent': entries[:5],
    }


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description='结构化拒绝日志：记录和查询门禁拒绝事件。'
    )
    subparsers = parser.add_subparsers(dest='command')

    # 记录拒绝
    log_parser = subparsers.add_parser('log', help='记录一次拒绝')
    log_parser.add_argument('--task-id', required=True)
    log_parser.add_argument('--gate', required=True)
    log_parser.add_argument('--reason', required=True)
    log_parser.add_argument('--source', default='')

    # 查询统计
    subparsers.add_parser('stats', help='输出拒绝统计')

    # 查询最近记录
    recent_parser = subparsers.add_parser('recent', help='最近的拒绝记录')
    recent_parser.add_argument('--limit', type=int, default=10)

    args = parser.parse_args()

    if args.command == 'log':
        entry = log_rejection(args.task_id, args.gate, args.reason,
                              source=args.source)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    elif args.command == 'stats':
        stats = get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif args.command == 'recent':
        entries = read_rejections(limit=args.limit)
        for e in entries:
            print(json.dumps(e, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
