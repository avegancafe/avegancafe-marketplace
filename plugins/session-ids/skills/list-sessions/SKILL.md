---
name: list-sessions
description: List all known Claude Code sessions and their readable ids from the session-ids state directory. Use when the user asks what sessions exist, wants to look up which readable id maps to which session, or needs to resolve an [assignee:<id>] link from a _projects/ todo.md back to a session.
---

# List known sessions

The session-ids plugin keeps one record per session in
`${CLAUDE_SESSION_IDS_DIR:-$HOME/.claude/session-ids}/`.

## Steps

1. Run:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/session-info.sh" --list
   ```

   Output is one session per line: `readable_id`, `session_id` (UUID), and
   `started_at`, tab-separated.

2. Present it as a small table, most recent first. If the user is resolving
   an `[assignee:<id>]` link from a todo.md, match on the `readable_id`
   column and offer the full record
   (`session-info.sh <session_id>`) for details.

## Notes

- Records are per machine and per user (`$HOME`); sessions from other
  machines won't appear.
- Ids are random per session and not guaranteed globally unique across a
  long history — when two sessions collide on the same readable id, use
  `started_at` and the session UUID to disambiguate.
