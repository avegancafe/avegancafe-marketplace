#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["pyannote.audio>=4.0,<5", "numpy"]
# ///
"""Label who is speaking in /slurp recordings, using voiceprints Kyle has confirmed.

Runs after transcribe.py, on its staging dirs (/tmp/slurp/<recorder_id>/). Local only:
the model downloads once from Hugging Face (gated: needs HF_TOKEN), then nothing leaves
the machine. Voiceprints live in ~/.config/local/slurp/voiceprints.json, machine-local and
never committed. They are biometric data about other people.

    diarize.py run [ID ...]              # diarize staged recordings (default: all not yet done)
    diarize.py run ID --force            # redo one
    diarize.py label ID SPEAKER_01 NAME  # "that voice is NAME": save its voiceprint, rematch all staged
    diarize.py enroll NAME sample.m4a    # voiceprint from a clip of NAME talking alone
    diarize.py people                    # list saved voiceprints
    diarize.py forget NAME [--source ID] # delete a person's voiceprints (or one sample)

Each run writes <staging>/diarization.json:
  {model, speakers: [{id, display, name, score, labelled, minor, talk_s, candidates, clips}],
   turns: [{start, end, speaker}], segment_speakers: [speaker id | null per transcript segment]}
and short clips of each speaker in <staging>/clips/ for Kyle to listen to (afplay <clip>).
stdout: JSON summary per recording. stderr: progress.
Exit 2: nothing staged. Exit 3: no Hugging Face access (HF_TOKEN unset or terms not accepted).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

STAGING = Path("/tmp/slurp")
DEFAULT_DEVICE = Path("/Volumes/IC RECORDER")
MODEL = "pyannote/speaker-diarization-community-1"
LIBRARY = Path.home() / ".config/local/slurp/voiceprints.json"
SAMPLE_RATE = 16_000

# Cosine similarity between a speaker's voiceprint and a saved one. Same-voice pairs on this
# model usually score well above 0.5 and different voices well below. Noisy pocket audio pulls
# both toward the middle, so a match also has to beat the runner-up by MARGIN. Tune with --threshold.
THRESHOLD = 0.5
MARGIN = 0.1
MINOR_TALK_S = 8.0  # less total speech than this: likely noise or a passer-by, don't ask about it
CLIPS_PER_SPEAKER = 3
CLIP_MAX_S = 12.0
CLIP_MIN_S = 2.0


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


# ---------------------------------------------------------------- voiceprint library

def load_library() -> dict:
    if LIBRARY.exists():
        lib = json.loads(LIBRARY.read_text())
        if lib.get("model") != MODEL:
            sys.exit(f"{LIBRARY} was built with {lib.get('model')}, not {MODEL}; voiceprints from "
                     "different models aren't comparable. Move it aside and re-label.")
        return lib
    return {"model": MODEL, "people": {}}


def save_library(lib: dict) -> None:
    write_json(LIBRARY, lib)
    LIBRARY.chmod(0o600)


def unit(v) -> np.ndarray | None:
    v = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(v)
    return v / n if n > 0 and np.isfinite(n) else None


def match_speakers(speakers: list[dict], lib: dict, threshold: float) -> None:
    """Fill each speaker's candidates/name/score from the library. Labelled speakers keep their name.
    Greedy one-to-one: a person names at most one speaker per recording."""
    people = {name: [u for s in samples if (u := unit(s["embedding"])) is not None]
              for name, samples in lib["people"].items()}
    taken = {s["name"] for s in speakers if s.get("labelled")}
    pairs = []
    for sp in speakers:
        e = unit(sp["embedding"]) if sp.get("embedding") else None
        scores = sorted(((max(float(e @ u) for u in us), name) for name, us in people.items() if us),
                        reverse=True) if e is not None else []
        sp["candidates"] = [{"name": n, "score": round(sc, 3)} for sc, n in scores[:3]]
        if sp.get("labelled"):
            continue
        sp["name"], sp["score"] = None, None
        if scores and scores[0][0] >= threshold and (len(scores) == 1 or scores[0][0] - scores[1][0] >= MARGIN):
            pairs.append((scores[0][0], scores[0][1], sp))
    for score, name, sp in sorted(pairs, key=lambda p: -p[0]):
        if name not in taken:
            taken.add(name)
            sp["name"], sp["score"] = name, round(score, 3)


# ---------------------------------------------------------------- audio + model

def decode(path: Path) -> np.ndarray:
    """Mono 16 kHz float32 via ffmpeg (keeps pyannote off torchcodec/ffmpeg-version trouble)."""
    out = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


_PIPELINE = None


def pipeline():
    global _PIPELINE
    if _PIPELINE is None:
        import torch
        from pyannote.audio import Pipeline

        log(f"loading {MODEL} (first run downloads it)...")
        try:
            _PIPELINE = Pipeline.from_pretrained(MODEL, token=os.environ.get("HF_TOKEN") or None)
        except Exception as e:  # gated repo: 401/403 surfaces as various hub errors
            log(f"Can't load {MODEL}: {e}\nNeeds a Hugging Face read token in HF_TOKEN "
                f"(~/.config/local/.env) and the model's terms accepted at https://hf.co/{MODEL}")
            sys.exit(3)
        if _PIPELINE is None:
            log(f"Can't load {MODEL}: set HF_TOKEN and accept the terms at https://hf.co/{MODEL}")
            sys.exit(3)
        if torch.backends.mps.is_available():
            _PIPELINE.to(torch.device("mps"))
    return _PIPELINE


def diarize_audio(samples: np.ndarray, **hints) -> tuple[list[dict], dict[str, list[float] | None]]:
    """-> (exclusive turns [{start, end, speaker}], {speaker: embedding})."""
    import torch

    pipe = pipeline()
    audio = {"waveform": torch.from_numpy(samples).unsqueeze(0), "sample_rate": SAMPLE_RATE}
    try:
        out = pipe(audio, **hints)
    except (RuntimeError, NotImplementedError) as e:  # an op missing on Apple's GPU: redo on CPU
        log(f"GPU run failed ({e}); retrying on CPU")
        pipe.to(torch.device("cpu"))
        out = pipe(audio, **hints)
    turns = [{"start": round(t.start, 2), "end": round(t.end, 2), "speaker": spk}
             for t, _, spk in out.exclusive_speaker_diarization.itertracks(yield_label=True)]
    labels = out.speaker_diarization.labels()
    embs = out.speaker_embeddings
    emb = {spk: (embs[i].tolist() if embs is not None and unit(embs[i]) is not None else None)
           for i, spk in enumerate(labels)}
    return turns, emb


# ---------------------------------------------------------------- per recording

def overlap(a0, a1, b0, b1) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def assign_segments(segments: list[dict], turns: list[dict]) -> list[str | None]:
    """Each transcript segment -> the speaker with the most speech inside it (None: nobody)."""
    out = []
    for seg in segments:
        talk: dict[str, float] = {}
        for t in turns:
            if t["end"] > seg["start"] and t["start"] < seg["end"]:
                talk[t["speaker"]] = talk.get(t["speaker"], 0) + overlap(seg["start"], seg["end"], t["start"], t["end"])
        out.append(max(talk, key=talk.get) if talk else None)
    return out


def cut_clips(audio: Path, stage: Path, spk: str, turns: list[dict], segments: list[dict]) -> list[dict]:
    """The speaker's longest solo stretches, so Kyle can hear who it is."""
    clips_dir = stage / "clips"
    clips_dir.mkdir(exist_ok=True)
    mine = sorted((t for t in turns if t["speaker"] == spk and t["end"] - t["start"] >= CLIP_MIN_S),
                  key=lambda t: t["start"] - t["end"])[:CLIPS_PER_SPEAKER]
    clips = []
    for n, t in enumerate(sorted(mine, key=lambda t: t["start"]), 1):
        start, end = t["start"], min(t["end"], t["start"] + CLIP_MAX_S)
        path = clips_dir / f"{spk}-{n}.mp3"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{start}", "-t", f"{end - start:.2f}",
                        "-i", str(audio), "-ac", "1", "-q:a", "5", str(path)], check=True)
        text = " ".join(s["text"] for s in segments if s["end"] > start and s["start"] < end)
        clips.append({"path": str(path), "start": start, "end": end, "text": text})
    return clips


