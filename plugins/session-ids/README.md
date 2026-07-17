# session-ids

A Claude Code plugin that gives every session a readable id — two random
words joined with a dash, adjective first, noun second (e.g. `brave-otter`,
`quiet-harbor`).

## How it works

- A **SessionStart hook** (`hooks/hooks.json` →
  `scripts/generate-session-id.sh`) runs at the start of every session. It
  generates the id, persists a per-session JSON record, and injects the id
  into the session's context so Claude always knows it.
- Resuming a session (`resume` / `clear` / `compact`) **keeps** its existing
  id; only genuinely new sessions get a new one.
- State lives in `${CLAUDE_SESSION_IDS_DIR:-$HOME/.claude/session-ids}/`:
  one `<session_id>.json` per session plus a `latest` symlink.

Record shape:

```json
{
  "readable_id": "brave-otter",
  "session_id": "3f2c9e9a-…",
  "started_at": "2026-07-17T17:00:00Z",
  "last_seen_at": "2026-07-17T18:30:00Z",
  "source": "resume",
  "cwd": "/home/user/some-repo"
}
```

## Skill library

| Skill | Purpose |
|-------|---------|
| `session-id` | Retrieve the current session's readable id. |
| `session-info` | Full details on the current session (id, UUID, times, source, cwd). |
| `list-sessions` | List all known sessions and their ids; resolve `[assignee:<id>]` links. |

## Pairs with the `projects` plugin

The readable id doubles as an **assignee id**: todos in a `_projects/`
`todo.md` link assignees as `[assignee:brave-otter]`.
