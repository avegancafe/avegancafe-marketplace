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
| [**avegancafe**](https://github.com/avegancafe/avegancafe-plugin) | Personal beads (`bd`) issue-tracking toolkit: capture/triage logging, tight bead titles, concurrency-aware posture, and a parent-epic-status `PostToolUse` hook. |
| [**projects**](plugins/projects) | Manages a `_projects/` folder: date-prefixed project dirs (`YYYY-MM-DD--<name>`), each with a `todo.md` (`@priority` mentions, `[assignee:<id>]` links) and a <256-line notes README. Vendored in this repo. |
| [**session-ids**](plugins/session-ids) | Gives every session a readable adjective-noun id (e.g. `brave-otter`) via a `SessionStart` hook, plus skills to retrieve session info. Vendored in this repo. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
/plugin install projects@avegancafe-marketplace
/plugin install session-ids@avegancafe-marketplace
```

Then restart Claude Code.

> **Note:** the marketplace and the external plugin repos are **private**. Adding/installing clones them over your GitHub SSH access (`git@github.com:avegancafe/...`). The `projects` and `session-ids` plugins live in this repo under [`plugins/`](plugins/) and install straight from the marketplace clone.
