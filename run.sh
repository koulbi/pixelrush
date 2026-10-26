#!/usr/bin/env bash
# Launch PIXELRUSH from the project folder.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 main.py "$@"
