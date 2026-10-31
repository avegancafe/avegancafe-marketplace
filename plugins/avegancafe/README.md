# avegancafe

Kyle's personal Claude Code plugin — a home for one-off skills that don't
warrant a plugin of their own.

## Install

```bash
/plugin install avegancafe --marketplace avegancafe/avegancafe-marketplace
```

## Skills

| Skill | Purpose |
|-------|---------|
| `work-notes-vault` | Kyle's private Obsidian work vault, [`avegancafe/notes--work`](https://github.com/avegancafe/notes--work) (expected at `~/workspace/notes--work/`): locating/refreshing it, its layout, and its weekly-synced **Granola meeting archive** (`granola/notes/`, `.md` + raw `.json`) — schema, `rg`/`jq` mining recipes, freshness limits, and what not to touch. Lets Claude "mine my Granola meetings for X" from any working directory; the vault's own `.claude/CLAUDE.md` stays the authority on its conventions. No meeting content lives here — only the archive's structure. |
| `hifi-h2` | Tags store-bought FLACs from MusicBrainz (full tags, 500×500 baseline cover, `NN - Title` names), audits the Rockbox HIFI H2 library for tracks that would land under `<Untagged>` (missing album artist, ID3v1-only, truncated titles), and covers mounting, copying and the Rockbox database rebuild. |
| `phone-push` | Sends a push notification to Kyle's phone, now or at a scheduled time, through a one-time or recurring cloud routine (`RemoteTrigger`) that calls `PushNotification`; can check Gmail/HEY first and push a one-line result. Covers the create body, UTC timing, connectors, prompt templates and run debugging. |
| `flipper-usb` | Drives Kyle's Flipper Zero over USB: a hard-timeout CLI helper (`flipper_cli.py`: commands, SD text files, button presses, live logs), ufbt builds matched to the firmware API, finding `MissingImports`, the one-process-per-serial-port rules, and a probe-app recipe for GPIO boards (with ESP32 Marauder v1.17 findings). |
`side-quest` moved to a work plugin outside this marketplace in 2.0.0 (skill + `Stop` hook).
The `session-title` mod (`/session-title`, `/autoname`) moved to its own public plugin,
[`session-management`](https://github.com/avegancafe/session-management), in 3.0.0.

