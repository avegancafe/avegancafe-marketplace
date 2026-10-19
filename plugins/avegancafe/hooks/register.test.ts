import { expect, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

import { clean } from './register'

const TITLE = 'feat(SessionTitle): auto-name sessions by convention'

const stub = (on: On, reply: string) => {
  const prompts: string[] = []
  on('model.complete', (_$, e) => {
    prompts.push(String(e.prompt))
    return { value: { isAnswered: true, text: reply, usage: { input_tokens: 1, output_tokens: 1 } } } as never
  })
  on('command.register', () => ({ value: {} }) as never)
  on('classic.UserPromptSubmit', () => ({}))
  return prompts
}

const submit = ($: Engine, prompt: string, opts: { session_title?: string; source?: string } = {}) =>
  $.classic.UserPromptSubmit({ prompt, source: 'user', ...opts } as never)

test('clean normalizes sloppy replies and rejects junk', () => {
  expect(clean('`Feat(claudePlugins): Add session title mod.`')).toBe('feat(ClaudePlugins): add session title mod')
  expect(clean('fix (Auth) : handle expired tokens')).toBe('fix(Auth): handle expired tokens')
  expect(clean('Sure! Here is a title')).toBeUndefined()
  expect(clean('docs(Readme): update')).toBeUndefined()
  const long = clean(`chore(DevEnv): ${'word '.repeat(30)}`)
  expect(long!.length <= 72).toBe(true)
})

test('first prompt is titled from that prompt alone', async ($, on) => {
  const prompts = stub(on, TITLE)
  const r = await submit($, 'make a hook that renames sessions')
  expect(r.sessionTitle).toBe(TITLE)
  expect(prompts).toHaveLength(1)
  expect(prompts[0]).toContain('make a hook that renames sessions')
})

test('later prompts never retitle or call the model', async ($, on) => {
  const prompts = stub(on, TITLE)
  await submit($, 'first')
  const r2 = await submit($, 'second', { session_title: TITLE })
  const r3 = await submit($, 'third')
  expect(r2.sessionTitle).toBeUndefined()
  expect(r3.sessionTitle).toBeUndefined()
  expect(prompts).toHaveLength(1)
})

test('injected prompts are skipped and do not use up the first prompt', async ($, on) => {
  const prompts = stub(on, TITLE)
  expect((await submit($, 'task finished', { source: 'system' })).sessionTitle).toBeUndefined()
  expect((await submit($, 'wake up', { source: 'loop_wakeup' })).sessionTitle).toBeUndefined()
  expect(prompts).toHaveLength(0)
  expect((await submit($, 'make a hook that renames sessions')).sessionTitle).toBe(TITLE)
})

test('an already-named session is left alone', async ($, on) => {
  const prompts = stub(on, TITLE)
  const r = await submit($, 'continue', { session_title: 'my own name' })
  expect(r.sessionTitle).toBeUndefined()
  await submit($, 'more')
  expect(prompts).toHaveLength(0)
})

test('a junk model reply gives no title and is not retried', async ($, on) => {
  const prompts = stub(on, 'Sure! Here is a title')
  expect((await submit($, 'first')).sessionTitle).toBeUndefined()
  expect((await submit($, 'second')).sessionTitle).toBeUndefined()
  expect(prompts).toHaveLength(1)
})
