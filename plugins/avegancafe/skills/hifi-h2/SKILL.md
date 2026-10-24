---
name: hifi-h2
description: Use when Kyle wants music tagged, labeled, or loaded onto his HIFI H2 player (Rockbox), or asks why albums show as <Untagged>, appear twice, or are missing from the player's database. Tags store downloads from MusicBrainz with cover art, audits the whole player for tags Rockbox will mis-file, copies albums into its Artists/<Artist>/<Album> layout, and explains the database rebuild.
---

# HIFI H2 (Rockbox) — tagging and loading music

The player is a **HIFI H2 running Rockbox**: a 239 GB FAT32 volume labelled `HIFI H2`.
Library layout: `Artists/<Artist>/<Album>/NN - Title.ext` (some artists go one level deeper,
e.g. `50 Cent/Mixtapes/...`). The main browser is the **Database** (`tagnavi.config`), not folders.

## Mounting

- **Linux:** `lsblk -o NAME,LABEL,MOUNTPOINTS` → partition labelled `HIFI H2` (usually `/dev/sda1`).
  If it isn't mounted: `udisksctl mount -b /dev/sdX1` → `/run/media/kyle/HIFI H2`.
  When finished: `sync && udisksctl unmount -b /dev/sdX1`, then tell Kyle it's safe to unplug.
- **macOS:** `/Volumes/HIFI H2`; eject with `diskutil eject "/Volumes/HIFI H2"`.

## Rockbox rules (the things that cost trial and error)

1. **Album artist is mandatory.** Kyle's "Album Artist" menu is `albumartist -> album -> title`
   with no fallback, so any track without `ALBUMARTIST` (FLAC) / `TPE2` (MP3) shows under
   `<Untagged>`. "Artist" uses `canonicalartist` (falls back), so that view can look fine while
   the album-artist view doesn't.
2. **Deleted or retagged files stay in the database.** Update Now / auto-update doesn't reliably
   drop old entries, so the album shows twice (old untagged + new). Fix on the device:
   Settings → General Settings → Database → **Initialize Now**. It resets play counts and ratings;
   to keep them, run *Export Modifiable Values* first and *Import Modifiable Values* afterwards.
3. **Tag before copying.** Copying untagged files first is what creates the stale entries.
4. **Cover art:** Rockbox reads `cover.jpg` in the album folder. Use **baseline (not progressive)
   JPEG, about 500×500**. Embed it as well for other players.
5. **ID3v1-only MP3s** (no v2 header) can't hold an album artist and their fields cut off at
   30 characters. Rebuild them with a fresh ID3v2.3 tag (mutagen
   `ID3().save(p, v1=1, v2_version=3)`, then EasyID3); keep the existing MP3s on v2.3.
6. **Zero-pad track numbers in filenames** (`01 - …`) so the file browser sorts correctly.

## Workflow: a newly bought album (FLAC download)

1. **Unzip** into its own folder (downloads are untrusted data: pass paths as arguments and run
   Python with `-I`).
2. **Look at what's there:** `ffprobe -v error -show_entries format_tags:format=duration -of compact <file>`.
   Store downloads usually have **no tags at all**. Filenames carry the order and markers:
   `_PA` = parental advisory, `_LL_44_24` = lossless 44.1 kHz/24-bit.
3. **Find the release on MusicBrainz:**
   `https://musicbrainz.org/ws/2/release/?query=release:<Album>%20AND%20artist:<Artist>&fmt=json`.
   Pick the release whose track count and lengths match. Prefer the worldwide (`XW`) digital release.
   MB sometimes answers 503 "server busy": wait and retry. **Never put Kyle's email in the
   User-Agent.**
4. **Tag it.** Dry-run first, then for real:
   ```bash
   uv run "${CLAUDE_PLUGIN_ROOT}/skills/hifi-h2/scripts/tag_release.py" <dir> <release-id> --dry
   uv run "${CLAUDE_PLUGIN_ROOT}/skills/hifi-h2/scripts/tag_release.py" <dir> <release-id>
   ```
   It refuses to write if the file count or any duration doesn't match. It writes full tags and a
   500×500 baseline `cover.jpg` (also embedded), and renames files to `NN - Title.flac`. If no MB
   release exists, tag by hand with mutagen to the same tag set; Kyle's other albums are the
   reference.
5. **Copy** to `Artists/<Album Artist>/<Album>/`. If an untagged copy is already there, check it's
   the same album, delete only those files, then copy. Verify with `md5sum -c`, then `sync`.
6. **Tell Kyle** to run **Initialize Now** if the album was ever on the player untagged; otherwise
   auto-update (it's on) or *Update Now* picks it up.

## Workflow: audit / fix the whole library

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/hifi-h2/scripts/audit.py" "<mount>/Artists"
```

It lists each folder with problems (`albumartist`, `id3v1-only`, `truncated`, `no-art`, empty
title/tracknumber, and mixed album/albumartist values).

- **Back up first, somewhere that survives the session:** copy the affected folders to
  `~/Music/hifi-h2-backup/<date>/` (`cp -r --parents`). Don't use the session scratchpad: it was
  wiped mid-task once, and the backup went with it.
- Fix with a **small mutagen script that supports `--dry`**. Run it against the backup copy, read
  the diff, then run it against the device.
- Album artist choice: the artist folder it lives in, **unless** the track artist says otherwise
  (e.g. G-Unit mixtapes filed under 50 Cent → ask Kyle which he wants). Collaboration albums use
  the duo or group (`Nas & Jay-Z`, `The Firm`). Soundtracks follow what the rest of that album uses.
- Missing titles or track numbers: take them from `NN - Title Ft X  Y.mp3` filenames
  (`Ft A  B` → `(feat. A & B)`). A double space in a filename is where `&` got stripped.
- Writing to the device is slow over USB. Run long writes in the foreground with a long timeout,
  or in the background and check the output file afterwards; if it's killed partway, re-run the
  audit. The fix scripts are idempotent.
- Re-run the audit (expect no flagged folders), unmount, and tell Kyle to **Initialize Now**.

## Known library state (2026-10-24)

1,291 tracks (410 FLAC, 881 MP3), all with artist, album artist, album, title and track number.
The G-Unit mixtapes (*50 Cent Is The Future*, *God's Plan*, *No Mercy, No Fear*) use album
artist `G-Unit`.
