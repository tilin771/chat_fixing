#!/usr/bin/env bash
set -euo pipefail

# Go to repo root (assumes scripts/ is inside the deployment folder)
cd "$(dirname "$0")/.." || exit 0  # if it doesn't exist, nothing to stop

# Bring down the stack if present
if command -v docker compose >/dev/null 2>&1; then
  docker-compose down || true
else
  docker-compose down || true
fi

# Also try stopping by container name (optional, tolerant)
docker rm -f streamlit 2>/dev/null || true
