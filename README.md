# encore-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-9-blue)](#skills)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20%7C%20Cursor%20%7C%20Codex-green)](#install)

A portable workflow skills library for GitLab teams. Works across Claude Code, Cursor, and Codex. Covers two full loops: one for PMs and designers, one for developers — from rough idea to confirmed-resolved issue.

---

## Skills

### Setup

| Skill | What it does |
|-------|--------------|
| [`gitlab-config`](skills/gitlab-config/SKILL.md) | Wire up GitLab API access — multiple instances, tokens, project aliases. Run once before anything else. |

### PM / Designer loop

| Skill | What it does |
|-------|--------------|
| [`pm-workflow`](skills/pm-workflow/SKILL.md) | Full PM loop — draft issue, interact with users and stakeholders to validate, refine until dev-ready, finalize. No codebase needed. |
| [`write-issue`](skills/write-issue/SKILL.md) | Turn a rough idea into a structured GitLab issue with clear problem statement and testable acceptance criteria. |

### Developer loop

| Skill | What it does |
|-------|--------------|
| [`workflow`](skills/workflow/SKILL.md) | Full dev loop orchestrator — analyze → fix → review → MR → post-merge verify → update memory. |
| [`analyze-issue`](skills/analyze-issue/SKILL.md) | Read an issue, identify the root cause (not just symptoms), surface real risks, produce an implementation approach. |
| [`fix-issue`](skills/fix-issue/SKILL.md) | Implement following the human-thinking loop — understand, plan, code, verify the problem is actually gone. |
| [`review-code`](skills/review-code/SKILL.md) | Pre-MR self-review — problem solved first, then security, correctness, and code quality. |
| [`create-mr`](skills/create-mr/SKILL.md) | Create a GitLab MR with a high-level summary that tells the reviewer what matters in 30 seconds. |
| [`project-memory`](skills/project-memory/SKILL.md) | Record root cause, fix approach, and gotchas into `docs/CONTEXT.md` — so the next fix starts from knowledge, not a blank scan. |

---

## Install

```bash
# Install (Claude Code)
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --claude

# Upgrade
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --upgrade
```

**Other tools — from a local clone:**

```bash
git clone https://github.com/encoreshao/encore-skills.git
cd encore-skills

./scripts/setup.sh --cursor    # Cursor (run inside your project)
./scripts/setup.sh --codex     # Codex (run inside your project)
./scripts/setup.sh --all       # All three at once
```

---

## Prerequisites

Before using any GitLab skill, run `gitlab-config` setup once:

```bash
cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json
chmod 600 ~/.gitlab/config.json
# Edit with your GitLab instances and tokens
```

See [`skills/gitlab-config/SKILL.md`](skills/gitlab-config/SKILL.md) for full setup and multi-instance configuration.

---

## Workflows

### PM / Designer — no codebase required

```
write-issue → share → gather-feedback → refine → validate → finalize
      ↑                      |
      └───────── iterate ────┘
```

Done when a developer can pick up the issue and start without asking a single clarifying question.

### Developer — full loop with memory

```
analyze-issue → fix-issue → review-code → create-mr → [merge] → project-memory
      ↑ reads                                                           |
 docs/CONTEXT.md                                                        ↓
      └──────────────────────────────────── docs/CONTEXT.md grows smarter each cycle
```

Each cycle follows the same thinking: **Understand → Plan → Implement → Validate → Ship or loop.**

The `workflow` skill runs the full developer loop as a single guided session.

---

## Requirements

| Requirement | Used by |
|-------------|---------|
| git | All dev skills |
| Python 3.8+ and pip | `gitlab-config` |
| GitLab Personal Access Token (`api` scope) | All GitLab skills |
| glab CLI *(optional)* | `create-mr`, `review-code`, `pm-workflow` |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or edit skills, frontmatter requirements, and the validation workflow.

```bash
# Validate all skill frontmatter locally
.github/scripts/validate-skills.sh
```

---

## License

[MIT](LICENSE) — free to use, fork, and adapt.
