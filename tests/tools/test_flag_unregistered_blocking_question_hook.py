"""Tests for .claude/hooks/flag_unregistered_blocking_question.py -- the
Stop-hook safety net for the [ACTION NEEDED] rule (root-caused 2026-07-11:
background/action_needed.py works correctly when called, but nothing
detects when the agent forgets to call it -- see the hook's own module
docstring for the full root-cause writeup)."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "flag_unregistered_blocking_question.py"

# Import as a module (not just subprocess) so the pure-logic functions
# (_last_assistant_text, the regex) can be unit-tested directly without
# any risk of a real send_ntfy() call.
_spec = importlib.util.spec_from_file_location("flag_hook", HOOK_PATH)
flag_hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(flag_hook)


def _write_transcript(tmp_path, entries: list[dict]) -> Path:
    path = tmp_path / "transcript.jsonl"
    with path.open("w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    return path


class TestLastAssistantText:
    def test_extracts_string_content(self, tmp_path):
        path = _write_transcript(tmp_path, [
            {"message": {"role": "user", "content": "hi"}},
            {"message": {"role": "assistant", "content": "the final answer"}},
        ])
        assert flag_hook._last_assistant_text(str(path)) == "the final answer"

    def test_extracts_list_of_text_blocks(self, tmp_path):
        path = _write_transcript(tmp_path, [
            {"message": {"role": "assistant", "content": [
                {"type": "text", "text": "part one"},
                {"type": "tool_use", "name": "Bash"},
                {"type": "text", "text": "part two"},
            ]}},
        ])
        assert flag_hook._last_assistant_text(str(path)) == "part one\npart two"

    def test_returns_last_assistant_message_not_first(self, tmp_path):
        path = _write_transcript(tmp_path, [
            {"message": {"role": "assistant", "content": "first"}},
            {"message": {"role": "user", "content": "reply"}},
            {"message": {"role": "assistant", "content": "second, the real last one"}},
        ])
        assert flag_hook._last_assistant_text(str(path)) == "second, the real last one"

    def test_missing_file_returns_none(self, tmp_path):
        assert flag_hook._last_assistant_text(str(tmp_path / "nope.jsonl")) is None

    def test_malformed_lines_skipped_not_crashed(self, tmp_path):
        path = tmp_path / "transcript.jsonl"
        path.write_text("not json\n" + json.dumps({"message": {"role": "assistant", "content": "ok"}}) + "\n")
        assert flag_hook._last_assistant_text(str(path)) == "ok"

    def test_unexpected_shape_does_not_crash(self, tmp_path):
        path = tmp_path / "transcript.jsonl"
        path.write_text(json.dumps({"something": "else entirely"}) + "\n")
        assert flag_hook._last_assistant_text(str(path)) is None


class TestBlockingPhraseRegex:
    def test_matches_awaiting_your_steer(self):
        assert flag_hook._BLOCKING_PHRASE_RE.search("Awaiting your steer on this.")

    def test_matches_your_call(self):
        assert flag_hook._BLOCKING_PHRASE_RE.search("that's your call")

    def test_matches_case_insensitively(self):
        assert flag_hook._BLOCKING_PHRASE_RE.search("YOUR STEER needed")

    def test_does_not_match_normal_text(self):
        assert not flag_hook._BLOCKING_PHRASE_RE.search("All tests pass, committed and pushed.")

    def test_does_not_match_unrelated_question(self):
        assert not flag_hook._BLOCKING_PHRASE_RE.search("What time is it in London?")


class TestRegisterRecentlyTouched:
    def test_false_when_file_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr(flag_hook, "REGISTER_FILE", tmp_path / "nope.json")
        assert flag_hook._register_recently_touched() is False

    def test_true_when_just_written(self, monkeypatch, tmp_path):
        f = tmp_path / "register.json"
        f.write_text("{}")
        monkeypatch.setattr(flag_hook, "REGISTER_FILE", f)
        assert flag_hook._register_recently_touched() is True

    def test_false_when_old(self, monkeypatch, tmp_path):
        import os
        f = tmp_path / "register.json"
        f.write_text("{}")
        old = 1000000000  # far in the past
        os.utime(f, (old, old))
        monkeypatch.setattr(flag_hook, "REGISTER_FILE", f)
        assert flag_hook._register_recently_touched() is False


class TestMainDoesNotSendWhenNotWarranted:
    def test_no_send_when_no_blocking_phrase(self, tmp_path, monkeypatch, capsys):
        path = _write_transcript(tmp_path, [
            {"message": {"role": "assistant", "content": "All done, committed and pushed."}},
        ])
        monkeypatch.setattr(sys, "stdin", _FakeStdin(json.dumps({"transcript_path": str(path)})))
        with patch("background.ntfy_utils.send_ntfy") as mock_send:
            flag_hook.main()
            mock_send.assert_not_called()

    def test_no_send_when_register_recently_touched(self, tmp_path, monkeypatch):
        path = _write_transcript(tmp_path, [
            {"message": {"role": "assistant", "content": "Awaiting your steer on this."}},
        ])
        register = tmp_path / "register.json"
        register.write_text("{}")
        monkeypatch.setattr(flag_hook, "REGISTER_FILE", register)
        monkeypatch.setattr(sys, "stdin", _FakeStdin(json.dumps({"transcript_path": str(path)})))
        with patch("background.ntfy_utils.send_ntfy") as mock_send:
            flag_hook.main()
            mock_send.assert_not_called()


class _FakeStdin:
    def __init__(self, text: str):
        self._text = text

    def read(self):
        return self._text


class TestHookSubprocessRobustness:
    """Subprocess-based, matching the existing hook test convention --
    only cases that structurally CANNOT trigger a real send (malformed
    input, missing transcript_path, benign text)."""

    def _run(self, payload_str: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=payload_str,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )

    def test_exits_zero_for_malformed_json(self):
        assert self._run("not json").returncode == 0

    def test_exits_zero_for_missing_transcript_path(self):
        assert self._run(json.dumps({"session_id": "abc"})).returncode == 0

    def test_exits_zero_for_nonexistent_transcript_file(self):
        result = self._run(json.dumps({"transcript_path": "/nonexistent/path.jsonl"}))
        assert result.returncode == 0


class TestDebugLog:
    """2026-07-11, director-flagged: the hook never visibly fired despite a
    clear trigger match on a real turn, and the broad except-Exception-pass
    made a silent crash indistinguishable from "ran fine, decided not to
    fire". This log closes that observability gap."""

    def test_logs_every_invocation(self, tmp_path, monkeypatch):
        log_file = tmp_path / "debug.log"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        flag_hook._debug_log("test entry")
        assert "test entry" in log_file.read_text()

    def test_logs_are_timestamped(self, tmp_path, monkeypatch):
        log_file = tmp_path / "debug.log"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        flag_hook._debug_log("test entry")
        content = log_file.read_text()
        assert content.startswith("[20")  # a real timestamp, not a bare line

    def test_appends_not_overwrites(self, tmp_path, monkeypatch):
        log_file = tmp_path / "debug.log"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        flag_hook._debug_log("first")
        flag_hook._debug_log("second")
        content = log_file.read_text()
        assert "first" in content
        assert "second" in content

    def test_rotates_at_max_lines(self, tmp_path, monkeypatch):
        log_file = tmp_path / "debug.log"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_MAX_LINES", 5)
        for i in range(10):
            flag_hook._debug_log(f"entry {i}")
        lines = [l for l in log_file.read_text().splitlines() if l.strip()]
        assert len(lines) == 5
        assert "entry 9" in lines[-1]
        assert "entry 0" not in log_file.read_text()

    def test_never_raises_even_if_write_fails(self, monkeypatch):
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", Path("/nonexistent_dir_xyz/debug.log"))
        flag_hook._debug_log("this must not raise")  # no exception = pass


