# Contributing to avegancafe-marketplace

This repo is a Claude Code **plugin marketplace**: a thin index that points at the
plugin repos. It holds no plugin code, and CI fails if any shows up
([`scripts/check-index-only.sh`](scripts/check-index-only.sh)).

## Changing a plugin

Open the PR on **that plugin's own repo** (each entry's `source.url` in
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) names it), and
bump `version` in its `.claude-plugin/plugin.json`. Merging the bump to its `main`
is the release: its `release.yml` tells this repo, and the *Sync plugin versions*
workflow updates the entry, `metadata.version` and this CHANGELOG on `main` by
itself. Nothing to do here.

## Golden rule: bump the version

**Every change to this repo bumps the version**, including docs. Update, together,
in one PR:

1. `metadata.version` in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) (semver)
2. A new entry in [`CHANGELOG.md`](CHANGELOG.md)

**Plugin entry versions are not yours to bump**; the sync owns them (rule 3 in
[`CLAUDE.md`](CLAUDE.md)).

## Adding a plugin

1. Make the plugin its own repo (new ones are named `avegancafe/claude-plugin-<name>`).
2. Copy `release.yml` from an existing plugin repo (e.g.
   `avegancafe/claude-plugin-duet`, `.github/workflows/release.yml`) and set its
   `MARKETPLACE_DISPATCH_TOKEN` secret (`gh secret set MARKETPLACE_DISPATCH_TOKEN -R avegancafe/<repo>`,
   same fine-grained PAT: this repo only, Contents read & write). Without it the
   entry silently stops tracking releases.
3. Add an entry to `plugins[]` here with an HTTPS `url` source
   (`https://github.com/avegancafe/<repo>.git`; SSH only for a private repo). The
   `name` must match the plugin's `plugin.json` `name`, and `version` its current
   version (once, when adding it; the sync keeps it current after that).
4. Add it to the README's plugin table and bump the marketplace version.

## Validation

```bash
claude plugin validate .
scripts/check-index-only.sh
find scripts -name '*.sh' -print0 | xargs -0 -r shellcheck
```

CI runs these on every PR (`.github/workflows/ci.yml`), plus a check that
`metadata.version` matches the newest CHANGELOG entry.

## Testing

```bash
/plugin marketplace add avegancafe/avegancafe-marketplace
/plugin install kitchen-brigade@avegancafe-marketplace
```

See [`CLAUDE.md`](CLAUDE.md) for the full maintainer guide and the pattern-library table of contents.
