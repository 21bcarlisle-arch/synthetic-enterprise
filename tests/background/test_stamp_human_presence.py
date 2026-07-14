"""Tests for .claude/hooks/stamp_human_presence.py -- the UserPromptSubmit hook
that records genuine human keystroke recency so tmux_relay._director_present()
can self-expire (2026-07-14, director: "presence must AUTO-EXPIRE after N minutes
without human keystrokes")."""
import importlib.util
import io
from pathlib import Path

import pytest

_HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "stamp_human_presence.py"


def _load(monkeypatch, tmp_path, stdin_text):
    """Load a fresh copy of the hook module with an isolated stamp file and the
    given stdin payload, then run main()."""
    spec = importlib.util.spec_from_file_location("stamp_human_presence_under_test", _HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    stamp = tmp_path / ".human_last_input"
    monkeypatch.setattr(mod, "_STAMP", stamp)
    monkeypatch.setattr(mod.sys, "stdin", io.StringIO(stdin_text))
    mod.main()
    return stamp


def test_human_prompt_stamps_presence(monkeypatch, tmp_path):
    stamp = _load(monkeypatch, tmp_path, '{"prompt": "please release the hold and get building"}')
    assert stamp.is_file()
    assert stamp.read_text().strip().isdigit()  # an epoch second


def test_supervisor_injected_turn_does_not_stamp(monkeypatch, tmp_path):
    """The machine's own injected turns must NEVER refresh presence -- else the
    autonomous loop's own grants would latch the hold forever (the self-
    refreshing-signal disease)."""
    stamp = _load(monkeypatch, tmp_path, '{"prompt": "[SUPERVISOR: turn granted -- self-refill from maturity map ..."}')
    assert not stamp.exists()


def test_resume_instruction_does_not_stamp(monkeypatch, tmp_path):
    stamp = _load(monkeypatch, tmp_path, '{"prompt": "Session resuming after crash or usage-limit reset. Run this recovery ..."}')
    assert not stamp.exists()


def test_ntfy_relayed_human_message_does_stamp(monkeypatch, tmp_path):
    """An NTFY relay carries a genuine human message (director's phone); the
    daemon marker sits at the END, so it correctly counts as human presence."""
    stamp = _load(monkeypatch, tmp_path,
                  '{"prompt": "what is the margin? [Received via NTFY from Rich\'s phone ...]"}')
    assert stamp.is_file()


def test_malformed_stdin_never_raises(monkeypatch, tmp_path):
    """A hook must never disrupt the session -- garbage stdin is swallowed."""
    stamp = _load(monkeypatch, tmp_path, "not json at all")
    # non-JSON is treated as raw prompt text (a human typed it) -> stamps, no raise
    assert stamp.is_file()
