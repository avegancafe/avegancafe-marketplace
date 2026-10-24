---
name: phone-push
description: Use when Kyle asks to notify his phone or send a push notification — "ping me", "remind me at <time>", "ping me when X arrives", "check my inbox at 3 and tell me". Sends a mobile push now or at a scheduled time through a one-time or recurring cloud routine, optionally after checking Gmail/HEY first.
---

# Phone push notifications (cloud routine → PushNotification)

A **cloud routine** (created with the `RemoteTrigger` tool) whose prompt calls `PushNotification`
with `status: "proactive"` reaches Kyle's phone through the Claude mobile app. Verified 2026-10-24.

The cloud routine is the delivery path. A `PushNotification` called from this local session is
skipped whenever Kyle is active at the desktop, so it can't be relied on for a reminder.

Load the tool first: `ToolSearch` with `select:RemoteTrigger`.

## Steps

1. **Pin the time.** Run `date -u` (and `TZ=America/New_York date`) right before computing anything;
   never reuse a time from earlier in the session. Convert Kyle's wording to UTC.
   Done when you have a future RFC3339 UTC timestamp, or a cron expression, or "now".
2. **Write the notification text**: one line, under 200 characters, no markdown, leading with what
   to act on ("Call Ana Photo at 11 — quote is $4.2k" beats "reminder"). For check-then-notify
   routines, write the rule that turns the check's result into that line.
3. **Create the routine** with `RemoteTrigger` `action: "create"` and the body below.
   Done when the response's summary line shows the parsed run time you intended.
4. **"Now" requests:** call `RemoteTrigger` `action: "run"` with the new routine's `trigger_id`.
   Do this for anything urgent too: a scheduled `run_once_at` fire can land a minute or more late.
5. **Report back** the routine name, its claude.ai link, and the fire time in both
   America/New_York and UTC, so Kyle can catch a wrong conversion.

## Create body

```json
{
  "name": "Reminder: call photographer 11am",
  "run_once_at": "2026-10-25T15:00:00Z",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "env_01HiT3B442ebKLVNAXpe2eCi",
      "session_context": {
        "model": "claude-sonnet-5-5",
        "sources": [],
        "allowed_tools": ["PushNotification"]
      },
      "events": [{
        "data": {
          "uuid": "<fresh lowercase v4 uuid>",
          "session_id": "",
          "type": "user",
          "parent_tool_use_id": null,
          "message": { "role": "user", "content": "<routine prompt>" }
        }
      }]
    }
  }
}
```

- **Schedule:** `run_once_at` (RFC3339 **UTC**, must be in the future) for one-shots, or
  `cron_expression` instead for recurring ones: UTC, or prefix `CRON_TZ=America/New_York `;
  the minimum interval is 1 hour.
- **`message.role` is required**; the create fails without it. Generate the uuid fresh each time
  (`uuidgen | tr A-Z a-z`).
- **Environment:** `env_01HiT3B442ebKLVNAXpe2eCi` ("Default", anthropic_cloud) is the one that
  worked. `RemoteTrigger list` shows the environments other routines use.
- **`allowed_tools`:** add the connector tools a check-then-notify prompt needs next to
  `PushNotification`.

## Connectors

Routines created through the API auto-attach the account's claude.ai connectors (HEY, Gmail, …).
To attach one explicitly, add `mcp_connections` to `session_context`:

```json
"mcp_connections": [
  {"connector_uuid": "33fbd45b-970a-4492-b62d-24f1558edba4", "name": "HEY",   "url": "https://hey-mcp-avegancafe.fly.dev/mcp"},
  {"connector_uuid": "f76022b1-1d72-4498-9f51-badfabad818c", "name": "Gmail", "url": "https://gmailmcp.googleapis.com/mcp/v1"}
]
```

Only claude.ai connectors exist in the cloud. Local MCP servers (Zola, anything from this
machine's config) are unavailable to routines; do that part locally first and bake the result
into the prompt.

## Prompt templates

**Plain reminder**

```text
Call the PushNotification tool exactly once with status "proactive" and this message:
"Call Ana Photo at 11 — quote is $4.2k, ask about second shooter"
Then print the same message as your final reply.
```

**Check, then notify**

```text
Read-only task: do not send, archive, label, or modify anything.
1. Search Gmail and HEY for messages from <sender address> or mentioning "Ana Photo" received since 2026-10-24.
2. Build one line under 200 characters, no markdown:
   - if found: "Ana Photo replied: <subject> — <one-clause gist>"
   - if not: "No reply from Ana Photo yet (checked 2pm)"
3. Call PushNotification once with status "proactive" and that line.
4. Print the same line as your final reply.
```

The final printed line is the fallback: if the push doesn't arrive, the text is still in the
run's session at claude.ai/code.

## Debugging and cleanup

- `RemoteTrigger list_runs` (by `trigger_id`) → `get_run_log` (by `session_id`) shows what a run did.
- An empty `list_runs` doesn't prove the routine never fired (skipped fires leave no row): check it
  with `RemoteTrigger get` (`enabled`, `next_run_at`) and tell Kyle what you saw.
- Routines can't be deleted through the tool. Disable one with `update` `{"enabled": false}` if
  needed, and point Kyle to https://claude.ai/code/routines to delete finished ones.
