#!/usr/bin/env bash
set -euo pipefail
gh issue list --state open --limit 200 --json number,title,labels,url
