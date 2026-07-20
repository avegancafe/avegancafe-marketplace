# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-17

### Added
- Two new plugins, vendored in this repo under `plugins/` and referenced with
  relative-path sources:
  - **`projects` (1.0.0)** — manages a `_projects/` folder: date-prefixed project
    directories (`YYYY-MM-DD--<name>`), each with a `todo.md` (checkbox todos,
    `@high`/`@medium`/`@low` priority mentions, `[assignee:<id>]` links) and a
    README.md for small notes capped at 256 lines. Initialization writes the
    top-level `_projects/README.md` conventions doc and a `CLAUDE.md` symlink
    pointing at it. Skills: `init-projects`, `new-project`, `project-todos`.
  - **`session-ids` (1.0.0)** — a SessionStart hook that gives every session a
    readable adjective-noun id (e.g. `brave-otter`), persists a per-session
    record, and injects the id into context; resumes keep their id. Skill
    library: `session-id`, `session-info`, `list-sessions`. Ids double as
    assignee ids for `projects` todo files.

### Changed
- The repo is no longer a *pure* index: plugins can now also be vendored under
  `plugins/`. README and CLAUDE.md updated to document the hybrid layout.

## [1.0.4] - 2026-06-30

### Changed
- Switched repo documentation to first person ("my"/"I") throughout — README and marketplace/plugin-entry descriptions. Bumped both plugin entries to match their repos' new versions (`kitchen-brigade` → `1.0.3`, `avegancafe` → `1.0.4`).

## [1.0.3] - 2026-06-30

### Changed
- Reframed the `avegancafe` plugin as a portable grab-bag of personal tooling (catch-all) and bumped its entry to `1.0.3`.

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
