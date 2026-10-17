#!/usr/bin/env bash
# YouTube video -> vault/Sources/YouTube transcript. Sets up a local venv with yt-dlp on first run.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/.venv/bin/python"
if [ ! -x "$PY" ]; then
  python3 -m venv "$HERE/.venv"
  "$HERE/.venv/bin/pip" install -q -U "yt-dlp[default]"
fi
exec "$PY" "$HERE/fetch.py" "$@"
