#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Render a staged transcript plus Claude-written metadata into the vault note.

The last step of /slurp: transcribe.py writes `transcript.json`, diarize.py adds a
`speaker` per segment, Claude writes `meta.json` (title, summary, calendar match) next to
it, and this serializes the note. Transcript lines are generated here, never by hand.

meta.json:
    {"title": "...", "slug": "...", "summary_md": "### Topic\\n- ...",
     "recording_notes": "Matched calendar event ...",        # the callout; optional
     "calendar_event": "Faith <> Kyle",                        # optional
     "attendees": ["Faith Komlo"],                             # optional, wikilinked
     "speakers": {"S1": "Kyle (inferred)", "S2": "[[Faith Komlo]] (inferred)"}}  # optional legend

    render.py /tmp/slurp/261029_1504             # writes the note, prints its path
    render.py /tmp/slurp/261029_1504 --vault DIR
    render.py /tmp/slurp/261029_1504 --stdout

A speaker label whose similarity is below LOW_SIM (or that was inherited by a segment too
short to embed) renders with a trailing `?`.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_VAULT = Path.home() / "workspace/notes--work/transcripts/recorder"
LOW_SIM = 0.4


def hms(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def line(seg: dict, base: datetime) -> str:
    wall = (base + timedelta(seconds=seg["start"])).strftime("%H:%M:%S")
    who = ""
    if seg.get("speaker"):
        sure = seg.get("speaker_sim") is not None and seg["speaker_sim"] >= LOW_SIM
        who = f"**{seg['speaker']}{'' if sure else '?'}:** "
    return f"[{wall} (+{hms(seg['start'])})] {who}{seg['text'].strip()}"


def render(t: dict, meta: dict) -> str:
    fm = [
        "---",
        f"title: {json.dumps(meta['title'], ensure_ascii=False)}",
        f"recorded_at: {t['recorded_at_local']}",
        f"duration: {hms(round(t['duration_s'] or 0))}",
        "source: ic-recorder",
        f"recorder_id: {t['recorder_id']}",
        f"model: {t['model']}",
    ]
    if t.get("diarization"):
        fm.append(f"diarization: {t['diarization']['model']}")
    if meta.get("calendar_event"):
        fm.append(f"calendar_event: {json.dumps(meta['calendar_event'], ensure_ascii=False)}")
    if meta.get("attendees"):
        fm.append(f"attendees: {json.dumps([f'[[{a}]]' for a in meta['attendees']], ensure_ascii=False)}")
    fm.append("---")

    body = [f"# {meta['title']}", "", "## Summary", ""]
    if meta.get("recording_notes"):
        body += [f"> **Recording notes.** {meta['recording_notes']}", ""]
    body += [meta["summary_md"].strip(), "", "## Transcript", ""]
    head = "_Times are UTC._"
    if t.get("diarization"):
        head += (" _Speakers are clustered from the audio of this recording only (one mic, no stored voiceprints);"
                 " `?` marks a low-confidence label._")
    body += [head, ""]
    if meta.get("speakers"):
        body += [", ".join(f"**{k}** = {v}" for k, v in sorted(meta["speakers"].items())), ""]

    base = datetime.fromisoformat(t["recorded_at_utc"])
    body.append("\n\n".join(line(s, base) for s in t["segments"]))
    return "\n".join(fm + [""] + body) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("staging_dir", type=Path)
    ap.add_argument("--vault", type=Path, default=DEFAULT_VAULT, help=f"vault recorder dir (default: {DEFAULT_VAULT})")
    ap.add_argument("--stdout", action="store_true", help="print the note instead of writing it")
    args = ap.parse_args()

    t = json.loads((args.staging_dir / "transcript.json").read_text())
    meta = json.loads((args.staging_dir / "meta.json").read_text())
    note = render(t, meta)
    if args.stdout:
        sys.stdout.write(note)
        return 0

    date = t["recorded_at_local"][:10]  # local date, unlike Granola's UTC paths
    out = args.vault / date[:4] / date[5:7] / f"{date}--{meta['slug']}--{t['recorder_id']}.md"
    for old in out.parent.glob(f"*--{t['recorder_id']}.md"):  # a re-render may change the slug
        if old != out:
            old.unlink()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(note, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
