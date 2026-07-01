# Workflow Skills Library — Design Spec
Date: 2026-07-01

## Goal

A portable skills library for a multi-role workflow (developer, PM, project manager, designer) that installs into Claude Code, Cursor, and Codex with a single command. Built around GitLab (issues, MRs, pipelines).

## Architecture: Single Source, Multi-Tool Adapters

One canonical `SKILL.md` per skill. A setup script transforms and installs into each tool's native format.

```
encore-skills/
  skills/
    analyze-issue/SKILL.md
    fix-issue/SKILL.md
    create-mr/SKILL.md
    write-issue/SKILL.md
    review-code/SKILL.md
    workflow/SKILL.md
  scripts/
    setup.sh            # install all tools
    setup-claude.sh     # symlink to ~/.claude/skills/
    setup-cursor.sh     # generate .cursor/rules/*.mdc in cwd
    setup-codex.sh      # generate AGENTS.md in cwd
  AGENTS.md             # pre-generated for Codex (this repo)
  CLAUDE.md             # for Claude (this repo)
  README.md
```

## Skills

| Skill | Role | Trigger phrase | Purpose |
|-------|------|---------------|---------|
| `analyze-issue` | Dev / PM | `/analyze-issue` | Read GitLab issue → requirements, risks, acceptance criteria, implementation plan |
| `fix-issue` | Dev | `/fix-issue` | Implement → identify risks → iterate to solution |
| `create-mr` | Dev | `/create-mr` | Create GitLab MR with description, linked issue, checklist |
| `write-issue` | PM | `/write-issue` | Write well-structured GitLab issue from rough idea |
| `review-code` | Dev / Lead | `/review-code` | Pre-MR review: security, logic, best practices |
| `workflow` | All | `/workflow` | Full loop orchestrator: analyze → fix → review → create-mr |

## Workflow Loop

```
write-issue → analyze-issue → fix-issue → review-code → create-mr
      ↑                                                        |
      └────────────── feedback / new issue ────────────────────┘
```

Each skill follows human thinking:
1. **Understand** — what is the problem exactly?
2. **Plan** — how to approach it, what are the risks?
3. **Implement** — do the work
4. **Validate** — does it meet requirements? any new risks?
5. **Ship or loop** — merge or go back

## Tool Adapter Behavior

### Claude Code
- `setup-claude.sh` symlinks `skills/<name>/` → `~/.claude/skills/<name>/`
- Skills available globally via `/skill-name`

### Cursor
- `setup-cursor.sh` reads each `SKILL.md`, generates `.cursor/rules/<name>.mdc`
- Frontmatter: `description` from SKILL.md frontmatter, `alwaysApply: false`, `globs: []`
- Run inside a project directory

### Codex
- `setup-codex.sh` reads all `SKILL.md` files, generates `AGENTS.md` in the project root
- Format: markdown table + per-skill usage instructions
- Run inside a project directory

## Setup Script Interface

```bash
# Install globally for Claude Code
./scripts/setup.sh --claude

# Install into current project (Cursor + Codex)
./scripts/setup.sh --cursor
./scripts/setup.sh --codex

# Install everything (Claude global + project-level Cursor & Codex)
./scripts/setup.sh --all

# Or via curl (one-liner for sharing)
curl -fsSL https://raw.githubusercontent.com/encore/encore-skills/main/scripts/setup.sh | bash -s -- --claude
```

## GitLab Integration

Skills reference GitLab CLI (`glab`) where available, and fall back to web URLs + copy-paste instructions. No hard dependency on `glab`.

## Constraints

- Skills must work without internet (no mandatory API calls in skill logic)
- Each skill is self-contained — no skill depends on another being installed
- `workflow` skill is the only one that references the others
- Setup scripts require only bash + standard Unix tools (no Node, Python, etc.)