def renumber(speakers: list[dict]) -> None:
    """display = name, else "Speaker N". N is fixed per recording by talk time (Speaker 1 talks
    most) and never shifts when others get named, so "Speaker 2" means the same voice all session."""
    for n, sp in enumerate(speakers, 1):
        sp.setdefault("number", n)
        sp["display"] = sp.get("name") or f"Speaker {sp['number']}"


def summary(rid: str, d: dict) -> dict:
    return {"recorder_id": rid, "speakers": [
        {k: sp.get(k) for k in ("id", "display", "name", "score", "labelled", "minor", "talk_s", "candidates", "clips")}
        for sp in d["speakers"]]}


def find_on_device(rid: str, device: Path) -> Path | None:
    rec = device / "REC_FILE"
    return next((p for p in rec.rglob(f"{rid}.*") if p.suffix.lower() == ".mp3"), None) if rec.is_dir() else None


def run_one(stage: Path, lib: dict, args) -> dict:
    rid = stage.name
    transcript = json.loads((stage / "transcript.json").read_text())
    audio = stage / "audio.mp3"
    if not audio.exists():
        src = find_on_device(rid, args.device)
        if not src:
            raise FileNotFoundError(f"{audio} is gone and {rid} isn't on {args.device}")
        shutil.copyfile(src, audio)

    log(f"{rid}: diarizing...")
    hints = {k: v for k, v in (("num_speakers", args.speakers), ("min_speakers", args.min_speakers),
                               ("max_speakers", args.max_speakers)) if v}
    turns, emb = diarize_audio(decode(audio), **hints)
    shutil.rmtree(stage / "clips", ignore_errors=True)
    talk: dict[str, float] = {}
    for t in turns:
        talk[t["speaker"]] = talk.get(t["speaker"], 0) + t["end"] - t["start"]
    speakers = [{"id": spk, "talk_s": round(talk.get(spk, 0), 1), "minor": talk.get(spk, 0) < MINOR_TALK_S,
                 "embedding": e, "labelled": False}
                for spk, e in sorted(emb.items(), key=lambda kv: -talk.get(kv[0], 0))]
    match_speakers(speakers, lib, args.threshold)
    for sp in speakers:
        sp["clips"] = [] if sp["minor"] else cut_clips(audio, stage, sp["id"], turns, transcript["segments"])
    renumber(speakers)
    d = {"recorder_id": rid, "model": MODEL, "threshold": args.threshold,
         "diarized_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "speakers": speakers, "turns": turns,
         "segment_speakers": assign_segments(transcript["segments"], turns)}
    write_json(stage / "diarization.json", d)
    named = [sp["display"] for sp in speakers if not sp["minor"]]
    log(f"{rid}: {len(speakers)} speaker(s): {', '.join(named) or 'none'}")
    return summary(rid, d)


