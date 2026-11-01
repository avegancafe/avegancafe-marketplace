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
| [**juliet**](https://github.com/avegancafe/claude-plugin-juliet) | Shared Claude tooling for [Juliet](https://github.com/avegancafe/Juliet), the scripted macOS + Fedora setup: the `noelle` agent and the Juliet config skills it preloads. The baseline for anyone running Juliet. |
| [**duet**](https://github.com/avegancafe/claude-plugin-duet) | How Claude Duet works, for the agents running inside it: where plugins come from and when they load, threads vs sessions, how a channel's repos are attached, and when complex work gets its own channel. Install it to your claude.ai chat plugins (not Claude Code). Grows as Duet behavior is learned. |
| [**avegancafe**](https://github.com/avegancafe/claude-plugin-avegancafe) | My personal plugin for one-off skills: `work-notes-vault` (my private Obsidian work vault and its Granola archive), `/slurp` (voice recorder transcripts), `hifi-h2` (music onto my Rockbox player), `phone-push` (push notifications to my phone) and `flipper-usb` (Flipper Zero over USB). |
| [**hairline**](https://github.com/avegancafe/claude-plugin-hairline) | Hairline figures: isometric line-drawing animations that answer the pointer, as one self-contained HTML file. `hairline-create` draws one from an idea; `hairline-adopt` rebuilds an SVG as one. From Lucas Marques' MIT-licensed hairline skills. |
| [**ascii-magic-art**](https://github.com/avegancafe/ascii-magic-art) | 734 animated ASCII art pieces (MIT, a fork of kailashsr38/ascii-magic-art) plus two skills: `embed-ascii-art` puts a piece on a web page, README or terminal, self-hosted and themed to the page; `make-ascii-piece` writes a new one by hand, as lettering, or from a photo. |
| [**task-graph**](https://github.com/avegancafe/claude-plugin-task-graph) | A live task graph pane you and Claude edit together: Claude records, claims and completes the outcomes you ask for, and your edits in the pane reach it. A mod. |

## Install a plugin

```bash
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install beadwork@avegancafe-marketplace
/plugin install session-management@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
/plugin install juliet@avegancafe-marketplace
/plugin install hairline@avegancafe-marketplace
/plugin install task-graph@avegancafe-marketplace
/plugin install ascii-magic-art@avegancafe-marketplace
```

Then restart Claude Code.

**duet** and **linear-todos** are the exceptions: they're for Claude Duet, which loads your claude.ai chat plugins, not Claude Code ones. Install them from this marketplace in your claude.ai chat plugins (it's linked as an account marketplace), then start a new Duet thread to pick them up.

> **Note:** the marketplace and every plugin repo are public, and every plugin installs over HTTPS from its own repo, so anyone can add them. This repo is only the index: plugin code and changes live in each plugin's repo (see [CONTRIBUTING.md](CONTRIBUTING.md)).
