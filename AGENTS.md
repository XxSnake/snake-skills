# Local Collaboration Rules

These rules apply to work in this repository.

## Context Boundaries

- ChatGPT, Codex CLI, Claude, and Gemini have independent memories. Do not assume another AI already knows the current context.
- Keep private background data out of this public repository, including personal master profiles, medication, family details, network proxy details, and personal location.

## Repository Layout

- The skills repository is `D:\repos\snake-skills\`.
- `codex/` contains skills for OpenAI Codex.
- `claude/` contains skills for Claude.
- The current priority Codex skill is `codex/book-to-share-pdf`.
- `codex/book-to-share-pdf` is installed into `~/.codex/skills/book-to-share-pdf` through a symlink, so edits to the repository source affect local Codex behavior immediately.

## Change Workflow

- Prefer maintaining long-term project rules in this root `AGENTS.md`.
- Put private background material only in local gitignored directories.
- After changing any skill, run `scripts/validate_skills.py` to validate `SKILL.md` frontmatter.
- When asked to sync a Codex skill designed in ChatGPT, use this default flow:
  1. Receive the complete `SKILL.md` content.
  2. Overwrite `D:\repos\snake-skills\codex\<skill-name>\SKILL.md`.
  3. Run validation.
  4. Show the git diff for confirmation.
  5. Commit only after confirmation.
