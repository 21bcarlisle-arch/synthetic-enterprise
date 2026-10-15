"""`benign` on the census answers ONE question, and two carriers were failing a different one.

THE CENSUS'S `benign` VERDICT MEANS: no write to this file can SHORTEN an episode. It is not a clean
bill of health. `.sent_ntfy_ids.json` and `.notify_transitions.json` were both correctly benign --
neither carries an episode-scoped field -- and both conflated ABSENT with PRESENT-BUT-UNREADABLE,
which is a different defect with a different consequence. Measured 2026-09-04:

    _read_transitions
        null                 -> None, out of a function annotated `-> dict`

The sent-ids half of this file (record_sent_id wrote a one-entry list over an unreadable record of
every id we had sent) was deleted on 2026-10-15 with the carrier: its only reader was the inbound
NTFY responder, retired by the director's mothball steer, and a record nobody reads has no failure
left to control. The measurement and its legs are in git history before that commit.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from background import notify as notify_mod  # noqa: E402

UNREADABLE = pytest.mark.parametrize("raw", [
    pytest.param('["a", "b"', id="truncated"),
    pytest.param("", id="empty-file"),
    pytest.param("null", id="json-null"),
    pytest.param('{"a": 1}', id="a-mapping"),
    pytest.param('"abc"', id="a-bare-string"),
])


@UNREADABLE
def test_the_transition_memory_always_returns_a_dict(tmp_path, monkeypatch, raw):
    """MUTATION: drop the `isinstance(loaded, dict)` screen and `null` returns None from a
    function annotated `-> dict`, one `.get` away from every caller. `-> dict` is not
    enforcement, which is the same lesson `episode_prior` was built on."""
    p = tmp_path / ".notify_transitions.json"
    p.write_text(raw)
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", p)
    assert isinstance(notify_mod._read_transitions(), dict)


def test_the_transition_memory_reaches_a_different_answer_when_readable(tmp_path, monkeypatch):
    """REACHABILITY: `isinstance(x, dict)` is satisfied by a function that returns `{}` always."""
    p = tmp_path / ".notify_transitions.json"
    p.write_text(json.dumps({"k": {"state": "RED", "ts": 1.0}}))
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", p)
    assert notify_mod._read_transitions()["k"]["state"] == "RED"
