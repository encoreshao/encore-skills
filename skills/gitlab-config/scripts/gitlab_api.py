#!/usr/bin/env python3
"""
GitLab API interaction script for fetching issues, merge requests, and posting comments.

Configuration:
- Config file: ./gitlab_config.json or ~/.gitlab/config.json
- Or environment variables: GITLAB_URL and GITLAB_TOKEN
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


def load_gitlab_config(instance_name: Optional[str] = None) -> tuple[str, str]:
    """
    Load GitLab configuration from config file or environment variables.

    Config file locations (in order):
    1. ./gitlab_config.json
    2. ~/.gitlab/config.json
    3. <script_dir>/gitlab_config.json

    Returns:
        tuple: (base_url, token)
    """
    config_paths = [
        Path.cwd() / 'gitlab_config.json',
        Path.home() / '.gitlab' / 'config.json',
        Path(__file__).parent.parent / 'gitlab_config.json'
    ]

    # Try to load from config file
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)

                # If no instance specified, use default
                if instance_name is None:
                    instance_name = config.get('default')
                    if not instance_name:
                        print("Warning: No default instance specified in config", file=sys.stderr)
                        continue

                # Get instance config
                instance = config.get('instances', {}).get(instance_name)
                if not instance:
                    print(f"Error: Instance '{instance_name}' not found in config", file=sys.stderr)
                    print(f"Available instances: {', '.join(config.get('instances', {}).keys())}", file=sys.stderr)
                    sys.exit(1)

                url = instance.get('url', '').rstrip('/')
                token = instance.get('token', '')

                if url and token:
                    return url, token

            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in {config_path}: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Warning: Error reading {config_path}: {e}", file=sys.stderr)
                continue

    # Fall back to environment variables
    url = os.environ.get('GITLAB_URL', '').rstrip('/')
    token = os.environ.get('GITLAB_TOKEN', '')

    if not url or not token:
        raise ValueError(
            "GitLab configuration not found.\n\n"
            "Option 1 - Config file:\n"
            "  Create gitlab_config.json with your GitLab instances\n"
            "  (see gitlab_config.json.template for example)\n\n"
            "Option 2 - Environment variables:\n"
            "  export GITLAB_URL='https://gitlab.com'\n"
            "  export GITLAB_TOKEN='glpat-xxxxxxxxxxxx'"
        )

    return url, token


def get_config_file() -> Optional[Path]:
    """Get the config file path if it exists."""
    config_paths = [
        Path.cwd() / 'gitlab_config.json',
        Path.home() / '.gitlab' / 'config.json',
        Path(__file__).parent.parent / 'gitlab_config.json'
    ]

    for config_path in config_paths:
        if config_path.exists():
            return config_path
    return None


def load_config() -> Optional[Dict]:
    """Load the full config file."""
    config_path = get_config_file()
    if not config_path:
        return None

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        return None


def resolve_project_alias(project_alias: str, instance_name: Optional[str] = None) -> tuple[str, Optional[str]]:
    """
    Resolve a project alias to its full project ID and determine instance.

    Args:
        project_alias: Project alias or full project ID
        instance_name: Optional instance name (overrides project config)

    Returns:
        tuple: (project_id, instance_name)
    """
    config = load_config()

    # If no config or no projects section, return as-is
    if not config or 'projects' not in config:
        return project_alias, instance_name

    projects = config.get('projects', {})

    # Check if this is a project alias
    if project_alias in projects:
        project_config = projects[project_alias]
        project_id = project_config.get('project_id', project_alias)

        # Use instance from project config if not explicitly specified
        if instance_name is None:
            instance_name = project_config.get('instance')

        return project_id, instance_name

    # Not an alias, return as-is
    return project_alias, instance_name


def list_instances() -> None:
    """List all configured GitLab instances."""
    config_path = get_config_file()

    if not config_path:
        print("No GitLab configuration file found.")
        print("\nSearched locations:")
        for path in [Path.cwd() / 'gitlab_config.json',
                     Path.home() / '.gitlab' / 'config.json',
                     Path(__file__).parent.parent / 'gitlab_config.json']:
            print(f"  - {path}")
        print("\nCreate a gitlab_config.json file (see gitlab_config.json.template)")
        return

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        default = config.get('default', '')
        instances = config.get('instances', {})

        print(f"Config file: {config_path}")
        print(f"Default instance: {default}\n")
        print("Available instances:")
        for name, instance in instances.items():
            desc = instance.get('description', 'No description')
            url = instance.get('url', 'No URL')
            marker = ' (default)' if name == default else ''
            print(f"  - {name}{marker}")
            print(f"    URL: {url}")
            print(f"    Description: {desc}")

    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        sys.exit(1)


def list_projects() -> None:
    """List all configured project aliases."""
    config_path = get_config_file()

    if not config_path:
        print("No GitLab configuration file found.")
        return

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        projects = config.get('projects', {})

        if not projects:
            print("No project aliases configured.")
            print("\nAdd a 'projects' section to your gitlab_config.json")
            return

        print(f"Config file: {config_path}\n")
        print("Available project aliases:")
        for alias, project in projects.items():
            project_id = project.get('project_id', 'No ID')
            instance = project.get('instance', 'default')
            desc = project.get('description', 'No description')
            print(f"  - {alias}")
            print(f"    Project ID: {project_id}")
            print(f"    Instance: {instance}")
            print(f"    Description: {desc}")
            print()

    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        sys.exit(1)


class GitLabAPI:
    """GitLab API client for issues, merge requests, and comments."""

    def __init__(self, instance_name: Optional[str] = None):
        self.base_url, self.token = load_gitlab_config(instance_name)

        self.headers = {
            'PRIVATE-TOKEN': self.token,
            'Content-Type': 'application/json'
        }
        self.api_url = f"{self.base_url}/api/v4"

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make API request with error handling."""
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}", file=sys.stderr)
            print(f"Response: {e.response.text}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def get_project(self, project_id: str) -> Dict:
        """Get project details."""
        return self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}")

    def get_issue(self, project_id: str, issue_iid: int) -> Dict:
        """Get issue details including description and comments."""
        issue = self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/issues/{issue_iid}")

        # Fetch comments/notes
        notes = self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/issues/{issue_iid}/notes")
        issue['notes'] = notes

        return issue

    def list_issues(self, project_id: str, state: str = 'opened', labels: Optional[List[str]] = None) -> List[Dict]:
        """List issues in a project."""
        params = {'state': state}
        if labels:
            params['labels'] = ','.join(labels)

        return self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/issues", params=params)

    def get_merge_request(self, project_id: str, mr_iid: int) -> Dict:
        """Get merge request details including changes and comments."""
        mr = self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/merge_requests/{mr_iid}")

        # Fetch changes (diffs)
        changes = self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/merge_requests/{mr_iid}/changes")
        mr['changes'] = changes.get('changes', [])

        # Fetch comments/notes
        notes = self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/merge_requests/{mr_iid}/notes")
        mr['notes'] = notes

        return mr

    def list_merge_requests(self, project_id: str, state: str = 'opened') -> List[Dict]:
        """List merge requests in a project."""
        params = {'state': state}
        return self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/merge_requests", params=params)

    def post_issue_comment(self, project_id: str, issue_iid: int, body: str) -> Dict:
        """Post a comment on an issue."""
        data = {'body': body}
        return self._request('POST', f"projects/{requests.utils.quote(project_id, safe='')}/issues/{issue_iid}/notes", json=data)

    def post_mr_comment(self, project_id: str, mr_iid: int, body: str) -> Dict:
        """Post a comment on a merge request."""
        data = {'body': body}
        return self._request('POST', f"projects/{requests.utils.quote(project_id, safe='')}/merge_requests/{mr_iid}/notes", json=data)

    def get_diff_content(self, project_id: str, mr_iid: int) -> str:
        """Get merge request diff as unified diff format."""
        changes = self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/merge_requests/{mr_iid}/changes")

        diff_content = []
        for change in changes.get('changes', []):
            diff_content.append(f"File: {change['old_path']} -> {change['new_path']}")
            diff_content.append(change['diff'])
            diff_content.append("\n")

        return "\n".join(diff_content)

    def list_project_issues_aggregate(self, project_id: str, days: int = 7) -> Dict[str, Any]:
        """Aggregate issue statistics for a project."""
        all_issues = self._request('GET', f"projects/{requests.utils.quote(project_id, safe='')}/issues",
                                   params={'per_page': 100})

        stats = {
            'total': len(all_issues),
            'opened': sum(1 for i in all_issues if i['state'] == 'opened'),
            'closed': sum(1 for i in all_issues if i['state'] == 'closed'),
            'by_label': {},
            'recent': []
        }

        # Count by labels
        for issue in all_issues:
            for label in issue.get('labels', []):
                stats['by_label'][label] = stats['by_label'].get(label, 0) + 1

        # Recent issues
        stats['recent'] = sorted(
            all_issues,
            key=lambda x: x['updated_at'],
            reverse=True
        )[:10]

        return stats