def rematch_all(lib: dict) -> list[dict]:
    changed = []
    for f in sorted(STAGING.glob("*/diarization.json")):
        d = json.loads(f.read_text())
        before = [sp.get("name") for sp in d["speakers"]]
        match_speakers(d["speakers"], lib, d.get("threshold", THRESHOLD))
        renumber(d["speakers"])
        write_json(f, d)
        if before != [sp.get("name") for sp in d["speakers"]]:
            changed.append(summary(d["recorder_id"], d))
    return changed


# ---------------------------------------------------------------- commands

def cmd_run(args) -> int:
    lib = load_library()
    stages = ([STAGING / i for i in args.ids] if args.ids else
              sorted(p.parent for p in STAGING.glob("*/transcript.json")))
    if not args.force:
        stages = [s for s in stages if not (s / "diarization.json").exists()]
    if not stages:
        log(f"nothing to diarize in {STAGING} (run transcribe.py first, or pass --force)")
        print("[]")
        return 2 if not any(STAGING.glob("*/transcript.json")) else 0
    results, failed = [], False
    for stage in stages:
        if not (stage / "transcript.json").exists():
            results.append({"recorder_id": stage.name, "error": "not staged (no transcript.json)"})
            failed = True
            continue
        try:
            results.append(run_one(stage, lib, args))
        except Exception as e:  # one bad recording shouldn't block the rest
            log(f"{stage.name}: ERROR {e}")
            results.append({"recorder_id": stage.name, "error": str(e)})
            failed = True
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 1 if failed else 0


