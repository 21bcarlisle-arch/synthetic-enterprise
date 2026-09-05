"""The push that puts a landing on `origin/main` is also what binds it to its claim.

THE DEFECT (2026-09-05, measured, one whole turn). `52b51bb22` and `f994aa6fb` repaired the claim
store at 08:29Z/08:34Z and were promoted correctly — and nobody ran the third command,
`delivery_lane --landed`. So the claim read `paths: []` and `landings: null`, the lane had no
evidence the work had moved, and at 09:06Z it re-offered the finished item to a fresh seat with no
memory of it, which spent the turn rediscovering finished work and racing a second lane that had
drawn the same hand-off.

IT IS UNRECOVERABLE AFTER THE FACT, which is why a reminder was never the fix. `record_landing`
refuses a commit older than the id's FIRST DRAW; a hand-off id never goes through `draw()`, so it
is absent from `DRAW_LEDGER_FILE` and `_binding_instant` falls back to `claimed_at` — under which
every commit that did the work correctly predates the claim and is refused. The binding happens in
the landing turn or it never happens, and a step that must be remembered every turn will be missed
again.

WHAT THESE LEGS HOLD, and the shape is deliberately NOT the sibling file's. `test_the_promotion_
route_refuses` is all refusals; this one is all non-refusals, because binding is DOING the work,
not gating it. A promotion that pushed has moved the work whether or not the bookkeeping followed,
so every leg below asserts that a bookkeeping failure costs the landing NOTHING and still says,
in named words, what went wrong.

NOTHING HERE PUSHES AND NOTHING HERE WRITES THE LIVE CLAIM STORE. The push is intercepted at
`_git_out` and the store is redirected to `tmp_path`; a control whose failing branch can damage
the live thing it guards is the trap this project has paid for repeatedly.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from background import delivery_lane as dl
from background import seat_work_in_hand as claims_mod
from tools.promote_worktree_landing import PromotionRefused, promote

PROJECT = Path(__file__).resolve().parents[2]


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=300)


@pytest.fixture
def promoting(tmp_path, tmp_path_factory, monkeypatch):
    """A linked worktree holding one real landing, with the push and the store both diverted.

    THE OBJECT DATABASE IS REAL AND SHARED, deliberately: `record_landing` reads the commit with
    `git show` run in `delivery_lane.PROJECT_DIR`, which is not the worktree `promote` was handed.
    A linked worktree shares `.git/objects`, so the read resolves — and leaving it unpatched is
    what makes that a tested property rather than an assumption.
    """
    path = tmp_path_factory.mktemp("bind") / "wt"
    r = _git(PROJECT, "worktree", "add", "--detach", "-q", str(path), "origin/main")
    if r.returncode != 0:
        pytest.skip(f"could not create a worktree: {r.stderr.strip()[:200]}")

    import tools.promote_worktree_landing as mod

    store = tmp_path / "claims.json"
    monkeypatch.setattr(dl, "CLAIMS_FILE", store)
    # Held by its own leg in the sibling file; here it would refuse on whatever the live seat
    # happens to hold, which would make these legs pass or fail on another lane's schedule.
    monkeypatch.setattr(claims_mod, "refuse_if_duplicated", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_refuse_if_ungated", lambda *a, **k: None)

    # The base the promotion is being added to -- a REAL sha, because `promote` passes it to the
    # binding as the `since` ref and a placeholder would make the subject unreadable rather than
    # wrong, which is the flattering failure.
    base = {"sha": _git(path, "rev-parse", "HEAD").stdout.strip()}
    monkeypatch.setattr(mod, "_refuse_if_not_fast_forward", lambda wt, c: base["sha"])

    # One real landing, touching one real file, so `_commit_facts` has paths to return.
    (path / "a_promoted_file.txt").write_text("landed\n")
    _git(path, "add", "a_promoted_file.txt")
    _git(path, "commit", "-q", "--no-verify", "-m", "a landing to bind")
    commit = _git(path, "rev-parse", "HEAD").stdout.strip()
    when = float(_git(path, "log", "-1", "--format=%ct").stdout.strip())

    pushes: list[tuple] = []
    real_out = mod._git_out
    remote_now = {"sha": commit}

    def fake_out(cwd, *args):
        if args[:1] == ("push",):
            pushes.append(args)
            return ""
        if args == ("rev-parse", f"{mod.REMOTE}/{mod.BRANCH}"):
            return remote_now["sha"]
        return real_out(cwd, *args)

    monkeypatch.setattr(mod, "_git_out", fake_out)
    # `promote` refuses early if the LOCAL remote ref already equals the commit; the real one
    # never will here, and `_git` (not `_git_out`) serves that check, so it stays real.

    try:
        yield {"worktree": path, "store": store, "commit": commit, "when": when,
               "pushes": pushes, "remote_now": remote_now, "mod": mod, "base": base,
               "git": lambda *a: _git(path, *a)}
    finally:
        _git(PROJECT, "worktree", "remove", "--force", str(path))
        _git(PROJECT, "worktree", "prune")


def _claim(promoting, work_id: str) -> None:
    claims_mod.claim(work_id, "the drawn work", paths=[], path=promoting["store"],
                     now=promoting["when"] - 60)


def test_a_promoted_landing_IS_BOUND_without_a_third_command(promoting):
    """THE WHOLE POINT, and it must come first: the push is the binding.

    Also the leg that stops every other one here being satisfied by a `_bind_to_claim` that binds
    NOTHING and reports politely — the refusal legs below all assert on `bound == []`.

    MUTATION (must fire): delete the `_bind_to_claim` call from `promote`, or move it into the
    `dry_run` branch.
    """
    _claim(promoting, "the-drawn-id")

    result = promote(promoting["worktree"], work_id="the-drawn-id")

    assert result["pushed"] is True
    assert result["bound"] == ["a_promoted_file.txt"], (
        "the promotion pushed and the claim was left with no paths -- which is the 2026-09-05 "
        "defect exactly, and it is invisible until the lane re-offers the finished item"
    )
    assert "a_promoted_file.txt" in result["binding"], "the report does not name what it bound"
    assert claims_mod._load(promoting["store"])["the-drawn-id"]["paths"] == \
        ["a_promoted_file.txt"], "the binding was reported but never written to the store"


def test_the_binding_happens_only_AFTER_the_push_is_VERIFIED(promoting):
    """`origin/main` reporting success is not `origin/main` holding the commit, and the binding's
    claim is the second one. Binding against an unverified push would make the tombstone say the
    work is on origin when the verification about to refuse says it is not.

    MUTATION (must fire): move `_bind_to_claim` above the `now != commit` check.
    """
    _claim(promoting, "the-drawn-id")
    promoting["remote_now"]["sha"] = "f" * 40  # the push "succeeded" and origin says otherwise

    with pytest.raises(PromotionRefused) as exc:
        promote(promoting["worktree"], work_id="the-drawn-id")

    assert "Verified rather than assumed" in str(exc.value)
    assert claims_mod._load(promoting["store"])["the-drawn-id"]["paths"] == [], (
        "a landing origin does not hold was bound to the claim"
    )


def test_a_REFUSED_binding_does_not_refuse_the_PROMOTION(promoting):
    """Binding is doing the work, not gating it. The landing is on `origin/main` either way, and
    turning a bookkeeping miss into a fifth refusal would put a new gate on the seat's own path
    for a failure that harms nobody but the bookkeeping.

    MUTATION (must fire): raise `PromotionRefused` when `_bind_to_claim` binds nothing.
    """
    # No claim at all for this id -- the ordinary reading after a --release, and the one that
    # must never cost a landing.
    result = promote(promoting["worktree"], work_id="an-id-nobody-claimed")

    assert result["pushed"] is True, "a bookkeeping refusal cost a landing that had succeeded"
    assert result["bound"] == []
    assert "NOT CLAIMED" in result["binding"], (
        "the refusal does not carry `refusal_reason`'s vocabulary, so a second implementation of "
        "it is drifting here -- two of its four causes mean STOP AND LOOK and one is ordinary"
    )


def test_a_promotion_with_NO_work_id_says_so_instead_of_going_quiet(promoting):
    """Silence here is the exact shape of the defect: a promotion that looked complete beside a
    claim reading `paths: []`. It cannot be fixed afterwards, so it has to be said now.

    MUTATION (must fire): return `[], ""` for a missing work id, or skip the print in `main`.
    """
    result = promote(promoting["worktree"], work_id=None)

    assert result["pushed"] is True
    assert "no --work-id" in result["binding"]
    assert "cannot be told afterwards" in result["binding"], (
        "the report does not say the binding is unrecoverable, which is the fact that makes it "
        "worth acting on rather than noting"
    )


def test_a_binding_that_RAISES_still_leaves_the_landing_promoted(promoting, monkeypatch):
    """`record_landing` declines to raise, but an import failure or a corrupt store one level
    below it does not. The landing is already on origin by then and nothing may take it back.

    MUTATION (must fire): drop the `except Exception` from `_bind_to_claim`.
    """
    def boom(*a, **k):
        raise RuntimeError("the store is a smoking hole")

    monkeypatch.setattr(dl, "record_landing", boom)
    _claim(promoting, "the-drawn-id")

    result = promote(promoting["worktree"], work_id="the-drawn-id")

    assert result["pushed"] is True
    assert result["bound"] == []
    assert "RuntimeError" in result["binding"] and "smoking hole" in result["binding"], (
        "the failure class is not named, which is the same non-answer the binding exists to end"
    )


def test_a_DRY_RUN_binds_nothing(promoting):
    """The binding follows the push that makes it true. A dry run has not pushed, so a claim it
    bound would assert something false about `origin/main` -- and would do it on the one run the
    caller chose specifically because it changes nothing.

    MUTATION (must fire): call `_bind_to_claim` before the `dry_run` return.
    """
    _claim(promoting, "the-drawn-id")

    result = promote(promoting["worktree"], work_id="the-drawn-id", dry_run=True)

    assert result["pushed"] is False
    assert result["bound"] == []
    assert promoting["pushes"] == [], "a dry run pushed"
    assert claims_mod._load(promoting["store"])["the-drawn-id"]["paths"] == [], (
        "a dry run wrote a binding for a push it did not make"
    )


def test_the_bound_paths_come_from_the_COMMIT_and_not_from_promotes_own_scope(promoting):
    """`promote` already holds `paths` from `_refuse_if_duplicated`, and handing THOSE to the
    binding would be the shorter code. It would also route the claim's scope through a caller,
    which is the 2026-08-21 hole `record_landing` closed by construction -- so the binding names
    only the commit and lets git answer.

    MUTATION (must fire): pass `paths` into `record_landing` from `promote`.
    """
    import inspect

    src = inspect.getsource(promoting["mod"]._bind_to_claim)
    assert "paths" not in inspect.signature(promoting["mod"]._bind_to_claim).parameters, (
        "the binding takes a path list from `promote`, so a landing's claimed scope is no longer "
        "git's answer"
    )
    assert "record_landing(work_id, commit=commit, since=since)" in src, (
        "the binding no longer names a commit and a base alone -- `since` is a REF, which only "
        "chooses git's question; a path list would choose git's answer"
    )


def test_a_MERGE_binds_MY_paths_and_not_the_side_it_merged_IN(promoting):
    """THE DEFECT THE FIRST LIVE RUN OF THIS BINDING REPRODUCED, filed LATENT 2026-09-04.

    `record_landing`'s default subject for a merge is `first-parent..commit`. Merging
    `origin/main` INTO your landing -- which is what `surgical_land --merge origin/main` produces,
    and therefore what EVERY re-gate after an origin move produces -- makes YOUR work the first
    parent, so that subject is precisely the OTHER lane's files. It binds them, exits 0, and
    prints a plausible count.

    IT IS WORSE THAN A WRONG LIST. The turn is judged on whether the BOUND paths moved on the
    shared tree; the other lane's paths did move, so the turn is graded PASS on their commit while
    its own work stays unbound and re-offerable. A `LANDED NOTHING` would be better, being legible.

    THE SECOND ASSERT IS THE LOAD-BEARING ONE: without it a binding that returned an empty list
    would satisfy the first, and "bound nothing" is the flattering reading of this failure.

    MUTATION (must fire): stop passing `remote_head` as `since`, or make `_commit_facts` ignore
    it -- both restore the first-parent subject and both bind `their_file.txt`.
    """
    git = promoting["git"]
    mine = promoting["commit"]

    # The other lane's commit, from the SAME base -- this is `origin/main` moving.
    # DETACHED, never `-b`: a named branch is a ref in the SHARED repo, and the worktree teardown
    # does not remove it. The first draft used `-b other-lane`, which passed once and then made
    # every later run fail -- `checkout -b` refused the existing ref, HEAD never moved, the merge
    # merged nothing and the leg read as "the binding is broken". A test that leaks a ref into
    # the repo it runs against poisons its own next run.
    git("checkout", "-q", "--detach", promoting["base"]["sha"])
    (promoting["worktree"] / "their_file.txt").write_text("theirs\n")
    git("add", "their_file.txt")
    git("commit", "-q", "--no-verify", "-m", "another lane's landing")
    theirs = git("rev-parse", "HEAD").stdout.strip()

    # Re-gate: merge origin/main INTO my landing. My work is the FIRST parent.
    git("checkout", "-q", mine)
    git("merge", "-q", "--no-ff", "-m", "merge origin/main", theirs)
    merged = git("rev-parse", "HEAD").stdout.strip()
    promoting["remote_now"]["sha"] = merged
    promoting["base"]["sha"] = theirs          # origin/main, as it stood before this push

    _claim(promoting, "the-drawn-id")
    result = promote(promoting["worktree"], work_id="the-drawn-id")

    assert "their_file.txt" not in result["bound"], (
        "the merge bound the side it merged IN -- another lane's work, credited to this claim, "
        "with a success line on it"
    )
    assert result["bound"] == ["a_promoted_file.txt"], (
        "the binding must name what this promotion ADDS to origin/main, and nothing else"
    )