def main():
    """CLI interface for GitLab API operations."""
    if len(sys.argv) < 2:
        print("Usage: gitlab_api.py [--instance=<name>] <command> [args...]", file=sys.stderr)
        print("\nCommands:", file=sys.stderr)
        print("  list-instances                                   - List configured GitLab instances", file=sys.stderr)
        print("  list-projects                                    - List configured project aliases", file=sys.stderr)
        print("  get-issue <project> <issue_iid>                 - Fetch issue with comments", file=sys.stderr)
        print("  list-issues <project> [state] [labels...]       - List issues with filters", file=sys.stderr)
        print("  get-mr <project> <mr_iid>                       - Fetch merge request with changes", file=sys.stderr)
        print("  list-mrs <project> [state]                      - List merge requests", file=sys.stderr)
        print("  post-issue-comment <project> <issue_iid> <comment>", file=sys.stderr)
        print("  post-mr-comment <project> <mr_iid> <comment>", file=sys.stderr)
        print("  get-diff <project> <mr_iid>                     - Get unified diff for MR", file=sys.stderr)
        print("  aggregate-issues <project> [days]               - Get issue statistics", file=sys.stderr)
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

    # Handle list commands (don't need API initialization)
    if command == 'list-instances':
        list_instances()
        return

    if command == 'list-projects':
        list_projects()
        return

    # Resolve project alias if a project argument is provided
    if len(args) > 1:
        project_arg = args[1]
        resolved_project_id, resolved_instance = resolve_project_alias(project_arg, instance_name)
        args[1] = resolved_project_id

        # Use the instance from project config if not explicitly set
        if instance_name is None and resolved_instance is not None:
            instance_name = resolved_instance

    # Initialize API with optional instance name
    api = GitLabAPI(instance_name)

    try:
        if command == 'get-issue':
            project_id, issue_iid = args[1], int(args[2])
            result = api.get_issue(project_id, issue_iid)

        elif command == 'list-issues':
            project_id = args[1]
            state = args[2] if len(args) > 2 else 'opened'
            labels = args[3:] if len(args) > 3 else None
            result = api.list_issues(project_id, state, labels)

        elif command == 'get-mr':
            project_id, mr_iid = args[1], int(args[2])
            result = api.get_merge_request(project_id, mr_iid)

        elif command == 'list-mrs':
            project_id = args[1]
            state = args[2] if len(args) > 2 else 'opened'
            result = api.list_merge_requests(project_id, state)

        elif command == 'post-issue-comment':
            project_id, issue_iid, comment = args[1], int(args[2]), args[3]
            result = api.post_issue_comment(project_id, issue_iid, comment)

        elif command == 'post-mr-comment':
            project_id, mr_iid, comment = args[1], int(args[2]), args[3]
            result = api.post_mr_comment(project_id, mr_iid, comment)

        elif command == 'get-diff':
            project_id, mr_iid = args[1], int(args[2])
            result = api.get_diff_content(project_id, mr_iid)
            print(result)
            return

        elif command == 'aggregate-issues':
            project_id = args[1]
            days = int(args[2]) if len(args) > 2 else 7
            result = api.list_project_issues_aggregate(project_id, days)

        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)

        print(json.dumps(result, indent=2))

    except IndexError:
        print(f"Invalid arguments for command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
