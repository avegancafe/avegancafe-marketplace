---
name: session-info
description: Report full info about the current Claude Code session — readable id (adjective-noun), session UUID, start time, last-seen time, how the session started (startup/resume/clear/compact), and working directory. Use when the user asks about the current session, "what session is this", when it started, or wants session details beyond just the id.
---

# Get info about the current session

The session-ids plugin's SessionStart hook stores a JSON record per session.

## Steps

1. Get the record:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/session-info.sh" [session_id]
   ```

   Without an argument it prints the most recently started/resumed session's
   record. If the session UUID is known from injected context (the hook's
   `session_id: <uuid>` line), pass it explicitly — that's exact even when
   several sessions run concurrently.

2. Report the fields in plain language:

   | Field | Meaning |
   |-------|---------|
   | `readable_id` | The session's readable adjective-noun id |
   | `session_id` | Claude Code's session UUID |
   | `started_at` | When the id was first generated (UTC) |
   | `last_seen_at` | Last SessionStart event (startup or resume) |
   | `source` | How the session last started: `startup`, `resume`, `clear`, `compact` |
   | `cwd` | Working directory at session start |

3. Supplement with live environment facts when relevant: current working
   directory, git branch (`git branch --show-current`), and anything else
   the user asked about.

## Notes

- If the state directory is missing, the hook hasn't run (plugin just
  installed?) — say so and suggest restarting the session.
