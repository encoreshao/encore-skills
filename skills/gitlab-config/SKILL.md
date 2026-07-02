---
name: gitlab-config
description: Wire up GitLab API access — multiple instances, project aliases, tokens. Run this once before any other GitLab skill.
license: MIT
compatibility: Python 3.8+ required. pip required for dependency install.
metadata:
  author: encoreshao
  version: "1.2"
  tags: gitlab config setup multi-instance token api cache memory
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

## Local memory (instance / project / issue cache)

Every other skill should prefer these over the plain `get-issue`/`get-project` calls above — they hit the API the same way, but merge the result into `~/.gitlab/cache/<instance>/...` instead of throwing it away. Nothing already cached is ever dropped; new data layers on top.

```bash
python $GITLAB sync-project <project>              # project metadata + team roster -> project.json, feeds users.json
python $GITLAB sync-issue <project> <issue_iid>     # issue + notes, merged by note id -> issues/<iid>.json
python $GITLAB cached-issue <project> <issue_iid>   # read the cache with no network call

CACHE="$HOME/.claude/skills/gitlab-config/scripts/gitlab_cache.py"
python $CACHE get-users <instance>                            # instance-level team/user directory
python $CACHE get-project <instance> <project_id>              # project-level metadata
python $CACHE annotate <instance> <project_id> <issue_iid> <key> <value>   # record your own analysis/notes against an issue
```

Why this exists: analysis, triage, and reply-drafting all re-read the same issue and the same team roster repeatedly. `sync-issue` still calls the API every time (so new comments are never missed) but merges onto the cached copy — so your own annotations (root cause, which comments you've already handled) survive, and you're not re-deriving what you already knew. `sync-project` builds the team directory once so usernames resolve to real names without a separate lookup per comment.

Cache layout:
```
~/.gitlab/cache/<instance>/users.json                              # instance-level: every user seen, keyed by id
~/.gitlab/cache/<instance>/projects/<project>/project.json         # project-level: metadata + members
~/.gitlab/cache/<instance>/projects/<project>/issues/<iid>.json    # issue-level: issue + notes + your own `_notes` annotations
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `GitLab configuration not found` | Create `~/.gitlab/config.json` or set env vars |
| `Instance 'X' not found` | Check spelling; run `list-instances` |
| `HTTP 401` | Token expired or wrong scope — regenerate with `api` scope |
| `HTTP 403` | Token lacks permission for this action |
| `HTTP 404` | Wrong project ID or issue number |
