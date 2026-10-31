---
name: channels-for-complex-work
description: Use in Claude Duet before starting work that might be too big for one thread, meaning several parts that need coordinating (a migration, a rework across repos, a multi-step project), to decide between one thread and a new channel; especially in the main chat or a channel's coordinator. Also use when Kyle asks about or adds to an operation that already has its own channel, when running a channel's Tasks list as its coordinator, or when a thread finds its task has grown into several coordinated parts. Kyle's rule: complex multi-task operations get their own channel, coordinated through that channel's Tasks list, so the main chat stays clean.
---

# Channels for complex work

Kyle's standing preference for every Duet chat (his words, Oct 31 2026): for
complex operations that need several coordinated tasks, **create a channel for
the operation and run its parts as tasks on that channel's Tasks list**, each
with its own session. Don't run the operation from the main chat.

Why: the main chat is a conversation, and a long operation run from there fills
it with progress, relays and follow-ups. Inside a channel, each task's session
is like a Slack thread: Kyle opens it to check how that part is going, while the
channel's top level, and his main chat, stay conversational.

Bias toward the channel. Kyle has noticed coordinators lean toward doing work
in the main chat; when in doubt between one big thread and a channel, pick the
channel.

If the operation already has a channel, don't do its work where you are: pass
Kyle's asks to that channel (see "Steering from the main chat").

## Picking where work goes

| The ask | Where it goes |
|---------|---------------|
| A question you can answer, or a quick lookup the coordinator's own tools can reach | Answer it in the chat. |
| Anything that reads or changes a GitHub repo, however small | A task/thread: the coordinator can't read the channel's repos (see `duet-basics`). |
| Clearly one piece of work with one result, even a long one (a single PR, a draft, a research question) | One task/thread in the current chat. If you can't tell whether it's one piece or several, treat it as several. |
| An operation with **several parts** that each need their own session, run in parallel or in sequence, or that depend on each other (a rework across repos, a migration, a multi-step project, anything Kyle calls "a beast") | **A new channel**, with one task per part. |
| An ongoing area Kyle will keep coming back to (a project, a repo, a life area) | A channel, even if today's ask is small. |

Signs it's channel-sized: you're about to write a plan with three or more
steps that each need real work; parts could run at the same time; parts wait on
each other or on Kyle at different points; the work will span more than a day;
or one thread would end up juggling several PRs or deliverables.

A thread that finds mid-way that its task is really several coordinated parts
should stop growing it and say so in its report, naming the channel and the
tasks it would hold. Threads don't create channels or tasks; the main chat
does, from that report.

If a channel for the area already exists (check the channel list first), use it
and add tasks there instead of making a new one.

## Setting it up from the coordinator

1. **Make the channel.** Use the coordinator's channel-creation tool (in the
   main chat: `create_project` with the `channel` template). Name it for the
   operation in Kyle's words, and give it a topic that says what it's for.
2. **Brief the channel's Claude in the handover.** The channel's coordinator
   starts cold and only knows what the handover says. Include:
   - Kyle's ask, in his words, and what "done" looks like.
   - The parts, as a proposed task list: one task per part, each with its
     result, and which ones depend on which.
   - Anything already decided or found (repos, constraints, links Kyle gave).
   - To load the `channels-for-complex-work` skill (duet plugin), so it runs
     the channel by this skill.
   - This rule: make each part a task on the channel's Tasks list and start
     its session there; keep the channel's top level for questions, decisions
     and short updates; never do the parts' work in the coordinator itself.
   - Any repos the work needs, so the channel adds them before starting the
     tasks that need them (threads started before a repo is added can't read
     it; see `duet-basics`).
3. **Tell Kyle in one line** in the main chat that the operation has its own
   channel now, with a link, and what the channel will do first. Don't repeat
   the plan; it lives in the channel.

## Inside the channel

- The channel's coordinator turns the plan into tasks on its Tasks list and
  starts each task's session. Tasks that don't depend on each other run in
  parallel; dependent ones start when what they wait on is done.
- Each task's session owns its part end to end and reports on its own task.
  Kyle checks a part by opening that task.
- The coordinator keeps the Tasks list true: new parts become new tasks, done
  parts are marked done, blocked ones say what they wait on. The list is the
  operation's status board.
- The channel's top level stays short: decisions Kyle has to make, blockers,
  and a note when the whole operation is done.

## Steering from the main chat

Once the channel exists, the main chat doesn't do its work.

- When Kyle asks the main chat about the operation, or adds to it, pass it to
  the channel's coordinator (`message_project` from the main chat) and tell Kyle in a line that
  you've passed it on.
- Read the channel's timeline or Tasks list to answer "how's it going"
  questions; don't restart or duplicate its tasks from the main chat.
- When the channel reports the operation done, tell Kyle in the main chat in a
  line, with a link.

Tool names above are the ones seen so far and can change; use what your
session's tool list offers for creating a channel, messaging it and managing
its tasks. If a name here is wrong, fix it in this skill (see "Adding to this
plugin" in `duet-basics`).
