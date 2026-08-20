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
