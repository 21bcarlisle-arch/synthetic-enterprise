"""The idle-but-healthy heartbeat made a commit on main every thirty minutes (director, 2026-10-04).

THE DEFECT. `_refresh_published_liveness_on_skip` committed `site/data/tick_heartbeat.json` and
`docs/observability/agent_status.json` to main and pushed them, so that a healthy machine whose
output had not changed still showed a fresh heartbeat. Over the fortnight measured that was 199
non-merge commits carrying nothing but runtime state -- 185 of 890 first-parent advances of
origin/main (21%) -- every one of which other lanes had to merge around, and each one touching
`site/` also redeployed the whole site.

THE PROPERTY, keyed to what main is rather than to today's commit count: a heartbeat publish on a
SKIP leaves origin/main, the local HEAD and the index exactly as they were -- AND it does reach
its readers, in the private ops repo and on origin's parentless `liveness` branch. The second half
is the rare-branch rule: a function that does nothing passes the first half perfectly.

REAL GIT, NOT A STUB: a bare origin and a clone of it, so `refs/heads/main` on the remote is the
thing asked. Only the ops repo's `commit_and_push` is injected, because `ops_repo` refuses any
test process outright by design and its own behaviour is its own tests' subject.
"""
from __future__ import annotations

import json
import subprocess
from functools import partial
from pathlib import Path

import pytest

import background.process_run_complete as prc


def _git(*args, cwd):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


