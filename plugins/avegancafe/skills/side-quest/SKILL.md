---
name: side-quest
description: Use before finishing or summarizing any task during which you noticed a worthwhile problem outside its scope — a missing auth or permission check, a swallowed exception, a skipped or stale test, a README step that no longer works, an unrelated bug — instead of only mentioning it in your reply.
---

# Side quest

Stay on the main task, and still get tangential findings fixed: offer to **fork** this session into a named background session (`claude --bg --resume … --fork-session`) that fixes it in its own git worktree of the affected repo while this session keeps going.

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

Fork **this** session into a named background session. The fork inherits the whole conversation, so it already knows the finding, the evidence, and what you're doing — no handoff doc. It does its work in a **git worktree of the repo the finding lives in**, so it never touches your working tree.

1. Find that repo's root: `git -C <dir of the finding's file> rev-parse --show-toplevel`. It may differ from your working directory — e.g. you started in `~/workspace` and the finding is in `~/workspace/<repo>`.
2. Run from your current working directory, filling in every `<…>`:

```bash
claude --bg --resume "$CLAUDE_CODE_SESSION_ID" --fork-session \
  --name "<type>(<Scope>): <imperative summary>" \
  "You are a fork of this session. Your only job: <the finding, path:line>. Done = <what done looks like>.
First create a git worktree of the repo at <repo root> (not of your current directory): git -C <repo root> worktree add <repo root>/.claude/worktrees/side-quest-<slug> -b side-quest/<slug> <default branch, e.g. origin/main>. Do all reading, editing, testing and git work inside that worktree.
Touch only what this fix needs. Commit on side-quest/<slug>, push, and open a draft PR if the repo uses them. Don't start side quests of your own — list any further findings in your report, which ends with the branch, PR link, and files changed."
```

- `--resume … --fork-session` copies this conversation into a new session ID; the original keeps going untouched.
- `--name` (`-n`) is **required** — it's the fork's title in agent view, `claude agents`, and `claude attach <name>`. Fill in all three parts:
  - `<type>` is exactly one of `fix`, `chore` or `feat` — never `refactor`, `docs`, `test` or anything else (a refactor or doc fix is `chore`).
  - `<Scope>` is the domain the fix works in: the least common denominator that covers everything it touches (`Auth`, `Billing`, `Onboarding`), as one PascalCase word — never a file, function or path.
  - `<imperative summary>` is lowercase, imperative, no trailing period — e.g. `fix(Auth): require admin to delete users`.
- Don't pass `--worktree`: it worktrees the folder the session started in, which may be a parent like `~/workspace` rather than the repo. The worktree step in the prompt targets the right repo.
- If the finding only exists on your current branch (not on the default branch), base the worktree on `HEAD` instead and say so in the prompt.
- It prints `backgrounded · <id> · <name>`; tell the user `claude attach <id>` (or `←` in agent view) to look in.

If `$CLAUDE_CODE_SESSION_ID` is unset, or the command refuses ("Workspace not trusted", `claude` not on PATH), fall back to **Note it for later** and tell the user why.

## Common mistakes

| Mistake | Instead |
|---------|---------|
| Fixing it inline "since I'm here" | Ask. Scope creep is exactly what this prevents. |
| Silently ignoring it to stay focused | Ask. A one-line question costs the user seconds. |
| Offering a fork for something the task needs | It's part of the task — fix it. |
| Offering forks for nits | Mention or drop them; save forks for things worth a PR. |
| A fork prompt without the worktree step | The fork would edit your working tree — always have it create a worktree of the finding's repo first. |
| Waiting on the fork or checking on it | It reports on its own; carry on with the main task. |
