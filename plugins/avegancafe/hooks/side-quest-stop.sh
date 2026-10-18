#!/usr/bin/env bash
# Stop hook for the side-quest skill. If the final reply defers an out-of-scope
# finding ("separately…", "outside this task…", "left it alone…") and side-quest
# wasn't invoked since the user's last prompt, block once and let Claude decide
# whether it's a real side quest. Fails open: any missing input → exit 0.
command -v jq >/dev/null || exit 0
input=$(cat)
[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0
last=$(jq -r '.last_assistant_message // empty' <<<"$input")
[ -n "$last" ] || exit 0
pat='separately|separate (problem|issue|bug|thing)|outside (the |this )?(task|scope|change)|out of scope|unrelated to (this|the|your) (task|change)|want me to (fix|add|address|patch)|you may want to|if you.d like|worth (fixing|adding|a follow-up)|(didn.t|did not|haven.t) (change|fix|touch|look into)|left (it|that|this|them|both|those) (alone|as[- ]is|as it was|unchanged)|(wasn.t|was not|isn.t|not) part of (this|the) (task|fix|change)|(noticed|found) but (didn.t|did not)|already (broken|there)|before this change'
grep -qiE "$pat" <<<"$last" || exit 0
tp=$(jq -r '.transcript_path // empty' <<<"$input")
if [ -f "$tp" ]; then
  # Already invoked since the last real user prompt (skip meta/skill-body and tool-result entries)?
  invoked=$(jq -s '
    (map(.type == "user" and (.isMeta != true) and (.message.content | type == "string")) | rindex(true) // -1) as $i
    | .[($i + 1):]
    | any(.type == "assistant" and any(.message.content[]?; .type == "tool_use" and .name == "Skill" and ((.input.skill // "") | test("side-quest"))))
  ' "$tp" 2>/dev/null)
  [ "$invoked" = "true" ] && exit 0
fi
jq -n '{decision:"block", reason:"side-quest check: does your reply leave unfixed a real problem you found outside this task (a bug, risk, stale test or wrong doc) that is not already tracked, that the user did not ask you to only list, and that you did not already fix? If yes, invoke the side-quest skill now and follow it. If no, end your turn silently: output nothing more."}'
