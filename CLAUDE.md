# CLAUDE.md — avegancafe-marketplace

Guidance for Claude Code when working **on this repository**.

## What this repo is

A Claude Code **plugin marketplace** — a thin index that points at the actual plugin repos. It contains no plugin code itself.

## Layout

```
.claude-plugin/marketplace.json   # The index: name, owner, and the plugins[] list. REQUIRED.
README.md
```

## How it references plugins

Each entry in `plugins[]` uses a `url` source pointing at the plugin's **own private repo** over SSH:

```json
{
  "name": "kitchen-brigade",
  "source": { "source": "url", "url": "git@github.com:avegancafe/kitchen-brigade.git" },
  "version": "1.0.0",
  "description": "..."
}
```

The plugins are NOT vendored here — they live in separate repos (`avegancafe/kitchen-brigade`, `avegancafe/avegancafe`).

## Rules when editing

- **Keep each `version` in sync** with the `version` in that plugin repo's `.claude-plugin/plugin.json`. When a plugin is released, bump it here too.
- **Use SSH `git@github.com:...` URLs** (all repos are private; SSH is the configured auth). Don't rewrite them to HTTPS.
- **Adding a plugin** = add an entry to `plugins[]`. The `name` must match the plugin's `plugin.json` `name`.
- Validate JSON before committing (e.g. `python3 -m json.tool .claude-plugin/marketplace.json`).
