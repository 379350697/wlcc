#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
script = root / 'scripts' / 'emit_heartbeat.py'
cases = [
    ('stop-trigger', ['--stage','demo-extreme','--current-task','demo-long-chain-autonomy','--next-step','report-stage-complete','--trigger-reason','stage-complete-stop','--risk-or-blocker','current stage boundary reached','--requires-human','--throttle-seconds','0'], 'stage-complete-stop'),
    ('degraded-trigger', ['--stage','demo-extreme','--current-task','demo-long-chain-autonomy','--next-step','continue-loop','--trigger-reason','degraded-continue','--risk-or-blocker','retrieval_priority','--throttle-seconds','0'], 'degraded-continue'),
    ('periodic-trigger', ['--stage','demo-extreme','--current-task','demo-long-chain-autonomy','--next-step','continue-loop','--trigger-reason','periodic-step','--risk-or-blocker','none','--throttle-seconds','0'], 'periodic-step'),
]
failed = []
lines = ['# HEARTBEAT_TRIGGER_TEST_RESULT', '']
for name, args, expected in cases:
    res = subprocess.run(['python3', str(script), *args], capture_output=True, text=True)
    data = json.loads((root / '.agent' / 'heartbeat' / 'latest-heartbeat.json').read_text(encoding='utf-8'))
    ok = res.returncode == 0 and data.get('triggerReason') == expected
    lines.append(f'## {name}')
    lines.append(f"- triggerReason: {data.get('triggerReason', 'MISSING')}")
    lines.append(f"- result: {'PASS' if ok else 'FAIL'}")
    lines.append('')
    if not ok:
        failed.append(name)
lines.append('## Overall')
lines.append(f"- {'PASS' if not failed else 'FAIL: ' + ', '.join(failed)}")
out = root / 'tests' / 'HEARTBEAT_TRIGGER_TEST_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(0 if not failed else 1)
