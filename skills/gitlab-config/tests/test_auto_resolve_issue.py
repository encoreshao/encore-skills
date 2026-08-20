import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import auto_resolve_issue


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_create_merge_request_threads_bundle_name_to_load_gitlab_config(monkeypatch):
    captured = {}

    def fake_load_gitlab_config(instance_name=None, bundle_name=None):
        captured["instance_name"] = instance_name
        captured["bundle_name"] = bundle_name
        return "https://gitlab.example.com", "some-token"

    monkeypatch.setattr(auto_resolve_issue, "load_gitlab_config", fake_load_gitlab_config)

    def fake_post(url, headers=None, json=None):
        return _FakeResponse({"web_url": "https://gitlab.example.com/mr/1"})

    monkeypatch.setattr("requests.post", fake_post)

    auto_resolve_issue.create_merge_request(
        "group/project", "loop/issue-1", "main", "title", "description", 1,
        instance_name="ekohe", bundle_name="sonar-limited",
    )

    assert captured == {"instance_name": "ekohe", "bundle_name": "sonar-limited"}


def test_main_create_mr_passes_resolved_bundle_through(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "gitlab_config.json").write_text(json.dumps({
        "projects": {"stripes": {"project_id": "ekohe/sonar/sonar-next.web", "instance": "ekohe", "bundle": "sonar-limited"}},
    }))

    captured = {}

    def fake_create_merge_request(project_id, source_branch, target_branch, title, description, issue_iid, instance_name=None, bundle_name=None):
        captured["project_id"] = project_id
        captured["instance_name"] = instance_name
        captured["bundle_name"] = bundle_name
        return {"web_url": "https://gitlab.example.com/mr/1"}

    monkeypatch.setattr(auto_resolve_issue, "create_merge_request", fake_create_merge_request)
    monkeypatch.setattr(sys, "argv", [
        "auto_resolve_issue.py", "create-mr", "stripes", "loop/issue-1", "main", "title", "description", "1",
    ])

    auto_resolve_issue.main()

    assert captured == {"project_id": "ekohe/sonar/sonar-next.web", "instance_name": "ekohe", "bundle_name": "sonar-limited"}
    assert "web_url" in capsys.readouterr().out
