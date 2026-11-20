#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "${0##*/}" >> "$FORBIDDEN_COMMANDS"
printf 'Heavyweight command entered fast verification: %s\n' "${0##*/}" >&2
exit 98
