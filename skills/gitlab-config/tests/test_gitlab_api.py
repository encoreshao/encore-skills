import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import gitlab_api


def _write_config(tmp_path, config):
    (tmp_path / "gitlab_config.json").write_text(json.dumps(config))


def test_load_gitlab_config_uses_bundle_token_when_given(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "default": "ekohe",
        "instances": {"ekohe": {"url": "https://gitlab.ekohe.com", "token": "instance-token"}},
        "bundles": {"sonar-limited": {"instance": "ekohe", "token": "bundle-token"}},
    })

    url, token = gitlab_api.load_gitlab_config("ekohe", "sonar-limited")

    assert url == "https://gitlab.ekohe.com"
    assert token == "bundle-token"


def test_load_gitlab_config_falls_back_to_instance_token_without_bundle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "default": "ekohe",
        "instances": {"ekohe": {"url": "https://gitlab.ekohe.com", "token": "instance-token"}},
    })

    url, token = gitlab_api.load_gitlab_config("ekohe", None)

    assert url == "https://gitlab.ekohe.com"
    assert token == "instance-token"


def test_load_gitlab_config_rejects_bundle_for_wrong_instance(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "default": "ekohe",
        "instances": {
            "ekohe": {"url": "https://gitlab.ekohe.com", "token": "ekohe-token"},
            "stripes": {"url": "https://gitlab.stripes.ai", "token": "stripes-token"},
        },
        "bundles": {"sonar-limited": {"instance": "stripes", "token": "bundle-token"}},
    })

    with pytest.raises(SystemExit):
        gitlab_api.load_gitlab_config("ekohe", "sonar-limited")

    assert "not 'ekohe'" in capsys.readouterr().err


def test_resolve_project_alias_returns_bundle_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "projects": {"stripes": {"project_id": "ekohe/sonar/sonar-next.web", "instance": "ekohe", "bundle": "sonar-limited"}},
    })

    project_id, instance_name, bundle_name = gitlab_api.resolve_project_alias("stripes")

    assert project_id == "ekohe/sonar/sonar-next.web"
    assert instance_name == "ekohe"
    assert bundle_name == "sonar-limited"


def test_resolve_project_alias_returns_none_bundle_when_absent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "projects": {"camp": {"project_id": "ekohe/kurrant/camp", "instance": "ekohe"}},
    })

    _project_id, _instance, bundle_name = gitlab_api.resolve_project_alias("camp")

    assert bundle_name is None


def test_gitlabapi_uses_bundle_token(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "default": "ekohe",
        "instances": {"ekohe": {"url": "https://gitlab.ekohe.com", "token": "instance-token"}},
        "bundles": {"sonar-limited": {"instance": "ekohe", "token": "bundle-token"}},
    })

    api = gitlab_api.GitLabAPI("ekohe", "sonar-limited")

    assert api.headers["PRIVATE-TOKEN"] == "bundle-token"


def test_project_info_prints_bundle(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "projects": {"stripes": {"project_id": "ekohe/sonar/sonar-next.web", "instance": "ekohe", "bundle": "sonar-limited"}},
    })

    gitlab_api.project_info("stripes")

    output = json.loads(capsys.readouterr().out)
    assert output == {"project_id": "ekohe/sonar/sonar-next.web", "instance": "ekohe", "bundle": "sonar-limited"}


def test_project_info_unknown_alias_exits(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {"projects": {}})

    with pytest.raises(SystemExit):
        gitlab_api.project_info("nope")

    assert "Unknown project alias" in capsys.readouterr().err


def test_load_gitlab_config_rejects_empty_bundle_token(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "not-a-real-home")
    monkeypatch.delenv("GITLAB_URL", raising=False)
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)
    _write_config(tmp_path, {
        "default": "ekohe",
        "instances": {"ekohe": {"url": "https://gitlab.ekohe.com", "token": "instance-token"}},
        "bundles": {"sonar-limited": {"instance": "ekohe", "token": ""}},
    })

    with pytest.raises(SystemExit):
        gitlab_api.load_gitlab_config("ekohe", "sonar-limited")

    assert "sonar-limited" in capsys.readouterr().err


