/**
 * `title` is the last title this mod produced; `locked` stops it touching the
 * title (set when someone renamed the session by hand, or via the command).
 */
export type TitleState = { title?: string; locked: boolean }

declare module 'claude-code' {
  interface PluginState {
    'avegancafe': { sessionTitle: TitleState }
  }
}
