---
name: gitlab-config
description: Wire up GitLab API access — multiple instances, project aliases, tokens. Run this once before any other GitLab skill.
license: MIT
compatibility: Python 3.8+ required. pip required for dependency install.
metadata:
  author: encoreshao
  version: "1.1"
  tags: gitlab config setup multi-instance token api
---

# GitLab Config

Do this once. Every other skill reads from the same config — get it right here and everything else just works.

## Install

```bash
pip install requests
# or
pip install -r ~/.claude/skills/gitlab-config/requirements.txt
```

## Configure

```bash
cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json
chmod 600 ~/.gitlab/config.json
```

Edit `~/.gitlab/config.json`:

```json
{
  "default": "work",
  "instances": {
    "work": {
      "url": "https://gitlab.company.com",
      "token": "glpat-xxxxxxxxxxxxxxxxxxxx"
    },
    "personal": {
      "url": "https://gitlab.com",
      "token": "glpat-yyyyyyyyyyyyyyyyyyyy"
    }
  },
  "projects": {
    "webapp": {
      "project_id": "acme/webapp",
      "instance": "work"
    }
  }
}
```

Get a token: **GitLab → Settings → Access Tokens** — create with `api` scope. It won't be shown again.

**Env var fallback** (single instance only):
```bash
export GITLAB_URL="https://gitlab.com"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
```

## Verify

```bash
python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-instances
python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-projects
```

## API reference

All other skills use these scripts:

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"

# Issues
python $GITLAB get-issue <project> <issue_iid>
python $GITLAB list-issues <project> [state] [labels...]
python $GITLAB post-issue-comment <project> <issue_iid> "<comment>"

# Merge Requests
python $GITLAB get-mr <project> <mr_iid>
python $GITLAB list-mrs <project> [state]
python $GITLAB get-diff <project> <mr_iid>
python $GITLAB post-mr-comment <project> <mr_iid> "<comment>"

# Stats
python $GITLAB aggregate-issues <project> [days]

# Override instance for a single call
python $GITLAB --instance=personal get-issue blog 42
```

`<project>` accepts: alias (`webapp`), numeric ID (`123`), or full path (`acme/webapp`).

Config lookup order: `./gitlab_config.json` → `~/.gitlab/config.json` → skill directory.

Instance resolution: `--instance` flag → project's configured instance → `default`.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `GitLab configuration not found` | Create `~/.gitlab/config.json` or set env vars |
| `Instance 'X' not found` | Check spelling; run `list-instances` |
| `HTTP 401` | Token expired or wrong scope — regenerate with `api` scope |
| `HTTP 403` | Token lacks permission for this action |
| `HTTP 404` | Wrong project ID or issue number |
