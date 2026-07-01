# Example: Multi-instance GitLab setup

## Scenario
Developer works across: company GitLab, personal GitLab.com, and a client's self-hosted instance.

## Config (~/.gitlab/config.json)

```json
{
  "default": "work",
  "instances": {
    "work": {
      "url": "https://gitlab.company.com",
      "token": "glpat-worktoken",
      "description": "Company GitLab"
    },
    "personal": {
      "url": "https://gitlab.com",
      "token": "glpat-personaltoken",
      "description": "Personal projects"
    },
    "client": {
      "url": "https://gitlab.client.com",
      "token": "glpat-clienttoken",
      "description": "Client project"
    }
  },
  "projects": {
    "webapp": {
      "project_id": "myorg/webapp",
      "instance": "work",
      "description": "Main web app"
    },
    "skills": {
      "project_id": "encoreshao/encore-skills",
      "instance": "personal",
      "description": "This skills library"
    }
  }
}
```

## Usage

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"

# Work instance (default)
python $GITLAB get-issue webapp 42

# Personal instance (via project alias)
python $GITLAB get-issue skills 7

# Client instance (explicit flag)
python $GITLAB --instance=client get-issue "client/mobile-app" 15

# Verify all instances
python $GITLAB list-instances
python $GITLAB list-projects
```
