#!/usr/bin/env bash
set -euo pipefail

LABELS="$1"

required_prefixes=("type:" "prio:" "status:" "release:" "feat:")
for prefix in "${required_prefixes[@]}"; do
  if [[ "$LABELS" != *"$prefix"* ]]; then
    echo "missing required label prefix: $prefix" >&2
    exit 1
  fi
done
