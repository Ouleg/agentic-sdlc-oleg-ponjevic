#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

docker compose up -d

body='{"start": {"x": 0, "y": 1, "heading": "E"}, "grid": {"width": 3, "height": 3, "obstacles": [{"x": 1, "y": 1}]}, "commands": "FLFFRFF"}'
expected='{"position":{"x":2,"y":2},"heading":"E","blocked":[{"index":0,"reason":"obstacle"},{"index":3,"reason":"boundary"}]}'
response_file=$(mktemp /tmp/opencode/nav_infra_001_1_s3.XXXXXX.json)
trap 'rm -f "$response_file"' EXIT

status=$(curl --silent --show-error --retry 20 --retry-delay 1 --retry-all-errors \
  --output "$response_file" --write-out '%{http_code}' \
  -X POST http://127.0.0.1:8000/simulate \
  -H 'Content-Type: application/json' \
  -d "$body")

python3 - "$status" "$response_file" "$expected" <<'PY'
import json
import sys

status, response_file, expected = sys.argv[1:4]
with open(response_file) as stream:
    actual = json.load(stream)
assert status == "200", status
assert actual == json.loads(expected), actual
print("NAV-INFRA-001.1-S3 OK")
PY
