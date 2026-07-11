"""Tests for background/director_input_log.py.

Deliberately stricter isolation than the ntfy_mirror precedent
(tests/background/test_ntfy_mirror.py, which writes real content into the
real public-repo mirror file when PYTEST_CURRENT_TEST is deleted): a write
here can trigger a real `git push` to the private ops repo, a much bigger
consequence than a local file write, so every test that exercises
append_entry() mocks commit_and_push out entirely -- no test run should
ever touch the real synthetic-enterprise-ops repo."""
from unittest.mock import patch

import pytest

from background import director_input_log as dil


@pytest.fixture
def isolated_log(tmp_path, monkeypatch):
    """Patches LOG_FILE and mocks commit_and_push -- but does NOT delete
    PYTEST_CURRENT_TEST here: pytest re-sets that env var fresh at the
    "call" phase boundary, so a delenv done during fixture *setup* does not
    survive into the test body (confirmed empirically -- the working
    ntfy_mirror.py precedent calls delenv as the first line of the TEST
    FUNCTION itself, during "call" phase, not inside a shared fixture).
    Every test using this fixture must call
    `monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)` itself,
    as its own first line."""
    monkeypatch.setattr(dil, "LOG_FILE", tmp_path / "director_input_log.md")
    with patch("background.director_input_log.commit_and_push") as mock_push:
        yield mock_push


class TestHasSignedSuffix:
    def test_true_for_a_real_wake_signature_shape(self):
        assert dil.has_signed_suffix("some text|1783767358|" + "a" * 64)

    def test_false_for_plain_text(self):
        assert not dil.has_signed_suffix("just a normal console message")

    def test_false_for_short_hex_that_isnt_64_chars(self):
        assert not dil.has_signed_suffix("committed as|1783767358|d3a731b4")


class TestSplitSignedSegments:
    def test_single_segment_returned_unchanged(self):
        text = "some text|1783767358|" + "a" * 64
        assert dil.split_signed_segments(text) == [text]

    def test_plain_text_returned_unchanged(self):
        text = "no signature here at all"
        assert dil.split_signed_segments(text) == [text]

    def test_splits_two_concatenated_segments(self):
        seg1 = "[SUPERVISOR: first]|1783779512|" + "a" * 64
        seg2 = "[SUPERVISOR: second]|1783780232|" + "b" * 64
        result = dil.split_signed_segments(seg1 + seg2)
        assert result == [seg1, seg2]

    def test_splits_three_concatenated_segments(self):
        seg1 = "[A]|1783779512|" + "a" * 64
        seg2 = "[B]|1783780232|" + "b" * 64
        seg3 = "[C]|1783781000|" + "c" * 64
        result = dil.split_signed_segments(seg1 + seg2 + seg3)
        assert result == [seg1, seg2, seg3]


class TestHmacStatus:
    def test_none_when_no_signature_present(self):
        assert dil._hmac_status("plain window message") is None

    def test_true_for_a_validly_signed_message(self, monkeypatch):
        monkeypatch.setenv("SE_WAKE_HMAC_KEY", "test-key-123")
        monkeypatch.setattr(dil, "WAKE_HMAC_KEY", "test-key-123")
        with patch("background.director_input_log.verify_wake_message", return_value="the text"):
            assert dil._hmac_status("[SUPERVISOR: x]|123456789|" + "a" * 64) is True

    def test_false_for_an_invalidly_signed_message(self, monkeypatch):
        monkeypatch.setattr(dil, "WAKE_HMAC_KEY", "test-key-123")
        with patch("background.director_input_log.verify_wake_message", return_value=None):
            assert dil._hmac_status("[SUPERVISOR: x]|123456789|" + "a" * 64) is False


class TestHmacStatusMultiSegmentRealSigning:
    """2026-07-11, director-caught real bug: the supervisor concatenates
    multiple independently-signed wake messages with no separator when
    granting one turn for several queued items (e.g. two run_complete
    markers at once, real example: 14:30:32 UTC director_input_log.md
    entry). Uses REAL sign_wake_message()/verify_wake_message() -- no
    mocking -- for the strongest possible regression proof."""

    def test_two_genuinely_signed_messages_concatenated_verify_true(self):
        from background.ntfy_utils import sign_wake_message
        seg1 = sign_wake_message("[SUPERVISOR: first real message]")
        seg2 = sign_wake_message("[SUPERVISOR: second real message]")
        concatenated = seg1 + seg2
        # Before the fix, this would have been False -- the naive
        # single-suffix check verifies "[msg1]|ts1|hash1[msg2]|ts2" against
        # hash2, which was never the real signed payload.
        assert dil._hmac_status(concatenated) is True

    def test_three_genuinely_signed_messages_concatenated_verify_true(self):
        from background.ntfy_utils import sign_wake_message
        segs = [sign_wake_message(f"[SUPERVISOR: message {i}]") for i in range(3)]
        assert dil._hmac_status("".join(segs)) is True

    def test_one_genuine_plus_one_forged_segment_verifies_false(self):
        """The 'not a security hole' claim, proven: splicing one real
        signed segment with one fabricated one must still fail overall --
        never silently accept the real half and ignore the fake one."""
        from background.ntfy_utils import sign_wake_message
        real_seg = sign_wake_message("[SUPERVISOR: genuine]")
        forged_seg = "[SUPERVISOR: forged]|1783780232|" + "f" * 64
        assert dil._hmac_status(real_seg + forged_seg) is False

    def test_single_genuinely_signed_message_still_works(self):
        """Regression guard: the common single-message case must not break
        from the multi-segment handling being added."""
        from background.ntfy_utils import sign_wake_message
        seg = sign_wake_message("[SUPERVISOR: only message]")
        assert dil._hmac_status(seg) is True


