#!/usr/bin/env bash
# Print the stored record for a session.
#
# Usage:
#   session-info.sh              # the latest session record
#   session-info.sh <session_id> # record for a specific session UUID
#   session-info.sh --list       # all known sessions (readable_id  session_id  started_at)
set -euo pipefail

STATE_DIR="${CLAUDE_SESSION_IDS_DIR:-$HOME/.claude/session-ids}"

if [[ ! -d "$STATE_DIR" ]]; then
  echo "error: no session-id state at $STATE_DIR (has the SessionStart hook run?)" >&2
  exit 1
fi

field() { sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" "$2" | head -1; }

if [[ "${1:-}" == "--list" ]]; then
  lines=""
  for record in "$STATE_DIR"/*.json; do
    [[ -e "$record" ]] || continue
    lines+="$(printf '%s\t%s\t%s' "$(field readable_id "$record")" "$(field session_id "$record")" "$(field started_at "$record")")"$'\n'
  done
  if [[ -z "$lines" ]]; then
    echo "no session records in $STATE_DIR"
  else
    # Most recent first: started_at (column 3) is ISO-8601 UTC, so a reverse
    # lexicographic sort is a reverse chronological sort.
    printf '%s' "$lines" | sort -t $'\t' -k3,3r
  fi
  exit 0
fi

if [[ -n "${1:-}" ]]; then
  RECORD="$STATE_DIR/$1.json"
else
  RECORD="$STATE_DIR/latest"
fi

if [[ ! -e "$RECORD" ]]; then
  echo "error: no record at $RECORD" >&2
  exit 1
fi

cat "$RECORD"
