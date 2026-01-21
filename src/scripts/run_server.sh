#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/server"

python3 -m uvicorn app:app --host 0.0.0.0 --port 26472
