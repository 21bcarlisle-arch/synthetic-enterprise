"""The promote route binds its own landing, and only a landing that actually pushed.

THE DEFECT THESE LEGS EXIST FOR (2026-09-05, measured on the delivery lane's own draw).
`52b51bb22` and `f994aa6fb` repaired the claim store and reached `origin/main`; nobody ran
`delivery_lane --landed` for either, so the claim still read `paths: []`, the lane had no evidence
the work had moved, and the item was re-offered at 09:06Z to a fresh seat that spent its turn
rediscovering finished work. The binding cannot be added afterwards -- `record_landing` refuses a
commit older than the id's first draw -- so a step that has to be REMEMBERED on every landing turn
is a step that is permanently lost when it is missed.

The two properties, and each has a leg that fails when it is broken:

  * a verified push binds that commit's paths to `--work-id`;
  * a promotion that never pushed binds NOTHING -- a binding is evidence work reached origin, and
    writing one for a refused promotion tells the lane a claim is moving when it is not.

`_refuse_if_ungated` is the one refusal stubbed out here: it shells into the whole `surgical_land
--verify` gate, which is a different subject with its own controls, and it fires before anything
this file is about.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))

from background import delivery_lane, seat_work_in_hand  # noqa: E402
from tools import promote_worktree_landing as promote_mod  # noqa: E402

WORK_ID = "a-promotion-binds-its-own-landing"


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=T", *args],
        cwd=str(cwd), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, f"git {' '.join(args)}: {proc.stderr}"
    return proc.stdout.strip()


@pytest.fixture()
def world(tmp_path, monkeypatch):
    """A real bare remote, a real clone with a real unpushed commit, and temp claim stores.

    Real git throughout: the subject is what happens either side of an actual `git push`, and a
    stubbed push could not tell a binding written before it from one written after.
    """
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "--bare", "--initial-branch=main", "--quiet", str(remote))

    work = tmp_path / "work"
    _git(tmp_path, "clone", "--quiet", str(remote), str(work))
    _git(work, "checkout", "--quiet", "-b", "main")
    (work / "base.txt").write_text("base\n")
    _git(work, "add", "base.txt")
    _git(work, "commit", "--quiet", "-m", "base")
    _git(work, "push", "--quiet", "origin", "HEAD:main")

    (work / "delivered.txt").write_text("the landing\n")
    _git(work, "add", "delivered.txt")
    _git(work, "commit", "--quiet", "-m", "the landing")

    store = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", store)
    monkeypatch.setattr(delivery_lane, "PROJECT_DIR", work)
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "seat_claims.json")
    monkeypatch.setattr(promote_mod, "_refuse_if_ungated", lambda worktree, commit: None)
    return {"remote": remote, "work": work, "store": store, "tmp": tmp_path}


def _claim(store: Path, *, age_seconds: float = 120.0) -> None:
    """Claim WORK_ID a couple of minutes ago, so the commit under test is newer than the first draw.

    `record_landing` compares the commit's own timestamp against the claim, and a claim made in
    the same whole second as the commit is refused as older work -- a real property of the lane,
    and not the one these legs are about.

    TWO MINUTES AND NOT AN HOUR, because `refuse_if_duplicated` sweeps every store it reads with
    `seat_work_in_hand`'s own 45-minute deadline rather than the delivery lane's 100. An hour-old
    claim is swept out from under the promotion by the duplication check itself, and the leg then
    fails with a KeyError that says nothing about binding.
    """
    seat_work_in_hand.claim(WORK_ID, "under test", path=store, now=time.time() - age_seconds)


def test_a_verified_push_binds_that_commits_paths_to_the_claim(world):
    _claim(world["store"])
    result = promote_mod.promote(world["work"], work_id=WORK_ID)

    assert result["pushed"] is True
    assert result["bound"] == ["delivered.txt"], result["binding"]
    assert "delivered.txt" in result["binding"]
    # The store, not the return value: the lane reads the claim, and a binding that lived only in
    # this process is the unbound landing again wearing a receipt.
    held = seat_work_in_hand._load(world["store"])[WORK_ID]["paths"]
    assert held == ["delivered.txt"], held


def test_a_promotion_that_never_pushed_binds_nothing(world):
    _claim(world["store"])
    # A rival lands on the remote first, so the fast-forward refusal fires AFTER the claim exists
    # and BEFORE any push of ours. Nothing of ours reached origin, so nothing may be bound.
    rival = world["tmp"] / "rival"
    _git(world["tmp"], "clone", "--quiet", str(world["remote"]), str(rival))
    (rival / "rival.txt").write_text("theirs\n")
    _git(rival, "add", "rival.txt")
    _git(rival, "commit", "--quiet", "-m", "rival")
    _git(rival, "push", "--quiet", "origin", "HEAD:main")

    with pytest.raises(promote_mod.PromotionRefused):
        promote_mod.promote(world["work"], work_id=WORK_ID)

    assert seat_work_in_hand._load(world["store"])[WORK_ID]["paths"] == []


def test_a_dry_run_binds_nothing(world):
    _claim(world["store"])
    result = promote_mod.promote(world["work"], work_id=WORK_ID, dry_run=True)

    assert result["pushed"] is False
    assert result["bound"] == []
    assert seat_work_in_hand._load(world["store"])[WORK_ID]["paths"] == []


def test_an_unbindable_claim_does_not_refuse_a_promotion_that_pushed(world):
    """No claim at all: the push still succeeds and the reason is named, not swallowed.

    Binding is doing the work, not a gate on it. Refusing here would put a new refusal on the
    seat's own delivery path, and the failure mode -- a landing stuck in a worktree because the
    claim was swept -- is worse than the one it would catch.
    """
    result = promote_mod.promote(world["work"], work_id=WORK_ID)

    assert result["pushed"] is True
    assert result["bound"] == []
    assert "NOT CLAIMED" in result["binding"]
    assert WORK_ID in result["binding"]


def test_a_promotion_with_no_work_id_says_so_rather_than_binding_silently(world):
    result = promote_mod.promote(world["work"])

    assert result["pushed"] is True
    assert result["bound"] == []
    assert "--work-id" in result["binding"]
