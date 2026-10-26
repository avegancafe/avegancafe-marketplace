---
name: slurp
description: Use when Kyle runs /slurp or asks to transcribe his voice recorder, pull recordings off the IC RECORDER, archive recorder audio as notes, or label/enroll/forget the voices in his recordings ("that's Abby", "who's speaker 2"). Transcribes every recording on the USB recorder locally, labels speakers from voiceprints he has confirmed (asking him about new voices with short clips), writes titled + summarized transcripts into his notes--work vault, commits and pushes them, and leaves the audio on the device (already-transcribed recordings are skipped on later runs).
---

# /slurp — IC RECORDER → notes--work

Kyle's USB voice recorder mounts at `/Volumes/IC RECORDER` and stores recordings as
`REC_FILE/FOLDER*/YYMMDD_HHMM.mp3` (local time, e.g. `261021_2240` = 2026-10-21 22:40).
`scripts/transcribe.py` does **transcription only** (local `mlx-whisper`, nothing leaves the
machine). `scripts/diarize.py` works out who spoke when and names the voices it knows (local
pyannote). You do everything after: asking Kyle about new voices, titles, summaries, vault files, git.

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
If every recording is `transcribed`, say so and stop after the report (step 7).

## 3. Label speakers

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/slurp/scripts/diarize.py" run
```

This diarizes every staged recording that hasn't been diarized yet (`new` and `cached` alike; pass ids to limit
it, `--force` to redo). Run it in the background for long recordings. The first run downloads
pyannote and its model. Exit 3 = no Hugging Face access: tell Kyle the one-time setup below,
then carry on **without speaker labels** (write the transcript as if diarization didn't exist).
It writes `<staging_dir>/diarization.json` and prints, per recording, `speakers[]`:
`{id, display, name, score, labelled, minor, talk_s, candidates[{name, score}], clips[{path, start, end, text}]}`.

- **`name` set, `labelled: false`**: matched to a voiceprint Kyle confirmed earlier (`score` is
  the cosine similarity; 1.0 = identical). Use it, and list it in the report with its score so he
  can correct it.
- **`name` null, `minor: false`**: a voice it doesn't know. Ask Kyle (below).
- **`minor: true`**: under ~8 s of speech in total (noise, a passer-by). Don't ask about it.

**Asking Kyle.** One message covering every unknown speaker across the run. For each one give the recording
(date/time), its `display` ("Speaker 2"), its talk time, the best candidate if any
("closest: Abby Pfeiffer, 0.41"), and each clip's transcript `text` with `afplay "<path>"`.
Offer to play the clips: `afplay` plays out loud on his Mac, so you can run it when he asks.
List `J2/People/` first, so the names he gives match note titles and later turn into wikilinks.

**When he names one**, record it:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/slurp/scripts/diarize.py" label <recorder_id> "Speaker 2" "Abby Pfeiffer"
```

That saves the voice's voiceprint, then re-matches every staged recording. Check `rematched`:
voices it now recognizes elsewhere in the batch are named, so don't ask about those again. To
correct a wrong match, label the speaker with the right name (the same command). "Don't know" or "skip" →
leave it as `Speaker N`. **Only Kyle names voices.** Never `label` or `enroll` from your own
reading of the transcript, however obvious the name looks: a wrong voiceprint mislabels every
future recording.

If Kyle isn't around to answer (an unattended run), write the notes with `Speaker N`, list the
unknown speakers and their clips in the report, and when he names them later, `label` them, then
update those notes (frontmatter `speakers` and transcript lines) and commit as
`recorder: label speakers (YYYY-MM-DD)`. That has to happen before a reboot wipes `/tmp/slurp/`.

**Other voiceprint commands** (same script). Use them when Kyle asks:
- `enroll "<Name>" <audio file>`: a voiceprint from a clip of one person talking (20+ s,
  ideally recorded on the recorder itself, so it sounds like the real recordings).
- `people`: who has voiceprints, and which recordings they were learned from.
- `forget "<Name>" [--source <recorder_id>]`: delete someone's voiceprints, or one bad sample.
- `run --threshold 0.6`: stricter auto-naming, if it names the wrong people. The default is 0.5,
  and a match also has to beat the runner-up by 0.1.

Voiceprints live in `~/.config/local/slurp/voiceprints.json`: machine-local, never committed
(biometric data about other people). Never copy them into the vault or any repo.

