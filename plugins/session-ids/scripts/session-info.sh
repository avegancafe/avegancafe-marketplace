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
  found=0
  for record in "$STATE_DIR"/*.json; do
    [[ -e "$record" ]] || continue
    found=1
    printf '%s\t%s\t%s\n' "$(field readable_id "$record")" "$(field session_id "$record")" "$(field started_at "$record")"
  done
  (( found )) || echo "no session records in $STATE_DIR"
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
