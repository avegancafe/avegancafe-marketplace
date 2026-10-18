# avegancafe

Kyle's personal Claude Code plugin — a home for one-off skills that don't
warrant a plugin of their own.

## Install

```bash
/plugin install avegancafe --marketplace avegancafe/avegancafe-marketplace
```

## Skills

| Skill | Purpose |
|-------|---------|
| `work-notes-vault` | Kyle's private Obsidian work vault, [`avegancafe/notes--work`](https://github.com/avegancafe/notes--work) (expected at `~/workspace/notes--work/`): locating/refreshing it, its layout, and its weekly-synced **Granola meeting archive** (`granola/notes/`, `.md` + raw `.json`) — schema, `rg`/`jq` mining recipes, freshness limits, and what not to touch. Lets Claude "mine my Granola meetings for X" from any working directory; the vault's own `.claude/CLAUDE.md` stays the authority on its conventions. No meeting content lives here — only the archive's structure. |
| `side-quest` | Keeps a session on task without losing tangential findings. When Claude is about to wrap up a task during which it noticed a worthwhile problem outside its scope — an unrelated bug, a missing permission check, a swallowed exception, a stale test, a broken README step — it asks once (fork / note / skip) and carries on. Fork runs `claude --bg --resume "$CLAUDE_CODE_SESSION_ID" --fork-session --name "fix(Scope): summary" "<scoped prompt>"`: a named background session that inherits the whole conversation and fixes it in the same folder. A `Stop` hook (`hooks/side-quest-stop.sh`) backs up the trigger: when a reply defers such a finding ("separately…", "left it alone…") and the skill wasn't used, it asks Claude once whether it's a real side quest. Blockers, already-requested work, in-diff typos, tracked issues and taste nits are handled in place. |

## Mods

| Mod | Purpose |
|-----|---------|
| `session-title` | Keeps the session title in `feat\|fix\|chore(Scope): imperative summary` form (e.g. `feat(ClaudePlugins): auto-name sessions by convention`). Haiku titles the first prompt synchronously; after each main-thread turn a background Haiku pass sharpens the title from the conversation so far, and the result lands on your next prompt (titles can only be set as a prompt is submitted). Renaming the session by hand pauses it. `/session-title` shows the current title; `/session-title lock` / `unlock` toggles it. |
