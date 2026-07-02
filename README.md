# encore-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-10-blue)](#skills)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20%7C%20Cursor%20%7C%20Codex-green)](#install)

A portable workflow skills library for GitLab teams. Works across Claude Code, Cursor, and Codex. Covers two full loops: one for PMs and designers, one for engineers — from rough idea to confirmed-resolved issue.

---

## Skills

### Setup

| Skill | What it does |
|-------|--------------|
| [`gitlab-config`](skills/gitlab-config/SKILL.md) | Wire up GitLab API access — multiple instances, tokens, project aliases — plus a local instance/project/issue cache so other skills don't refetch what they already know. Run once before anything else. |

### PM / Designer loop

| Skill | What it does |
|-------|--------------|
| [`pm-workflow`](skills/pm-workflow/SKILL.md) | Full PM loop — draft issue, interact with users and stakeholders to validate, refine until eng-ready, finalize. No codebase needed. |
| [`write-issue`](skills/write-issue/SKILL.md) | Turn a rough idea into a structured GitLab issue with clear problem statement and testable acceptance criteria. |

### Engineer loop

| Skill | What it does |
|-------|--------------|
| [`eng-workflow`](skills/eng-workflow/SKILL.md) | Full engineer loop orchestrator — analyze → fix → review → MR → post-merge verify → update memory. |
| [`analyze-issue`](skills/analyze-issue/SKILL.md) | Read an issue, identify the root cause (not just symptoms), surface real risks, produce an implementation approach. |
| [`fix-issue`](skills/fix-issue/SKILL.md) | Implement following the human-thinking loop — understand, plan, code, verify the problem is actually gone. |
| [`review-code`](skills/review-code/SKILL.md) | Pre-MR self-review — problem solved first, then security, correctness, and code quality. |
| [`create-mr`](skills/create-mr/SKILL.md) | Create a GitLab MR with a high-level summary that tells the reviewer what matters in 30 seconds, and calls out related work already mentioned in the issue thread. |
| [`triage-issue`](skills/triage-issue/SKILL.md) | Check an issue's comments for ones that need your reply, ground the reply in the actual codebase, post when it's clearly warranted. |
| [`project-memory`](skills/project-memory/SKILL.md) | Record root cause, fix approach, and gotchas into `docs/CONTEXT.md` — so the next fix starts from knowledge, not a blank scan. |

---

## Install

### Claude Code — CLI, Desktop app, and IDE extensions

Skills install globally into `~/.claude/skills/` and are picked up by all Claude Code surfaces automatically.

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --claude

# Upgrade
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --upgrade
```

Restart Claude Code (CLI, Desktop, or IDE extension) after install.

### Cursor

Installs per-project into `.cursor/rules/`. Run inside your project directory.

```bash
git clone https://github.com/encoreshao/encore-skills.git ~/.encore-skills
cd /your/project
bash ~/.encore-skills/scripts/setup.sh --cursor
```

Restart Cursor after install.

### Codex — CLI and Desktop

Generates an `AGENTS.md` file in the current project directory. Run inside your project.

```bash
git clone https://github.com/encoreshao/encore-skills.git ~/.encore-skills
cd /your/project
bash ~/.encore-skills/scripts/setup.sh --codex
```

### All tools at once

```bash
bash ~/.encore-skills/scripts/setup.sh --all
```

---

## Configure GitLab

After installing, set up GitLab access. Every skill that talks to GitLab reads from the same config file — do this once.

### From Claude Code (recommended)

Restart Claude Code after install, then type:

```
/gitlab-config
```

Follow the prompts to add your GitLab instance URL and Personal Access Token.

### From Cursor or Codex

In your AI session, prompt:

```
run the gitlab-config skill to set up my GitLab access
```

### Manual setup

```bash
cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json
chmod 600 ~/.gitlab/config.json
```

Edit `~/.gitlab/config.json` with your instance details:

```json
{
  "default": "work",
  "instances": {
    "work": {
      "url": "https://gitlab.yourcompany.com",
      "token": "glpat-xxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```

Get a token: **GitLab → Settings → Access Tokens** — create with `api` scope.

Verify it works:

```bash
python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-instances
```

> **Multiple GitLab servers?** Add more entries under `instances` — see [`skills/gitlab-config/SKILL.md`](skills/gitlab-config/SKILL.md) for multi-instance config.

---

## Local memory

`gitlab-config` also maintains a local cache under `~/.gitlab/cache/`, layered by scope, so `analyze-issue`, `triage-issue`, and `create-mr` don't re-fetch or re-derive what they already know:

```
~/.gitlab/cache/<instance>/users.json                              # instance-level: every user seen (team directory)
~/.gitlab/cache/<instance>/projects/<project>/project.json         # project-level: metadata + members
~/.gitlab/cache/<instance>/projects/<project>/issues/<iid>.json    # issue-level: issue + notes + your own analysis
```

`sync-issue` and `sync-project` still call the GitLab API every time — new comments are never missed — but merge the result onto whatever's cached instead of discarding it, so nothing already known gets overwritten. See [`skills/gitlab-config/SKILL.md`](skills/gitlab-config/SKILL.md#local-memory-instance--project--issue-cache) for the full command reference.

---

## Uninstall

```bash
# Remove from Claude Code / Claude Desktop
./scripts/uninstall.sh --claude

# Remove from Cursor (current project)
./scripts/uninstall.sh --cursor

# Remove from Codex (current project)
./scripts/uninstall.sh --codex

# Remove from all tools
./scripts/uninstall.sh --all
```

Or via the setup entry point:

```bash
./scripts/setup.sh --uninstall --claude
./scripts/setup.sh --uninstall --all
```

---

## Workflows

### PM / Designer — no codebase required

```
write-issue → share → gather-feedback → refine → validate → finalize
      ↑                      |
      └───────── iterate ────┘
```

Done when an engineer can pick up the issue and start without asking a single clarifying question.

### Engineer — full loop with memory

```
analyze-issue → fix-issue → review-code → create-mr → [merge] → project-memory
      ↑ reads                                                           |
 docs/CONTEXT.md                                                        ↓
      └──────────────────────────────────── docs/CONTEXT.md grows smarter each cycle
```

Each cycle follows the same thinking: **Understand → Plan → Implement → Validate → Ship or loop.**

The `eng-workflow` skill runs the full engineer loop as a single guided session.

---

## Requirements

| Requirement | Used by |
|-------------|---------|
| git | All engineer skills |
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
