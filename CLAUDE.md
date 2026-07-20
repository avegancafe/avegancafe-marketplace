# CLAUDE.md — avegancafe-marketplace

Guidance for Claude Code when working **on this repository**.

---

## ⚠️ CRITICAL — read before any change

1. **Bump the version on EVERY change to this repo.** Update `metadata.version` in
   [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) (semver) and
   add a matching entry to [`CHANGELOG.md`](CHANGELOG.md). Docs-only changes bump
   the patch version too.
2. **Keep each plugin entry's `version` in sync** with the `version` in that
   plugin repo's `.claude-plugin/plugin.json`. When a plugin releases, bump its
   entry here in the same change. The marketplace must never advertise a version
   the plugin repo doesn't have.
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
plugins/                          # Plugins vendored in this repo
  projects/                       # _projects/ folder manager (skills + scripts)
  session-ids/                    # readable session ids (SessionStart hook + skills)
README.md
```

## How it references plugins

External plugins use a `url` source pointing at the plugin's **own private
repo** over SSH — those are NOT vendored here (`avegancafe/kitchen-brigade`
and `avegancafe/avegancafe-plugin`).

```json
{
  "name": "kitchen-brigade",
  "source": { "source": "url", "url": "git@github.com:avegancafe/kitchen-brigade.git" },
  "version": "1.0.1"
}
```

> Note: the `avegancafe` plugin lives in the **`avegancafe-plugin`** repo
> (`avegancafe/avegancafe` is taken by the GitHub profile README). The plugin's
> installable name is still `avegancafe`.

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
