#!/usr/bin/env bash
# hook-probe: append one line per hook event so you can tell whether plugin
# hooks fire in an environment. Reads the hook's JSON from stdin, never prints
# to stdout (so it adds nothing to Claude's context), never blocks, always
# exits 0. No network calls.
#
# Line format (tab-separated):
#   <UTC timestamp>  <event>  tool=<tool name or ->  session=<session id>  cwd=<cwd>

input=$(cat 2>/dev/null || true)

field() {
  # Pull a top-level string field out of the JSON. Prefer jq, then python3,
  # then a crude sed fallback, since sandboxes may lack either tool.
  local key=$1 val=""
  if command -v jq >/dev/null 2>&1; then
    val=$(printf '%s' "$input" | jq -r --arg k "$key" '.[$k] // empty' 2>/dev/null)
  elif command -v python3 >/dev/null 2>&1; then
    val=$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    v = json.load(sys.stdin).get(sys.argv[1], "")
    print(v if isinstance(v, str) else "")
except Exception:
    pass' "$key" 2>/dev/null)
  else
    val=$(printf '%s' "$input" | tr -d '\n' | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p")
  fi
  printf '%s' "${val:--}"
}

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
line=$(printf '%s\t%s\ttool=%s\tsession=%s\tcwd=%s' \
  "$ts" "$(field hook_event_name)" "$(field tool_name)" "$(field session_id)" "$(field cwd)")

# Write to every location we can; any one of them succeeding is enough.
targets=(/tmp/hook-probe.log)
[ -n "${CLAUDE_PROJECT_DIR:-}" ] && targets+=("$CLAUDE_PROJECT_DIR/.hook-probe.log")
[ -n "${CLAUDE_PLUGIN_DATA:-}" ] && mkdir -p "$CLAUDE_PLUGIN_DATA" 2>/dev/null && targets+=("$CLAUDE_PLUGIN_DATA/hook-probe.log")

for f in "${targets[@]}"; do
  printf '%s\n' "$line" >>"$f" 2>/dev/null || true
done

exit 0