class TestMainLogsOutcomes:
    def test_logs_phrase_match_before_sending(self, tmp_path, monkeypatch):
        path = _write_transcript(tmp_path, [
            {"message": {"role": "assistant", "content": "Awaiting your steer on this."}},
        ])
        log_file = tmp_path / "debug.log"
        register = tmp_path / "register.json"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        monkeypatch.setattr(flag_hook, "REGISTER_FILE", register)
        monkeypatch.setattr(sys, "stdin", _FakeStdin(json.dumps({"transcript_path": str(path)})))
        with patch("background.ntfy_utils.send_ntfy", return_value="fake-id") as mock_send:
            flag_hook.main()
            mock_send.assert_called_once()
        content = log_file.read_text()
        assert "phrase match" in content
        assert "sent advisory ntfy" in content

    def test_logs_no_match_reason(self, tmp_path, monkeypatch):
        path = _write_transcript(tmp_path, [
            {"message": {"role": "assistant", "content": "All done, nothing pending."}},
        ])
        log_file = tmp_path / "debug.log"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        monkeypatch.setattr(sys, "stdin", _FakeStdin(json.dumps({"transcript_path": str(path)})))
        flag_hook.main()
        assert "no phrase match" in log_file.read_text()

    def test_logs_malformed_json_reason(self, tmp_path, monkeypatch):
        log_file = tmp_path / "debug.log"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        monkeypatch.setattr(sys, "stdin", _FakeStdin("not json"))
        flag_hook.main()
        assert "not valid JSON" in log_file.read_text()

    def test_real_transcript_shape_one_block_per_entry(self, tmp_path, monkeypatch):
        """The actual live transcript format: each content block (thinking/
        text/tool_use) is its own JSONL entry, not bundled in one message's
        content list -- confirmed by inspecting the real session transcript
        this session. Regression guard against the assumption gap."""
        path = tmp_path / "real_shape.jsonl"
        entries = [
            {"message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "x", "signature": "y"}]}},
            {"message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Bash", "input": {}}]}},
            {"message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}},
            {"message": {"role": "assistant", "content": [{"type": "text", "text": "awaiting your call on this."}]}},
        ]
        with path.open("w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        log_file = tmp_path / "debug.log"
        register = tmp_path / "register.json"
        monkeypatch.setattr(flag_hook, "DEBUG_LOG_FILE", log_file)
        monkeypatch.setattr(flag_hook, "REGISTER_FILE", register)
        monkeypatch.setattr(sys, "stdin", _FakeStdin(json.dumps({"transcript_path": str(path)})))
        with patch("background.ntfy_utils.send_ntfy", return_value="fake-id") as mock_send:
            flag_hook.main()
            mock_send.assert_called_once()
