#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mutagen"]
# ///
"""Report tracks the Rockbox database will mis-file, one line per album folder.

    audit.py <music root>            # e.g. "/run/media/kyle/HIFI H2/Artists"
    audit.py <root> --json           # machine-readable

Flags per track (counted per folder):
  albumartist   empty ALBUMARTIST/TPE2 -> lands under <Untagged> in "Album Artist"
  artist/album/title/tracknumber   empty
  id3v1-only    MP3 with no ID3v2 tag (no album artist possible, 30-char fields)
  truncated     title exactly 30 chars (ID3v1 truncation)
  no-art        folder has no cover.jpg/folder.jpg and the track has no embedded art
Also prints the distinct albumartist/album values for folders that are mixed.
"""
import collections, json, os, sys
import mutagen
from mutagen.id3 import ID3, ID3NoHeaderError

AUDIO = (".flac", ".mp3", ".m4a", ".ogg", ".opus")
root = sys.argv[1]
as_json = "--json" in sys.argv
report = {}

for dp, dn, fn in os.walk(root):  # not sorted(): that exhausts the walk before dn is pruned
    dn[:] = sorted(d for d in dn if not d.startswith(".") and d != "System Volume Information")
    files = [f for f in sorted(fn) if f.lower().endswith(AUDIO) and not f.startswith("._")]
    if not files:
        continue
    lower = {f.lower() for f in fn}
    folder_art = bool(lower & {"cover.jpg", "folder.jpg"})
    flags = collections.Counter()
    aa, al = collections.Counter(), collections.Counter()
    for f in files:
        p = os.path.join(dp, f)
        try:
            m = mutagen.File(p, easy=True)
        except Exception:
            flags["unreadable"] += 1
            continue
        t = (m.tags if m and m.tags else {}) or {}
        g = lambda k: (t.get(k) or [""])[0]
        for k in ("artist", "album", "title", "tracknumber", "albumartist"):
            if not g(k):
                flags[k] += 1
        if len(g("title")) == 30:
            flags["truncated"] += 1
        aa[g("albumartist")] += 1
        al[g("album")] += 1
        has_art = False
        if f.lower().endswith(".mp3"):
            try:
                id3 = ID3(p, load_v1=False)  # with v1 fallback a v1-only file loads fine
                has_art = any(k.startswith("APIC") for k in id3.keys())
            except ID3NoHeaderError:
                flags["id3v1-only"] += 1
        else:
            raw = mutagen.File(p)
            rt = raw.tags or {}
            has_art = bool(getattr(raw, "pictures", None)) or any(
                k in rt for k in ("covr", "metadata_block_picture", "METADATA_BLOCK_PICTURE", "coverart"))
        if not (folder_art or has_art):
            flags["no-art"] += 1
    rel = os.path.relpath(dp, root)
    entry = {"tracks": len(files), "flags": dict(flags)}
    if len(aa) > 1 or len(al) > 1:
        entry["albumartist_values"] = dict(aa)
        entry["album_values"] = dict(al)
    report[rel] = entry

if as_json:
    print(json.dumps(report, indent=1))
else:
    bad = 0
    for rel, e in report.items():
        if e["flags"] or "album_values" in e:
            bad += 1
            print(f"{e['tracks']:3d}  {rel}  {e['flags']}")
            if "album_values" in e:
                print(f"       albumartist={e['albumartist_values']}  album={e['album_values']}")
    total = sum(e["tracks"] for e in report.values())
    print(f"-- {total} tracks in {len(report)} folders; {bad} folders need attention")
