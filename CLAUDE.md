# CLAUDE.md — avegancafe-marketplace

Guidance for Claude Code when working **on this repository**.

---

## ⚠️ CRITICAL — read before any change

1. **This repo is the marketplace index and nothing else.** It holds the manifest
   ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)), its docs
   and its CI. **New plugins, and new functionality for existing plugins (skills,
   agents, commands, hooks, mods, MCP config), go in each plugin's own repo**,
   never here. Adding a plugin means making its repo first (new ones are named
   `avegancafe/claude-plugin-<name>`), then adding an entry here that points at it.
   No `plugins/` folder, no plugin content, no local path sources:
   [`scripts/check-index-only.sh`](scripts/check-index-only.sh) fails CI if any
   of these appear.
2. **Bump the version on EVERY change to this repo.** Update `metadata.version` in
   [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) (semver) and
   add a matching entry to [`CHANGELOG.md`](CHANGELOG.md). Docs-only changes bump
   the patch version too.
3. **Don't hand-edit plugin entry versions — they sync automatically.** When a
   plugin's version changes on its repo's `main`, its own `release.yml` sends a
   `plugin-released` repository_dispatch (authenticated by that repo's
   `MARKETPLACE_DISPATCH_TOKEN` secret: fine-grained PAT, this repo only, Contents:
   read & write). `.github/workflows/sync-plugin-versions.yml` then sets that
   entry's `version`, bumps `metadata.version` (patch), adds a CHANGELOG entry, and
   commits to `main` as `github-actions[bot]`.
   - To resync by hand: Actions → *Sync plugin versions* → Run workflow (name +
     version), or run `scripts/sync-plugin-version.sh <name> <version>` locally.
   The marketplace must never advertise a version the plugin doesn't have; if an
   entry looks stale, check that plugin's last `release.yml` run first.
4. **Public plugin repos use HTTPS sources** (`https://github.com/avegancafe/<repo>.git`)
   so people without a GitHub SSH key can install them. All current plugins are
   public. Only a private plugin repo would use an SSH `git@github.com:...` URL.

---

## 📚 Pattern library — `.claude/patterns/`

Durable patterns for this repo live in [`.claude/patterns/`](.claude/patterns/).
**This section is their table of contents — keep it in sync whenever a pattern
file is added, renamed, or removed.**

| Pattern | What it covers |
|---------|----------------|
| _(none yet)_ | Add patterns via the `/learn` skill, or by hand into `.claude/patterns/<slug>.md`, then list them here. |

See [`.claude/patterns/README.md`](.claude/patterns/README.md) for the convention.

---

## What this repo is

A Claude Code **plugin marketplace**: an index pointing at plugin repos. It holds
no plugin code.

## Layout

```
.claude-plugin/marketplace.json   # The index: name, owner, metadata, plugins[]. REQUIRED.
.claude/patterns/                 # Durable repo patterns (see ToC above)
.github/workflows/ci.yml          # Validate index, index-only check, version vs CHANGELOG, shellcheck
.github/workflows/sync-plugin-versions.yml  # Auto-sync entry versions (see rule 3)
scripts/sync-plugin-version.sh    # The sync itself: entry version + metadata bump + CHANGELOG
scripts/check-index-only.sh       # Fails on plugin content or local path sources (see rule 1)
README.md, CONTRIBUTING.md, CHANGELOG.md
```

## Plugins and their repos

| Plugin | Repo |
|--------|------|
| `kitchen-brigade` | `avegancafe/kitchen-brigade` |
| `beadwork` | `avegancafe/beadwork` |
| `session-management` | `avegancafe/session-management` |
| `linear-todos` | `avegancafe/linear-todos` |
| `avegancafe` | `avegancafe/claude-plugin-avegancafe` |
| `juliet` | `avegancafe/claude-plugin-juliet` |
| `duet` | `avegancafe/claude-plugin-duet` |
| `hairline` | `avegancafe/claude-plugin-hairline` |
| `task-graph` | `avegancafe/claude-plugin-task-graph` |
| `ascii-magic-art` | `avegancafe/ascii-magic-art` (a fork of upstream, so it keeps upstream's name) |

`avegancafe`, `juliet` and `duet` were vendored here under `plugins/` until
marketplace 3.10.0; each moved to its own repo with its history.

> Note: `beadwork` was the `avegancafe` grab-bag plugin (repo
> `avegancafe/avegancafe-plugin`) until 2.0.0, when it became a dedicated beads
> plugin. GitHub redirects the old repo URL, but sources use the new one. The
> current `avegancafe` plugin (added in marketplace 2.0.0) is a new, unrelated
> plugin that reuses the name.

Every entry uses a `url` source:

```json
{
  "name": "duet",
  "source": { "source": "url", "url": "https://github.com/avegancafe/claude-plugin-duet.git" },
  "version": "0.3.0"
}
```

Adding a plugin also means wiring its release notification — see "Adding a plugin"
in [`CONTRIBUTING.md`](CONTRIBUTING.md); without it the entry's version silently
stops tracking releases.

## Editing rules

- Adding a plugin = make its repo, then add an entry to `plugins[]`; `name` must
  match the plugin's `plugin.json` `name` and `version` its current version.
- Changing a plugin = a PR on that plugin's repo, not here. Its version bump
  reaches this index through the sync.
- Validate before committing: `claude plugin validate .` and
  `scripts/check-index-only.sh`.
