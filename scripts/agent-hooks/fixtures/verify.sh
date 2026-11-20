#!/usr/bin/env bash
set -euo pipefail
[ "$*" = "${VERIFY_EXPECT_ARGS:-}" ]
printf 'Fixture verification output\n'
exit "${VERIFY_EXIT:-0}"