def test_main_instance_override_drops_alias_bundle(tmp_path, monkeypatch):
    """An explicit --instance= override must ignore the alias's own bundle,
    not carry it forward to an instance the bundle wasn't configured for."""
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "default": "ekohe",
        "instances": {
            "ekohe": {"url": "https://gitlab.ekohe.com", "token": "ekohe-token"},
            "other": {"url": "https://gitlab.other.com", "token": "other-token"},
        },
        "projects": {"stripes": {"project_id": "ekohe/sonar/sonar-next.web", "instance": "ekohe", "bundle": "sonar-limited"}},
        "bundles": {"sonar-limited": {"instance": "ekohe", "token": "bundle-token"}},
    })

    captured = {}

    class FakeGitLabAPI:
        def __init__(self, instance_name=None, bundle_name=None):
            captured["instance_name"] = instance_name
            captured["bundle_name"] = bundle_name
            self.instance_name = instance_name

        def list_merge_requests(self, project_id, state, assignee_username=None, author_username=None):
            return []

    monkeypatch.setattr(gitlab_api, "GitLabAPI", FakeGitLabAPI)
    monkeypatch.setattr(sys, "argv", [
        "gitlab_api.py", "--instance=other", "list-mrs", "stripes", "opened",
    ])

    gitlab_api.main()

    assert captured == {"instance_name": "other", "bundle_name": None}


def _api_with_fake_request(tmp_path, monkeypatch):
    """A real GitLabAPI whose low-level _request is replaced with a fake
    the test controls, so list_issues/list_merge_requests exercise their
    own pagination/param-building logic without a real HTTP call."""
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "default": "ekohe",
        "instances": {"ekohe": {"url": "https://gitlab.ekohe.com", "token": "tok"}},
    })
    return gitlab_api.GitLabAPI("ekohe")


def test_list_issues_passes_assignee_and_author_filters(tmp_path, monkeypatch):
    api = _api_with_fake_request(tmp_path, monkeypatch)
    captured = {}

    def fake_request(method, endpoint, params=None):
        captured["params"] = params
        return []

    monkeypatch.setattr(api, "_request", fake_request)

    api.list_issues("a/b", assignee_username="encore", author_username="encore")

    assert captured["params"]["assignee_username"] == "encore"
    assert captured["params"]["author_username"] == "encore"


def test_list_issues_omits_filters_when_not_given(tmp_path, monkeypatch):
    api = _api_with_fake_request(tmp_path, monkeypatch)
    captured = {}

    def fake_request(method, endpoint, params=None):
        captured["params"] = params
        return []

    monkeypatch.setattr(api, "_request", fake_request)

    api.list_issues("a/b")

    assert "assignee_username" not in captured["params"]
    assert "author_username" not in captured["params"]


def test_list_issues_pages_through_all_results(tmp_path, monkeypatch):
    """GitLab's REST API silently caps a single response at its default
    per_page (20) - a project with more open issues than that must not have
    the rest go missing. A full page (== per_page) means "there might be
    more"; a short page means "that was the last one"."""
    api = _api_with_fake_request(tmp_path, monkeypatch)
    pages = {1: [{"iid": i} for i in range(100)], 2: [{"iid": 100}]}
    calls = []

    def fake_request(method, endpoint, params=None):
        calls.append(dict(params))
        return pages[params["page"]]

    monkeypatch.setattr(api, "_request", fake_request)

    result = api.list_issues("a/b")

    assert len(result) == 101
    assert len(calls) == 2
    assert calls[0]["per_page"] == 100
    assert calls[1]["page"] == 2


def test_list_issues_stops_after_short_page(tmp_path, monkeypatch):
    api = _api_with_fake_request(tmp_path, monkeypatch)
    calls = []

    def fake_request(method, endpoint, params=None):
        calls.append(dict(params))
        return [{"iid": 1}, {"iid": 2}]

    monkeypatch.setattr(api, "_request", fake_request)

    result = api.list_issues("a/b")

    assert len(result) == 2
    assert len(calls) == 1


