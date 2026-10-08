# Contributing to avegancafe-marketplace

This repo is a Claude Code **plugin marketplace** — a thin index that points at the
plugin repos. It holds no plugin code.

## Golden rule: bump the version

**Every change bumps the version** — including docs. Update, together, in one PR:

1. `metadata.version` in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) (semver)
2. A new entry in [`CHANGELOG.md`](CHANGELOG.md)

**Plugin entry versions are not yours to bump** — when a plugin releases, the
*Sync plugin versions* workflow updates its entry, `metadata.version`, and this
CHANGELOG on `main` by itself (see rule 2 in [`CLAUDE.md`](CLAUDE.md)).

## Adding or updating a plugin

- Add/edit an entry in `plugins[]`. The `name` must match the plugin's `plugin.json` `name`.
- Use an SSH `url` source: `git@github.com:avegancafe/<repo>.git` (all repos are private).
- Set `version` to match the plugin repo's current `plugin.json` version (once, when
  adding it; the sync keeps it current after that).
- **External plugin:** copy `release.yml` from `avegancafe/beadwork`
  (`.github/workflows/release.yml`) into the new repo and set its
  `MARKETPLACE_DISPATCH_TOKEN` secret (`gh secret set MARKETPLACE_DISPATCH_TOKEN -R avegancafe/<repo>`,
  same fine-grained PAT: this repo only, Contents read & write). Without it the
  entry silently stops tracking releases.
- **Vendored plugin** (`plugins/<name>/`): nothing extra — its `plugin.json` changing
  on `main` triggers the sync.

## Validation

```bash
claude plugin validate .                                  # the index
for p in plugins/*/; do claude plugin validate "$p"; done  # vendored plugins
find scripts plugins -name '*.sh' -print0 | xargs -0 -r shellcheck
```

CI runs all three on every PR (`.github/workflows/ci.yml`).

## Testing

```bash
/plugin marketplace add avegancafe/avegancafe-marketplace
/plugin install kitchen-brigade@avegancafe-marketplace
/plugin install beadwork@avegancafe-marketplace
```

See [`CLAUDE.md`](CLAUDE.md) for the full maintainer guide and the pattern-library table of contents.
