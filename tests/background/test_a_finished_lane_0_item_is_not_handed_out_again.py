"""A Lane 0 item whose finish is already on origin/main is not handed out again (F5).

The defect: a focus row outlives its finish because the seat re-derives focus every three hours and
still names it, so `a-site-control-stops-rewriting-a-tracked-feed` was drawn after `0df1dc405` had
finished it, and `the-qep-value-arms-are-retaken-at-origin-one-leg-at-a-time` was redrawn 16
minutes after its own delivery. `delivery_lane.finished_on_origin` now reads two statements of a
finish -- a `NEXT: ... direction item <id>, finished` trailer and a `--premise-spent` disposition --
and both draw loops skip on it.

The repo is REAL, with a real `refs/remotes/origin/main`: the property under test is "on origin, not
on a local ref", and a stubbed `_git` cannot tell those apart.
"""
from __future__ import annotations

import os
import subprocess
import time
from datetime import datetime, timezone

import pytest
import yaml

from background import delivery_lane as dl
from background import direction as d
from background import seat_continuation as sc
from background import seat_work_in_hand as claims_mod


@pytest.fixture()
def lane(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def git(*args):
        out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, env=env)
        assert out.returncode == 0, out.stderr
        return out.stdout.strip()

    def commit(message):
        git("commit", "-q", "--allow-empty", "-m", message)
        return git("rev-parse", "HEAD")

    git("init", "-q")
    commit("seed")
    monkeypatch.setattr(dl, "PROJECT_DIR", root)
    monkeypatch.setattr(claims_mod, "PROJECT_DIR", root)

    direction_path = tmp_path / "DIRECTION.yaml"
    map_path = tmp_path / "maturity_map.yaml"
    map_path.write_text(yaml.safe_dump([{"id": "EP1_real_atom", "level_current": 1}]),
                        encoding="utf-8")
    monkeypatch.setattr(dl, "MATURITY_MAP", map_path)
    monkeypatch.setattr(d, "DIRECTION_PATH", direction_path)
    monkeypatch.setattr(sc, "STORE", tmp_path / ".seat_continuation.json")
    monkeypatch.setattr(dl, "_live_holders", lambda: [])

    def focus(ids):
        direction_path.write_text(yaml.safe_dump({
            "version": 1, "oriented_at": datetime.now(timezone.utc).isoformat(),
            "focus": [{"id": i, "what": "do the thing", "why": "because"} for i in ids],
            "not_now": [{"what": "something", "why": "it loses to the above"}],
        }), encoding="utf-8")

    return {"git": git, "commit": commit, "focus": focus, "claims": tmp_path / "claims.json"}


def _drawn_an_hour_ago(lane, *ids):
    for i in ids:
        dl.record_draw(i, time.time() - 3600, path=lane["claims"])


def test_the_partition_finished_refused_unfinished_and_local_only_handed_out(lane):
    """One control over the whole partition, so a refusal that refuses EVERYTHING cannot pass.

    `named-not-finished` is the refuted retire-on-naming case (8dbb82c53): its id is on origin in
    a `NEXT:` line that hands it on. `local-only` carries a correct finished trailer on a commit
    origin does not have.

    MUTATION (seen red): make `finished_on_origin` ignore the trailer (return None after the
    premise leg) -- the refusal set empties and `finished` is handed out first.
    """
    ids = ("finished", "named-not-finished", "local-only")
    _drawn_an_hour_ago(lane, *ids)
    done = lane["commit"]("x\n\nNEXT: none -- direction item finished, finished")
    lane["commit"]("y\n\nNEXT: none -- direction item named-not-finished, handed on; leg 2 owed")
    lane["git"]("update-ref", "refs/remotes/origin/main", "HEAD")
    lane["commit"]("z\n\nNEXT: none -- direction item local-only, finished")

    verdicts = {i: dl.finished_on_origin({"id": i}, path=lane["claims"]) for i in ids}
    assert verdicts == {"finished": done, "named-not-finished": None, "local-only": None}

    lane["focus"](list(ids))
    handed = []
    while (item := dl.next_item(path=lane["claims"])) is not None:
        handed.append(item["id"])
        claims_mod.claim(item["id"], note="", paths=[], path=lane["claims"])
    assert handed == ["named-not-finished", "local-only"]
    assert [(i["id"], sha) for i, sha in dl.LAST_FINISHED_SKIPS] == [("finished", done)]


def test_the_refusal_names_its_sha_in_the_doorbell(lane):
    _drawn_an_hour_ago(lane, "finished", "next")
    done = lane["commit"]("x\n\nNEXT: none -- direction item finished, finished here")
    lane["git"]("update-ref", "refs/remotes/origin/main", "HEAD")
    lane["focus"](["finished", "next"])
    bell = dl.draw(path=lane["claims"], claim=False)
    assert "LANE 0 DELIVERY" in bell and "`finished` at " + done[:9] in bell


def test_a_finish_older_than_this_incarnation_does_not_count(lane):
    """A continuation's `written_at` is the window's edge: an id reused for new work after its old
    finish is handed out. Without the edge, one trailer would silence the id for ever."""
    lane["commit"]("x\n\nNEXT: none -- direction item reused, finished")
    lane["git"]("update-ref", "refs/remotes/origin/main", "HEAD")
    later = time.time() + 5
    assert dl.finished_on_origin({"id": "reused", "written_at": later}, path=lane["claims"]) is None
    assert dl.finished_on_origin({"id": "reused", "written_at": later - 3600},
                                 path=lane["claims"]) is not None


def test_a_premise_spent_disposition_on_origin_refuses_and_one_off_origin_does_not(lane):
    _drawn_an_hour_ago(lane, "spent", "spent-locally")
    on_origin = lane["commit"]("published")
    lane["git"]("update-ref", "refs/remotes/origin/main", "HEAD")
    local = lane["commit"]("local only")
    ledger_path = dl._ledger_path(lane["claims"])
    ledger = claims_mod._load(ledger_path)
    now = time.time()
    ledger["spent"]["premise_spent"] = {"commit": on_origin, "reason": "r", "at": now}
    ledger["spent-locally"]["premise_spent"] = {"commit": local, "reason": "r", "at": now}
    claims_mod._save(ledger, ledger_path)
    assert dl.finished_on_origin({"id": "spent"}, path=lane["claims"]) == on_origin
    assert dl.finished_on_origin({"id": "spent-locally"}, path=lane["claims"]) is None


def test_an_id_never_drawn_and_without_a_written_at_is_never_refused(lane):
    lane["commit"]("x\n\nNEXT: none -- direction item undrawn, finished")
    lane["git"]("update-ref", "refs/remotes/origin/main", "HEAD")
    assert dl.finished_on_origin({"id": "undrawn"}, path=lane["claims"]) is None
