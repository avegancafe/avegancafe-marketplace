# hook-probe

A diagnostic plugin that answers one question: **do plugin hooks fire here?**

It registers a hook on `SessionStart`, `UserPromptSubmit`, `PostToolUse` (every
tool) and `Stop`. Each one appends a line to a log file:

```
2026-10-31T19:04:12Z	PostToolUse	tool=Bash	session=4f1c…	cwd=/workspace
```

It writes to every place it can, so at least one should work:

- `/tmp/hook-probe.log`
- `$CLAUDE_PROJECT_DIR/.hook-probe.log`
- `$CLAUDE_PLUGIN_DATA/hook-probe.log`

No network calls, nothing printed to Claude's context, never blocks a tool, always
exits 0. It uses `jq` or `python3` to read the hook JSON if either exists, and a
`sed` fallback if not.

## Test it in Claude Tag (Claude in Slack)

1. Attach `hook-probe` from this marketplace to a Slack channel.
2. Start a **new** thread there (hooks load when the session starts).
3. Ask Claude: `run ls, then cat /tmp/hook-probe.log`.
4. Read the result:
   - `SessionStart`, `UserPromptSubmit` and `PostToolUse tool=Bash` lines → hooks fire.
   - The file doesn't exist → hooks don't fire there (or `/tmp` is blocked; also
     ask for `cat "$CLAUDE_PROJECT_DIR/.hook-probe.log"`).
   - `Stop` lines show up after the turn ends, so ask a second time to see them.

## Test it locally

```bash
/plugin install hook-probe@avegancafe-marketplace
# restart Claude Code, run any command, then:
cat /tmp/hook-probe.log
```

Remove it when you're done: it logs every tool call for as long as it's enabled.
