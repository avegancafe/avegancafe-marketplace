#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mutagen"]
# ///
"""Tag one album folder of FLACs from a MusicBrainz release, embed cover art, rename.

    tag_release.py <album dir> <musicbrainz release id> [--dry] [--no-rename] [--genre Jazz]

Files are matched to tracks by the FIRST number in the filename (store downloads look
like `3_Artist_Album_Title_LL_44_24.flac`). It refuses to write unless the file count
equals the release's track count and every file's duration is within 3 s of its track.

Writes Vorbis comments: TITLE, ARTIST (with " feat. " join phrases), ALBUMARTIST, ALBUM,
DATE, YEAR, ORIGINALDATE, TRACKNUMBER/TRACKTOTAL/TOTALTRACKS, DISCNUMBER/DISCTOTAL/
TOTALDISCS, GENRE (release-group's top genre unless --genre), LABEL, BARCODE, ISRC,
MUSICBRAINZ_* ids; ITUNESADVISORY=1 when the filename has a `_PA` (parental advisory) marker.
Cover: Cover Art Archive front -> 500x500 baseline JPEG (ffmpeg) -> embedded (type 3)
and written as cover.jpg. Rename: `NN - Title.flac`.
"""
import json, os, re, subprocess, sys, tempfile, time, urllib.request
from mutagen.flac import FLAC, Picture

args = [a for a in sys.argv[1:] if not a.startswith("--")]
d, rel_id = args[0], args[1]
dry, rename = "--dry" in sys.argv, "--no-rename" not in sys.argv
genre = sys.argv[sys.argv.index("--genre") + 1] if "--genre" in sys.argv else None
UA = {"User-Agent": "avegancafe-hifi-h2/1.0"}  # MusicBrainz wants a UA; no personal contact info


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except Exception as e:  # MB returns 503 "server busy" under load; back off
            if i == tries - 1:
                raise
            print(f"retry {url}: {e}", file=sys.stderr)
            time.sleep(2 * (i + 1))


rel = json.loads(get(f"https://musicbrainz.org/ws/2/release/{rel_id}?inc=recordings+artist-credits+labels+release-groups+isrcs+genres&fmt=json"))
rg = rel["release-group"]
if genre is None:
    time.sleep(1)
    rgj = json.loads(get(f"https://musicbrainz.org/ws/2/release-group/{rg['id']}?inc=genres&fmt=json"))
    gs = sorted(rgj.get("genres", []), key=lambda g: -g["count"])
    genre = gs[0]["name"].title() if gs else ""


def credit(ac):
    return "".join(c["name"] + c.get("joinphrase", "") for c in ac)


tracks = []
for medium in rel["media"]:
    for t in medium["tracks"]:
        tracks.append((medium["position"], len(medium["tracks"]), t))
if len(rel["media"]) > 1:
    sys.exit("multi-disc release: tag each disc folder by hand or extend this script")

files = sorted((f for f in os.listdir(d) if f.lower().endswith(".flac")),
               key=lambda f: int(re.search(r"\d+", f).group()))
if len(files) != len(tracks):
    sys.exit(f"{len(files)} files but release has {len(tracks)} tracks — wrong release/edition?")

for f, (_, _, t) in zip(files, tracks):
    n = int(re.search(r"\d+", f).group())
    if n != int(t["position"]):
        sys.exit(f"{f}: number {n} doesn't line up with track {t['position']}")
    length = FLAC(os.path.join(d, f)).info.length
    if not t.get("length"):
        sys.exit(f"{f}: MusicBrainz has no length for track {t['position']}, can't verify the match")
    if abs(length - t["length"] / 1000) > 3:
        sys.exit(f"{f}: {length:.0f}s vs MusicBrainz {t['length']/1000:.0f}s — wrong release?")

cover = os.path.join(d, "cover.jpg")
pic = None
if rel.get("cover-art-archive", {}).get("front"):
    with tempfile.NamedTemporaryFile(suffix=".img") as raw:
        raw.write(get(f"https://coverartarchive.org/release/{rel_id}/front"))
        raw.flush()
        if not dry:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw.name, "-vf", "scale=500:500",
                            "-q:v", "2", cover], check=True)
    if not dry:
        pic = Picture()
        pic.type, pic.mime, pic.width, pic.height, pic.depth = 3, "image/jpeg", 500, 500, 24
        pic.data = open(cover, "rb").read()
else:
    print("no front cover on Cover Art Archive — add cover.jpg by hand", file=sys.stderr)

label = (rel.get("label-info") or [{}])[0].get("label") or {}
for f, (disc, total, t) in zip(files, tracks):
    rec = t["recording"]
    tags = {
        "TITLE": t["title"], "ARTIST": credit(t["artist-credit"]),
        "ALBUMARTIST": credit(rel["artist-credit"]), "ALBUM": rel["title"],
        "DATE": rel.get("date", ""), "YEAR": rel.get("date", "")[:4],
        "ORIGINALDATE": rg.get("first-release-date", ""),
        "TRACKNUMBER": str(t["position"]), "TRACKTOTAL": str(total), "TOTALTRACKS": str(total),
        "DISCNUMBER": str(disc), "DISCTOTAL": "1", "TOTALDISCS": "1",
        "GENRE": genre, "LABEL": label.get("name", ""), "BARCODE": rel.get("barcode") or "",
        "ISRC": (rec.get("isrcs") or [""])[0],
        "MUSICBRAINZ_ALBUMID": rel_id, "MUSICBRAINZ_RELEASEGROUPID": rg["id"],
        "MUSICBRAINZ_TRACKID": rec["id"],
    }
    # The _PA marker is gone after the first run's rename, so keep an advisory already written.
    if re.search(r"_PA(\b|_|\.)", f) or FLAC(os.path.join(d, f)).get("ITUNESADVISORY"):
        tags["ITUNESADVISORY"] = "1"
    tags = {k: v for k, v in tags.items() if v}
    safe_title = re.sub(r'[\\/:*?"<>|]', "_", t["title"])  # FAT32-illegal characters
    new = f"{int(t['position']):02d} - {safe_title}.flac"
    print(f"{f} -> {new if rename else f}: {tags['ARTIST']} / {tags['TITLE']}")
    if dry:
        continue
    p = os.path.join(d, f)
    fl = FLAC(p)
    fl.delete()
    for k, v in tags.items():
        fl[k] = v
    if pic:  # without a replacement, keep whatever art is already embedded
        fl.clear_pictures()
        fl.add_picture(pic)
    fl.save()
    if rename and new != f:
        os.rename(p, os.path.join(d, new))
print(f"{'would tag' if dry else 'tagged'} {len(files)} files: {tags['ALBUMARTIST']} — {rel['title']} ({rel.get('date','')}), genre {genre!r}")
