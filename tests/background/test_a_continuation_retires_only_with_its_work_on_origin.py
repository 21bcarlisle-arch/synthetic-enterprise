"""A continuation retires only when origin/main holds its work, or a successor holds the rest.

THE N16 SHAPE. A tick bound a landing from its worktree, its `surgical_land` died, nothing reached
origin, and `--release` retired the continuation anyway, which stranded the N15/N16 rows on the
shared tree through the outage. Three instances in two stretches. The release is the tick's belief
and origin is the fact, so `retire` now asks `delivery_lane.focus_tombstone_refusal`, the same test
focus rows already pass through.

ONE CONTROL OVER THE WHOLE PARTITION, because a guard that refuses everything passes every refusing
leg: the unpromoted id is held and names why, the promoted id retires, and the superseded id
retires with nothing on origin.
"""
from __future__ import annotations

import json
import os
import subprocess

from background import delivery_lane, seat_continuation

STRANDED = "n16-a-continuation-whose-surgical-land-died"
PROMOTED = "a-continuation-whose-landing-reached-origin"
HANDED_ON = "a-continuation-whose-rest-a-successor-holds"


def _repo(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args, when=None):
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ["PATH"]}
        if when:
            env.update(GIT_AUTHOR_DATE=f"@{when}", GIT_COMMITTER_DATE=f"@{when}")
        return subprocess.run(("git", *args), cwd=repo, check=True, text=True,
                              capture_output=True, env=env).stdout.strip()

    git("init", "-q")
    monkeypatch.setattr(delivery_lane, "PROJECT_DIR", repo)
    return git


def _setup(tmp_path, monkeypatch):
    git = _repo(tmp_path, monkeypatch)
    git("commit", "-q", "--allow-empty", "-m", f"the landing\n\nNEXT: {PROMOTED}", when=1_700_000_000)
    git("update-ref", delivery_lane.PUBLISHED_REF, "HEAD")
    # The worktree commit that `--landed` bound but that never left: the door died before promote.
    git("commit", "-q", "--allow-empty", "-m", f"NEXT: {STRANDED}", when=1_700_000_100)

    store = tmp_path / "continuations.json"
    monkeypatch.setattr(seat_continuation, "STORE", store)
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda *a, **k: [])
    claims = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", claims)
    monkeypatch.setattr(delivery_lane, "current_orientation", lambda *a, **k: "o1")
    claims.with_suffix(".draws.json").write_text(json.dumps({
        STRANDED: {"first_drawn_at": 1.0, "last_drawn_at": 1.0, "last_landing_at": 1_700_000_100},
        PROMOTED: {"first_drawn_at": 1.0, "last_drawn_at": 1.0, "last_landing_at": 1_700_000_000},
    }))
    rows = [{"id": i, "what": "w", "why": "y", "done_means": "d", "written_at": 1.0}
            for i in (STRANDED, PROMOTED, HANDED_ON)]
    rows.append({"id": "the-successor", "what": "the rest", "why": "y", "done_means": "d",
                 "written_at": 2.0, "supersedes": [HANDED_ON]})
    seat_continuation._save(rows, store)
    return git, store


def test_the_N16_shape_is_HELD_naming_why_and_a_promoted_or_handed_on_id_RETIRES(
        tmp_path, monkeypatch, capsys):
    """MUTATION: drop the `origin_refusal` leg from `retire` and the stranded id retires (leg 1);
    make `origin_refusal` always refuse and legs 2 and 3 fail."""
    _, store = _setup(tmp_path, monkeypatch)

    outcomes = tuple(delivery_lane.retire_continuation(i) for i in (STRANDED, PROMOTED, HANDED_ON))
    assert outcomes == (False, True, True), outcomes

    retired = {i["id"] for i in seat_continuation.retired(store)}
    assert retired == {PROMOTED, HANDED_ON}
    held = next(i for i in json.loads(store.read_text()) if i["id"] == STRANDED)
    reason = held["retire_held"]["reason"]
    assert "no commit on origin/main binds it" in reason and f"--supersedes {STRANDED}" in reason
    assert f"did NOT retire the continuation {STRANDED}" in capsys.readouterr().out
    # The stranded row stays offered, which is the point: the next tick redraws it.
    assert STRANDED in {i["id"] for i in seat_continuation.live(now=2.0, path=store)}


def test_the_hold_is_a_reading_so_promoting_the_landing_lets_the_same_release_retire(
        tmp_path, monkeypatch):
    git, store = _setup(tmp_path, monkeypatch)
    assert seat_continuation.retire(STRANDED, path=store) is False
    git("update-ref", delivery_lane.PUBLISHED_REF, "HEAD")
    assert seat_continuation.held_reason(STRANDED, path=store) is None
    assert seat_continuation.retire(STRANDED, path=store) is True


def test_an_origin_probe_that_cannot_answer_HOLDS(tmp_path):
    def broken(_id):
        raise OSError("git gone")
    reason = seat_continuation.origin_refusal({"id": "x"}, [], origin_evidence=broken)
    assert reason and "could not be asked" in reason
