#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent
heartbeat_dir = root / '.agent' / 'heartbeat'
history_path = heartbeat_dir / 'heartbeat-history.json'
latest_path = heartbeat_dir / 'latest-heartbeat.json'
summary_path = heartbeat_dir / 'heartbeat-summary.json'
summary_md_path = root / 'tests' / 'HEARTBEAT_SUMMARY_RESULT.md'


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def extract_day(ts: str):
    try:
        return datetime.fromisoformat(ts).strftime('%Y-%m-%d')
    except ValueError:
        return 'unknown'


def main():
    history = load_json(history_path, [])
    latest = load_json(latest_path, {})

    by_stage = Counter()
    by_day = Counter()
    anomalies = []
    requires_human_count = 0

    for item in history:
        by_stage[item.get('stage', 'unknown')] += 1
        by_day[extract_day(item.get('emittedAt', ''))] += 1
        if item.get('requiresHuman'):
            requires_human_count += 1
        trigger = item.get('triggerReason', 'unknown')
        if trigger in {'stage-complete-stop', 'risk-stop', 'wait-confirmation', 'degraded-continue', 'anomaly-stop'}:
            anomalies.append({
                'emittedAt': item.get('emittedAt', 'unknown'),
                'triggerReason': trigger,
                'currentTask': item.get('currentTask', 'unknown'),
                'humanSummary': item.get('humanSummary', ''),
            })

    stage_summary = [{'stage': stage, 'count': count} for stage, count in sorted(by_stage.items())]
    daily_summary = [{'day': day, 'count': count} for day, count in sorted(by_day.items())]

    summary = {
        'latest': latest,
        'historyCount': len(history),
        'requiresHumanCount': requires_human_count,
        'stageSummary': stage_summary,
        'dailySummary': daily_summary,
        'anomalyHeartbeats': anomalies,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = ['# HEARTBEAT_SUMMARY_RESULT', '', '## latest']
    if latest:
        lines.append(f"- stage: {latest.get('stage', 'unknown')}")
        lines.append(f"- currentTask: {latest.get('currentTask', 'unknown')}")
        lines.append(f"- triggerReason: {latest.get('triggerReason', 'unknown')}")
        lines.append(f"- humanSummary: {latest.get('humanSummary', 'none')}")
    else:
        lines.append('- none')

    lines.append('')
    lines.append('## summary')
    lines.append(f'- historyCount: {len(history)}')
    lines.append(f'- requiresHumanCount: {requires_human_count}')

    lines.append('')
    lines.append('## dailySummary')
    if daily_summary:
        for item in daily_summary:
            lines.append(f"- {item['day']}: {item['count']}")
    else:
        lines.append('- none')

    lines.append('')
    lines.append('## stageSummary')
    if stage_summary:
        for item in stage_summary:
            lines.append(f"- {item['stage']}: {item['count']}")
    else:
        lines.append('- none')

    lines.append('')
    lines.append('## anomalyHeartbeats')
    if anomalies:
        for item in anomalies[-10:]:
            lines.append(f"- {item['emittedAt']} | {item['triggerReason']} | {item['currentTask']} | {item['humanSummary']}")
    else:
        lines.append('- none')

    summary_md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {summary_path}')
    print(f'OK: wrote {summary_md_path}')


if __name__ == '__main__':
    main()
