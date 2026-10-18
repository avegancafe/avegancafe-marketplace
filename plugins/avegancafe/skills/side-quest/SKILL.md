---
name: side-quest
description: Use when, partway through a task, you notice a worthwhile problem the current task does not need fixed — an unrelated bug, a security or data-loss risk, a stale or broken test, a misleading doc, dead code, a refactor that would pay off — and you feel the pull to either detour into it or let it slide.
---

# Side quest

Stay on the main task, and still get tangential findings fixed: offer to hand each one to a **separate background Claude session** (`claude --bg`) that works it in its own worktree, while this session keeps going.

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

The new session starts cold — it sees **none** of this conversation. Write its prompt to a fresh temp file (`PROMPT_FILE=$(mktemp)`) containing: the finding with `path:line` evidence, why it matters, what "done" looks like, a scope fence ("fix only this; don't touch <the main task's area>"), and how to finish (commit on its branch, push, open a draft PR if the repo uses them, end with a report).

Run from the repo root:

```bash
claude --bg -n "fix(Scope): imperative summary" -w side-quest-<slug> "$(cat "$PROMPT_FILE")"
```

- `-n` names the session in agents view — use `type(Scope): imperative summary`.
- `-w` gives it its own git worktree and branch, so it can't collide with this session's edits. Drop `-w` outside a git repo.
- It prints `backgrounded · <id> · <name>`; tell the user `claude attach <id>` (or `←` in agent view) to look in.

If it refuses with "Workspace not trusted", or `claude` isn't on PATH, fall back to **Note it for later** and tell the user why.

## Common mistakes

| Mistake | Instead |
|---------|---------|
| Fixing it inline "since I'm here" | Ask. Scope creep is exactly what this prevents. |
| Silently ignoring it to stay focused | Ask. A one-line question costs the user seconds. |
| Offering a fork for something the task needs | It's part of the task — fix it. |
| Offering forks for nits | Mention or drop them; save forks for things worth a PR. |
| A spawn prompt that says "fix the thing we saw" | The fork has no context — paste the evidence. |
| Waiting on the fork or checking on it | It reports on its own; carry on with the main task. |