def cmd_label(args) -> int:
    f = STAGING / args.id / "diarization.json"
    if not f.exists():
        sys.exit(f"{f} not found: run `diarize.py run {args.id}` first")
    d = json.loads(f.read_text())
    sp = next((s for s in d["speakers"] if args.speaker in (s["id"], s.get("display"))), None)
    if not sp:
        sys.exit(f"no speaker {args.speaker!r} in {args.id}: " + ", ".join(f"{s['id']} ({s['display']})" for s in d["speakers"]))
    if not sp.get("embedding"):
        sys.exit(f"{args.speaker} has no voiceprint (too little clean speech); can't learn from it")
    lib = load_library()
    samples = lib["people"].setdefault(args.name, [])
    samples[:] = [s for s in samples if s.get("source") != args.id]  # relabelling replaces, never duplicates
    for others in lib["people"].values():  # this recording's voice can't also be someone else
        if others is not samples:
            others[:] = [s for s in others if not (s.get("source") == args.id and s.get("speaker") == sp["id"])]
    samples.append({"embedding": sp["embedding"], "source": args.id, "speaker": sp["id"],
                    "added": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    lib["people"] = {k: v for k, v in lib["people"].items() if v}
    save_library(lib)
    for other in d["speakers"]:  # a person is one speaker per recording
        if other is not sp and other.get("labelled") and other.get("name") == args.name:
            other.update(labelled=False, name=None)
    sp.update(name=args.name, score=None, labelled=True)
    renumber(d["speakers"])
    write_json(f, d)
    log(f"{args.id} {sp['id']} = {args.name} ({len(samples)} sample(s) saved)")
    print(json.dumps({"labelled": summary(args.id, d), "rematched": rematch_all(lib)}, indent=2, ensure_ascii=False))
    return 0


def cmd_enroll(args) -> int:
    turns, emb = diarize_audio(decode(args.audio))
    talk: dict[str, float] = {}
    for t in turns:
        talk[t["speaker"]] = talk.get(t["speaker"], 0) + t["end"] - t["start"]
    if not talk:
        sys.exit("no speech found in the sample")
    main = max(talk, key=talk.get)
    if not emb.get(main):
        sys.exit("couldn't fingerprint the sample (too short or too noisy); use 20+ s of one person talking")
    if len(talk) > 1:
        log(f"warning: sample has {len(talk)} voices; using the one that talks most ({talk[main]:.0f}s)")
    lib = load_library()
    lib["people"].setdefault(args.name, []).append(
        {"embedding": emb[main], "source": f"enroll:{args.audio.name}", "speaker": main,
         "added": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    save_library(lib)
    log(f"enrolled {args.name} from {args.audio.name} ({talk[main]:.0f}s of speech)")
    print(json.dumps({"enrolled": args.name, "talk_s": round(talk[main], 1), "rematched": rematch_all(lib)},
                     indent=2, ensure_ascii=False))
    return 0


def cmd_people(_args) -> int:
    lib = load_library()
    print(json.dumps({n: [s["source"] for s in v] for n, v in sorted(lib["people"].items())}, indent=2, ensure_ascii=False))
    return 0


def cmd_forget(args) -> int:
    lib = load_library()
    if args.name not in lib["people"]:
        sys.exit(f"no voiceprints for {args.name!r}")
    if args.source:
        lib["people"][args.name] = [s for s in lib["people"][args.name] if s.get("source") != args.source]
    else:
        lib["people"][args.name] = []
    lib["people"] = {k: v for k, v in lib["people"].items() if v}
    save_library(lib)
    for f in STAGING.glob("*/diarization.json"):  # un-confirm labels that relied on what was deleted
        d = json.loads(f.read_text())
        if d["recorder_id"] == args.source or not args.source:
            for sp in d["speakers"]:
                if sp.get("labelled") and sp.get("name") == args.name:
                    sp.update(labelled=False, name=None)
            write_json(f, d)
    print(json.dumps({"forgot": args.name, "source": args.source, "rematched": rematch_all(lib)}, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="diarize staged recordings")
    r.add_argument("ids", nargs="*", help="recorder ids (default: every staged one not yet diarized)")
    r.add_argument("--force", action="store_true", help="redo recordings that already have diarization.json")
    r.add_argument("--threshold", type=float, default=THRESHOLD, help=f"auto-name cutoff (default {THRESHOLD})")
    r.add_argument("--speakers", type=int, help="exact number of speakers, when known")
    r.add_argument("--min-speakers", type=int)
    r.add_argument("--max-speakers", type=int)
    r.add_argument("--device", type=Path, default=DEFAULT_DEVICE, help="recorder mount, to restage wiped audio")
    r.set_defaults(fn=cmd_run)

    lb = sub.add_parser("label", help="name a speaker in a recording and save their voiceprint")
    lb.add_argument("id")
    lb.add_argument("speaker", help='SPEAKER_01 or its display name ("Speaker 2")')
    lb.add_argument("name", help="person's name, matching their J2/People note when there is one")
    lb.set_defaults(fn=cmd_label)

    en = sub.add_parser("enroll", help="save a voiceprint from a clip of one person talking")
    en.add_argument("name")
    en.add_argument("audio", type=Path)
    en.set_defaults(fn=cmd_enroll)

    sub.add_parser("people", help="list saved voiceprints").set_defaults(fn=cmd_people)

    fg = sub.add_parser("forget", help="delete a person's voiceprints")
    fg.add_argument("name")
    fg.add_argument("--source", help="only the sample learned from this recorder id")
    fg.set_defaults(fn=cmd_forget)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
