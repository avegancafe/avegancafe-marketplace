---
name: duet-basics
description: Use when working inside Claude Duet (a main chat, a channel or a thread) and unsure how plugins, threads, channels, repos or sessions behave there — e.g. why a plugin isn't showing up, how to pick up a newly installed plugin, or how to give a channel access to a GitHub repo. Also covers how to add what you learn about Duet back into this plugin.
---

# Claude Duet basics

Facts about how Claude Duet behaves, learned while working in it. Each one was
observed, not guessed. If something here turns out wrong, fix it (see the last
section) rather than working around it silently.

## Plugins

- **Duet loads the user's claude.ai chat plugins, not their Claude Code plugins.**
  A plugin installed only in Claude Code (`/plugin install …` in the CLI) does not
  show up in Duet. To use one in Duet, install it to the claude.ai chat plugins.
- Kyle's marketplace, `avegancafe/avegancafe-marketplace`, is linked to his
  claude.ai account as an account marketplace, so its plugins (this one included)
  can be installed from there.
- **Plugins load when a session starts.** There is no command to resync plugins or
  restart a running session.
- **Every new thread is a fresh session.** To pick up a plugin that was just
  installed, start a new thread; the current one won't see it.
- The plugin list a channel's coordinator session reports can be empty even while
  account plugins are loading in its threads, so an empty list there doesn't prove
  a plugin is missing.

## Channels, threads and repos

- A channel's GitHub repos are added by the channel's coordinator session
  (`update_project_settings` with `add_repo`).
- The coordinator session itself can't read those repos. Threads it starts
  **after** the repo was added can. So to work in a newly added repo, have the
  coordinator start a new thread.

## Adding to this plugin

When you learn something specific to how Duet works (not general Claude or
Claude Code behavior), add it here so future threads and channels know it:

1. Put it in the skill that fits its subject, or add a new skill under
   `plugins/duet/skills/<name>/SKILL.md` when it's a new subject. Keep each line a
   fact plus, when useful, what to do about it. Don't record guesses.
2. Follow the repo's `CLAUDE.md`: bump `plugins/duet/.claude-plugin/plugin.json`
   and the `duet` entry in `.claude-plugin/marketplace.json` together, bump
   `metadata.version`, add a `CHANGELOG.md` entry, and list any new skill in
   `plugins/duet/README.md`.
3. Open a PR on `avegancafe/avegancafe-marketplace` for Kyle to merge. Never push
   to `main` or merge it yourself.
