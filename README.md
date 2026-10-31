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
| [**linear-todos**](https://github.com/avegancafe/linear-todos) | Manage my Linear TODO team from Claude Duet through the Linear connector: add todos from plain text (`eod`, `eow`, `!high`), list, done, snooze, and the morning digest and evening review. Install it to your claude.ai chat plugins (not Claude Code). |
| [**juliet**](plugins/juliet) | Shared Claude tooling for [Juliet](https://github.com/avegancafe/Juliet), the scripted macOS + Fedora setup: the `noelle` agent and the Juliet config skills it preloads. The baseline for anyone running Juliet. Vendored in this repo. |
| [**duet**](plugins/duet) | How Claude Duet works, for the agents running inside it: where plugins come from and when they load, threads vs sessions, and how a channel's repos are attached. Install it to your claude.ai chat plugins (not Claude Code). Grows as Duet behavior is learned. Vendored in this repo. |
| [**avegancafe**](plugins/avegancafe) | My personal plugin for one-off skills. Ships `work-notes-vault` (knows my private Obsidian work vault, `avegancafe/notes--work`, and how to mine its weekly-synced Granola meeting archive with `rg`/`jq`). Vendored in this repo. `side-quest` moved to a work plugin; `session-title` moved to `session-management`. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install beadwork@avegancafe-marketplace
/plugin install session-management@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
/plugin install juliet@avegancafe-marketplace
```

Then restart Claude Code.

**duet** and **linear-todos** are the exceptions: they're for Claude Duet, which loads your claude.ai chat plugins, not Claude Code ones. Install them from this marketplace in your claude.ai chat plugins (it's linked as an account marketplace), then start a new Duet thread to pick them up.

> **Note:** the marketplace and every plugin repo (`kitchen-brigade`, `beadwork`, `session-management`, `linear-todos`) are public, and the external plugins install over HTTPS, so anyone can add them. The `avegancafe`, `juliet` and `duet` plugins live in this repo under [`plugins/`](plugins/) and installs straight from the marketplace clone.
