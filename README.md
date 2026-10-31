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
| [**juliet**](plugins/juliet) | Shared Claude tooling for [Juliet](https://github.com/avegancafe/Juliet), the scripted macOS + Fedora setup: the `noelle` agent and the Juliet config skills it preloads. The baseline for anyone running Juliet. Vendored in this repo. |
| [**duet**](plugins/duet) | How Claude Duet works, for the agents running inside it: where plugins come from and when they load, threads vs sessions, and how a channel's repos are attached. Install it to your claude.ai chat plugins (not Claude Code). Grows as Duet behavior is learned. Vendored in this repo. |
| [**avegancafe**](plugins/avegancafe) | My personal plugin for one-off skills. Ships `work-notes-vault` (knows my private Obsidian work vault, `avegancafe/notes--work`, and how to mine its weekly-synced Granola meeting archive with `rg`/`jq`). Vendored in this repo. `side-quest` moved to a work plugin; `session-title` moved to `session-management`. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install beadwork@avegancafe-marketplace
/plugin install session-management@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
/plugin install hook-probe@avegancafe-marketplace
/plugin install juliet@avegancafe-marketplace
/plugin install duet@avegancafe-marketplace
```

Then restart Claude Code.

> **Note:** the marketplace and every plugin repo (`kitchen-brigade`, `beadwork`, `session-management`) are public, and the external plugins install over HTTPS, so anyone can add them. The `avegancafe`, `juliet` and `duet` plugins live in this repo under [`plugins/`](plugins/) and installs straight from the marketplace clone.
