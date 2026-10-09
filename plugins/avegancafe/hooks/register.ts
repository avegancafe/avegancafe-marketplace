import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, SessionMessage } from 'claude-code'

import type { TitleState } from '../types'

const COMMAND = 'session-title'
const MAX_LEN = 72

const state = atom({ plugin: 'avegancafe', key: 'sessionTitle' } as const, { locked: false } as TitleState)

export const TITLE_RE = /^(fix|chore|feat)\([A-Z][A-Za-z0-9]*\): [a-z0-9].*\S$/

const RULES = `You name coding sessions. Reply with ONE line and nothing else, in exactly this form:

<type>(<Scope>): <description>

- <type> is one of: feat (new capability), fix (something broken), chore (maintenance, config, docs, refactors, investigations, tooling).
- <Scope> is ONE PascalCase word naming the high-level area: a product area, system or repo (e.g. Auth, Billing, ClaudePlugins, Beads, CI, DevEnv). No spaces, no dots, no slashes.
- <description> is an imperative, lowercase phrase that says what the session is doing ("add retry to export uploads", not "added" or "adding"). No trailing period. Keep the whole line under ${MAX_LEN} characters.

If a current title is given, keep it unless the work has clearly shifted or become more specific; when it has, sharpen it rather than rewriting from scratch.`

/** Normalizes a model reply into a valid title, or undefined if it can't. */
export const clean = (raw: string): string | undefined => {
  const line = raw
    .split('\n')
    .map(l => l.trim().replace(/^[`"'*]+|[`"'*.]+$/g, ''))
    .find(l => l.length > 0)
  if (!line) return undefined
  const m = /^(fix|chore|feat)\s*\(\s*([A-Za-z0-9]+)\s*\)\s*:\s*(.+)$/i.exec(line)
  const [, type = '', scope = '', desc = ''] = m ?? []
  if (!type || !scope || !desc) return undefined
  let title = `${type.toLowerCase()}(${scope.charAt(0).toUpperCase()}${scope.slice(1)}): ${desc.charAt(0).toLowerCase()}${desc.slice(1)}`
  if (title.length > MAX_LEN) title = title.slice(0, title.lastIndexOf(' ', MAX_LEN))
  return TITLE_RE.test(title) ? title : undefined
}

const clip = (s: string, n: number) => (s.length > n ? `${s.slice(0, n)}…` : s)

/** A compact digest of the conversation: every user ask plus the latest answer. */
const digest = async ($: EngineInterface) => {
  const messages: readonly SessionMessage[] = await $.session.messages()
  // Skip harness-injected user rows (system reminders, command wrappers).
  const asks = messages
    .filter(m => m.role === 'user' && m.text.trim() && !m.text.trimStart().startsWith('<'))
    .map(m => clip(m.text.trim(), 500))
  const lastAnswer = [...messages].reverse().find(m => m.role === 'assistant' && m.text.trim())
  const recent = asks.slice(1).slice(-6)
  return [
    asks[0] && `First request:\n${asks[0]}`,
    recent.length > 0 && `Later requests:\n${recent.map(a => `- ${a}`).join('\n')}`,
    lastAnswer && `Latest assistant reply (excerpt):\n${clip(lastAnswer.text.trim(), 800)}`,
  ]
    .filter(Boolean)
    .join('\n\n')
}

const generate = async ($: EngineInterface, context: string, current?: string) => {
  const prompt = `${current ? `Current title: ${current}\n\n` : ''}${context}\n\nTitle:`
  const r = await $.model.complete({ model: 'haiku', system: RULES, prompt, maxTokens: 60, effort: 'low' })
  return r.isAnswered ? clean(r.text) : undefined
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: COMMAND,
      description: 'Show the auto session title, or `lock` / `unlock` it',
    })
    return next(e)
  })

  on('command.run', { command: COMMAND }, async ($, e) => {
    const arg = e.args.trim().toLowerCase()
    if (arg === 'lock' || arg === 'unlock') {
      await update($, state, s => ({ ...s, locked: arg === 'lock' }))
      return { text: arg === 'lock' ? 'Session title locked.' : 'Session title unlocked; it updates on your next prompt.' }
    }
    const s = await read($, state)
    return { text: `${s.title ?? '(no title yet)'}${s.locked ? ' (locked)' : ''}` }
  })

  // The title can only be set as a prompt enters, so this applies whatever the
  // last refinement produced; the very first prompt is titled synchronously.
  on('classic.UserPromptSubmit', async ($, e, next) => {
    const result = await next(e)
    if (result.block) return result

    const s = await read($, state)
    if (s.locked) return result

    const current = e.session_title
    if (s.title && current && current !== s.title) {
      // Renamed by hand since we last set it: leave it alone.
      await update($, state, x => ({ ...x, locked: true }))
      $.ui.toast(`Session renamed by hand; auto-title paused (/${COMMAND} unlock to resume)`)
      return result
    }

    let title = s.title
    if (!title && current && TITLE_RE.test(current)) title = current // resumed session
    if (!title) {
      const history = (await $.session.turns()) > 1 ? await digest($) : ''
      title = await generate($, `${history ? `${history}\n\n` : ''}New request:\n${clip(e.prompt, 1500)}`)
    }
    if (!title) return result

    if (title !== s.title) await update($, state, x => ({ ...x, title }))
    return title === current ? result : { ...result, sessionTitle: title }
  })

  // After each main-thread turn, refine the title in the background so the next
  // prompt picks it up without waiting on a model call.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined || e.isAborted) return result
    const s = await read($, state)
    if (s.locked) return result
    void (async () => {
      const title = await generate($, await digest($), s.title)
      if (title && !(await read($, state)).locked) await update($, state, x => ({ ...x, title }))
    })().catch(() => {})
    return result
  })
}
