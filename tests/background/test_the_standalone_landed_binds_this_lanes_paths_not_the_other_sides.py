"""`--landed` on a `merge origin/main INTO my landing` bound the OTHER lane's paths, exit 0.

THE DEFECT THIS EXISTS TO CATCH, filed LATENT 2026-09-04 as
`SEAT_FINDING_LANDED_ON_A_MERGE_BINDS_THE_OTHER_LANES_PATHS_AND_REPORTS_SUCCESS`, reproduced live
on 2026-09-05 through the promote seam. `_commit_facts` read a merge as `first-parent..commit`.
That is right for `merge my branch INTO origin` and BACKWARDS for `merge origin/main INTO my
landing` — which is the shape `tools.surgical_land --merge origin/main` produces, and therefore
the shape EVERY re-gate after an origin move produces. The claim was bound to the paths of the
lane that was merged in, and the command printed `bound 3 path(s)` over it.

Why worse than a wrong list: the turn is graded on whether the BOUND paths moved on the shared
tree, and the other lane had just moved them. So the turn grades PASS on somebody else's commit
while its own ten paths are bound to nothing and re-offered. `refuse_if_duplicated` reads bound
paths too, so a mis-bind holds another lane's files hostage as well.

The promote route was repaired first (it holds the pre-push `origin/main` and passes it as
`since`). This is the same defect one door along: the STANDALONE `--landed`, which is the route a
tick uses when it lands WITHOUT promoting, and which had no base to hand.

WHAT WAS MEASURED BEFORE CHOOSING, on this repo's real history (2026-09-05):

  * `42d253da5` / `179a6e042`, both real `merge origin/main:` landings. First-parent diff = the
    merged-in lane's files; second-parent diff = the landing's own. The guess is backwards, not
    merely unproven.
  * Today's `origin/main` as a blanket default `since` — the finding's option 2 — returns EMPTY
    for both, because they have since been pushed. As an unconditional default it converts the
    documented-harmless post-promote re-run into a refusal.
  * Both parents of both merges answer ANCESTOR to today's `origin/main`. Publication separates
    the sides only BEFORE the merge is itself pushed — which is exactly when the standalone
    `--landed` runs.

So neither filed option survived whole: the base is derived from publication where git can say
(option 2's answer, from the merge's own parents rather than a moving ref), and REFUSED with both
sides named where it cannot (option 1's fail-closed, kept for the case that needs it).
"""

from __future__ import annotations

import subprocess
import time

import pytest

from background import delivery_lane, seat_work_in_hand


def _git(repo, *args):
    subprocess.run(("git",) + args, cwd=repo, check=True, capture_output=True, text=True)


