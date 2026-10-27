---
name: slurp
description: Use when Kyle runs /slurp or asks to transcribe his voice recorder, pull recordings off the IC RECORDER, or archive recorder audio as notes. Transcribes every recording on the USB recorder locally, writes titled + summarized transcripts into his notes--work vault, commits and pushes them, and leaves the audio on the device (already-transcribed recordings are skipped on later runs).
---

# /slurp — IC RECORDER → notes--work

Kyle's USB voice recorder mounts at `/Volumes/IC RECORDER` and stores recordings as
`REC_FILE/FOLDER*/YYMMDD_HHMM.mp3` (local time, e.g. `261021_2240` = 2026-10-21 22:40).
`scripts/transcribe.py` does **transcription only** (local `mlx-whisper`, nothing leaves the
machine). You do everything after: titles, summaries, vault files, git.

Vault: `~/workspace/notes--work` (`github.com/avegancafe/notes--work`, private). Read its
`.claude/CLAUDE.md` once before writing. Recorder transcripts go in `transcripts/recorder/`;
`transcripts/granola/` is the Granola sync's — never touch it.

## 1. Transcribe

Pull the vault first: the script skips any recording that already has a note there.

```bash
git -C ~/workspace/notes--work pull --rebase
uv run "${CLAUDE_PLUGIN_ROOT}/skills/slurp/scripts/transcribe.py"
```

Run it in the background for anything long (large-v3-turbo runs well faster than real time on
Kyle's M3 Pro; first run also downloads the model, ~1.6 GB). Exit 2 = recorder not mounted: tell
Kyle to plug it in and stop. Stdout is a JSON manifest `[{recorder_id, status, staging_dir?, note?}]`.
`status` is one of:

- `new`: transcribed just now.
- `cached`: transcribed earlier into `/tmp/slurp/` but not in the vault yet (a run that stopped
  before committing). Not redone; write its note like a `new` one.
- `transcribed`: already has a note in the vault (`note` is its path). Skipped: no note, no commit.
- `error`: report it.

Each `staging_dir` holds `audio.mp3` and `transcript.json`:
`{recorder_id, sha256, recorded_at_local, recorded_at_utc, duration_s, model, language, segments[{start,end,text}]}`.
`/tmp/slurp/` is wiped on reboot — that's intended.

To see what's on the device without transcribing anything (Kyle asks "what's on the recorder",
"what hasn't been slurped yet"), run it with `--status`: each recording comes back `transcribed`
(with its note) or `pending`.

## 2. Nothing to write for `transcribed`

The script already matched those to their notes by `recorder_id`, so skip straight past them.
If every recording is `transcribed`, say so and stop after the report (step 6).

## 3. Write one note per new recording

**First, match each recording to Kyle's calendar.** Most recordings are a meeting on Kyle's
Google Calendar, and the event tells you who the transcript can't. Load the Google Calendar
connector's `list_events` (ToolSearch `calendar list_events`) and list the primary calendar
from ~30 min before `recorded_at_local` to its end (`+ duration_s`). Match each recording to the
event whose window it falls in. Kyle usually starts the recorder a few minutes after the event
starts, and meetings often run over (on 2026-10-27, a 15:32 recording matched "Kyle <> Rachel",
15:30–16:00, and ran to 16:22). Skip events Kyle declined, room resources, and the bot address.

- **A clear match with one other attendee** (a 1:1) names the other party. Use their name in the
  summary instead of "the counterpart", linked to their `J2/People/` note, and say in the
  `Recording notes` callout which event it matched.
- **A group event** lists who *might* be speaking, not who is. Use it to resolve first names in
  the transcript ("Abby" in a meeting with abby@ → `[[Abby Pfeiffer]]`), but still mark
  attributions *(inferred)*.
- **No match, or back-to-back events it could be either of** (a corridor chat, a lunch): leave the
  other party unnamed and say so in the callout. Never pick between two candidate events on a hunch.
- If Kyle names the other party afterward, update the note. Kyle's word beats the calendar.

Then read `transcript.json` and write
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
calendar_event: "Kyle <> Rachel"             # matched event title; omit when no match
attendees: ["[[Rachel Foley]]"]              # other attendees, linked; omit when no match
---

# <title>

## Summary

<Granola-style: ### headings per topic, bullets, decisions and action items called out>

## Transcript

_Times are UTC._

[02:43:05 (+00:03:05)] <segment text>

[02:43:08 (+00:03:08)] <next segment text>
```

- **Transcript lines:** one per segment, with a **blank line between segments**. GitHub's
  markdown preview joins single-newline lines into one paragraph. The first time is the UTC wall clock
  (`recorded_at_utc` + `start`, `HH:MM:SS`); the time in parentheses is the offset from the start of the recording.
  Write these lines with a short script (e.g. `jq` or Python over `segments`), not by hand.
  Never edit the transcript text itself.
- **No speaker labels.** The recorder has one mic. If the summary attributes something to a
  person, say it's inferred from content ("Zara (inferred)").
- **Link people.** Before writing the summary, list `J2/People/`. Write a name as a
  `[[wikilink]]` to its note when one matches (Carl → `[[Karl]]`, Abby → `[[Abby Pfeiffer]]`).
  Leave names with no note as transcribed, still marked *(inferred)*. Never guess who an
  unnamed speaker is. A calendar match (above) isn't a guess, but the transcript's
  content alone is.
- **Whisper repetition loops.** Noisy audio (a recorder in a pocket, a restaurant) makes
  whisper repeat a phrase dozens of times ("Yeah." ×40). Leave them in the transcript. Open
  the summary with a one-line `> **Recording notes.**` callout that gives the loop stretches
  as approximate offsets, and treat numbers and names near them as transcription-uncertain.
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

## 5. Leave the audio on the device

Don't delete, move, rename, eject or unmount anything on the recorder. Recordings stay there, and later
runs skip them as `transcribed`. The recorder holds about 14 GiB, and its MP3s run about 86 MB per
recorded hour, so it fills after roughly 170 hours. In the report, say how much space is free
(`df -h "/Volumes/IC RECORDER"`), and flag it once less than 10% is free.

If Kyle asks to clear the device: only recordings reported `transcribed` whose note is in
`origin/main` (`git -C ~/workspace/notes--work log origin/main --oneline -- <note path>` returns a
commit) are eligible. Give him the exact `rm` command for those files, quoting the path because it
contains a space, and let him run it.

## 6. Report

Number transcribed, then each new title → GitHub link with its duration, plus how many recordings
were skipped as already `transcribed`, the recorder's free space, and anything errored and why. Link each note at the commit that added it, so the link
works from any machine and session:
`https://github.com/avegancafe/notes--work/blob/<commit-sha>/<note path>`. Repo-relative
paths don't open when the session's working directory isn't the vault.
