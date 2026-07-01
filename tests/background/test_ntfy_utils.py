import json

from background import ntfy_utils


def _fake_run(stdout):
    return lambda cmd, **kw: type("R", (), {"stdout": stdout})()


def test_send_ntfy_records_id(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run('{"id": "abc123"}'))

    msg_id = ntfy_utils.send_ntfy("hello")

    assert msg_id == "abc123"
    assert json.loads(sent_ids_file.read_text()) == ["abc123"]


def test_send_ntfy_handles_unparseable_response(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run("not json"))

    msg_id = ntfy_utils.send_ntfy("hello")

    assert msg_id is None
    assert not sent_ids_file.exists()


def test_was_sent_by_us_true_for_recorded_id(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    sent_ids_file.write_text(json.dumps(["id1", "id2"]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    assert ntfy_utils.was_sent_by_us("id1") is True
    assert ntfy_utils.was_sent_by_us("id3") is False


def test_was_sent_by_us_false_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", tmp_path / "missing.json")
    assert ntfy_utils.was_sent_by_us("id1") is False


def test_was_sent_by_us_false_for_none_id(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    sent_ids_file.write_text(json.dumps(["id1"]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    assert ntfy_utils.was_sent_by_us(None) is False


def test_record_sent_id_caps_at_max_entries(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils, "MAX_SENT_IDS", 3)

    for i in range(5):
        ntfy_utils.record_sent_id(f"id{i}")

    assert json.loads(sent_ids_file.read_text()) == ["id2", "id3", "id4"]


def test_send_ntfy_appends_to_existing_ids(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    import json as _json
    sent_ids_file.write_text(_json.dumps(["existing"]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run('{"id": "new123"}'))

    ntfy_utils.send_ntfy("hello")

    ids = _json.loads(sent_ids_file.read_text())
    assert "existing" in ids
    assert "new123" in ids


def test_record_sent_id_creates_file_if_missing(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "missing.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    ntfy_utils.record_sent_id("newid")

    import json as _json
    assert _json.loads(sent_ids_file.read_text()) == ["newid"]


def test_was_sent_by_us_empty_file(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "empty.json"
    import json as _json
    sent_ids_file.write_text(_json.dumps([]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    assert ntfy_utils.was_sent_by_us("id1") is False


def test_send_ntfy_no_id_key_returns_none(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run('{"error": "bad"}'))

    msg_id = ntfy_utils.send_ntfy("hello")

    assert msg_id is None
