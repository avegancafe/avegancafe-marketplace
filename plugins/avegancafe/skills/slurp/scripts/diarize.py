#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["speechbrain>=1.0,<2", "torch<2.9", "torchaudio<2.9", "numpy", "scikit-learn"]
# ///
"""Label each segment of a staged transcript with an anonymous speaker (S1, S2, ...).

Runs after transcribe.py, in place on `<staging_dir>/transcript.json`. Nothing is stored
outside that file: voices are compared only within one recording, never named, never
kept between runs. The recorder has one mic, so this is clustering, not identification.

  1. Embed every whisper segment with a speaker-embedding model (ECAPA, local, no token).
  2. Cluster only the long segments (>= ANCHOR_S of speech) -- the clean samples -- into
     speakers: exactly --speakers N when known (a 1:1 is 2), else the best-separated count.
  3. Label every segment with its nearest speaker centroid. Segments too short to embed
     reliably inherit the previous segment's speaker.

Adds `speaker` ("S1".. by order of first appearance, or null) and `speaker_sim` (cosine
to that centroid, 0-1) to each segment, and a top-level `diarization` block. Re-running
overwrites the previous labels.

    diarize.py /tmp/slurp/261029_1504 --speakers 2
    diarize.py /tmp/slurp/261029_1504            # unknown speaker count (group meeting)

stdout: JSON {recorder_id, speakers: {S1: {segments, speech_s}, ...}, unlabeled}
stderr: progress.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

MODEL = "speechbrain/spkrec-ecapa-voxceleb"
SR = 16000
ANCHOR_S = 3.0  # clean samples that define the speakers
MIN_S = 1.0  # shorter than this: too little audio for a stable embedding, inherit instead
MAX_S = 15.0  # crop long segments; more audio adds little
MAX_K = 6  # most speakers tried when the count is unknown
MIN_SILHOUETTE = 0.08  # below this no split beats "one speaker"
MIN_SHARE = 0.05  # a cluster with less of the anchor speech than this is noise, folded in


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_audio(path: Path) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32)


def embed_segments(audio: np.ndarray, segments: list[dict]) -> np.ndarray:
    """L2-normalized embedding per segment; a zero row where the segment is under MIN_S."""
    import torch
    from speechbrain.inference.speaker import EncoderClassifier  # deferred: slow import

    enc = EncoderClassifier.from_hparams(source=MODEL, savedir=str(Path.home() / ".cache/slurp" / MODEL),
                                         run_opts={"device": "cpu"})
    out = np.zeros((len(segments), 192), dtype=np.float32)
    with torch.no_grad():
        for i, s in enumerate(segments):
            if s["end"] - s["start"] < MIN_S:
                continue
            a = audio[int(s["start"] * SR):int(min(s["end"], s["start"] + MAX_S) * SR)]
            e = enc.encode_batch(torch.from_numpy(a.copy()).unsqueeze(0)).squeeze().numpy()
            out[i] = e / (np.linalg.norm(e) or 1.0)
            if i % 200 == 0:
                log(f"  embedded {i}/{len(segments)}")
    return out


def cluster(anchors: np.ndarray, n: int | None) -> np.ndarray:
    """Ward linkage on the unit vectors (euclidean there tracks cosine). Average linkage was
    the first try and failed on noisy walks: a few outlier segments (street noise, a barista)
    became their own tiny cluster and both real voices merged into the other (2026-10-29,
    61-min walking 1:1). Ward favors compact, comparably sized clusters and doesn't do that.
    With no known count, pick the k in 2..MAX_K with the best cosine silhouette, or 1 speaker
    when no split clears MIN_SILHOUETTE."""
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score

    if n is not None:
        return AgglomerativeClustering(n_clusters=n, linkage="ward").fit_predict(anchors)
    best, best_score = np.zeros(len(anchors), dtype=int), MIN_SILHOUETTE
    for k in range(2, min(MAX_K, len(anchors) - 1) + 1):
        labels = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(anchors)
        score = silhouette_score(anchors, labels, metric="cosine")
        log(f"  k={k}: silhouette {score:.3f}")
        if score > best_score:
            best, best_score = labels, score
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("staging_dir", type=Path)
    ap.add_argument("--speakers", type=int, help="known number of speakers (a 1:1 is 2)")
    args = ap.parse_args()

    tj = args.staging_dir / "transcript.json"
    t = json.loads(tj.read_text())
    segs = t["segments"]
    log(f"{t['recorder_id']}: embedding {len(segs)} segments ({MODEL})...")
    emb = embed_segments(load_audio(args.staging_dir / "audio.mp3"), segs)

    dur = np.array([s["end"] - s["start"] for s in segs])
    anchor_idx = np.where((dur >= ANCHOR_S) & emb.any(axis=1))[0]
    if len(anchor_idx) < 2 * (args.speakers or 1):
        log(f"{t['recorder_id']}: only {len(anchor_idx)} segments >= {ANCHOR_S}s; too little speech to diarize")
        return 1
    labels = cluster(emb[anchor_idx], args.speakers)

    # With an unknown count, fold noise clusters (a cough, a barista) into the rest; a known
    # count is kept as asked. Then build centroids.
    keep = sorted(set(labels)) if args.speakers else [
        c for c in set(labels) if dur[anchor_idx][labels == c].sum() >= MIN_SHARE * dur[anchor_idx].sum()]
    centroids = np.stack([emb[anchor_idx][labels == c].mean(axis=0) for c in keep])
    centroids /= np.linalg.norm(centroids, axis=1, keepdims=True)

    sims = emb @ centroids.T  # zero rows (too short) score 0 everywhere
    nearest = sims.argmax(axis=1)
    order: dict[int, str] = {}  # cluster -> "S<n>" by first appearance
    prev = None
    for i, s in enumerate(segs):
        if emb[i].any():
            c = int(nearest[i])
            name = order.setdefault(c, f"S{len(order) + 1}")
            s["speaker"], s["speaker_sim"] = name, round(float(sims[i, c]), 3)
        else:
            s["speaker"], s["speaker_sim"] = prev, None
        prev = s["speaker"]

    t["diarization"] = {"model": MODEL, "speakers": len(keep), "requested": args.speakers,
                        "anchor_s": ANCHOR_S, "anchors": len(anchor_idx)}
    tmp = tj.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(tj)

    summary = {}
    for s in segs:
        if s["speaker"]:
            d = summary.setdefault(s["speaker"], {"segments": 0, "speech_s": 0.0})
            d["segments"] += 1
            d["speech_s"] = round(d["speech_s"] + s["end"] - s["start"], 1)
    print(json.dumps({"recorder_id": t["recorder_id"], "speakers": summary,
                      "unlabeled": sum(1 for s in segs if not s["speaker"])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
