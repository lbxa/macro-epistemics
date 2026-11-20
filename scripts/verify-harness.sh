#!/usr/bin/env bash
set -euo pipefail

case "$#:${1:-}" in
  0:|1:--no-docker) ;;
  *) printf 'Usage: bash scripts/verify-harness.sh [--no-docker]\n' >&2; exit 2 ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

command -v uv >/dev/null 2>&1 || { printf 'Install uv for harness verification.\n' >&2; exit 1; }
if [ "$#" -eq 0 ]; then
  command -v docker >/dev/null 2>&1 || { printf 'Install Docker for isolated harness tests.\n' >&2; exit 1; }
  docker info >/dev/null
fi
export UV_CACHE_DIR="${UV_CACHE_DIR:-$repo_root/.tools/uv-cache}"
uv sync --project harness --locked
python_bin="$repo_root/harness/.venv/bin/python"
"$python_bin" scripts/generate-core-client.py --check
uv run --project harness --locked ruff check harness/src harness/tests
uv run --project harness --locked ruff format --check harness/src harness/tests
uv run --project harness --locked pytest harness/tests -m 'not integration' -n 0
if [ "$#" -eq 0 ]; then
  # A single case can allocate a private bridge per participant.
  uv run --project harness --locked pytest harness/tests -m integration -n 0
else
  printf 'Docker acceptance was deferred. Run bash scripts/verify.sh for the full gate.\n'
fi
