#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"

if ! command -v latexmk >/dev/null || ! command -v pdflatex >/dev/null; then
  if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    printf '%s\n' 'Install TeX Live with latexmk and pdfLaTeX to build the website.' >&2
    exit 1
  fi

  # Cloudflare Workers Builds uses Ubuntu x86-64 without TeX Live.
  tex_dir="$(mktemp -d)"
  trap 'rm -rf "$tex_dir"' EXIT
  release=v2025.12
  archive="$tex_dir/TinyTeX-1-$release.tar.gz"
  printf 'Installing TinyTeX %s for the website build.\n' "$release"
  curl --fail --silent --show-error --location --retry 3 \
    --connect-timeout 15 --max-time 180 \
    "https://github.com/rstudio/tinytex-releases/releases/download/$release/${archive##*/}" \
    --output "$archive"
  printf '%s  %s\n' c42f071e11a56349546ce3ee3e840a4bd5e0ddaf350a3434f7c9d7520ad281b2 "$archive" \
    | sha256sum --check
  tar -xzf "$archive" -C "$tex_dir"
  export PATH="$tex_dir/.TinyTeX/bin/x86_64-linux:$PATH"

  # Supplement the pinned distribution from the final TeX Live 2025 package set.
  tlmgr --repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2025/tlnet-final \
    install cm-super float microtype pdfcol tcolorbox tikzfill titlesec varwidth xurl
fi

export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1794821400}"
export FORCE_SOURCE_DATE=1
make -C "$repo_root/report" LATEXMK='latexmk -gg -no-shell-escape'
