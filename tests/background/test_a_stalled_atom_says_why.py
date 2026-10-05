"""A drawn-and-stalled atom carries the reason it has not moved, and the seat's brief prints it.

SEAT_FINDING_A_STALLED_FOCUS_ATOM_WAS_DRAWN_AS_A_TRAILING_LINE_AND_B11_MOVED_UNDER_OTHER_IDS_2026-10-05:
B11 and D48 sat at 151 unchanged draws for opposite reasons -- B11 landed twice on its own scope
under Lane 0 slugs, D48's scope file never existed -- and the only witness was the count.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone

import pytest

from background import delivery_seat, supervisor

MOVED_FP = "0|3|build|1|None"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(root), "config", k, v], check=True)
    monkeypatch.setattr(supervisor, "PROJECT_DIR", root)
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".atom_stall_tracker.json")
    a_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    _commit(root, "README", "seed",
            env={**os.environ, "GIT_COMMITTER_DATE": a_day_ago, "GIT_AUTHOR_DATE": a_day_ago})
    return root


def _commit(root, rel, subject, env=None):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(subject)
    subprocess.run(["git", "-C", str(root), "add", rel], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", subject], check=True, env=env)


def _draw_twice(atom):
    supervisor._record_atom_draw_and_check_stall(atom["id"], MOVED_FP, atom=atom)
    return supervisor._record_atom_draw_and_check_stall(atom["id"], MOVED_FP, atom=atom)


def _row(atom_id):
    return json.loads(supervisor.ATOM_STALL_STATE_FILE.read_text())[atom_id]


def test_every_reason_branch_is_reachable_and_names_what_it_saw(repo):
    """The partition control first: all three readings are reachable on real git, so a reader that
    returned one of them for everything would red here."""
    _commit(repo, "company/b11.py", "B11 slice landed under a Lane 0 slug")
    landed = {"id": "B11", "file_scope": ["company/b11.py"], "level_current": 0,
              "loop_stage": "build"}
    unbuilt = {"id": "D48", "file_scope": ["company/d48.py", "tests/test_d48.py"]}
    unscoped = {"id": "U"}
    reasons = {}
    for atom in (landed, unbuilt, unscoped):
        # the episode began before the commit, so the B11 commit is inside its window
        supervisor._record_atom_draw_and_check_stall(atom["id"], MOVED_FP, atom=atom)
        state = json.loads(supervisor.ATOM_STALL_STATE_FILE.read_text())
        state[atom["id"]]["episode_started_at"] -= 3600
        supervisor.ATOM_STALL_STATE_FILE.write_text(json.dumps(state))
        stalled, _ = supervisor._record_atom_draw_and_check_stall(atom["id"], MOVED_FP, atom=atom)
        assert stalled
        reasons[atom["id"]] = _row(atom["id"])["stop_reason"]
    assert "1 commit(s) landed on its file_scope" in reasons["B11"]
    assert "B11 slice landed under a Lane 0 slug" in reasons["B11"]
    assert "level 0, build" in reasons["B11"]
    assert "no commit touched its file_scope" in reasons["D48"]
    assert "0 of 2 scope path(s) exist on disk" in reasons["D48"]
    assert "no file_scope declared" in reasons["U"]


def test_the_window_is_the_streak_not_all_history(repo):
    """A commit from before the streak began is not evidence about the streak."""
    an_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    _commit(repo, "company/b11.py", "an old slice",
            env={**os.environ, "GIT_COMMITTER_DATE": an_hour_ago, "GIT_AUTHOR_DATE": an_hour_ago})
    atom = {"id": "B11", "file_scope": ["company/b11.py"]}
    _draw_twice(atom)
    reason = _row("B11")["stop_reason"]
    assert "no commit touched its file_scope" in reason and "when the streak began" in reason
    assert "1 of 1 scope path(s) exist on disk" in reason


def test_a_streak_older_than_its_start_field_says_its_window_is_a_guess(repo):
    atom = {"id": "D48", "file_scope": ["company/d48.py"]}
    supervisor.ATOM_STALL_STATE_FILE.write_text(json.dumps({"D48": {
        "fingerprint": MOVED_FP, "consecutive_unchanged": 151, "stalled": True}}))
    supervisor._record_atom_draw_and_check_stall("D48", MOVED_FP, atom=atom)
    row = _row("D48")
    assert row["consecutive_unchanged"] == 152
    assert row["episode_started_at"] is None
    assert "the streak's start is unrecorded" in row["stop_reason"]


def test_an_unstalled_draw_and_a_closed_episode_carry_no_reason(repo):
    atom = {"id": "B11", "file_scope": ["company/b11.py"]}
    supervisor._record_atom_draw_and_check_stall("B11", MOVED_FP, atom=atom)
    assert "stop_reason" not in _row("B11")
    _draw_twice(atom)
    assert "stop_reason" in _row("B11")
    supervisor._record_atom_draw_and_check_stall("B11", "1|3|build|1|None", atom=atom)  # it moved
    assert "stop_reason" not in _row("B11")


def test_an_unreadable_git_says_it_cannot_say(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path)       # not a repository
    reason = supervisor._atom_stop_reason({"id": "D48", "file_scope": ["x.py"]}, None, 0.0)
    assert reason.endswith("-- cannot say")


def test_the_brief_prints_the_reason_beside_the_atom(repo):
    _draw_twice({"id": "D48", "file_scope": ["company/d48.py"]})
    supervisor._record_atom_draw_and_check_stall("B7", MOVED_FP, atom={"id": "B7"})  # not stalled
    since = datetime.now(timezone.utc) - timedelta(hours=3)
    rows = delivery_seat.atoms_stalled_with_reason(since)
    assert [r["id"] for r in rows] == ["D48"]
    assert "0 of 1 scope path(s) exist on disk" in rows[0]["stop_reason"]
    later = delivery_seat.atoms_stalled_with_reason(datetime.now(timezone.utc) + timedelta(hours=1))
    assert later == []
    prompt = delivery_seat._prompt({"atoms_stalled_with_reason": rows})
    assert "- D48 (2 unchanged draws): no commit touched its file_scope" in prompt
