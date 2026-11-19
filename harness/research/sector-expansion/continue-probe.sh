#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export PATH="$PWD/.tools/bin:$PWD/.tools/cargo/bin:$PATH"
while true; do
  # Stop waiting at 10:05 UTC; the diagnostic itself has a 10:15 deadline.
  if [[ "$(date -u +%s)" -ge 1794823500 ]]; then
    exit 3
  fi
  if ! state="$(harness/.venv/bin/python -c 'import json; print(json.load(open("harness/results/sector-full/progress.json"))["status"])')"; then
    sleep 1
    continue
  fi
  case "$state" in
    complete|complete_with_failures) break ;;
    interrupted|deadline_reached|budget_limited) exit 2 ;;
  esac
  sleep 15
done
exec flock --nonblock "$PWD/.harness/sector-probe.lock" \
  harness/.venv/bin/python -m veracity_harness.sector_probe \
  --main harness/results/sector-full --output harness/results/sector-arithmetic-probe \
  --api-cap 10 --deadline 2026-11-16T10:15:00+00:00 --dotenv credentials.env
