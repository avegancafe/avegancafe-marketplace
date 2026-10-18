---
name: side-quest
description: Use before finishing or summarizing any task during which you noticed a worthwhile problem outside its scope — a missing auth or permission check, a swallowed exception, a skipped or stale test, a README step that no longer works, an unrelated bug — instead of only mentioning it in your reply.
---

# Side quest

Stay on the main task, and still get tangential findings fixed: offer to **fork** this session into a named background session (`claude --bg --resume … --fork-session`) that fixes it in the same folder while this session keeps going.

## Is it a side quest?

It is one only if **all three** hold:

| Test | Question |
|------|----------|
| **Not required** | Can the current task ship correctly without it? |
| **Worth doing** | Would a teammate thank you for fixing it — a real bug, risk, broken/misleading test or doc, or a refactor with clear payoff? |
| **Not already in hand** | The user hasn't asked for it, it isn't already tracked, and it isn't a one-line tweak inside lines you are already changing? |

Otherwise handle it in place:

- **Required** (it blocks or breaks the current task) → fix it as part of the task. Not a side quest.
- **Already asked for, or the user said "just note it"** → do what they said.
- **Trivial and inside your diff** (a typo on a line you're editing) → just fix it.
- **Taste or speculation** ("I'd have named this differently", "this *might* be slow") → mention it at most; don't offer a fork.

## When you find one

1. **Ask once, right away, then keep working.** Use `AskUserQuestion`:
   - *What you found* (one line, with `path:line`) and *why it matters* (one line).
   - Options: **Spawn a side quest (Recommended)** · **Note it for later** · **Skip**.
   - Several findings at once → one question, `multiSelect`, one "Spawn: <finding>" option each; unchecked ones are noted for later.
2. **Return to the main task immediately**, whatever the answer. Never start fixing the side quest in this session.
3. **Spawn** → run the command below and report the id it printed.
   **Note** → file it in the project's tracker if there is one (e.g. `bd create` when `.beads/` exists); otherwise carry it to your final report.
   **Skip** → drop it.

## Spawning

Fork **this** session into a named background session in the same folder. The fork inherits the whole conversation, so it already knows the finding, the evidence, and what you're doing — no handoff doc.

Run from your current working directory:

```bash
claude --bg --resume "$CLAUDE_CODE_SESSION_ID" --fork-session \
  --name "fix(Scope): imperative summary" \
  "You are a fork of this session. Your only job: <the finding, path:line>. Done = <what done looks like>. The original session is still working on <main task> in this same folder — touch only the files this fix needs; don't switch branches, stash, reset, or commit anything you didn't change. Leave your change uncommitted and end with the files you touched. Don't start side quests of your own — list any further findings in your report."
```

- `--resume … --fork-session` copies this conversation into a new session ID; the original keeps going untouched.
- `--name` (`-n`) is **required** — it's the fork's title in agent view, `claude agents`, and `claude attach <name>`. Use `type(Scope): imperative summary`, e.g. `fix(Admin): require admin on delete_user`.
- No `--worktree`: the fork shares this folder, so the scope fence in the prompt is what keeps the two from colliding. If the fix should become its own branch/PR instead, add `--worktree side-quest-<slug>` and tell it to commit and push there.
- It prints `backgrounded · <id> · <name>`; tell the user `claude attach <id>` (or `←` in agent view) to look in.
- **After forking, fence yourself too:** the fork's edits land in your working tree uncommitted. Stage only explicit paths from your own task (never `git add -A` / `git commit -a`) and leave the fork's files alone.

If `$CLAUDE_CODE_SESSION_ID` is unset, or the command refuses ("Workspace not trusted", `claude` not on PATH), fall back to **Note it for later** and tell the user why.

## Common mistakes

| Mistake | Instead |
|---------|---------|
| Fixing it inline "since I'm here" | Ask. Scope creep is exactly what this prevents. |
| Silently ignoring it to stay focused | Ask. A one-line question costs the user seconds. |
| Offering a fork for something the task needs | It's part of the task — fix it. |
| Offering forks for nits | Mention or drop them; save forks for things worth a PR. |
| A fork prompt without a scope fence | Both sessions share the folder — name the files it may touch and forbid branch/stash/commit moves. |
| Waiting on the fork or checking on it | It reports on its own; carry on with the main task. |
