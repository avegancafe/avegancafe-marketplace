---
name: init-projects
description: Initialize a _projects/ folder in the current repo — creates the top-level README.md describing the folder's structure and conventions, plus a CLAUDE.md symlink pointing at it so Claude sessions pick up the rules. Use when the user asks to set up, initialize, or bootstrap the _projects/ folder, or when another projects skill needs _projects/ and it doesn't exist yet.
---

# Initialize the _projects/ folder

Set up `_projects/` at the root of the current repository (or wherever the
user asks for it).

## Steps

1. Run the bundled script from the directory that should contain `_projects/`:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/init-projects.sh" [base-dir]
   ```

   `base-dir` defaults to the current directory. The script is idempotent:
   it never overwrites an existing README or symlink.

2. Verify the result:
   - `_projects/README.md` exists and documents the folder conventions
     (project folder naming, todo.md format, the 256-line README limit).
   - `_projects/CLAUDE.md` is a **symlink** to `README.md` (`ls -la _projects/`).

## Conventions the README establishes

- One folder per project, named `YYYY-MM-DD--<project-name>` (kebab-case).
- Each project folder contains `todo.md`, a `README.md` for small notes
  (**must stay under 256 lines**), and any ad-hoc project files.
- `todo.md` uses Markdown checkboxes with `@high`/`@medium`/`@low` priority
  mentions and `[assignee:<id>]` assignee links (ids are readable
  adjective-noun session ids from the `session-ids` plugin).

If the script is unavailable for some reason, create the same structure by
hand following the conventions above — but never replace the CLAUDE.md
symlink with a regular file.
