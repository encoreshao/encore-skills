# encore-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-8-blue)](#skills)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20%7C%20Cursor%20%7C%20Codex-green)](#install)

A portable workflow skills library for GitLab-focused development teams. Installs into Claude Code, Cursor, and Codex with a single command. Covers the full loop from writing an issue to merging a reviewed MR.

---

## Skills

| Skill | Who | What it does |
|-------|-----|--------------|
| [`gitlab-config`](skills/gitlab-config/SKILL.md) | Everyone | Wire up GitLab API access — multiple instances, tokens, project aliases |
| [`write-issue`](skills/write-issue/SKILL.md) | PM / Dev | Turn a rough idea into a structured GitLab issue with testable acceptance criteria |
| [`analyze-issue`](skills/analyze-issue/SKILL.md) | Dev / PM | Identify root cause, surface real risks, produce an implementation approach |
| [`fix-issue`](skills/fix-issue/SKILL.md) | Dev | Implement following the human-thinking loop — understand, plan, code, verify |
| [`review-code`](skills/review-code/SKILL.md) | Dev / Lead | Pre-MR self-review — problem solved first, then security, correctness, quality |
| [`create-mr`](skills/create-mr/SKILL.md) | Dev | Create a GitLab MR with a high-level summary that tells the reviewer what matters |
| [`workflow`](skills/workflow/SKILL.md) | All | Full loop: write-issue → analyze → fix → review → MR → post-merge verify |
| [`project-memory`](skills/project-memory/SKILL.md) | All | Record what was learned into `docs/CONTEXT.md` so the next fix starts from knowledge, not a blank scan. Supports per-domain files for large projects. |

---

## Install

**One-liner (Claude Code):**

```bash
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --claude
```

**From a local clone:**

```bash
git clone https://github.com/encoreshao/encore-skills.git
cd encore-skills

./scripts/setup.sh --claude    # Claude Code (global)
./scripts/setup.sh --cursor    # Cursor (run inside your project)
./scripts/setup.sh --codex     # Codex (run inside your project)
./scripts/setup.sh --all       # All three at once
```

**Upgrade later:**

```bash
./scripts/setup.sh --upgrade
```

---

## Prerequisites

Before using any GitLab skills, run the `gitlab-config` setup once:

```bash
cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json
chmod 600 ~/.gitlab/config.json
# Edit ~/.gitlab/config.json with your GitLab instances and tokens
```

See [`skills/gitlab-config/SKILL.md`](skills/gitlab-config/SKILL.md) for full setup instructions and multi-instance configuration.

---

## Workflow

```
write-issue → analyze-issue → fix-issue → review-code → create-mr → [merge] → project-memory
      ↑            ↑ reads                                                            |
      │      docs/CONTEXT.md                                                          ↓
      └──────── feedback / new issue ──────────────────── docs/CONTEXT.md grows smarter
```

Each phase follows human thinking:

1. **Understand** — what is the actual problem, not just the reported symptom?
2. **Plan** — minimal change, explicit scope boundary, known risks
3. **Implement** — follow existing patterns, one commit per concern
4. **Validate** — does it solve the root cause? tests pass? no regressions?
5. **Ship or loop** — merge, or return to the step that needs fixing

The `workflow` skill runs the full loop as a single guided session.

---

## Requirements

- **git** — required by all skills
- **Python 3.8+** and **pip** — required by `gitlab-config`
- **glab CLI** — optional but useful for `create-mr` and `review-code`
- **GitLab project access** — a Personal Access Token with `api` scope

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