@pytest.fixture
def world(tmp_path, monkeypatch):
    seed = tmp_path / "seed"
    seed.mkdir()
    _git("init", "-q", "-b", "main", cwd=seed)
    _git("config", "user.email", "t@example.invalid", cwd=seed)
    _git("config", "user.name", "T", cwd=seed)
    for rel in prc.LIVENESS_SURFACE_FILES:
        (seed / rel).parent.mkdir(parents=True, exist_ok=True)
        (seed / rel).write_text('{"ts": 0}\n')
    _git("add", "-A", cwd=seed)
    _git("commit", "-q", "-m", "seed", cwd=seed)
    origin = tmp_path / "origin.git"
    _git("clone", "-q", "--bare", str(seed), str(origin), cwd=tmp_path)
    clone = tmp_path / "clone"
    _git("clone", "-q", str(origin), str(clone), cwd=tmp_path)
    _git("config", "user.email", "t@example.invalid", cwd=clone)
    _git("config", "user.name", "T", cwd=clone)

    # RESIDENT seat through the production discriminator, as the sibling seat-guard tests do.
    home = tmp_path / "home"
    marker = home / ".config" / "synthetic-enterprise" / ".env.ntfy"
    marker.parent.mkdir(parents=True)
    marker.write_text("SE_NTFY_TOPIC=not-a-real-secret\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("SE_SEAT", raising=False)

    # The on-disk heartbeat has moved since the last commit -- the state the beat exists for.
    for rel in prc.LIVENESS_SURFACE_FILES:
        (clone / rel).write_text('{"ts": 1234, "fresh": true}\n')

    ops = tmp_path / "ops"
    ops_commits = []
    monkeypatch.setattr(prc, "PROJECT_DIR", clone)
    monkeypatch.setattr(prc, "LIVENESS_LAST_PUSH_FILE", tmp_path / ".liveness_last_push.json")
    monkeypatch.setattr(prc, "_publish_liveness_to_ops", partial(
        prc._publish_liveness_to_ops, ops_dir=ops,
        commit=lambda rels, msg: ops_commits.append(rels)))
    monkeypatch.setattr(prc, "_publish_liveness_branch", partial(
        prc._publish_liveness_branch, cwd=clone))
    records = []
    monkeypatch.setattr(prc, "_record_liveness_surface_publish",
                        lambda label, sha: records.append(("publish", sha)))
    monkeypatch.setattr(prc, "_record_liveness_surface_refusal",
                        lambda label, cause, evidence, git_hash: records.append(
                            ("refusal", evidence)))
    return {"clone": clone, "origin": origin, "ops": ops, "ops_commits": ops_commits,
            "records": records}


def _main_state(w):
    return (_git("rev-parse", "refs/heads/main", cwd=w["origin"]),
            _git("rev-parse", "HEAD", cwd=w["clone"]),
            _git("diff", "--cached", "--name-only", cwd=w["clone"]))


def test_a_due_heartbeat_makes_no_commit_on_main_and_does_reach_both_readers(world):
    before = _main_state(world)

    assert prc._refresh_published_liveness_on_skip("abc123") is True, world["records"]

    assert _main_state(world) == before, "the heartbeat moved main, HEAD or the index"
    # ...and the working-tree copies are still dirty, i.e. NOT swept into any commit.
    assert set(_git("diff", "--name-only", cwd=world["clone"]).split()) == set(
        prc.LIVENESS_SURFACE_FILES)

    # THE RARE BRANCH: it did publish. Ops copy, byte-for-byte, and the commit asked for.
    for rel in prc.LIVENESS_SURFACE_FILES:
        name = Path(rel).name
        assert (world["ops"] / "liveness" / name).read_text() == (world["clone"] / rel).read_text()
    assert world["ops_commits"] == [["liveness/tick_heartbeat.json", "liveness/agent_status.json"]]

    # The public branch: one parentless commit whose whole tree is the heartbeat.
    tip = _git("rev-parse", "refs/heads/liveness", cwd=world["origin"])
    assert _git("rev-list", "--count", tip, cwd=world["origin"]) == "1"
    assert _git("ls-tree", "--name-only", tip, cwd=world["origin"]) == "tick_heartbeat.json"
    shown = json.loads(_git("show", tip + ":tick_heartbeat.json", cwd=world["origin"]))
    assert shown == {"ts": 1234, "fresh": True}
    unrelated = subprocess.run(["git", "merge-base", tip, "refs/heads/main"],
                               cwd=str(world["origin"]), capture_output=True, text=True)
    assert unrelated.returncode == 1, "the liveness commit shares history with main"
    assert world["records"] == [("publish", tip)]


def test_a_second_beat_replaces_the_branch_rather_than_growing_it(world, monkeypatch):
    assert prc._refresh_published_liveness_on_skip("a") is True
    (world["clone"] / "site/data/tick_heartbeat.json").write_text('{"ts": 5678}\n')
    monkeypatch.setattr(prc, "_liveness_due", lambda: True)
    assert prc._refresh_published_liveness_on_skip("b") is True
    tip = _git("rev-parse", "refs/heads/liveness", cwd=world["origin"])
    assert _git("rev-list", "--count", tip, cwd=world["origin"]) == "1"
    assert json.loads(_git("show", tip + ":tick_heartbeat.json", cwd=world["origin"])) == {
        "ts": 5678}


def test_inside_the_throttle_nothing_is_written_anywhere(world):
    """The partition's other side, on the same world: the first beat lands, the second is
    throttled by the heartbeat's OWN clock and writes nothing."""
    assert prc._refresh_published_liveness_on_skip("a") is True
    tip = _git("rev-parse", "refs/heads/liveness", cwd=world["origin"])
    (world["clone"] / "site/data/tick_heartbeat.json").write_text('{"ts": 9}\n')
    assert prc._refresh_published_liveness_on_skip("b") is False
    assert _git("rev-parse", "refs/heads/liveness", cwd=world["origin"]) == tip
    assert len(world["ops_commits"]) == 1


def test_a_refused_branch_push_is_named_and_still_leaves_main_alone(world, monkeypatch):
    _git("remote", "set-url", "origin", str(world["clone"].parent / "no-such.git"),
         cwd=world["clone"])
    before = _git("rev-parse", "HEAD", cwd=world["clone"])
    assert prc._refresh_published_liveness_on_skip("abc") is False
    assert _git("rev-parse", "HEAD", cwd=world["clone"]) == before
    (kind, evidence), = world["records"]
    assert kind == "refusal" and "liveness branch:" in evidence, world["records"]
    # The ops leg is independent of the public one and still landed.
    assert world["ops_commits"]