def test_list_merge_requests_passes_assignee_and_author_filters(tmp_path, monkeypatch):
    api = _api_with_fake_request(tmp_path, monkeypatch)
    captured = {}

    def fake_request(method, endpoint, params=None):
        captured["params"] = params
        return []

    monkeypatch.setattr(api, "_request", fake_request)

    api.list_merge_requests("a/b", assignee_username="encore", author_username="encore")

    assert captured["params"]["assignee_username"] == "encore"
    assert captured["params"]["author_username"] == "encore"


def test_list_merge_requests_pages_through_all_results(tmp_path, monkeypatch):
    api = _api_with_fake_request(tmp_path, monkeypatch)
    pages = {1: [{"iid": i} for i in range(100)], 2: [{"iid": 100}]}

    def fake_request(method, endpoint, params=None):
        return pages[params["page"]]

    monkeypatch.setattr(api, "_request", fake_request)

    result = api.list_merge_requests("a/b")

    assert len(result) == 101


def test_main_list_issues_parses_assignee_and_author_flags(tmp_path, monkeypatch):
    """The CLI's list-issues subcommand accepts --assignee=/--author= flags
    in addition to its existing positional state/labels args, so
    dashboard_server.py (and anyone else) can ask GitLab to filter
    server-side instead of fetching everything and filtering client-side."""
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {"projects": {}})
    captured = {}

    class FakeGitLabAPI:
        def __init__(self, instance_name=None, bundle_name=None):
            self.instance_name = instance_name

        def list_issues(self, project_id, state, labels, assignee_username=None, author_username=None):
            captured["args"] = (project_id, state, labels, assignee_username, author_username)
            return []

    monkeypatch.setattr(gitlab_api, "GitLabAPI", FakeGitLabAPI)
    monkeypatch.setattr(sys, "argv", [
        "gitlab_api.py", "list-issues", "a/b", "opened", "--assignee=encore", "--author=encore",
    ])

    gitlab_api.main()

    assert captured["args"] == ("a/b", "opened", None, "encore", "encore")


def test_main_list_issues_still_parses_labels_alongside_flags(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {"projects": {}})
    captured = {}

    class FakeGitLabAPI:
        def __init__(self, instance_name=None, bundle_name=None):
            pass

        def list_issues(self, project_id, state, labels, assignee_username=None, author_username=None):
            captured["args"] = (project_id, state, labels, assignee_username, author_username)
            return []

    monkeypatch.setattr(gitlab_api, "GitLabAPI", FakeGitLabAPI)
    monkeypatch.setattr(sys, "argv", [
        "gitlab_api.py", "list-issues", "a/b", "opened", "bug", "urgent", "--assignee=encore",
    ])

    gitlab_api.main()

    assert captured["args"] == ("a/b", "opened", ["bug", "urgent"], "encore", None)


def test_main_list_mrs_parses_assignee_and_author_flags(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {"projects": {}})
    captured = {}

    class FakeGitLabAPI:
        def __init__(self, instance_name=None, bundle_name=None):
            pass

        def list_merge_requests(self, project_id, state, assignee_username=None, author_username=None):
            captured["args"] = (project_id, state, assignee_username, author_username)
            return []

    monkeypatch.setattr(gitlab_api, "GitLabAPI", FakeGitLabAPI)
    monkeypatch.setattr(sys, "argv", [
        "gitlab_api.py", "list-mrs", "a/b", "opened", "--author=encore",
    ])

    gitlab_api.main()

    assert captured["args"] == ("a/b", "opened", None, "encore")


def test_resolve_project_alias_returns_3tuple_for_non_alias(tmp_path, monkeypatch):
    """When project arg is not a configured alias, resolve_project_alias still returns 3-tuple with None bundle."""
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, {
        "projects": {"myproj": {"project_id": "a/b/c", "instance": "default"}},
    })

    project_id, instance_name, bundle_name = gitlab_api.resolve_project_alias("unknown/project")

    assert project_id == "unknown/project"
    assert instance_name is None
    assert bundle_name is None
