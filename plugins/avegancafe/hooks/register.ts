import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { TitleState } from '../types'

const COMMAND = 'session-title'
const MAX_LEN = 72

const state = atom({ plugin: 'avegancafe', key: 'sessionTitle' } as const, { done: false } as TitleState)

export const TITLE_RE = /^(fix|chore|feat)\([A-Z][A-Za-z0-9]*\): [a-z0-9].*\S$/

const RULES = `You name coding sessions. Reply with ONE line and nothing else, in exactly this form:

<type>(<Scope>): <description>

- <type> is one of: feat (new capability), fix (something broken), chore (maintenance, config, docs, refactors, investigations, tooling).
- <Scope> is ONE PascalCase word naming the high-level area: a product area, system or repo (e.g. Auth, Billing, ClaudePlugins, Beads, CI, DevEnv). No spaces, no dots, no slashes.
- <description> is an imperative, lowercase phrase that says what the session is doing ("add retry to export uploads", not "added" or "adding"). No trailing period. Keep the whole line under ${MAX_LEN} characters.`

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

const generate = async ($: EngineInterface, request: string) => {
  const prompt = `Request:\n${clip(request, 1500)}\n\nTitle:`
  const r = await $.model.complete({ model: 'haiku', system: RULES, prompt, maxTokens: 60, effort: 'low' })
  return r.isAnswered ? clean(r.text) : undefined
}

/** Prompts typed by a person (interactive, or `-p` / SDK); not wakeups or injected messages. */
const isFromPerson = (source: string | undefined) => source === undefined || source === 'user' || source === 'sdk'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: COMMAND, description: 'Show the auto session title' })
    return next(e)
  })

  on('command.run', { command: COMMAND }, async $ => {
    const s = await read($, state)
    return { text: s.title ?? '(no title yet)' }
  })

  // Titles the session once, from the first message the person sends, and
  // never touches it again.
  on('classic.UserPromptSubmit', async ($, e, next) => {
    const result = await next(e)
    if (result.block || !isFromPerson(e.source)) return result

    const s = await read($, state)
    if (s.done) return result
    if (e.session_title) {
      // Already named (resumed, renamed by hand, or started with a name).
      await update($, state, x => ({ ...x, done: true }))
      return result
    }

    const text = e.prompt.trim()
    if (!text || text.startsWith('<')) return result

    // Mark done first, so a slow or failed call never retries on a later prompt.
    await update($, state, x => ({ ...x, done: true }))
    const title = await generate($, text).catch(() => undefined)
    if (!title) return result
    await update($, state, x => ({ ...x, title }))
    return { ...result, sessionTitle: title }
  })
}
