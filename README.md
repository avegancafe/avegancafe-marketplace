# avegancafe-marketplace

My personal [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin marketplace.

## Add the marketplace

```bash
/plugin marketplace add avegancafe/avegancafe-marketplace
```

## Plugins

| Plugin | Description |
|--------|-------------|
| [**kitchen-brigade**](https://github.com/avegancafe/kitchen-brigade) | Lean, stack-agnostic multi-agent orchestration modeled on the brigade de cuisine. `/chef` routes to strategize / implement / workflow / diagnose; the chef runs the cast (sous-chef, cook, expediter). |
| [**beadwork**](https://github.com/avegancafe/beadwork) | Beads (`bd`) toolkit: a live pane (mod) with Claude's task list + open beads, capture/triage logging, tight bead titles, and a parent-epic-status hook. |
| [**projects**](plugins/projects) | Manages a `_projects/` folder: date-prefixed project dirs (`YYYY-MM-DD--<name>`), each with a `todo.md` (`@priority` mentions, `[assignee:<id>]` links) and a <256-line notes README. Vendored in this repo. |
| [**session-ids**](plugins/session-ids) | Gives every session a readable adjective-noun id (e.g. `brave-otter`) via a `SessionStart` hook, plus skills to retrieve session info. Vendored in this repo. |
| [**notes-work**](plugins/notes-work) | Knows Kyle's private Obsidian work vault (`avegancafe/notes--work`): its layout, and how to mine its weekly-synced Granola meeting archive with `rg`/`jq`. Vendored in this repo. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install beadwork@avegancafe-marketplace
/plugin install projects@avegancafe-marketplace
/plugin install session-ids@avegancafe-marketplace
/plugin install notes-work@avegancafe-marketplace
```

Then restart Claude Code.

> **Note:** the marketplace and the external plugin repos are **private**. Adding/installing clones them over your GitHub SSH access (`git@github.com:avegancafe/...`). The `projects`, `session-ids`, and `notes-work` plugins live in this repo under [`plugins/`](plugins/) and install straight from the marketplace clone.
