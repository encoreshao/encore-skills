# encore-skills

This repo contains workflow skills for Claude Code, Cursor, and Codex. It dogfoods itself: this repo is also a project that Claude, Cursor, and Codex can work on, using its own skills.

## Structure

- `skills/` — canonical skill sources (one directory per skill, each with SKILL.md). Single source of truth — never edit generated adapters below directly.
- `scripts/` — setup scripts for each tool (`setup-claude.sh`, `setup-cursor.sh`, `setup-codex.sh`, `setup.sh` entry point, `uninstall.sh`, `upgrade.sh`)
- `docs/` — specs and plans
- `.cursor/rules/*.mdc` — generated, committed adapter for Cursor (self-hosted mode: each file just `@`-references `skills/<name>/SKILL.md`, no content duplicated)
- `AGENTS.md` — generated, committed adapter for Codex (self-hosted mode: table of skill names/paths, no content duplicated)

## Adding a skill

1. Create `skills/<name>/SKILL.md` with frontmatter: `name`, `description`
2. Run `./scripts/setup.sh --claude` to install into Claude Code
3. Run `./scripts/setup-cursor.sh` and `./scripts/setup-codex.sh` to regenerate `.cursor/rules/` and `AGENTS.md` — commit the results so Cursor/Codex users of this repo stay in sync

## Skills follow the human-thinking workflow

Understand → Plan → Implement → Validate → Ship or Loop
