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
| [**avegancafe**](plugins/avegancafe) | My personal plugin for one-off skills. Ships `work-notes-vault`: knows my private Obsidian work vault (`avegancafe/notes--work`) and how to mine its weekly-synced Granola meeting archive with `rg`/`jq`. Vendored in this repo. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install beadwork@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
```

Then restart Claude Code.

> **Note:** the marketplace and the external plugin repos are **private**. Adding/installing clones them over your GitHub SSH access (`git@github.com:avegancafe/...`). The `avegancafe` plugin lives in this repo under [`plugins/`](plugins/) and installs straight from the marketplace clone.
