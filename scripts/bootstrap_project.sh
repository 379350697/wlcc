#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p \
  "$ROOT/.agent/tasks" \
  "$ROOT/.agent/resume" \
  "$ROOT/.agent/logs" \
  "$ROOT/.agent/audit" \
  "$ROOT/.agent/backups" \
  "$ROOT/.agent/tmp" \
  "$ROOT/.agent/locks" \
  "$ROOT/.agent/heartbeat" \
  "$ROOT/.agent/state/tasks" \
  "$ROOT/.agent/state/supervision" \
  "$ROOT/.agent/state/handoffs" \
  "$ROOT/.agent/state/ownership" \
  "$ROOT/.agent/state/evidence" \
  "$ROOT/memory/long-term" \
  "$ROOT/memory/session" \
  "$ROOT/tests" \
  "$ROOT/dist"

python3 "$ROOT/scripts/bootstrap_runtime_fixtures.py"

echo "OK: bootstrap complete -> $ROOT"
