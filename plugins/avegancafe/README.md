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
| `hifi-h2` | Tags store-bought FLACs from MusicBrainz (full tags, 500×500 baseline cover, `NN - Title` names), audits the Rockbox HIFI H2 library for tracks that would land under `<Untagged>` (missing album artist, ID3v1-only, truncated titles), and covers mounting, copying and the Rockbox database rebuild. |
`side-quest` moved to the `j2-sandbox` plugin in 2.0.0 (skill + `Stop` hook).
The `session-title` mod (`/session-title`, `/autoname`) moved to its own public plugin,
[`session-management`](https://github.com/avegancafe/session-management), in 3.0.0.

