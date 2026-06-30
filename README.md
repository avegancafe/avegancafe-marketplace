# avegancafe-marketplace

Kyle's personal [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin marketplace.

## Add the marketplace

```bash
/plugin marketplace add avegancafe/avegancafe-marketplace
```

## Plugins

| Plugin | Description |
|--------|-------------|
| [**kitchen-brigade**](https://github.com/avegancafe/kitchen-brigade) | Lean, stack-agnostic multi-agent orchestration modeled on the brigade de cuisine. `/chef` routes to strategize / implement / workflow / diagnose; the chef runs the cast (sous-chef, cook, expediter). |
| [**avegancafe**](https://github.com/avegancafe/avegancafe-plugin) | Personal beads (`bd`) issue-tracking toolkit: capture/triage logging, tight bead titles, concurrency-aware posture, and a parent-epic-status `PostToolUse` hook. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
```

Then restart Claude Code.

> **Note:** the marketplace and both plugin repos are **private**. Adding/installing clones them over your GitHub SSH access (`git@github.com:avegancafe/...`).
