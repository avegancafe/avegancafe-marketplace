#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mlx-whisper"]
# ///
"""Transcribe every recording on the IC RECORDER into /tmp/slurp/ (transcription only).

No git, no vault writes, no deletion -- the /slurp skill does all of that. Each
recording `REC_FILE/**/YYMMDD_HHMM.mp3` is copied to `/tmp/slurp/<id>/audio.mp3`,
checksummed against the device copy, and transcribed to `transcript.json`. A
recording whose staged `transcript.json` already matches the device file's
sha256 is reported `cached` and not re-transcribed. A recording that already has a note in
the vault (a `recorder_id:` frontmatter match) is reported `transcribed` and skipped, so
recordings can stay on the device across runs without being redone.

    transcribe.py                       # default device /Volumes/IC RECORDER
    transcribe.py --status              # list what's on the device and whether it's in the vault; no transcription
    transcribe.py --device /Volumes/X   # another mount point
    transcribe.py --vault <dir>         # another vault recorder dir
    transcribe.py --only 261021_2240    # just these recorder ids

stdout: JSON manifest  [{"recorder_id", "status": new|cached|transcribed|pending|error,
                         "staging_dir"?, "note"?, "error"?}]
        (`pending` = not in the vault yet; only --status reports it)
stderr: progress.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DEVICE = Path("/Volumes/IC RECORDER")
STAGING = Path("/tmp/slurp")
MODEL = "mlx-community/whisper-large-v3-turbo"
DEFAULT_VAULT = Path.home() / "workspace/notes--work/transcripts/recorder"


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def recorded_at(recorder_id: str) -> datetime | None:
    """`YYMMDD_HHMM` in the machine's local timezone (the recorder has no tz), tz-aware."""
    try:
        return datetime.strptime(recorder_id[:11], "%y%m%d_%H%M").astimezone()
    except ValueError:
        return None


def vault_notes(vault: Path) -> dict[str, Path]:
    """recorder_id -> note path, from each note's `recorder_id:` frontmatter line."""
    notes = {}
    for md in vault.rglob("*.md") if vault.is_dir() else []:
        with md.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("recorder_id:"):
                    notes[line.split(":", 1)[1].strip()] = md
                    break
                if line.startswith("## "):  # past the frontmatter
                    break
    return notes


def duration_s(path: Path) -> float | None:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return round(float(out), 3)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


def transcribe_one(src: Path) -> dict:
    rid = src.stem
    stage = STAGING / rid
    stage.mkdir(parents=True, exist_ok=True)
    src_sha = sha256(src)
    out_json = stage / "transcript.json"

    if out_json.exists():
        try:
            if json.loads(out_json.read_text()).get("sha256") == src_sha:
                log(f"{rid}: cached")
                return {"recorder_id": rid, "status": "cached", "staging_dir": str(stage)}
        except ValueError:
            pass  # corrupt partial output: redo it

    audio = stage / "audio.mp3"
    shutil.copyfile(src, audio)
    if sha256(audio) != src_sha:
        raise RuntimeError(f"staged copy of {src} does not match the device file")

    import mlx_whisper  # deferred: slow import, and not needed for cached runs

    log(f"{rid}: transcribing ({MODEL})...")
    result = mlx_whisper.transcribe(str(audio), path_or_hf_repo=MODEL)
    when = recorded_at(rid)
    payload = {
        "recorder_id": rid,
        "source_path": str(src),
        "sha256": src_sha,
        "recorded_at_local": when.isoformat() if when else None,
        "recorded_at_utc": when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if when else None,
        "duration_s": duration_s(audio),
        "model": MODEL,
        "language": result.get("language"),
        "segments": [
            {"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()}
            for s in result.get("segments", [])
            if s["text"].strip()
        ],
    }
    tmp = out_json.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(out_json)  # atomic: a crash never leaves a half-written transcript.json
    log(f"{rid}: {len(payload['segments'])} segments")
    return {"recorder_id": rid, "status": "new", "staging_dir": str(stage)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--device", type=Path, default=DEFAULT_DEVICE, help=f"recorder mount (default: {DEFAULT_DEVICE})")
    ap.add_argument("--vault", type=Path, default=DEFAULT_VAULT, help=f"vault recorder dir (default: {DEFAULT_VAULT})")
    ap.add_argument("--only", nargs="+", metavar="ID", help="only these recorder ids (e.g. 261021_2240)")
    ap.add_argument("--status", action="store_true", help="list recordings and their vault status; transcribe nothing")
    args = ap.parse_args()

    rec_dir = args.device / "REC_FILE"
    if not rec_dir.is_dir():
        log(f"Recorder not mounted: {rec_dir} not found. Plug it in (it mounts as {DEFAULT_DEVICE}).")
        return 2

    files = sorted(p for p in rec_dir.rglob("*") if p.suffix.lower() == ".mp3" and not p.name.startswith("."))
    if args.only:
        files = [p for p in files if p.stem in set(args.only)]
    log(f"{len(files)} recording(s) on {args.device}")
    if not args.vault.is_dir():
        log(f"warning: vault dir {args.vault} not found; treating every recording as not yet transcribed")
    notes = vault_notes(args.vault)

    manifest = []
    for src in files:
        note = notes.get(src.stem)
        if note or args.status:
            log(f"{src.stem}: {'transcribed -> ' + str(note) if note else 'pending'}")
            manifest.append({"recorder_id": src.stem, "status": "transcribed" if note else "pending",
                             **({"note": str(note)} if note else {})})
            continue
        try:
            manifest.append(transcribe_one(src))
        except Exception as e:  # keep going: one bad file shouldn't block the rest
            log(f"{src.stem}: ERROR {e}")
            manifest.append({"recorder_id": src.stem, "status": "error", "staging_dir": str(STAGING / src.stem),
                             "error": str(e)})
    print(json.dumps(manifest, indent=2))
    return 1 if any(m["status"] == "error" for m in manifest) else 0


if __name__ == "__main__":
    sys.exit(main())