def _rev(repo, ref="HEAD"):
    return subprocess.run(["git", "rev-parse", ref], cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


def _commit(repo, name, body):
    (repo / name).write_text(body)
    _git(repo, "add", name)
    _git(repo, "commit", "-m", f"add {name}")
    return _rev(repo)


@pytest.fixture
def merged(tmp_path, monkeypatch):
    """A REAL repository in the exact shape `surgical_land --merge origin/main` leaves behind.

    Real git, because the subject IS git's answer: a stub returning the paths we want would
    prove nothing about which parent the diff is taken against.

      base ──── other_lane.txt        <- origin/main, another lane's work
        └────── mine.txt ──── MERGE   <- HEAD. first parent is MINE, second is origin/main.
    """
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    base = _commit(r, "base.txt", "base\n")

    other = _commit(r, "other_lane.txt", "not mine\n")
    _git(r, "update-ref", "refs/remotes/origin/main", other)

    _git(r, "checkout", "-q", "-b", "my-landing", base)
    mine = _commit(r, "mine.txt", "mine\n")
    _git(r, "merge", "--no-ff", "-m", "merge origin/main: re-gate on the new base", other)

    monkeypatch.setattr(delivery_lane, "PROJECT_DIR", r)
    return {"repo": r, "merge": _rev(r), "mine": mine, "other": other, "base": base}


def _claim(tmp_path, monkeypatch, focus_id="land-the-backwards-merge"):
    store = tmp_path / "claims.json"
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", store)
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", store)
    seat_work_in_hand.claim(focus_id, "test", [], path=store, now=time.time() - 3600)
    return store


def test_the_merge_really_did_deliver_this_lanes_file(merged):
    """The FIXTURE's own precondition, asserted before anything is asked of the code.

    Without this, every refusal below is satisfiable by a merge that delivered nothing at all,
    and a test suite that cannot tell "correctly refused an ambiguous merge" from "the fixture
    built an empty one" is grading its own scaffolding. It also fixes the two sides by NAME, so
    the assertions further down cannot quietly agree with whichever answer the code gives.
    """
    assert _rev(merged["repo"], "HEAD^1") == merged["mine"], "first parent must be MY landing"
    assert _rev(merged["repo"], "HEAD^2") == merged["other"], "second parent must be origin/main"
    delivered = subprocess.run(["git", "diff", "--name-only", merged["other"], merged["merge"]],
                               cwd=merged["repo"], check=True, capture_output=True,
                               text=True).stdout.split()
    assert delivered == ["mine.txt"], "the merge delivers exactly this lane's one file"


def test_a_backwards_merge_binds_this_lanes_paths(merged):
    """The defect itself, at the layer that had it.

    MUTATION (must fire): restore `_git("diff", ..., parents[0], commit)` — the first-parent read
    this replaced — and `paths` comes back `["other_lane.txt"]`, which is the live failure
    exactly: the other lane's file, bound to this claim, with nothing of ours in it.
    """
    when, paths = delivery_lane._commit_facts("HEAD")

    assert paths == ["mine.txt"], (
        "a `merge origin/main INTO my landing` must bind what the landing ADDED to origin/main. "
        "['other_lane.txt'] here means the first-parent guess is back and the claim is being "
        "credited with another lane's work."
    )
    assert when > 0.0


def test_record_landing_binds_the_backwards_merge_end_to_end(merged, tmp_path, monkeypatch):
    """The layer the doorbell actually names, because that is where it reported success.

    `_commit_facts` is necessary and not sufficient: what ran on 2026-09-04 was
    `--landed <id>`, and what it printed was a plausible count over the wrong list.

    MUTATION (must fire): first-parent read restored, and `other_lane.txt` reaches `file_scope`
    while `mine.txt` does not — the assertion pair below separates those, so a fix that binds
    BOTH sides (also wrong: it holds the other lane's files hostage) cannot pass either.
    """
    store = _claim(tmp_path, monkeypatch)

    bound = delivery_lane.record_landing("land-the-backwards-merge", commit="HEAD", path=store)

    assert "mine.txt" in bound, "this lane's landing must reach its own claim"
    assert "other_lane.txt" not in bound, (
        "the merged-in lane's paths must NOT be bound here: the turn is graded on whether bound "
        "paths moved, so binding theirs grades this turn on their commit"
    )


def test_an_already_pushed_merge_refuses_and_names_both_sides(merged, tmp_path, monkeypatch):
    """The case publication CANNOT separate — measured, not hypothesised: once the merge is
    pushed, both parents answer ANCESTOR to `origin/main`, which is how both real merges in this
    repo's history read today.

    Fail closed there. A refusal costs one re-run with `--commit`; the guess costs a claim bound
    to somebody else's files, and that has no symptom at all.

    MUTATION (must fire): make `_merge_base_side` fall back to `parents[0]` when it cannot
    separate the sides — the tempting "be helpful" edit — and this binds `other_lane.txt` again.
    """
    _git(merged["repo"], "update-ref", "refs/remotes/origin/main", merged["merge"])
    store = _claim(tmp_path, monkeypatch)

    bound = delivery_lane.record_landing("land-the-backwards-merge", commit="HEAD", path=store)
    reason = delivery_lane.refusal_reason("land-the-backwards-merge", commit="HEAD", path=store)

    assert bound == [], "an unseparable merge must bind nothing rather than guess"
    assert "BOTH" in reason and "origin/main" in reason, (
        "the refusal has to name its cause, not recite the four it might be"
    )
    for side in ("mine.txt", "other_lane.txt"):
        sha = subprocess.run(["git", "log", "-1", "--format=%h", "--", side],
                             cwd=merged["repo"], check=True, capture_output=True,
                             text=True).stdout.strip()
        assert sha and sha in reason, (
            f"the refusal must name the {side} side by sha -- 'pass --commit' is not actionable "
            f"without saying WHICH commits are the candidates"
        )
    assert "--commit" in reason and "--since" in reason, "and both ways out of it"


def test_no_readable_origin_refuses_rather_than_falling_back(merged, tmp_path, monkeypatch):
    """`origin/main` is the discriminator, so its ABSENCE must be a failed check, not an open one.

    R15: an unavailable check is a failed check. The fall-back-to-first-parent version of this
    would be silent in the one direction that costs a mis-bind, and no test of the happy path
    would ever see it.

    MUTATION (must fire): return `parents[0], ""` when `published` is empty and this binds
    `other_lane.txt`.
    """
    _git(merged["repo"], "update-ref", "-d", "refs/remotes/origin/main")
    store = _claim(tmp_path, monkeypatch)

    bound = delivery_lane.record_landing("land-the-backwards-merge", commit="HEAD", path=store)
    reason = delivery_lane.refusal_reason("land-the-backwards-merge", commit="HEAD", path=store)

    assert bound == []
    assert "NEITHER" in reason, reason
    assert "UNREADABLE or touched no files" not in reason, (
        "a merge that plainly touched files must not be reported as touching none -- that is the "
        "cause-naming failure `refusal_reason` exists to end, and it is what this returned "
        "before the merge branch got its own reason"
    )


def test_the_ordinary_single_parent_commit_is_untouched(merged, tmp_path, monkeypatch):
    """The majority route. It must not have moved, and the merge work must not reach it.

    MUTATION: this stays green under the first-parent restoration, which is exactly why it is
    not the only leg here — it is a regression guard, and the two merge legs above are the
    witnesses for the fix.
    """
    when, paths = delivery_lane._commit_facts(merged["mine"])

    assert paths == ["mine.txt"]
    assert when > 0.0


def test_the_cli_takes_since_so_the_standalone_can_ask_promotes_question(merged, tmp_path,
                                                                        monkeypatch, capsys):
    """The escape the refusal names has to EXIST, and the CLI is where it was missing.

    `record_landing` has taken `since` since the promote repair; `--landed` had no way to pass
    one, so the only remedy a session could apply was `--commit`, and on an already-pushed merge
    that means picking a parent by eye. A refusal that names a flag argparse does not have is a
    refusal that cannot be acted on.

    MUTATION (must fire): drop `since=args.since` from the `record_landing` call in `main` and
    the ambiguous merge stays refused, so this fails on the exit code.
    """
    _git(merged["repo"], "update-ref", "refs/remotes/origin/main", merged["merge"])
    _claim(tmp_path, monkeypatch)

    code = delivery_lane.main(["--landed", "land-the-backwards-merge",
                               "--since", merged["other"]])
    out = capsys.readouterr().out

    assert code == 0, out
    assert "mine.txt" in out and "other_lane.txt" not in out, out


def test_the_cli_refusal_is_derived_from_the_since_it_was_given(merged, tmp_path,
                                                                monkeypatch, capsys):
    """A reason keyed to a question the caller did not ask reads as measured and is not.

    Here the caller names the merge itself as the base, so the true cause is "adds NOTHING to
    that" — and re-deriving without `since` would report the unseparable-parents cause instead,
    which is a different remedy.

    MUTATION (must fire): drop `since=args.since` from the `refusal_reason` call in `main`.
    """
    _claim(tmp_path, monkeypatch)

    code = delivery_lane.main(["--landed", "land-the-backwards-merge",
                               "--since", merged["merge"]])
    out = capsys.readouterr().out

    assert code == 1
    assert "adds NOTHING" in out, out
    assert "BOTH" not in out, ("the refusal must answer the question that was asked, not the one "
                               "the default would have asked")
