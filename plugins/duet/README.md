# duet

How [Claude Duet](https://claude.ai/messages) works, written for the Claude agents
running inside it. Install it to your **claude.ai chat plugins** (not Claude Code)
so every new Duet thread and channel starts out knowing how plugins, threads,
channels, repos and sessions behave there.

The plugin grows as Duet behavior is learned: whenever a Duet session learns
something Duet-specific, it adds or updates a skill here through a PR.

## Install

Install `duet` from the `avegancafe-marketplace` account marketplace in your
claude.ai chat plugins. It takes effect in threads started after that.

## Skills

| Skill | Purpose |
|-------|---------|
| `duet-basics` | Where Duet's plugins come from and when they load, how threads and sessions relate, how a channel's repos are attached, how channel instructions set lasting behavior (like always using a plugin agent), and how to add new learnings to this plugin. |
