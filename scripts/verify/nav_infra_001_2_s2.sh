#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

docker compose up -d

container_id=$(docker compose ps -q rover)
before=$(docker logs "$container_id" | grep -c '^{' || true)

body='{"start": {"x": 0, "y": 1, "heading": "E"}, "grid": {"width": 3, "height": 3, "obstacles": [{"x": 1, "y": 1}]}, "commands": "FLFFRFF"}'
curl --silent --show-error --retry 20 --retry-delay 1 --retry-all-errors \
  --output /dev/null \
  -X POST http://127.0.0.1:8000/simulate \
  -H 'Content-Type: application/json' \
  -d "$body"

sleep 1
after=$(docker logs "$container_id" | grep -c '^{' || true)
entry=$(docker logs "$container_id" | grep '^{' | tail -1)

python3 - "$before" "$after" "$entry" <<'PY'
import json
import sys

before, after, entry_line = sys.argv[1:4]
entry = json.loads(entry_line)
assert int(after) - int(before) == 1, (before, after)
assert entry["level"] == "INFO", entry
assert entry["event"] == "simulation_complete", entry
assert entry["request_id"], entry
assert entry["grid"] == {"width": 3, "height": 3, "obstacle_count": 1}, entry
assert entry["start"] == {"x": 0, "y": 1, "heading": "E"}, entry
assert entry["command_count"] == 7, entry
assert entry["result"] == {
    "x": 2,
    "y": 2,
    "heading": "E",
    "blocked_count": 2,
}, entry
assert entry["error"] is None, entry
assert isinstance(entry["duration_ms"], (int, float)), entry
print("NAV-INFRA-001.2-S2 OK")
PY
