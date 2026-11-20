#!/usr/bin/env bash
set -euo pipefail

case "${0##*/}:$*" in
  'docker:info') stage=docker ;;
  'uv:sync --project harness --locked') stage=sync ;;
  'python:scripts/generate-core-client.py --check') stage=client ;;
  'uv:run --project harness --locked ruff check harness/src harness/tests') stage=lint ;;
  'uv:run --project harness --locked ruff format --check harness/src harness/tests') stage=format ;;
  'uv:run --project harness --locked pytest harness/tests -m not integration -n 0') stage=unit ;;
  'uv:run --project harness --locked pytest harness/tests -m integration -n 0') stage=integration ;;
  *) printf 'Unexpected harness gate command: %s %s\n' "${0##*/}" "$*" >&2; exit 1 ;;
esac
printf '%s\n' "$stage" >> "$GATE_CALLS"
[ "${GATE_FAIL:-}" != "$stage" ]
