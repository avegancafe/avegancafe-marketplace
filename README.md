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
| [**session-management**](https://github.com/avegancafe/session-management) | Auto-names sessions in `feat\|fix\|chore(Scope): imperative summary` form from your first prompt; `/autoname` re-titles from the session history. Public. |
| [**hook-probe**](plugins/hook-probe) | Diagnostic: logs every SessionStart, UserPromptSubmit, PostToolUse and Stop hook to `/tmp/hook-probe.log` so you can check whether plugin hooks fire somewhere (e.g. Claude Tag). Vendored in this repo. |
| [**avegancafe**](plugins/avegancafe) | My personal plugin for one-off skills. Ships `work-notes-vault` (knows my private Obsidian work vault, `avegancafe/notes--work`, and how to mine its weekly-synced Granola meeting archive with `rg`/`jq`). Vendored in this repo. `side-quest` moved to `j2-sandbox`; `session-title` moved to `session-management`. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install beadwork@avegancafe-marketplace
/plugin install session-management@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
/plugin install hook-probe@avegancafe-marketplace
```

Then restart Claude Code.

> **Note:** the marketplace, `kitchen-brigade` and `session-management` are public; `beadwork` is private. `session-management` installs over HTTPS, so anyone can add it. The other external plugins clone over your GitHub SSH access (`git@github.com:avegancafe/...`), so they need an SSH key on GitHub (and, for `beadwork`, repo access). The `avegancafe` plugin lives in this repo under [`plugins/`](plugins/) and installs straight from the marketplace clone.
