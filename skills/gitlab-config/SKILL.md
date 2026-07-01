---
name: gitlab-config
description: Configure and verify GitLab API access — multiple instances, project aliases, and Personal Access Tokens. Run this first before any other GitLab skill.
license: MIT
compatibility: Python 3.8+ required. pip required for dependency install.
metadata:
  author: encoreshao
  version: "1.0"
  tags: gitlab config setup multi-instance token api
---

# GitLab Config

Sets up GitLab API access for all other skills. Supports multiple GitLab servers (work, personal, client) from a single config file.

## First-time setup

### 1. Install Python dependency

```bash
pip install requests
# or
pip install -r ~/.claude/skills/gitlab-config/requirements.txt
```

### 2. Create your config file

```bash
cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json
chmod 600 ~/.gitlab/config.json
```

Then edit `~/.gitlab/config.json` with your real instances and tokens.

### 3. Get a GitLab Personal Access Token

For each GitLab instance:
1. Go to **Settings → Access Tokens** (or `https://<your-gitlab>/-/user_settings/personal_access_tokens`)
2. Create a token with **`api`** scope
3. Copy and paste it into your config — it won't be shown again

### 4. Verify

```bash
python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-instances
python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-projects
```

## Config file

Location (checked in order):
1. `./gitlab_config.json` (current project directory)
2. `~/.gitlab/config.json` ← recommended for personal config
3. `~/.claude/skills/gitlab-config/gitlab_config.json`

```json
{
  "default": "work",
  "instances": {
    "work": {
      "url": "https://gitlab.company.com",
      "token": "glpat-xxxxxxxxxxxxxxxxxxxx",
      "description": "Company GitLab"
    },
    "personal": {
      "url": "https://gitlab.com",
      "token": "glpat-yyyyyyyyyyyyyyyyyyyy",
      "description": "Personal projects"
    }
  },
  "projects": {
    "webapp": {
      "project_id": "acme/webapp",
      "instance": "work",
      "description": "Main web app"
    }
  }
}
```

**Env variable fallback** (single instance only):
```bash
export GITLAB_URL="https://gitlab.com"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
```

## API script reference

All other skills use these scripts. Call them as:

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"

# List instances and projects
python $GITLAB list-instances
python $GITLAB list-projects

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

# Use a specific instance (overrides default and project config)
python $GITLAB --instance=personal get-issue blog 42
```

`<project>` accepts: project alias (`webapp`), numeric ID (`123`), or full path (`acme/webapp`).

## Instance resolution priority

1. `--instance=<name>` flag (explicit)
2. Instance configured on the project alias
3. `default` instance in config

## Troubleshooting

| Error | Fix |
|-------|-----|
| `GitLab configuration not found` | Create `~/.gitlab/config.json` or set env vars |
| `Instance 'X' not found` | Check instance name spelling; run `list-instances` |
| `HTTP 401` | Token expired or wrong scope — regenerate with `api` scope |
| `HTTP 403` | Token lacks permission for this action |
| `HTTP 404` | Wrong project ID or issue number |
