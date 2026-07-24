"""Tests for background/director_comments.py -- DIRECTOR_COMMENTS_BOX.md.

Hard requirement under test throughout: a submission with a missing or
wrong PIN must NEVER be staged, and the daemon must never fabricate
authenticity."""
import json

import pytest

from background import director_comments as dc


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dc, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(dc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(dc, "COMMENTS_TOPIC", "test-comments-topic")
    monkeypatch.setattr(dc, "COMMENTS_PIN", "correct-pin-123")
    # Isolate the intake lock at a tmp path (absent => unlocked) so the tests here never read the
    # REAL .comment_intake_locked flag (which is present live per the 2026-07-24 security incident).
    monkeypatch.setattr(dc, "INTAKE_LOCK_FILE", tmp_path / ".comment_intake_locked")
    (tmp_path / "staging").mkdir()
    yield


def _submission(pin="correct-pin-123", page="/supplier/", state="tab=regulatory", data_ts="abc1234", comment="looks wrong"):
    return f"PIN:{pin}\nPAGE:{page}\nSTATE:{state}\nDATA_TS:{data_ts}\n---\n{comment}"


def test_parse_valid_submission():
    parsed = dc.parse_comment_submission(_submission())
    assert parsed["page"] == "/supplier/"
    assert parsed["state"] == "tab=regulatory"
    assert parsed["data_ts"] == "abc1234"
    assert parsed["comment"] == "looks wrong"


def test_parse_rejects_wrong_pin():
    assert dc.parse_comment_submission(_submission(pin="wrong")) is None


def test_parse_rejects_missing_pin_field():
    msg = "PAGE:/supplier/\nSTATE:tab=regulatory\n---\nlooks wrong"
    assert dc.parse_comment_submission(msg) is None


def test_parse_rejects_malformed_no_delimiter():
    assert dc.parse_comment_submission("just some text with no structure at all") is None


def test_parse_rejects_when_comments_pin_not_configured(monkeypatch):
    monkeypatch.setattr(dc, "COMMENTS_PIN", None)
    assert dc.parse_comment_submission(_submission()) is None


def test_parse_handles_missing_optional_fields():
    msg = "PIN:correct-pin-123\nPAGE:/customers/\n---\nnice work"
    parsed = dc.parse_comment_submission(msg)
    assert parsed["page"] == "/customers/"
    assert parsed["state"] == ""
    assert parsed["data_ts"] == ""
    assert parsed["comment"] == "nice work"


def test_write_comment_to_staging_creates_readable_file():
    parsed = {"page": "/supplier/", "state": "tab=regulatory", "data_ts": "abc1234", "comment": "C6 looks wrong again"}
    path = dc._write_comment_to_staging(parsed)
    assert path.exists()
    content = path.read_text()
    assert "/supplier/" in content
    assert "tab=regulatory" in content
    assert "abc1234" in content
    assert "C6 looks wrong again" in content


def _mock_response(lines):
    return type("R", (), {"text": "\n".join(json.dumps(l) for l in lines)})()


def test_check_once_stages_valid_submission(monkeypatch):
    calls = []
    monkeypatch.setattr(dc, "notify", lambda msg, **k: calls.append(msg))
    monkeypatch.setattr(
        dc.requests, "get",
        lambda url, params, timeout: _mock_response([
            {"event": "message", "time": 1000, "id": "m1", "message": _submission()},
        ]),
    )
    new_since = dc.check_once(500)
    assert new_since == 1000
    staged = list(dc.STAGING_DIR.iterdir())
    assert len(staged) == 1
    assert "director page comment" in staged[0].read_text().lower()
    assert len(calls) == 1  # ack NTFY sent


def test_check_once_never_stages_wrong_pin(monkeypatch):
    calls = []
    monkeypatch.setattr(dc, "notify", lambda msg, **k: calls.append(msg))
    monkeypatch.setattr(
        dc.requests, "get",
        lambda url, params, timeout: _mock_response([
            {"event": "message", "time": 1000, "id": "m1", "message": _submission(pin="guessed")},
        ]),
    )
    dc.check_once(500)
    assert list(dc.STAGING_DIR.iterdir()) == []
    assert calls == []  # no ack for a rejected submission


def test_check_once_ignores_messages_at_or_before_watermark(monkeypatch):
    monkeypatch.setattr(dc, "notify", lambda msg, **k: None)
    monkeypatch.setattr(
        dc.requests, "get",
        lambda url, params, timeout: _mock_response([
            {"event": "message", "time": 500, "id": "m1", "message": _submission()},
        ]),
    )
    new_since = dc.check_once(1000)
    assert new_since == 1000
    assert list(dc.STAGING_DIR.iterdir()) == []


def test_check_once_handles_network_error(monkeypatch):
    def _raise(*a, **k):
        import requests as real_requests
        raise real_requests.RequestException("network down")
    monkeypatch.setattr(dc.requests, "get", _raise)
    assert dc.check_once(500) == 500


def test_check_once_skips_when_topic_not_configured(monkeypatch):
    monkeypatch.setattr(dc, "COMMENTS_TOPIC", None)
    calls = []
    monkeypatch.setattr(dc.requests, "get", lambda *a, **k: calls.append(1))
    assert dc.check_once(500) == 500
    assert calls == []


def test_check_once_multiple_submissions_mixed_valid_invalid(monkeypatch):
    calls = []
    monkeypatch.setattr(dc, "notify", lambda msg, **k: calls.append(msg))
    monkeypatch.setattr(
        dc.requests, "get",
        lambda url, params, timeout: _mock_response([
            {"event": "message", "time": 1000, "id": "m1", "message": _submission(comment="good one")},
            {"event": "message", "time": 1001, "id": "m2", "message": _submission(pin="bad", comment="forged")},
            {"event": "message", "time": 1002, "id": "m3", "message": _submission(comment="another good one")},
        ]),
    )
    dc.check_once(500)
    staged = list(dc.STAGING_DIR.iterdir())
    assert len(staged) == 2
    all_content = " ".join(p.read_text() for p in staged)
    assert "good one" in all_content
    assert "another good one" in all_content
    assert "forged" not in all_content

# ── INTAKE LOCK — fail closed (DIRECTOR_SECURITY_COMMENT_CHANNEL_INCIDENT 2026-07-24) ────────────
# R15 both ways: locked => a VALID, correct-PIN submission still stages NOTHING (the lock is not a
# PIN check — it refuses even authentic-looking input); unlocked => the same submission stages
# normally (so the lock is a real, removable gate, not the channel simply being dead).

def test_intake_lock_flag_absent_is_unlocked(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "INTAKE_LOCK_FILE", tmp_path / "nope")
    assert dc.intake_locked() is False


def test_intake_lock_flag_present_is_locked(tmp_path, monkeypatch):
    flag = tmp_path / ".comment_intake_locked"
    flag.write_text("locked")
    monkeypatch.setattr(dc, "INTAKE_LOCK_FILE", flag)
    assert dc.intake_locked() is True


def test_write_comment_refuses_when_locked(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "INTAKE_LOCK_FILE", tmp_path / ".comment_intake_locked")
    (tmp_path / ".comment_intake_locked").write_text("locked")
    monkeypatch.setattr(dc, "STAGING_DIR", tmp_path / "staging2")
    monkeypatch.setattr(dc, "LOG_FILE", tmp_path / "log2.md")
    out = dc._write_comment_to_staging({"page": "/supplier/", "state": "", "data_ts": "", "comment": "forged authentic-looking comment"})
    assert out is None
    assert not (tmp_path / "staging2").exists() or list((tmp_path / "staging2").iterdir()) == []


def test_check_once_stages_nothing_when_locked_even_valid_pin(monkeypatch):
    """The load-bearing lock proof: a submission with the CORRECT PIN — indistinguishable from a
    genuine one — stages NOTHING while locked, and the daemon does not even poll the network."""
    dc.INTAKE_LOCK_FILE.write_text("locked")  # the tmp-isolated flag from _isolate
    net = []
    monkeypatch.setattr(dc.requests, "get", lambda *a, **k: net.append(1))
    calls = []
    monkeypatch.setattr(dc, "notify", lambda msg, **k: calls.append(msg))
    new_since = dc.check_once(500)
    assert new_since == 500                       # watermark unchanged (no silent catch-up on unlock)
    assert net == []                              # did not poll while locked
    assert list(dc.STAGING_DIR.iterdir()) == []   # staged nothing
    assert calls == []                            # echoed nothing


def test_check_once_stages_again_once_unlocked(monkeypatch):
    """Removing the flag re-opens the channel (mutation of the lock proof): the SAME valid submission
    that staged nothing while locked now stages — proving the earlier silence was the lock, not a
    dead channel."""
    monkeypatch.setattr(dc, "notify", lambda msg, **k: None)
    monkeypatch.setattr(
        dc.requests, "get",
        lambda url, params, timeout: _mock_response([
            {"event": "message", "time": 1000, "id": "m1", "message": _submission()},
        ]),
    )
    # locked -> nothing
    dc.INTAKE_LOCK_FILE.write_text("locked")
    dc.check_once(500)
    assert list(dc.STAGING_DIR.iterdir()) == []
    # unlocked -> stages
    dc.INTAKE_LOCK_FILE.unlink()
    new_since = dc.check_once(500)
    assert new_since == 1000
    assert len(list(dc.STAGING_DIR.iterdir())) == 1


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
