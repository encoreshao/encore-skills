# encore-skills

A portable workflow skills library for GitLab-focused development. Works with Claude Code, Cursor, and Codex.

## Skills

| Skill | Role | Purpose |
|-------|------|---------|
| `write-issue` | PM | Turn a rough idea into a structured GitLab issue |
| `analyze-issue` | Dev / PM | Read an issue → requirements, risks, implementation plan |
| `fix-issue` | Dev | Implement following the human-thinking loop |
| `review-code` | Dev / Lead | Pre-MR code review |
| `create-mr` | Dev | Create a GitLab Merge Request |
| `workflow` | All | Full loop: analyze → fix → review → create-mr |

## Install

```bash
# Claude Code (global)
./scripts/setup.sh --claude

# Cursor (project-level, run inside your project)
./scripts/setup.sh --cursor

# Codex (project-level, run inside your project)
./scripts/setup.sh --codex

# All at once
./scripts/setup.sh --all
```

## One-liner install (Claude Code)

```bash
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --claude
```

## Workflow loop

```
write-issue → analyze-issue → fix-issue → review-code → create-mr
      ↑                                                        |
      └────────────── feedback / new issue ────────────────────┘
```

Each phase follows human thinking:
1. **Understand** — what is the problem exactly?
2. **Plan** — how to approach it, what are the risks?
3. **Implement** — do the work
4. **Validate** — does it meet requirements? any new risks?
5. **Ship or loop** — merge or go back
