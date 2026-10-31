# juliet

Claude Code tooling for [Juliet](https://github.com/avegancafe/Juliet), the
scripted macOS + Fedora setup at `~/.config/Juliet`. This is the shared
baseline for anyone running Juliet; Kyle's personal tooling lives in the
`avegancafe` plugin.

## Install

```bash
/plugin install juliet --marketplace avegancafe/avegancafe-marketplace
```

## Agent

| Agent | Purpose |
|-------|---------|
| `noelle` | Thin entry point for computer-config work. Invoking it means "I'm changing my computer config — work within Juliet". All behavior lives in the skills below, which it preloads. |

## Skills

| Skill | Purpose |
|-------|---------|
| `juliet-config` | Core workflow: orient in Juliet, decide managed vs ad-hoc and shared vs personal, cover both OSes, no sudo, report back. |
| `juliet-extension` | The Juliet vs extension-repo split (`juliet-kyle`, `juliet-j2`): where each kind of change goes and why an extension edit applies only after a push. |
| `juliet-cross-platform` | macOS ↔ Fedora mapping: Brewfile ↔ DNFfile/Flatpakfile, OS-gating, equivalent tools. |
| `juliet-bootstrap-step` | Add or change a `setup-*` step in `bin/bootstrap.d/` for system-level changes. |
| `add-app-config` | Add configuration for a new application under `symlinked/`. |
| `add-fish-alias` | Create a fish alias or function. |

Skills use absolute `~/.config/Juliet/...` paths, so they work from any directory.
