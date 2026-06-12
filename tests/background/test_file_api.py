import os

os.environ["FILE_API_KEY"] = "test-key-abc123"

from fastapi.testclient import TestClient

from background.file_api import app

client = TestClient(app)
HEADERS = {"X-Api-Key": "test-key-abc123"}
BAD_HEADERS = {"X-Api-Key": "wrong"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_read_rejects_bad_key():
    r = client.get("/read?path=calibration/weather-engine.md", headers=BAD_HEADERS)
    assert r.status_code == 403


def test_write_rejects_bad_key():
    r = client.post("/write", json={"path": "test.md", "content": "x"}, headers=BAD_HEADERS)
    assert r.status_code == 403


def test_write_path_traversal_blocked():
    r = client.post(
        "/write",
        json={"path": "../../CLAUDE.md", "content": "pwned"},
        headers=HEADERS,
    )
    assert r.status_code == 400


def test_read_path_traversal_blocked():
    r = client.get("/read?path=../CLAUDE.md", headers=HEADERS)
    assert r.status_code == 400


def test_read_missing_file_returns_404():
    r = client.get("/read?path=does-not-exist.md", headers=HEADERS)
    assert r.status_code == 404


def test_list_returns_files():
    r = client.get("/list", headers=HEADERS)
    assert r.status_code == 200
    assert "files" in r.json()


def test_stage_ui_renders_filename_and_content():
    r = client.get("/stage-ui", params={"filename": "note.md", "content": "hello world", "key": "abc"})
    assert r.status_code == 200
    assert "note.md" in r.text
    assert "hello world" in r.text


def test_stage_ui_escapes_html_in_filename_and_content():
    r = client.get(
        "/stage-ui",
        params={"filename": "<script>alert(1)</script>", "content": "<img src=x onerror=alert(1)>", "key": "abc"},
    )
    assert r.status_code == 200
    # The visible HTML (filename heading + <pre> content block) must be escaped.
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in r.text
    assert "&lt;img src=x onerror=alert(1)&gt;" in r.text
    assert "<pre><img" not in r.text
    assert "<h1><script>" not in r.text


def test_write_and_read_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("background.file_api.REPO_ROOT", tmp_path)
    monkeypatch.setattr("background.file_api.STAGING_DIR", tmp_path)
    monkeypatch.setattr("background.file_api.DOCS_DIR", tmp_path)
    content = "# Test instruction\nDo something."
    r = client.post(
        "/write",
        json={"path": "TEST_PHASE.md", "content": content},
        headers=HEADERS,
    )
    assert r.status_code == 200
