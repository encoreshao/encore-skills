#!/usr/bin/env python3
"""
Automated issue resolution workflow script.

This script coordinates the full workflow of:
1. Fetching issue details
2. Creating a feature branch
3. (Claude implements the fix)
4. Pushing the branch
5. Creating a merge request
6. Posting a comment on the original issue
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional

# Import config functions from gitlab_api
sys.path.insert(0, str(Path(__file__).parent))
from gitlab_api import load_gitlab_config, resolve_project_alias


def run_command(cmd: list, capture=True) -> str:
    """Run shell command and return output."""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True)
            return ""
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e.stderr if capture else e}", file=sys.stderr)
        sys.exit(1)


def create_branch_from_issue(issue_iid: int, issue_title: str) -> str:
    """Create a git branch based on issue number."""
    # Sanitize title for branch name
    sanitized_title = issue_title.lower()
    sanitized_title = ''.join(c if c.isalnum() or c in (' ', '-') else '' for c in sanitized_title)
    sanitized_title = '-'.join(sanitized_title.split())[:50]

    branch_name = f"issue-{issue_iid}-{sanitized_title}"

    # Create and checkout branch
    run_command(['git', 'checkout', '-b', branch_name])
    return branch_name


def push_branch(branch_name: str) -> None:
    """Push branch to remote."""
    run_command(['git', 'push', '-u', 'origin', branch_name], capture=False)


def create_merge_request(project_id: str, source_branch: str, target_branch: str,
                        title: str, description: str, issue_iid: int,
                        instance_name: Optional[str] = None) -> Dict:
    """Create a merge request via GitLab API."""
    import requests

    base_url, token = load_gitlab_config(instance_name)

    api_url = f"{base_url}/api/v4"
    headers = {
        'PRIVATE-TOKEN': token,
        'Content-Type': 'application/json'
    }

    # Add issue reference to description
    full_description = f"{description}\n\nCloses #{issue_iid}"

    data = {
        'source_branch': source_branch,
        'target_branch': target_branch,
        'title': title,
        'description': full_description,
        'remove_source_branch': True
    }

    response = requests.post(
        f"{api_url}/projects/{requests.utils.quote(project_id, safe='')}/merge_requests",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()


def main():
    """CLI interface for automated issue resolution."""
    if len(sys.argv) < 2:
        print("Usage: auto_resolve_issue.py [--instance=<name>] <command> [args...]", file=sys.stderr)
        print("\nCommands:", file=sys.stderr)
        print("  create-branch <issue_iid> <issue_title>", file=sys.stderr)
        print("  push-branch <branch_name>", file=sys.stderr)
        print("  create-mr <project> <source_branch> <target_branch> <title> <description> <issue_iid>", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("  --instance=<name>  Specify which GitLab instance to use (from config file)", file=sys.stderr)
        print("\nNote: <project> can be a project alias (from config) or full project ID", file=sys.stderr)
        sys.exit(1)

    # Parse instance flag
    instance_name = None
    args = sys.argv[1:]
    if args[0].startswith('--instance='):
        instance_name = args[0].split('=', 1)[1]
        args = args[1:]
        if not args:
            print("Error: No command specified", file=sys.stderr)
            sys.exit(1)

    command = args[0]

    try:
        if command == 'create-branch':
            issue_iid = int(args[1])
            issue_title = args[2]
            branch_name = create_branch_from_issue(issue_iid, issue_title)
            print(json.dumps({'branch_name': branch_name}))

        elif command == 'push-branch':
            branch_name = args[1]
            push_branch(branch_name)
            print(json.dumps({'status': 'pushed', 'branch': branch_name}))

        elif command == 'create-mr':
            project_arg = args[1]
            # Resolve project alias and instance
            project_id, resolved_instance = resolve_project_alias(project_arg, instance_name)
            # Use resolved instance if not explicitly provided
            if instance_name is None and resolved_instance is not None:
                instance_name = resolved_instance

            source_branch = args[2]
            target_branch = args[3]
            title = args[4]
            description = args[5]
            issue_iid = int(args[6])
            mr = create_merge_request(project_id, source_branch, target_branch, title, description, issue_iid, instance_name)
            print(json.dumps(mr, indent=2))

        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)

    except IndexError:
        print(f"Invalid arguments for command: {command}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
