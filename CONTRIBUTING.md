# Contributing

## Adding a new skill

1. Create `skills/<name>/SKILL.md` — name must be lowercase, hyphenated, max 64 chars
2. Add required frontmatter:

```yaml
---
name: <name>          # must match folder name exactly
description: <text>   # activation-trigger language: "Use when..." or "Turns X into Y"
license: MIT
compatibility: <what tools/CLIs are required or optional>
metadata:
  author: <your-name>
  version: "1.0"
  tags: <space-separated list>
---
```

3. Add `examples/<scenario>.md` — at least one concrete input → output example
4. Run `./scripts/setup.sh --claude` to test locally
5. Run `./scripts/setup-cursor.sh` and `./scripts/setup-codex.sh` to regenerate `.cursor/rules/*.mdc` and `AGENTS.md`, and commit the results — this repo dogfoods its own skills for Cursor and Codex, so a new skill isn't usable there until these adapters are regenerated
6. Update `CHANGELOG.md` under `[Unreleased]`
7. Open an MR — the PR template will guide you

## Editing an existing skill

- Bump `metadata.version` in the skill's frontmatter (patch for fixes, minor for behavior changes)
- Add a line to `CHANGELOG.md` under `[Unreleased]`

## Skill writing guidelines

- **Description field is the activation trigger.** Write it so the AI knows exactly when to invoke this skill without reading the full content.
- **Concise beats thorough.** Every token competes with context. If a section can be a single line, make it one.
- **No vague instructions.** "Handle errors appropriately" is useless. Say what to do.
- **Examples are not optional.** They show what good output looks like — agents and humans both need them.
- **Root cause, not symptoms.** Skills that address root causes are reusable. Skills that address symptoms are workarounds.

## Frontmatter validation

CI runs a YAML + field check on every PR. To run locally:

```bash
.github/scripts/validate-skills.sh
```
