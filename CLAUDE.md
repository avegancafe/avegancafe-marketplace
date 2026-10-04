# CLAUDE.md — avegancafe-marketplace

Guidance for Claude Code when working **on this repository**.

---

## ⚠️ CRITICAL — read before any change

1. **Bump the version on EVERY change to this repo.** Update `metadata.version` in
   [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) (semver) and
   add a matching entry to [`CHANGELOG.md`](CHANGELOG.md). Docs-only changes bump
   the patch version too.
2. **Don't hand-edit plugin entry versions — they sync automatically.** When a
   plugin's version changes on its `main`, `.github/workflows/sync-plugin-versions.yml`
   sets that entry's `version`, bumps `metadata.version` (patch), adds a CHANGELOG
   entry, and commits to `main` as `github-actions[bot]`:
   - **External plugins** (own repos) trigger it with a `plugin-released`
     repository_dispatch sent by their own `release.yml`, authenticated by their
     `MARKETPLACE_DISPATCH_TOKEN` secret (fine-grained PAT, this repo only,
     Contents: read & write).
   - **Vendored plugins** (`plugins/*`) trigger it when their `plugin.json` changes
     on `main`.
   - To resync by hand: Actions → *Sync plugin versions* → Run workflow (name +
     version, or blank to sync every vendored plugin), or run
     `scripts/sync-plugin-version.sh <name> <version>` locally.
   The marketplace must never advertise a version the plugin doesn't have; if an
   entry looks stale, check that plugin's last `release.yml` run first.
3. **Use SSH `git@github.com:...` URLs.** All repos are private; SSH is the
   configured auth. Don't rewrite sources to HTTPS.

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

A Claude Code **plugin marketplace**. It's primarily an index pointing at
external plugin repos, but some plugins are **vendored directly in this repo**
under `plugins/` and referenced with relative-path sources.

## Layout

```
.claude-plugin/marketplace.json   # The index: name, owner, metadata, plugins[]. REQUIRED.
.claude/patterns/                 # Durable repo patterns (see ToC above)
.github/workflows/ci.yml          # Validate index + vendored plugins, version sync, shellcheck
.github/workflows/sync-plugin-versions.yml  # Auto-sync entry versions (see rule 2)
scripts/sync-plugin-version.sh    # The sync itself: entry version + metadata bump + CHANGELOG
plugins/                          # Plugins vendored in this repo
  projects/                       # _projects/ folder manager (skills + scripts)
  session-ids/                    # readable session ids (SessionStart hook + skills)
README.md
```

## How it references plugins

External plugins use a `url` source pointing at the plugin's **own private
repo** over SSH — those are NOT vendored here (`avegancafe/kitchen-brigade`
and `avegancafe/beadwork`).

```json
{
  "name": "kitchen-brigade",
  "source": { "source": "url", "url": "git@github.com:avegancafe/kitchen-brigade.git" },
  "version": "1.0.1"
}
```

> Note: `beadwork` was the `avegancafe` grab-bag plugin (repo
> `avegancafe/avegancafe-plugin`) until 2.0.0, when it became a dedicated beads
> plugin. GitHub redirects the old repo URL, but sources use the new one.

Vendored plugins (`projects`, `session-ids`) use a relative-path source:

```json
{
  "name": "projects",
  "source": "./plugins/projects",
  "version": "1.0.0"
}
```

## Editing rules

- Adding a plugin = add an entry to `plugins[]`; `name` must match the plugin's `plugin.json` `name`.
- For vendored plugins, the "keep versions in sync" rule applies to
  `plugins/<name>/.claude-plugin/plugin.json` in this repo — bump it and the
  marketplace entry together.
- Validate JSON before committing: `python3 -m json.tool .claude-plugin/marketplace.json`.
