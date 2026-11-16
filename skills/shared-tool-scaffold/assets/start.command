#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  {{PROJECT_NAME}} — Mac/Linux launcher. Double-click to start.
#  (First launch on Mac: right-click -> Open to clear Gatekeeper.)
# ─────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

echo ""
echo "  {{PROJECT_NAME}} — starting…"
echo ""

# ── 1. Find Python 3 ─────────────────────────────────────────
PYTHON=""
for cmd in python3 python3.13 python3.12 python3.11 python3.10 python; do
  if command -v "$cmd" &>/dev/null; then
    MAJOR=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo 0)
    if [ "$MAJOR" = "3" ]; then PYTHON="$cmd"; break; fi
  fi
done
if [ -z "$PYTHON" ]; then
  echo "  ERROR: Python 3 not found."
  echo "  Install it: https://www.python.org/downloads/  (or: brew install python)"
  read -r -p "  Press Enter to close…" _
  exit 1
fi
echo "  Python: $($PYTHON --version)"

# ── 2. Virtualenv (device-local, NOT in the shared folder) ───
VENV="$HOME/.cache/{{PROJECT_SLUG}}/venv"
if [ ! -d "$VENV" ]; then
  echo "  Creating local virtualenv (off the shared drive)…"
  mkdir -p "$HOME/.cache/{{PROJECT_SLUG}}"
  "$PYTHON" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "  Checking requirements…"
pip install -r requirements.txt --quiet --disable-pip-version-check 2>&1 | grep -v "already satisfied" || true

echo ""
echo "  Ready. Server on http://localhost:{{PORT}}  (Ctrl+C to stop)"
echo ""
python server.py
