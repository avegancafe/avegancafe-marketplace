---
name: slurp
description: Use when Kyle runs /slurp or asks to transcribe his voice recorder, pull recordings off the IC RECORDER, or archive recorder audio as notes. Transcribes every recording on the USB recorder locally, writes titled + summarized transcripts into his notes--work vault, commits and pushes them, and leaves the audio on the device (already-transcribed recordings are skipped on later runs).
---

# /slurp — IC RECORDER → notes--work

Kyle's USB voice recorder mounts at `/Volumes/IC RECORDER` and stores recordings as
`REC_FILE/FOLDER*/YYMMDD_HHMM.mp3` (local time, e.g. `261021_2240` = 2026-10-21 22:40).
Three scripts work on one staged `transcript.json`, and everything runs locally:
`scripts/transcribe.py` transcribes it (`mlx-whisper`), `scripts/diarize.py` labels each
segment with an anonymous speaker (`S1`, `S2`, …), and `scripts/render.py` serializes it into
the vault note. You do the judgment in between: calendar match, title, summary, and git.

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

### Diarize

After the calendar match (step 3) tells you how many people were there, label speakers in
place for each `new`/`cached` recording:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/slurp/scripts/diarize.py" <staging_dir> --speakers 2   # a 1:1
uv run "${CLAUDE_PLUGIN_ROOT}/skills/slurp/scripts/diarize.py" <staging_dir>                # unknown count
```

It embeds each segment's audio with a local speaker model (ECAPA; ~20 MB, first run downloads
it), clusters only the long, clean segments (≥ 3 s) into speakers, then gives every segment its
nearest speaker. It adds `speaker` and `speaker_sim` to each segment. About 30 s per
25-minute recording, so background it for several recordings.

- **Anonymous, and stored nowhere.** Voices are compared only within one recording. No
  voiceprint is saved, named, or reused across recordings, so `S1` in one note has nothing to do
  with `S1` in another. Keep it that way: a stored voiceprint of a coworker is biometric PII.
- **Pass `--speakers` only when you know the count.** A 1:1 calendar match means 2. A group
  event's attendee list is an upper bound, not a count, so leave the flag off there.
- Exit 1 = too little long speech to diarize (a near-empty recording). Render it without labels.

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

Then diarize (step 1), read `transcript.json`, and write `<staging_dir>/meta.json`:

```json
{
  "title": "<short descriptive title you write>",
  "slug": "<lowercase, ASCII, hyphens, ≤ 60 chars>",
  "calendar_event": "Kyle <> Rachel",
  "attendees": ["Rachel Foley"],
  "speakers": {"S1": "Kyle (inferred)", "S2": "[[Rachel Foley]] (inferred)"},
  "recording_notes": "Matched calendar event \"Kyle <> Rachel\" (15:30–16:00 ET) ...",
  "summary_md": "### <topic>\n- ...\n\n### Action items\n- ..."
}
```

Leave out `calendar_event` and `attendees` when there's no match, and `speakers` when you can't
tell who is who. Then render the note:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/slurp/scripts/render.py" <staging_dir>
```

It writes `transcripts/recorder/YYYY/MM/YYYY-MM-DD--<slug>--<recorder_id>.md` and prints the
path. The date comes from **`recorded_at_local`** (unlike Granola, whose paths use UTC dates).
It builds the frontmatter, the `> **Recording notes.**` callout, your summary, a speaker legend,
and one transcript line per segment:

```markdown
[19:06:05 (+00:02:05)] **S2:** I did the NPM switchover.

[19:06:09 (+00:02:09)] **S1?:** Sick.
```

That's the UTC wall clock, the offset into the recording, and the speaker. A trailing `?` marks
a low-confidence label: a short interjection, or a segment too short to embed. Re-running
`render.py` (say, after Kyle names someone) rewrites the note in place, including a changed slug.

- **Never hand-write or edit transcript lines.** Change `meta.json` and re-render instead.
- **Map speakers to people from content, once.** `S1`/`S2` come from the audio; which one is
  Kyle comes from what they say ("as head of eng…", the counterpart describing their own
  work). Put that in `speakers` with *(inferred)*, and use it for attributions in the
  summary. In a 1:1, Kyle is one of the two clusters. If the content doesn't settle it, leave
  `speakers` out rather than guess.
- **Labels are evidence, not truth.** Clustering is reliable at turn boundaries on full sentences
  and weak on one-word replies. Don't hang an attribution on a single `?` line.
- **Link people.** Before writing the summary, list `J2/People/`. Write a name as a
  `[[wikilink]]` to its note when one matches (Carl → `[[Karl]]`, Abby → `[[Abby Pfeiffer]]`).
  Leave names with no note as transcribed, still marked *(inferred)*. Never guess who an
  unnamed speaker is. A calendar match (above) isn't a guess, but the transcript's
  content alone is.
- **Whisper repetition loops.** Noisy audio (a recorder in a pocket, a restaurant) makes
  whisper repeat a phrase dozens of times ("Yeah." ×40). Leave them in the transcript. Give the loop
  stretches as approximate offsets in `recording_notes` (rendered as the callout that opens the summary), and treat numbers and names near them as transcription-uncertain.
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
