#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.sidecar.reports import check_state_view_consistency

issues, out = check_state_view_consistency(root)
print(f'OK: wrote {out}')
raise SystemExit(1 if issues else 0)
