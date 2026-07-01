# encore-skills

This repo contains workflow skills for Claude Code, Cursor, and Codex.

## Structure

- `skills/` — canonical skill sources (one directory per skill, each with SKILL.md)
- `scripts/` — setup scripts for each tool
- `docs/` — specs and plans

## Adding a skill

1. Create `skills/<name>/SKILL.md` with frontmatter: `name`, `description`
2. Run `./scripts/setup.sh --claude` to install into Claude Code
3. Run `./scripts/setup-cursor.sh` and `./scripts/setup-codex.sh` to regenerate adapter files

## Skills follow the human-thinking workflow

Understand → Plan → Implement → Validate → Ship or Loop
