#!/usr/bin/env python3
"""
Local, merge-safe cache for GitLab data, layered by scope:

  ~/.gitlab/cache/<instance>/users.json                       - instance-level user directory
  ~/.gitlab/cache/<instance>/projects/<project>/project.json  - project-level metadata (incl. members)
  ~/.gitlab/cache/<instance>/projects/<project>/issues/<iid>.json - issue-level issue + notes + our own annotations

Every write deep-merges onto whatever is already on disk. Nothing already
cached is ever dropped or blindly overwritten - new data is layered on top,
so repeated syncs accumulate knowledge instead of resetting it.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

CACHE_ROOT = Path.home() / ".gitlab" / "cache"


def _sanitize(project_id: str) -> str:
    return project_id.replace('/', '__')


def _instance_dir(instance: str) -> Path:
    d = CACHE_ROOT / instance
    d.mkdir(parents=True, exist_ok=True)
    return d


def _project_dir(instance: str, project_id: str) -> Path:
    d = _instance_dir(instance) / "projects" / _sanitize(project_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _read_json(path: Path) -> Dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def _write_json(path: Path, data: Dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def deep_merge(base: Dict, new: Dict) -> Dict:
    """Recursively merge new onto base. New values win on leaf conflicts;
    nothing present in base disappears unless new explicitly replaces it."""
    merged = dict(base)
    for key, value in new.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


# ---- Instance-level: user directory ----

_USER_FIELDS = ('id', 'username', 'name', 'public_email', 'web_url', 'state')


def upsert_users(instance: str, users: List[Dict]) -> Dict:
    """Merge a batch of GitLab user objects into the instance's user directory."""
    path = _instance_dir(instance) / "users.json"
    cache = _read_json(path)
    for user in users:
        if not user or not user.get('id'):
            continue
        uid = str(user['id'])
        entry = {k: user[k] for k in _USER_FIELDS if k in user}
        cache[uid] = deep_merge(cache.get(uid, {}), entry)
    _write_json(path, cache)
    return cache


def get_users(instance: str) -> Dict:
    return _read_json(_instance_dir(instance) / "users.json")


# ---- Project-level: metadata and membership ----

def upsert_project(instance: str, project_id: str, data: Dict) -> Dict:
    path = _project_dir(instance, project_id) / "project.json"
    merged = deep_merge(_read_json(path), data)
    _write_json(path, merged)
    return merged


def get_project(instance: str, project_id: str) -> Dict:
    return _read_json(_project_dir(instance, project_id) / "project.json")


# ---- Issue-level: issue + notes + our own annotations ----

def _issue_path(instance: str, project_id: str, issue_iid) -> Path:
    d = _project_dir(instance, project_id) / "issues"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{issue_iid}.json"


def sync_issue(instance: str, project_id: str, issue_iid, fresh_issue: Dict) -> Dict:
    """Merge a freshly-fetched issue+notes payload into the cached copy.

    Notes are merged by id, so a note already on disk never disappears and
    new notes just get appended - callers see the full history without
    refetching it, and our own annotations (see annotate_issue) survive
    because deep_merge only overwrites keys fresh_issue actually provides."""
    path = _issue_path(instance, project_id, issue_iid)
    cache = _read_json(path)

    cached_notes = {str(n['id']): n for n in cache.get('notes', [])}
    for note in fresh_issue.get('notes', []):
        cached_notes[str(note['id'])] = note

    merged = deep_merge(cache, fresh_issue)
    merged['notes'] = sorted(cached_notes.values(), key=lambda n: n.get('created_at', ''))
    _write_json(path, merged)

    seen_users = [merged.get('author'), merged.get('assignee'), *merged.get('assignees', [])]
    seen_users += [n.get('author') for n in merged['notes']]
    upsert_users(instance, [u for u in seen_users if u])

    return merged


def get_issue_cache(instance: str, project_id: str, issue_iid) -> Optional[Dict]:
    path = _issue_path(instance, project_id, issue_iid)
    return _read_json(path) if path.exists() else None


def annotate_issue(instance: str, project_id: str, issue_iid, key: str, value: Any) -> Dict:
    """Record our own knowledge against an issue (e.g. root-cause analysis,
    which note ids we've already replied to) without touching GitLab's data."""
    path = _issue_path(instance, project_id, issue_iid)
    cache = _read_json(path)
    cache.setdefault('_notes', {})[key] = value
    _write_json(path, cache)
    return cache


def main():
    if len(sys.argv) < 2:
        print("Usage: gitlab_cache.py <command> [args...]", file=sys.stderr)
        print("\nRead-only (no network, no gitlab-config needed):", file=sys.stderr)
        print("  get-issue <instance> <project_id> <issue_iid>", file=sys.stderr)
        print("  get-users <instance>", file=sys.stderr)
        print("  get-project <instance> <project_id>", file=sys.stderr)
        print("  annotate <instance> <project_id> <issue_iid> <key> <value>", file=sys.stderr)
        print("\nNote: writes (sync-issue, sync-project) are driven from gitlab_api.py, not here.", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    try:
        if command == 'get-issue':
            result = get_issue_cache(sys.argv[2], sys.argv[3], sys.argv[4])
            if result is None:
                print("null")
                return
        elif command == 'get-users':
            result = get_users(sys.argv[2])
        elif command == 'get-project':
            result = get_project(sys.argv[2], sys.argv[3])
        elif command == 'annotate':
            result = annotate_issue(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(result, indent=2))
    except IndexError:
        print(f"Invalid arguments for command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
