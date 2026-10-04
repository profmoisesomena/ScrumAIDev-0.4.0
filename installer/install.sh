#!/usr/bin/env sh
set -eu

VERSION="${SCRUMAIDEV_VERSION:-0.4.1}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE="${1:-}"

if [ -z "$SOURCE" ]; then
  LOCAL_WHEEL=$(find "$SCRIPT_DIR" -maxdepth 1 -type f -name "scrumaidev-${VERSION}-*.whl" -print -quit 2>/dev/null || true)
  if [ -n "$LOCAL_WHEEL" ]; then
    SOURCE="$LOCAL_WHEEL"
  elif [ -f "$SCRIPT_DIR/../pyproject.toml" ]; then
    SOURCE=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
  else
    SOURCE="scrumaidev==$VERSION"
  fi
fi

if command -v uv >/dev/null 2>&1; then
  echo "Installing ScrumAIDev from: $SOURCE"
  uv tool install --force "$SOURCE"
  scrumaidev version
elif command -v pipx >/dev/null 2>&1; then
  echo "Installing ScrumAIDev with pipx from: $SOURCE"
  pipx install --force "$SOURCE"
  scrumaidev version
else
  echo "ERROR: neither 'uv' nor 'pipx' was found. Install uv (recommended) or pipx first." >&2
  exit 2
fi
