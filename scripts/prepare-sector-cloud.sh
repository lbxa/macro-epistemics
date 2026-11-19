#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
export CARGO_HOME="$repo_root/.tools/cargo"
export RUSTUP_HOME="$repo_root/.tools/rustup"
export PATH="$repo_root/.tools/bin:$CARGO_HOME/bin:$PATH"
export CARGO_BUILD_JOBS=8
export UV_CACHE_DIR="$repo_root/.tools/uv-cache"
export UV_PYTHON=3.12
# The existing container runs as root without the chown capability.
export TAR_OPTIONS=--no-same-owner
mkdir -p "$repo_root/.tools/bin"

if ! command -v cargo >/dev/null 2>&1; then
  curl --fail --location https://sh.rustup.rs -o "$repo_root/.tools/rustup-init.sh"
  sh "$repo_root/.tools/rustup-init.sh" -y --profile minimal --default-toolchain 1.94.0 --no-modify-path
fi
if ! command -v uv >/dev/null 2>&1; then
  python3 -m venv "$repo_root/.tools/bootstrap"
  "$repo_root/.tools/bootstrap/bin/pip" install 'uv==0.9.17'
  ln -sf "$repo_root/.tools/bootstrap/bin/uv" "$repo_root/.tools/bin/uv"
fi
bash scripts/setup.sh
cargo build --workspace --locked
printf 'Cloud engine and locked Python harness ready.\n'
