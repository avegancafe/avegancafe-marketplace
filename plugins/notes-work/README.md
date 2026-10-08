# notes-work

A Claude Code plugin that teaches Claude about Kyle's private Obsidian work vault,
[`avegancafe/notes--work`](https://github.com/avegancafe/notes--work) (expected
locally at `~/workspace/notes--work/`).

The vault's own `.claude/CLAUDE.md` stays the authority on its conventions; this
plugin exists so Claude knows the vault — and especially its weekly-synced
**Granola meeting archive** (`granola/notes/`) — exists *outside* that repo, e.g.
when asked to "mine my Granola meetings for X" from any working directory.

## Install

```bash
/plugin install notes-work --marketplace avegancafe/avegancafe-marketplace
```

## Skills

| Skill | Purpose |
|-------|---------|
| `work-notes-vault` | Locate/refresh the vault, its layout, the Granola archive's file layout and schema (`.md` + raw `.json`), `rg`/`jq` mining recipes, freshness limits, and what not to touch. |

No meeting content lives in this plugin — only the archive's structure. The
vault itself is private.