**One-time setup** (exit 3): Kyle makes a free Hugging Face account, accepts the terms at
<https://hf.co/pyannote/speaker-diarization-community-1>, creates a read token, and adds
`HF_TOKEN=<token>` to `~/.config/local/.env` (then opens a new shell). Never ask him to paste the
token into the chat.

## 4. Write one note per new recording

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
speakers: [Kyle, Abby Pfeiffer, Speaker 3]   # non-minor `display`s in talk order; omit without diarization
diarization: pyannote/speaker-diarization-community-1   # omit without diarization
---

# <title>

## Summary

<Granola-style: ### headings per topic, bullets, decisions and action items called out>

## Transcript

_Times are UTC._

[02:43:05 (+00:03:05)] **Kyle:** <segment text>

[02:43:08 (+00:03:08)] **Abby Pfeiffer:** <next segment text>
```

- **Transcript lines:** one per segment, with a **blank line between segments**. GitHub's
  markdown preview joins single-newline lines into one paragraph. The first time is the UTC wall clock
  (`recorded_at_utc` + `start`, `HH:MM:SS`); the time in parentheses is the offset from the start of the recording.
  Write these lines with a short script (e.g. `jq` or Python over `segments`), not by hand.
  Never edit the transcript text itself.
- **Speaker labels** come from `diarization.json`: segment `i` gets the `display` of the
  speaker whose `id` is `segment_speakers[i]`, as `**<display>:** ` before the text (no label when it is
  `null`). Use plain names here, not wikilinks. Without diarization, write lines with no label.
- **Names in the summary.** Voices named by diarization are named in the summary too. A person
  you infer only from content (a voice still `Speaker N`, someone mentioned) is marked
  *(inferred)*: "Zara (inferred)". One pocket mic means short interjections and crosstalk
  can land on the wrong speaker, so don't build a claim on a single line's label.
- **Link people.** Before writing the summary, list `J2/People/`. Write a name as a
  `[[wikilink]]` to its note when one matches (Carl → `[[Karl]]`, Abby → `[[Abby Pfeiffer]]`).
  Leave inferred names with no note as transcribed, still marked *(inferred)*. Never guess who
  an unnamed speaker is.
- **Whisper repetition loops.** Noisy audio (a recorder in a pocket, a restaurant) makes
  whisper repeat a phrase dozens of times ("Yeah." ×40). Leave them in the transcript. Open
  the summary with a one-line `> **Recording notes.**` callout that gives the loop stretches
  as approximate offsets, and treat numbers and names near them as transcription-uncertain.
- **Title/summary from the transcript only.** A recording that's empty or near-silent still gets a
  note (title like "Empty recording") so it isn't lost silently; tell Kyle about it.
- The recorder's clock has no timezone, so `recorded_at` assumes this Mac's current timezone.
  If Kyle says a recording was made elsewhere, fix `recorded_at` and the UTC times.

## 5. Commit and push

```bash
cd ~/workspace/notes--work
git add transcripts/recorder/        # never -A: other vault changes aren't yours to commit
git commit -m "recorder: transcribe N recordings (YYYY-MM-DD)"
git push
```

On push rejection: `git pull --rebase` and push again (repeat a couple of times; obsidian-git
and the Granola Action also push to `main`). Never force-push, stash, or reset. If a rebase
conflicts outside `transcripts/recorder/`, stop and report.

## 6. Leave the audio on the device

Don't delete, move, rename, eject or unmount anything on the recorder. Recordings stay there, and later
runs skip them as `transcribed`. The recorder holds about 14 GiB, and its MP3s run about 86 MB per
recorded hour, so it fills after roughly 170 hours. In the report, say how much space is free
(`df -h "/Volumes/IC RECORDER"`), and flag it once less than 10% is free.

If Kyle asks to clear the device: only recordings reported `transcribed` whose note is in
`origin/main` (`git -C ~/workspace/notes--work log origin/main --oneline -- <note path>` returns a
commit) are eligible. Give him the exact `rm` command for those files, quoting the path because it
contains a space, and let him run it.

## 7. Report

Number transcribed, then each new title → GitHub link with its duration and speakers (auto-matched
names with their score, voices still unknown), plus how many recordings
were skipped as already `transcribed`, the recorder's free space, and anything errored and why. Link each note at the commit that added it, so the link
works from any machine and session:
`https://github.com/avegancafe/notes--work/blob/<commit-sha>/<note path>`. Repo-relative
paths don't open when the session's working directory isn't the vault.