class TestClassifyChannel:
    def test_invalid_signature_is_unknown_unverified(self):
        assert dil.classify_channel("anything", hmac_status=False) == "unknown-unverified"

    def test_no_signature_defaults_to_window(self):
        assert dil.classify_channel("a live console paste", hmac_status=None) == "window"

    def test_valid_staging_watcher_tag(self):
        text = "[STAGING WATCHER: new staged instruction(s) landed -- X.md.]"
        assert dil.classify_channel(text, hmac_status=True) == "watcher-wake"

    def test_valid_supervisor_tag(self):
        text = "[SUPERVISOR: turn granted -- unprocessed staging -- X.md.]"
        assert dil.classify_channel(text, hmac_status=True) == "supervisor-wake"

    def test_valid_dispatcher_tag(self):
        text = "[DISPATCHER: URGENT -- respond.]"
        assert dil.classify_channel(text, hmac_status=True) == "ntfy"

    def test_valid_signature_no_recognised_bracket_still_a_relay(self):
        assert dil.classify_channel("some other signed relay text", hmac_status=True) == "supervisor-wake"


class TestAppendEntryPerChannelTag:
    """One test per channel tag, per DIRECTOR_INPUT_LOG.md's own DoD --
    except window-live/window-queued-midturn, which collapse into one
    "window" tag (see the module's own scope-limit docstring for why)."""

    @pytest.mark.parametrize("channel", [
        "window", "ntfy", "comments-box", "supervisor-wake",
        "watcher-wake", "advisor-staged", "unknown-unverified",
    ])
    def test_channel_tag_written_correctly(self, isolated_log, channel, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        dil.append_entry(channel, "test content", direction="in", hmac_verified=None)
        content = dil.LOG_FILE.read_text()
        assert f"[{channel}]" in content
        assert "test content" in content

    def test_hmac_status_recorded_in_entry(self, isolated_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        dil.append_entry("supervisor-wake", "x", hmac_verified=True)
        assert "[hmac:valid]" in dil.LOG_FILE.read_text()
        dil.append_entry("unknown-unverified", "y", hmac_verified=False)
        assert "[hmac:invalid]" in dil.LOG_FILE.read_text()
        dil.append_entry("window", "z", hmac_verified=None)
        assert "[hmac:n/a]" in dil.LOG_FILE.read_text()

    def test_content_is_scrubbed(self, isolated_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.setattr(dil, "NTFY_TOPIC", "my-secret-topic-value")
        dil.append_entry("ntfy", "the topic is my-secret-topic-value here")
        content = dil.LOG_FILE.read_text()
        assert "my-secret-topic-value" not in content
        assert "[redacted:" in content

    def test_noop_under_pytest_without_deleting_the_guard_var(self, tmp_path, monkeypatch):
        """PYTEST_CURRENT_TEST is always set for the duration of any test
        pytest runs -- confirms the guard actually fires when nothing
        deletes it (unlike every other test in this class, which does)."""
        monkeypatch.setattr(dil, "LOG_FILE", tmp_path / "should_not_exist.md")
        assert dil.LOG_FILE.parent == tmp_path
        dil.append_entry("window", "should not be written")
        assert not dil.LOG_FILE.exists()

    def test_commit_and_push_called_with_lock_held(self, isolated_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        dil.append_entry("window", "test")
        isolated_log.assert_called_once()


class TestClassifyAndLogMessage:
    def test_uses_channel_hint_when_given(self, isolated_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        dil.classify_and_log_message("some content", channel_hint="comments-box")
        assert "[comments-box]" in dil.LOG_FILE.read_text()

    def test_infers_channel_when_no_hint(self, isolated_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.setattr(dil, "WAKE_HMAC_KEY", None)
        dil.classify_and_log_message("a plain window paste, no signature")
        assert "[window]" in dil.LOG_FILE.read_text()
