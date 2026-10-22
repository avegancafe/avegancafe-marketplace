---
name: slurp
description: Use when Kyle runs /slurp or asks to transcribe his voice recorder, pull recordings off the IC RECORDER, or archive recorder audio as notes. Transcribes every recording on the USB recorder locally, writes titled + summarized transcripts into his notes--work vault, commits and pushes them, then clears the device.
---

# /slurp — IC RECORDER → notes--work

Kyle's USB voice recorder mounts at `/Volumes/IC RECORDER` and stores recordings as
`REC_FILE/FOLDER*/YYMMDD_HHMM.mp3` (local time, e.g. `261021_2240` = 2026-10-21 22:40).
`scripts/transcribe.py` does **transcription only** (local `mlx-whisper`, nothing leaves the
machine). You do everything after: titles, summaries, vault files, git, device cleanup.

Vault: `~/workspace/notes--work` (`github.com/avegancafe/notes--work`, private). Read its
`.claude/CLAUDE.md` once before writing. Recorder transcripts go in `transcripts/recorder/`;
`transcripts/granola/` is the Granola sync's — never touch it.

## 1. Transcribe

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/slurp/scripts/transcribe.py"
```

Run it in the background for anything long (large-v3-turbo runs well faster than real time on
Kyle's M3 Pro; first run also downloads the model, ~1.6 GB). Exit 2 = recorder not mounted: tell
Kyle to plug it in and stop. Stdout is a JSON manifest `[{recorder_id, status, staging_dir}]`;
`status` is `new`, `cached` (already transcribed in `/tmp/slurp/`, not redone) or `error`.
Each `staging_dir` holds `audio.mp3` and `transcript.json`:
`{recorder_id, sha256, recorded_at_local, recorded_at_utc, duration_s, model, language, segments[{start,end,text}]}`.

`/tmp/slurp/` is wiped on reboot — that's intended. Once the device is cleared, **the committed
transcript is the only copy of a recording.**

## 2. Skip what's already in the vault

```bash
V=~/workspace/notes--work; git -C "$V" pull --rebase
rg -l "^recorder_id: <id>$" "$V/transcripts/recorder"
```

A hit means it was committed on an earlier run (and the device delete probably failed) — don't
write it again; it's still eligible for step 5.

## 3. Write one note per new recording

Read `transcript.json`, then write
`transcripts/recorder/YYYY/MM/YYYY-MM-DD--<title-slug>--<recorder_id>.md`, where the date and
`YYYY/MM` come from **`recorded_at_local`** (unlike Granola, whose paths use UTC dates).
`<title-slug>`: lowercase, ASCII, hyphens, ≤ 60 chars.

```markdown
---
title: <short descriptive title you write>
recorded_at: 2026-10-21T22:40:00-04:00      # recorded_at_local
duration: 00:31:12                           # from duration_s
source: ic-recorder
recorder_id: 261021_2240
model: mlx-community/whisper-large-v3-turbo
---

# <title>

## Summary

<Granola-style: ### headings per topic, bullets, decisions and action items called out>

## Transcript

[02:43:05 (+00:03:05)] <segment text>
```

- **Transcript lines:** one per segment. The first time is the UTC wall clock
  (`recorded_at_utc` + `start`, `HH:MM:SS`); the time in parentheses is the offset from the start of the recording.
  Write these lines with a short script (e.g. `jq` or Python over `segments`), not by hand.
  Never edit the transcript text itself.
- **No speaker labels.** The recorder has one mic. If the summary attributes something to a
  person, say it's inferred from content ("Zara (inferred)").
- **Title/summary from the transcript only.** A recording that's empty or near-silent still gets a
  note (title like "Empty recording") so it isn't lost silently; tell Kyle about it.
- The recorder's clock has no timezone, so `recorded_at` assumes this Mac's current timezone.
  If Kyle says a recording was made elsewhere, fix `recorded_at` and the UTC times.

## 4. Commit and push

```bash
cd ~/workspace/notes--work
git add transcripts/recorder/        # never -A: other vault changes aren't yours to commit
git commit -m "recorder: transcribe N recordings (YYYY-MM-DD)"
git push
```

On push rejection: `git pull --rebase` and push again (repeat a couple of times; obsidian-git
and the Granola Action also push to `main`). Never force-push, stash, or reset. If a rebase
conflicts outside `transcripts/recorder/`, stop and report.

## 5. Clear the device — only after a successful push

For each recording that is now in `origin/main`
(`git -C ~/workspace/notes--work log origin/main --oneline -- <note path>` returns a commit):
re-check that the device file's sha256 still equals `transcript.json`'s `sha256`, list the
files you are about to delete in your message, then `rm` them from `/Volumes/IC RECORDER/REC_FILE/…`.
Leave anything that errored, wasn't committed, or whose checksum changed. Don't delete anything
outside `REC_FILE/`. Then `diskutil eject "/Volumes/IC RECORDER"` so Kyle can unplug it.

## 6. Report

Number transcribed, then each title → vault path with its duration, plus the files deleted from the device
and anything skipped/errored and why.
