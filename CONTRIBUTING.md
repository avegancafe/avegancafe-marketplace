# Contributing to avegancafe-marketplace

This repo is a Claude Code **plugin marketplace** — a thin index that points at the
plugin repos. It holds no plugin code.

## Golden rule: bump the version

**Every change bumps the version** — including docs. Update, together, in one PR:

1. `metadata.version` in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) (semver)
2. A new entry in [`CHANGELOG.md`](CHANGELOG.md)

When a **plugin** releases, also bump that plugin's entry `version` here so the
marketplace and the plugin's own `plugin.json` always agree.

## Adding or updating a plugin

- Add/edit an entry in `plugins[]`. The `name` must match the plugin's `plugin.json` `name`.
- Use an SSH `url` source: `git@github.com:avegancafe/<repo>.git` (all repos are private).
- Set `version` to match the plugin repo's current `plugin.json` version.

## Validation

```bash
python3 -m json.tool .claude-plugin/marketplace.json
```

## Testing

```bash
/plugin marketplace add avegancafe/avegancafe-marketplace
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install avegancafe@avegancafe-marketplace
```

See [`CLAUDE.md`](CLAUDE.md) for the full maintainer guide and the pattern-library table of contents.
