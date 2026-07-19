# encore-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-10-blue)](#skills)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20%7C%20Cursor%20%7C%20Codex-green)](#install)

A portable workflow skills library for GitLab teams. Works across Claude Code, Cursor, and Codex. Covers two full loops: one for PMs and designers, one for engineers — from rough idea to confirmed-resolved issue.

---

## Who it's for

- **Engineers** on a GitLab-based team who want an AI agent to carry an issue from analysis through a mergeable MR, without skipping root-cause analysis or self-review.
- **PMs and designers** who want to turn a rough idea into a dev-ready GitLab issue — no codebase access required.
- **Anyone using more than one AI coding tool** (e.g. Claude Code at the terminal, Cursor in the IDE, Codex in CI) who wants the same workflow behavior in all of them instead of maintaining separate prompts per tool.

If your team isn't on GitLab, the loop structure (`analyze → fix → review → ship`) still applies, but the GitLab-specific skills (`gitlab-config`, `create-mr`, `triage-issue`, `summarize-issue`) won't have anywhere to talk to.

---

## Table of Contents

- [Who it's for](#who-its-for)
- [Skills](#skills)
- [Install](#install)
- [Configure GitLab](#configure-gitlab)
- [Local memory](#local-memory)
- [Uninstall](#uninstall)
- [Workflows](#workflows)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

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
| [`eng-workflow`](skills/eng-workflow/SKILL.md) | Full engineer loop orchestrator — analyze → fix → review → MR → post-merge verify. |
| [`analyze-issue`](skills/analyze-issue/SKILL.md) | Read an issue, identify the root cause (not just symptoms), surface real risks, produce an implementation approach. |
| [`fix-issue`](skills/fix-issue/SKILL.md) | Implement following the human-thinking loop — understand, plan, code, verify the problem is actually gone. |
| [`review-code`](skills/review-code/SKILL.md) | Pre-MR self-review — problem solved first, then security, correctness, and code quality. |
| [`create-mr`](skills/create-mr/SKILL.md) | Create a GitLab MR with a high-level summary that tells the reviewer what matters in 30 seconds, and calls out related work already mentioned in the issue thread. |
| [`summarize-issue`](skills/summarize-issue/SKILL.md) | Once an issue is fixed and its MR exists, post a high-level markdown recap as an issue comment — fuller than `create-mr`'s one-line note. |
| [`triage-issue`](skills/triage-issue/SKILL.md) | Reply to an issue's comments — check which ones need a reply, ground the reply in the actual codebase, draft it in your voice — always shown for approval before it's posted. |

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

Installs per-project into `.cursor/rules/`. Run inside your project directory — the same one-liner as Claude Code, just with a different flag.

```bash
cd /your/project
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --cursor
```

Restart Cursor after install.

### Codex — CLI and Desktop

Generates an `AGENTS.md` file in the current project directory. Run inside your project.

```bash
cd /your/project
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --codex
```

### All tools at once

```bash
curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --all
```

Every one-liner above clones (or updates, if already present) a checkout to `~/.encore-skills` automatically — no manual `git clone` step needed for any tool. Re-run the same one-liner any time to upgrade.

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

Works regardless of which tool(s) you installed — `~/.encore-skills` is created by every install path above.

```bash
cp ~/.encore-skills/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json
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
python ~/.encore-skills/skills/gitlab-config/scripts/gitlab_api.py list-instances
```

> **Multiple GitLab servers?** Add more entries under `instances` — see [`skills/gitlab-config/SKILL.md`](skills/gitlab-config/SKILL.md) for multi-instance config.

---

## Local memory

`gitlab-config` also maintains a local cache under `~/.gitlab/cache/`, layered by scope, so `analyze-issue`, `triage-issue`, `create-mr`, and `summarize-issue` don't re-fetch or re-derive what they already know:

```
~/.gitlab/cache/<instance>/users.json                              # instance-level: every user seen (team directory)
~/.gitlab/cache/<instance>/groups/<group>/group.json                # group-level: metadata + members, shared by its projects
~/.gitlab/cache/<instance>/projects/<project>/project.json         # project-level: metadata, members, and your own project memory
~/.gitlab/cache/<instance>/projects/<project>/issues/<iid>.json    # issue-level: issue + notes + your own analysis
```

A GitLab group can hold several projects (e.g. group `acme/rocket` holds `rocket-web` and `rocket-mobile`) — `sync-project` detects the parent group and syncs it too, so the team roster is fetched once and shared across every project under it.

`sync-issue`, `sync-project`, and `sync-group` still call the GitLab API every time — new comments are never missed — but merge the result onto whatever's cached instead of discarding it, so nothing already known gets overwritten. See [`skills/gitlab-config/SKILL.md`](skills/gitlab-config/SKILL.md#local-memory-instance--group--project--issue-cache) for the full command reference.

---

## Uninstall

Every install path above sets up `~/.encore-skills` — run the uninstaller from there. For Cursor/Codex, run it from inside the project you installed into (per-project `.cursor/rules/` and `AGENTS.md` are removed relative to your current directory).

```bash
# Remove from Claude Code / Claude Desktop
~/.encore-skills/scripts/uninstall.sh --claude

# Remove from Cursor (run inside the project)
~/.encore-skills/scripts/uninstall.sh --cursor

# Remove from Codex (run inside the project)
~/.encore-skills/scripts/uninstall.sh --codex

# Remove from all tools
~/.encore-skills/scripts/uninstall.sh --all
```

Or via the setup entry point:

```bash
~/.encore-skills/scripts/setup.sh --uninstall --claude
~/.encore-skills/scripts/setup.sh --uninstall --all
```

(If you're working from a local clone of this repo instead, use `./scripts/...` relative to the repo root.)

---

## Workflows

### PM / Designer — no codebase required

```
write-issue → share → gather-feedback → refine → validate → finalize
      ↑                      |
      └───────── iterate ────┘
```

Done when an engineer can pick up the issue and start without asking a single clarifying question.

### Engineer — full loop

```
analyze-issue → fix-issue → review-code → create-mr → [merge]
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

This repo dogfoods itself — `CLAUDE.md`, `AGENTS.md`, and `.cursor/rules/*.mdc` at the repo root let Claude Code, Codex, and Cursor use these same skills while you work on this repo. `skills/` stays the single source of truth; after adding or editing a skill, regenerate the adapters:

```bash
./scripts/setup-cursor.sh   # refreshes .cursor/rules/*.mdc
./scripts/setup-codex.sh    # refreshes AGENTS.md
```

Commit the regenerated files alongside your skill change.

---

## License

[MIT](LICENSE) — free to use, fork, and adapt.
