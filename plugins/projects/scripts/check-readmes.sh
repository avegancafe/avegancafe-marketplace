#!/usr/bin/env bash
# Check that every project README.md in _projects/ is under the 256-line limit.
# Usage: check-readmes.sh [base-dir]   (default: current directory)
set -euo pipefail

BASE_DIR="${1:-.}"
PROJECTS_DIR="$BASE_DIR/_projects"
LIMIT=256

if [[ ! -d "$PROJECTS_DIR" ]]; then
  echo "error: $PROJECTS_DIR not found" >&2
  exit 1
fi

status=0
found=0
for readme in "$PROJECTS_DIR"/*/README.md; do
  [[ -e "$readme" ]] || continue
  found=1
  lines="$(wc -l < "$readme")"
  if (( lines >= LIMIT )); then
    echo "OVER LIMIT ($lines lines >= $LIMIT): $readme"
    status=1
  else
    echo "ok ($lines lines): $readme"
  fi
done

if (( ! found )); then
  echo "no project READMEs found under $PROJECTS_DIR"
fi
exit "$status"
