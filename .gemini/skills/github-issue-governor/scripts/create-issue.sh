#!/usr/bin/env bash
set -euo pipefail

TITLE="$1"
BODY_FILE="$2"
LABELS="$3"

gh issue create \
  --title "$TITLE" \
  --body-file "$BODY_FILE" \
  --label "$LABELS"
