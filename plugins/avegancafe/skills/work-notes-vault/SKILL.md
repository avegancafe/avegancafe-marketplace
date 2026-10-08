---
name: work-notes-vault
description: Use when Kyle asks about past work meetings or his Granola notes — "mine my Granola meetings for X", "what did we discuss about Y", "find the meeting where Z came up", "what did I tell <person>", meeting transcripts or summaries — or when reading or writing his J2 work notes vault (notes--work, Obsidian), even if Granola isn't named.
---

# Kyle's work notes vault (notes--work)

Kyle's Obsidian vault for J2 Health work notes. Besides hand-written notes, it holds a **full archive of his Granola meetings** (summaries + transcripts) that you can search with `rg`/`jq` — often better than the Granola API for "across all my meetings" questions.

## Locate and refresh the vault

| | |
|---|---|
| Local path | `~/workspace/notes--work/` (sibling of `~/workspace/notes--personal/`; cloud sessions may have it at `/workspace/notes--work/`) |
| Remote | `github.com/avegancafe/notes--work` — **private** |

```bash
V=~/workspace/notes--work; [ -d "$V" ] || V=/workspace/notes--work
[ -d "$V" ] || gh repo clone avegancafe/notes--work ~/workspace/notes--work
git -C "$V" pull --ff-only   # archive lands on GitHub weekly — always pull before mining
```

If the pull fails (local edits, divergence), mine the local copy and say it may be stale — don't stash, reset, or force anything.

## Vault layout

`J2/People/` (one note per person + `People.base`), `J2/Meetings/` (hand-written, `YYYY-MM-DD Title.md`), `J2/Projects/<slug>/`, `J2/Inbox/`, daily notes `YYYY-MM-DD.md` at the root, and `granola/` (the archive). **The vault's own `.claude/CLAUDE.md` is the authority on conventions** — read it before creating or editing any vault note.

## The Granola archive

```
granola/notes/YYYY/MM/YYYY-MM-DD--<title-slug>--<note_id>.md     readable
granola/notes/YYYY/MM/YYYY-MM-DD--<title-slug>--<note_id>.json   raw Granola API response
granola/state.json   { "last_synced_at": ... } — when the last sync ran
```

- Date in path = note `created_at` in **UTC** (an evening ET meeting can land on the next day). Transcript times are UTC too.
- Only notes **owned by kyle@j2health.com** are archived. Meetings someone else recorded aren't here.

**`.md`**: YAML header (`title`, `date`, `updated`, `owner`, `attendees` as `Name <email>`, `folders`, `web_url`, `id`), then `# Title`, `## Summary` (Granola's summary, headings demoted), `## Transcript` with one line per utterance:

```
[HH:MM:SS] me: …      ← Kyle's microphone
[HH:MM:SS] them: …    ← everyone else, undifferentiated
```

**`me` is Kyle; `them` is anyone else.** Never attribute a `them` line to a specific person from the label — infer only from content ("thanks, Sam") and say it's inferred. If a speaker `name` is ever present it replaces `me`/`them`.

**`.json`** keys: `id`, `object`, `title`, `owner{name,email}`, `created_at`, `updated_at`, `web_url`, `attendees[]{name,email}`, `calendar_event{event_title,organiser,invitees[]{email},scheduled_start_time,scheduled_end_time,calendar_event_id}`, `folder_membership[]{id,name}`, `space_membership`, `summary_text`, `summary_markdown`, `private_notes_text`, `private_notes_markdown`, `transcript[]{text,start_time,end_time,speaker{source,attribution}}` (`source`: `microphone`=me / `speaker`=them). Optional keys can be absent or null.

**Kyle's own typed notes (`private_notes_*`) are only in the `.json`** — the `.md` doesn't render them. Check them when he asks what *he* wrote down.

## Mining recipes

Run from the vault root. Search summaries first (cheap, high signal), then open transcripts for exact wording.

```bash
# Index: date, title, url, file — scope months with the path glob
jq -r '[.created_at[:10], .title, .web_url, input_filename] | @tsv' granola/notes/2026/0[3-5]/*.json | sort

# Which meetings mention a topic (summary or transcript)
rg -il 'credentialing' granola/notes -g '*.md'

# Summaries only
jq -r 'select((.summary_markdown // "") | test("credentialing"; "i")) | "\(.created_at[:10])  \(.title)  \(input_filename)"' granola/notes/*/*/*.json

# Meetings with a given attendee (name or email)
jq -r 'select(any(.attendees[]?; ((.email // "") + " " + (.name // "")) | test("alex"; "i"))) | "\(.created_at[:10])  \(.title)"' granola/notes/*/*/*.json

# By Granola folder (list names first: jq -r '.folder_membership[]?.name' … | sort | uniq -c)
jq -r --arg f "<folder name>" 'select(any(.folder_membership[]?; .name == $f)) | input_filename' granola/notes/*/*/*.json

# What Kyle himself said about something
rg -i '^\[[0-9:]+\] me: .*pricing' granola/notes -g '*.md'

# Kyle's typed notes
jq -r 'select((.private_notes_markdown // "") != "") | "\(.created_at[:10]) \(.title)\n\(.private_notes_markdown)\n"' granola/notes/*/*/*.json

# Summary section of one note
awk '/^## Summary/{p=1} /^## Transcript/{p=0} p' "granola/notes/2026/04/<file>.md"
```

For broad sweeps (many months, many hits), fan out by month or quarter to subagents and have each return findings with citations.

**Cite every claim** with the meeting date, title, Granola `web_url`, and the archive file path.

## Freshness and gaps

- **Lags up to a week.** The *Granola sync* GitHub Action runs Mondays 12:23 UTC. For anything after `state.json`'s `last_synced_at`, use Granola directly (Granola MCP/API, if connected), or offer to trigger a sync — it pushes to Kyle's repo, so confirm first: `gh workflow run granola-sync.yml -R avegancafe/notes--work`, then pull when it finishes.
- A note appears only after Granola has generated its summary.
- Transcripts deleted by Granola retention before the first sync are gone; once archived, the sync keeps them even if Granola later drops them.
- No hits doesn't mean it wasn't discussed — the meeting may be someone else's recording, unrecorded, or not yet synced. Say which.

## Rules

- **Never edit anything under `granola/`** — the sync regenerates it and will overwrite or prune your changes.
- `granola/` is an intentional raw archive, so the vault's "don't paste full transcripts" rule doesn't apply *to it*. When writing new vault notes (e.g. `J2/Meetings/`), link to the archived file and `web_url`; quote only the lines you need.
- The archive holds attendee emails and private discussions — keep excerpts out of public places (public repos, public channels, shared artifacts) unless Kyle says otherwise.
