import json
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


def test_write_rejects_empty_path():
    r = client.post("/write", json={"path": "", "content": "x"}, headers=HEADERS)
    assert r.status_code == 400


def test_write_rejects_path_resolving_to_staging_dir():
    r = client.post("/write", json={"path": ".", "content": "x"}, headers=HEADERS)
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


def test_stage_ui_get_returns_form():
    r = client.get("/stage-ui")
    assert r.status_code == 200
    assert "<form" in r.text
    assert 'name="filename"' in r.text
    assert 'name="content"' in r.text
    assert 'name="key"' in r.text


def test_stage_ui_post_renders_filename_and_content():
    r = client.post("/stage-ui", data={"filename": "note.md", "content": "hello world", "key": "abc"})
    assert r.status_code == 200
    assert "note.md" in r.text
    assert "hello world" in r.text


def test_stage_ui_post_escapes_html_in_filename_and_content():
    r = client.post(
        "/stage-ui",
        data={"filename": "<script>alert(1)</script>", "content": "<img src=x onerror=alert(1)>", "key": "abc"},
    )
    assert r.status_code == 200
    # The visible HTML (filename heading + <pre> content block) must be escaped.
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in r.text
    assert "&lt;img src=x onerror=alert(1)&gt;" in r.text
    assert "<pre><img" not in r.text
    assert "<h1><script>" not in r.text


def test_stage_ui_post_handles_large_content_without_url_limits():
    big_content = "x" * 50_000
    r = client.post("/stage-ui", data={"filename": "big.md", "content": big_content, "key": "abc"})
    assert r.status_code == 200
    assert big_content in r.text


def test_ui_stage_returns_mobile_form():
    r = client.get("/ui/stage")
    assert r.status_code == 200
    assert "viewport" in r.text
    assert 'id="filename"' in r.text
    assert 'id="content"' in r.text
    assert "/write" in r.text


def test_ui_status_returns_mobile_page_that_reads_latest():
    r = client.get("/ui/status")
    assert r.status_code == 200
    assert "viewport" in r.text
    assert "/read?path=status/LATEST.md" in r.text


def test_healthz_no_auth_required():
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["uvicorn"] == "alive"
    assert "funnel_active" in body
    assert "staging_writable" in body
    assert "last_file_received" in body


def test_healthz_reports_staging_writable(tmp_path, monkeypatch):
    monkeypatch.setattr("background.file_api.STAGING_DIR", tmp_path)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["staging_writable"] is True


def test_healthz_reports_last_file_received(tmp_path, monkeypatch):
    monkeypatch.setattr("background.file_api.STAGING_DIR", tmp_path)
    (tmp_path / "TASK_X.md").write_text("hello")
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["last_file_received"] is not None


def test_respond_rejects_invalid_gate_id():
    r = client.post("/respond", json={"gate": "../escape", "decision": "x"}, headers=HEADERS)
    assert r.status_code == 400


def test_respond_rejects_without_token_or_key():
    r = client.post("/respond", json={"gate": "phase4b", "decision": "approve"})
    assert r.status_code == 403


def test_respond_with_valid_api_key_records_decision(tmp_path, monkeypatch):
    monkeypatch.setattr("background.file_api.RESPONSES_DIR", tmp_path / "responses")
    monkeypatch.setattr("background.file_api.GATE_TOKENS_DIR", tmp_path / "tokens")
    monkeypatch.setattr("background.file_api.REPO_ROOT", tmp_path)
    r = client.post(
        "/respond",
        json={"gate": "phase4b", "decision": "approved, proceed"},
        headers=HEADERS,
    )
    assert r.status_code == 200
    recorded = json.loads((tmp_path / "responses" / "phase4b.json").read_text())
    assert recorded["decision"] == "approved, proceed"
    assert recorded["gate"] == "phase4b"


def test_respond_with_valid_gate_token_invalidates_it(tmp_path, monkeypatch):
    monkeypatch.setattr("background.file_api.RESPONSES_DIR", tmp_path / "responses")
    monkeypatch.setattr("background.file_api.GATE_TOKENS_DIR", tmp_path / "tokens")
    monkeypatch.setattr("background.file_api.REPO_ROOT", tmp_path)
    from background.file_api import generate_gate_token

    token = generate_gate_token("phase4b")

    r = client.post("/respond", json={"gate": "phase4b", "decision": "hold", "token": token})
    assert r.status_code == 200
    assert not (tmp_path / "tokens" / "phase4b.token").exists()

    # Token is single-use — a second attempt with the same token fails.
    r = client.post("/respond", json={"gate": "phase4b", "decision": "hold", "token": token})
    assert r.status_code == 403


def test_respond_rejects_wrong_gate_token(tmp_path, monkeypatch):
    monkeypatch.setattr("background.file_api.RESPONSES_DIR", tmp_path / "responses")
    monkeypatch.setattr("background.file_api.GATE_TOKENS_DIR", tmp_path / "tokens")
    monkeypatch.setattr("background.file_api.REPO_ROOT", tmp_path)
    from background.file_api import generate_gate_token

    generate_gate_token("phase4b")

    r = client.post("/respond", json={"gate": "phase4b", "decision": "hold", "token": "wrong-token"})
    assert r.status_code == 403


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
