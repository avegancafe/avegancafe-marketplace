import { expect, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

import { clean } from './register'

const stub = (on: On, reply: string) => {
  const prompts: string[] = []
  on('model.complete', (_$, e) => {
    prompts.push(String(e.prompt))
    return { value: { isAnswered: true, text: reply, usage: { input_tokens: 1, output_tokens: 1 } } } as never
  })
  on('session.turns', () => ({ value: 1 }))
  on('session.messages', () => ({ value: [] }) as never)
  on('command.register', () => ({ value: {} }) as never)
  on('ui.toast', () => ({ value: undefined }))
  on('classic.UserPromptSubmit', () => ({}))
  return prompts
}

const submit = ($: Engine, prompt: string, session_title?: string) =>
  $.classic.UserPromptSubmit({ prompt, session_title, source: 'user' } as never)

test('clean normalizes sloppy replies and rejects junk', () => {
  expect(clean('`Feat(claudePlugins): Add session title mod.`')).toBe('feat(ClaudePlugins): add session title mod')
  expect(clean('fix (Auth) : handle expired tokens')).toBe('fix(Auth): handle expired tokens')
  expect(clean('Sure! Here is a title')).toBeUndefined()
  expect(clean('docs(Readme): update')).toBeUndefined()
  const long = clean(`chore(DevEnv): ${'word '.repeat(30)}`)
  expect(long!.length <= 72).toBe(true)
})

test('first prompt is titled from the model reply', async ($, on) => {
  const prompts = stub(on, 'feat(SessionTitle): auto-name sessions by convention')
  const r = await submit($, 'make a hook that renames sessions')
  expect(r.sessionTitle).toBe('feat(SessionTitle): auto-name sessions by convention')
  expect(prompts[0]).toContain('make a hook that renames sessions')
})

test('a hand rename pauses auto-titling', async ($, on) => {
  stub(on, 'feat(SessionTitle): auto-name sessions by convention')
  await submit($, 'first')
  const r = await submit($, 'second', 'my own name')
  expect(r.sessionTitle).toBeUndefined()
  const r2 = await submit($, 'third', 'my own name')
  expect(r2.sessionTitle).toBeUndefined()
})

test('a resumed session keeps an already-conforming title', async ($, on) => {
  const prompts = stub(on, 'chore(Other): something else')
  const r = await submit($, 'continue', 'fix(Billing): handle refunds')
  expect(r.sessionTitle).toBeUndefined()
  expect(prompts).toHaveLength(0)
})
