# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-06-30

### Changed
- Bumped `kitchen-brigade` and `avegancafe` entries to `1.0.2`.
- `dinner-rush` skill moved from `avegancafe` to `kitchen-brigade`; entry descriptions updated to match.

## [1.0.1] - 2026-06-30

### Added
- Standard OSS community files: `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- `.claude/patterns/` pattern library with a table of contents maintained in `CLAUDE.md`.
- `metadata.version` to `marketplace.json`.

### Changed
- `CLAUDE.md` rewritten to lead with critical rules (version bumping, version sync) and serve as the pattern-library ToC.
- Bumped `kitchen-brigade` and `avegancafe` plugin entries to `1.0.1`.

## [1.0.0] - 2026-06-30

### Added
- Initial marketplace indexing two plugins: `kitchen-brigade` and `avegancafe` (in the `avegancafe-plugin` repo), both via SSH `url` sources.
