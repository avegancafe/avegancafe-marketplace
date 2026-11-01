# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.12.0] - 2026-11-01

### Added
- `task-graph` plugin (0.2.0), from its own repo [`avegancafe/claude-plugin-task-graph`](https://github.com/avegancafe/claude-plugin-task-graph): a live task graph pane (a mod) that you and Claude edit together. It was a mod in Juliet until now; its history came with it.

## [3.11.0] - 2026-11-01

### Added
- `hairline` plugin (0.1.0), from its own repo [`avegancafe/claude-plugin-hairline`](https://github.com/avegancafe/claude-plugin-hairline): the `hairline-create` and `hairline-adopt` skills from Lucas Marques' MIT-licensed [`lucasmarkes/hairline`](https://github.com/lucasmarkes/hairline), plus a video renderer and a figure viewer template. Replaces the vendored copy proposed in #21.

## [3.10.3] - 2026-11-01

### Changed
- `linear-todos` entry → 0.3.0 (synced automatically from the plugin's release; was 0.2.0).

## [3.10.2] - 2026-10-31

### Changed
- `duet` entry → 0.3.1 (synced automatically from the plugin's release; was 0.3.0).

## [3.10.1] - 2026-10-31

### Changed
- `juliet` entry → 1.0.1 (synced automatically from the plugin's release; was 1.0.0).

## [3.10.0] - 2026-10-31

### Changed
- The marketplace is now index-only. `avegancafe`, `juliet` and `duet` moved, with their history, to their own repos (`avegancafe/claude-plugin-avegancafe`, `avegancafe/claude-plugin-juliet`, `avegancafe/claude-plugin-duet`), and their entries point there over HTTPS. Plugin names and versions are unchanged, so existing installs keep working; each plugin's next version bump installs from its new repo.
- The *Sync plugin versions* workflow only takes `plugin-released` dispatches from plugin repos (and manual runs with a name and version); the vendored `plugin.json` trigger and the blank "sync every vendored plugin" run are gone.
- CLAUDE.md, CONTRIBUTING.md and the README say new plugins and plugin changes go in each plugin's own repo, and this repo holds only the manifest, docs and CI.
- The `avegancafe` entry's description lists all five of its skills.

### Added
- `scripts/check-index-only.sh`, run in CI: fails if a `plugins/` folder or any plugin content (a `plugin.json`, or a `skills/`, `agents/`, `commands/` or `hooks/` folder) appears, or a manifest entry uses a local path source.

### Removed
- The vendored `plugins/` folder, and CI's per-plugin validation and shellcheck of it.

## [3.9.2] - 2026-10-31

### Changed
- `linear-todos` entry → 0.2.0 (synced automatically from the plugin's release; was 0.1.0).

## [3.9.1] - 2026-10-31

### Removed
- `hook-probe`: the one-off diagnostic plugin that logged hook events to check whether plugin hooks fire in Claude Tag. Its job is done; the plugin folder, manifest entry and README/CLAUDE.md mentions are gone.

## [3.9.0] - 2026-10-31

### Added
- `duet` 0.3.0: new `channels-for-complex-work` skill with Kyle's rule that complex operations with several coordinated tasks get their own channel, with each part run as a task (and its own session) on that channel's Tasks list, so the main chat stays conversational. Covers when to answer directly, use one thread or make a channel; how to brief the channel's Claude in the handover; and how the main chat steers the channel instead of doing its work. `duet-basics` points to it.

## [3.8.0] - 2026-10-31

### Added
- `linear-todos` 0.1.0 (external, `avegancafe/linear-todos`): a Claude Duet skill that manages Kyle's Linear TODO team through the Linear connector (add with the CLI's date rules and `!priority` marker, list, done, snooze, morning digest, evening review). Install it to claude.ai chat plugins.

## [3.7.0] - 2026-10-31

### Changed
- `duet` 0.2.0: `duet-basics` now covers channel instructions: lasting channel behavior is set there, the coordinator proposes changes with `propose_channel_instructions` and they apply only when the user taps Update, and a channel always uses a plugin agent only when its instructions say so.

## [3.6.1] - 2026-10-31

### Changed
- Docs: the root README no longer gives a Claude Code install command for `duet`; it says to install it in claude.ai chat plugins and start a new Duet thread.

## [3.6.0] - 2026-10-31

### Added
- `duet` 0.1.0, vendored under `plugins/duet`: skills on how Claude Duet works, for the agents running inside it, meant to be installed to claude.ai chat plugins. First skill, `duet-basics`: Duet loads claude.ai chat plugins (not Claude Code ones), plugins load at session start and each new thread is a fresh session, a channel's repos are readable by threads started after they're added (not the coordinator), and how to add new Duet learnings here by PR.

## [3.5.4] - 2026-10-31

### Changed
- `beadwork` entry → 2.4.1 (synced automatically from the plugin's release; was 2.4.0).

## [3.5.3] - 2026-10-31

### Changed
- The marketplace and `beadwork` are now public. `kitchen-brigade` and `beadwork` entries install over HTTPS like `session-management`, so no GitHub SSH key is needed; README, CLAUDE.md and CONTRIBUTING.md say so.

## [3.5.2] - 2026-10-31

### Changed
- Docs: dropped internal work-plugin and coworker names from the root and `avegancafe` READMEs, the `juliet-extension` skill and the 3.0.0 changelog entry; the README no longer claims the marketplace is public.

## [3.5.1] - 2026-10-31

### Changed
- `session-management` entry → 1.3.0 (synced automatically from the plugin's release; was 1.2.2).

## [3.5.0] - 2026-10-31

### Added
- `juliet` 1.0.0, vendored under `plugins/juliet`: the `noelle` agent and its six Juliet skills (`juliet-config`, `juliet-extension`, `juliet-cross-platform`, `juliet-bootstrap-step`, `add-app-config`, `add-fish-alias`), moved out of Juliet's stowed `~/.claude`. Noelle and `juliet-config` now say Claude primitives belong in this marketplace (shared Juliet baseline → `juliet`, personal → `avegancafe`), and to ask Kyle before publishing.

## [3.4.1] - 2026-10-31

### Changed
- `session-management` entry → 1.2.2 (synced automatically from the plugin's release; was 1.2.1).

## [3.4.0] - 2026-10-31

### Added
- `hook-probe` 0.1.0, vendored under `plugins/hook-probe`: a diagnostic plugin that logs every SessionStart, UserPromptSubmit, PostToolUse and Stop hook to `/tmp/hook-probe.log`, to check whether plugin hooks fire in Claude Tag.

## [3.3.16] - 2026-10-30

### Changed
- `avegancafe` entry → 3.7.0 (synced automatically from the plugin's release; was 3.6.0).

## [3.3.15] - 2026-10-30

### Changed
- `avegancafe` entry → 3.6.0 (synced automatically from the plugin's release; was 3.5.0).

## [3.3.14] - 2026-10-27

### Changed
- `avegancafe` entry → 3.5.0 (synced automatically from the plugin's release; was 3.4.1).

## [3.3.13] - 2026-10-24

### Changed
- `avegancafe` entry → 3.4.1 (synced automatically from the plugin's release; was 3.4.0).

## [3.3.12] - 2026-10-24

### Changed
- `avegancafe` entry → 3.4.0 (synced automatically from the plugin's release; was 3.3.0).

## [3.3.11] - 2026-10-24

### Changed
- `avegancafe` entry → 3.3.0 (synced automatically from the plugin's release; was 3.2.1).

## [3.3.10] - 2026-10-22

### Changed
- `avegancafe` entry → 3.2.1 (synced automatically from the plugin's release; was 3.2.0).

## [3.3.9] - 2026-10-22

### Changed
- `avegancafe` entry → 3.2.0 (synced automatically from the plugin's release; was 3.1.3).

## [3.3.8] - 2026-10-22

### Changed
- `avegancafe` entry → 3.1.3 (synced automatically from the plugin's release; was 3.1.2).

## [3.3.7] - 2026-10-22

### Changed
- `avegancafe` entry → 3.1.2 (synced automatically from the plugin's release; was 3.1.1).

## [3.3.6] - 2026-10-22

### Changed
- `avegancafe` entry → 3.1.1 (synced automatically from the plugin's release; was 3.1.0).

## [3.3.5] - 2026-10-22

### Changed
- `avegancafe` entry → 3.1.0 (synced automatically from the plugin's release; was 3.0.0).

## [3.3.4] - 2026-10-20

### Changed
- `session-management` entry → 1.2.1 (synced automatically from the plugin's release; was 1.2.0).

## [3.3.3] - 2026-10-20

### Changed
- `session-management` entry → 1.2.0 (synced automatically from the plugin's release; was 1.1.0).

## [3.3.2] - 2026-10-19

### Changed
- `session-management` entry → 1.1.0 (synced automatically from the plugin's release; was 1.0.0).

## [3.3.1] - 2026-10-19

### Changed
- `avegancafe` entry → 3.0.0 (synced automatically from the plugin's release; was 2.2.0).

## [3.3.0] - 2026-10-19

### Added
- `session-management` 1.0.0 — the `session-title` mod (auto session titles, `/session-title`, `/autoname`) as its own public plugin, [`avegancafe/session-management`](https://github.com/avegancafe/session-management). Its entry uses an HTTPS source so it installs without a GitHub SSH key.

### Changed
- `avegancafe` 3.0.0 — **breaking:** the `session-title` mod is removed; install `session-management` to keep it. The plugin now ships only `work-notes-vault`.
- README: the access note no longer claims every repo is private.

## [3.2.1] - 2026-10-19

### Changed
- `avegancafe` entry → 2.2.0 (synced automatically from the plugin's release; was 2.1.0).

## [3.2.0] - 2026-10-19

### Added
- `avegancafe` 2.2.0 — `/autoname` re-titles the session on demand. It reads the conversation so far (your messages and Claude's replies; tool calls and injected notices left out, long sessions cut to the first prompt plus the latest turns) and asks Haiku for a title under the same `feat|fix|chore(Scope): summary` rules as the automatic first-prompt title, then applies it with `/rename`. Text after the command is an optional hint weighed on top of the history. The automatic title also no longer fires on a first message that is a slash command.

## [3.1.2] - 2026-10-19

### Changed
- `beadwork` entry → 2.4.0 (synced automatically from the plugin's release; was 2.3.0).

## [3.1.1] - 2026-10-19

### Changed
- `avegancafe` entry → 2.1.0 (synced automatically from the plugin's release; was 2.0.0).

## [3.1.0] - 2026-10-19

### Fixed
- `avegancafe` 2.1.0 — `session-title` now titles the session once, from your first message only, and never again. Before, a background Haiku pass re-titled the session after every turn, and the mismatch between the refined title and the shown one tripped the "renamed by hand" check, so a false "auto-title paused" toast popped up mid-conversation. It also ran on wakeups, task notifications and other injected prompts; those are now skipped. `/session-title lock` / `unlock` are gone (nothing changes the title after the first prompt); `/session-title` still shows it.

## [3.0.0] - 2026-10-19

### Changed
- `avegancafe` 2.0.0 — **breaking:** the `side-quest` skill and its `Stop` hook moved to a work plugin outside this marketplace. Update `avegancafe` to drop the old copy. `work-notes-vault` and `session-title` are unchanged.

### Removed
- `avegancafe`: `side-quest` skill and `hooks/side-quest-stop.sh`.

## [2.3.2] - 2026-10-18

### Fixed
- `avegancafe` 1.3.1 — the `side-quest` Stop hook now asks for a one-line "nothing else to flag" reply when there's no side quest, instead of "end your turn silently". Claude Code rejects an empty turn, so the silent instruction always led to a forced extra reply after a false positive.

## [2.3.1] - 2026-10-18

### Changed
- `kitchen-brigade` entry → 1.2.0 (synced automatically from the plugin's release; was 1.1.2).

## [2.3.0] - 2026-10-19

### Changed
- `avegancafe` 1.3.0 — `side-quest` now actually fires during organic work, and forks instead of cold-starting:
  - **Trigger:** description re-keyed from an internal state ("you feel the pull…") to the observable moment ("before finishing or summarizing any task during which you noticed…"), plus a `Stop` hook (`hooks/side-quest-stop.sh`) that catches replies deferring an out-of-scope finding ("separately…", "left it alone…", "outside this change…") and asks Claude, once, whether it's a real side quest. Organic test (real `claude -p` sessions in fixture repos with planted issues, plain task prompts): invocation on exposed findings went 0/12 (1.2.0) → 12/12, with 0/10 on decoys (blockers, in-diff typos, "just list it", already-tracked, clean repo).
  - **Spawn:** `claude --bg --resume "$CLAUDE_CODE_SESSION_ID" --fork-session --name "<type>(<Scope>): <summary>" "<prompt>"` — the fork inherits the whole conversation; its prompt has it create a git worktree of the repo the finding lives in (not of the session's folder, which may be a parent like `~/workspace`), commit and push a `side-quest/<slug>` branch, and open a draft PR.
  - **Guards:** the hook skips headless (`-p`/SDK) sessions unless `SIDE_QUEST_HOOK=1`, since it can't ask there and would replace the final result. The fork touches only what its fix needs and starts no side quests of its own.

## [2.2.0] - 2026-10-18

### Added
- `avegancafe` 1.2.0 — `side-quest` skill: when Claude notices a worthwhile problem the current task doesn't need fixed (an unrelated bug, security risk, stale test, misleading doc, refactor with payoff), it asks once whether to spawn a side quest, then carries on with the main task. A yes launches a cold-start `claude --bg -n "type(Scope): summary" -w side-quest-<slug>` session with a self-contained prompt, in its own worktree. Blockers, already-requested work, in-diff typos and taste nits are handled in place instead.

## [2.1.1] - 2026-10-17

### Changed
- `beadwork` entry → 2.3.0 (synced automatically from the plugin's release; was 2.2.0).

## [2.1.0] - 2026-10-09

### Added
- `avegancafe` 1.1.0 — `session-title` mod: names each session `feat|fix|chore(Scope): imperative summary` on its first prompt (Haiku), refines the title in the background after every main-thread turn, and applies the refinement on the next prompt. A hand rename pauses it; `/session-title` shows the title, `/session-title lock|unlock` toggles it.

## [2.0.0] - 2026-10-08

### Added
- `avegancafe` vendored plugin (1.0.0) — Kyle's personal plugin for one-off skills (unrelated to the old `avegancafe` plugin that became `beadwork`). Ships the `work-notes-vault` skill: where Kyle's private Obsidian work vault (`avegancafe/notes--work`) lives, its layout, and how to search/mine its weekly-synced Granola meeting archive (`granola/notes/`, `.md` + raw `.json`) with `rg`/`jq`. Structure only — no meeting content.

### Removed
- **Breaking:** the vendored `projects` and `session-ids` plugins and their marketplace entries. Uninstall them (`/plugin uninstall projects@avegancafe-marketplace`, `/plugin uninstall session-ids@avegancafe-marketplace`).

### Changed
- CI and CONTRIBUTING shellcheck every `*.sh` under `scripts/` and `plugins/` via `find`, so the step no longer fails when no vendored plugin has scripts.

## [1.2.11] - 2026-10-06

### Changed
- `beadwork` entry → 2.2.0 (synced automatically from the plugin's release; was 2.1.0).

## [1.2.10] - 2026-10-04

### Changed
- `beadwork` entry → 2.1.0 (synced automatically from the plugin's release; was 2.0.6).

## [1.2.9] - 2026-10-04

### Changed
- `beadwork` entry → 2.0.6 (synced automatically from the plugin's release; was 2.0.5).

## [1.2.8] - 2026-10-04

### Changed
- `kitchen-brigade` entry → 1.1.2 (synced automatically from the plugin's release; was 1.1.1).

## [1.2.7] - 2026-10-04

### Changed
- `beadwork` entry → 2.0.5 (synced automatically from the plugin's release; was 2.0.4).

## [1.2.6] - 2026-10-04

### Changed
- Docs: CONTRIBUTING no longer asks for hand-bumped plugin entries, explains wiring `release.yml` + `MARKETPLACE_DISPATCH_TOKEN` for a new external plugin, and validates with `claude plugin validate` instead of `json.tool`. CLAUDE.md points new external plugins at that checklist.

## [1.2.5] - 2026-10-04

### Changed
- `kitchen-brigade` entry → 1.1.1 (synced automatically from the plugin's release; was 1.1.0).

## [1.2.4] - 2026-10-04

### Changed
- `beadwork` entry → 2.0.4 (synced automatically from the plugin's release; was 2.0.3).

## [1.2.3] - 2026-10-04

### Added
- **Automatic plugin-version sync** (`.github/workflows/sync-plugin-versions.yml` + `scripts/sync-plugin-version.sh`). External plugins send a `plugin-released` repository_dispatch from their `main`; vendored plugins sync when their `plugin.json` changes on `main`. Each sync sets the entry's version, bumps `metadata.version` (patch), adds a CHANGELOG entry, validates, and commits to `main`.
- CI validates each vendored plugin and shellchecks all scripts.

### Changed
- `kitchen-brigade` entry → 1.1.0 — the index had drifted at 1.0.3 since kitchen-brigade 1.1.0 shipped on 2026-07-20.

### Removed
- CI's "vendored plugin versions match their entries" check — the sync workflow now makes them match on merge, so a PR bumping a vendored plugin no longer needs a hand-edited entry.

## [1.2.2] - 2026-10-04

### Changed
- `beadwork` entry → 2.0.3 (pane finds `.beads` above nested git repos).

## [1.2.1] - 2026-10-04

### Added
- CI (`.github/workflows/ci.yml`): `claude plugin validate`, `metadata.version` ↔ CHANGELOG sync, and vendored plugins' `plugin.json` versions ↔ their marketplace entries.

### Changed
- `beadwork` entry → 2.0.2 (adds its own CI).

## [1.2.0] - 2026-10-04

### Changed
- **`avegancafe` → `beadwork` (2.0.1).** The grab-bag plugin held only beads tooling, so it's renamed to a dedicated beads plugin; its repo is now `avegancafe/beadwork`. Adds the beadwork pane (a mod showing Claude's task list and open beads, `/beadwork`); skills renamed to `beadwork:logging-captures` and `beadwork:writing-titles`. Reinstall as `beadwork@avegancafe-marketplace` and disable `avegancafe@avegancafe-marketplace`.

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
