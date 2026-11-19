#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"
export PATH="$repo_root/.tools/bin:$repo_root/.tools/cargo/bin:$PATH"
export CARGO_HOME="$repo_root/.tools/cargo"
export RUSTUP_HOME="$repo_root/.tools/rustup"
export VERACITY_RATE_DB="$repo_root/.harness/sector-request-rate.sqlite"
export SECTOR_RUNNER_ID=cloud-ssh-gpu-alder
export SECTOR_SOURCE_REVISION=c7cfbd779718116ad679a22719bb68ec31ae5825
export WANDB_SILENT=true
mkdir -p "$repo_root/.harness"
exec flock --nonblock "$repo_root/.harness/sector-run.lock" \
  harness/.venv/bin/python -m veracity_harness.sector_study \
  --output harness/results/sector-full \
  --api-cap 1500 \
  --deadline 2026-11-16T10:00:00+00:00 \
  --dotenv credentials.env \
  --phase "${1:-all}"
