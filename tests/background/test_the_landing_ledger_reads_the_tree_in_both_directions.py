"""The delivery lane decides landing from the TREE, not from whether the author ran `--landed`.

THE DEFECT, which has two faces and is one thing. The lane recorded a landing only when somebody
ran `--landed`, so it could not tell work that EXISTS from work that was merely DESCRIBED:

  * a turn that LANDED CORRECTLY and skipped the binding step was swept, alarmed as having moved
    nothing, and re-offered to a later tick as unstarted work;
  * a turn that DESCRIBED the work and left it as uncommitted bytes on the shared disk was swept
    with exactly the same message, and nobody could tell the two apart without going and looking.

MEASURED, 2026-09-17, on this lane's own ledger and not inherited from the item that directed it.
`the-gas-tariff-type-read-becomes-the-c1b-roll-now-that-the-18-can-leave` was drawn at 1789538535
and `dcb8c6d10` -- its own work, on `simulation/run_phase2b.py`, a path its own prose names --
committed at 1789545141. `_landed_unbound` already existed and still could not see it, because the
window it joined over was `[drawn, drawn + CLAIM_STALE_SECONDS]` and the commit was **606 seconds
past that edge**. That is the central case rather than an edge one: the claim that gets swept is by
construction the turn that ran long, and the turn that ran long is the one whose commit lands after
its window. Across the whole ledger, 27 of the 68 rows reading "landed nothing" had landed.

The second face is the tree's 2026-09-17 BLOCKING finding -- the same nine paths stranded by the
same step on two consecutive nights -- whose own remedy asks for precisely this and names a one-leg
check as the cheap shape: *"The mechanism worth having asks the tree, not the author."*

WHAT THIS FILE GRADES, and the first test is the one that matters most: that all three verdicts are
REACHABLE. A tree check that answers `None` to everything satisfies every other assertion here, and
that is this project's recurring trap -- a guard that refuses everything passes all the tests
written about what it refuses.
"""

from __future__ import annotations

import os
import subprocess
import time

import pytest

from background import delivery_lane as dl
from background import seat_continuation
from background import seat_work_in_hand as claims_mod
from tests.background.residual_voices import could_not_ask


def _git(repo, *args):
    return subprocess.run(("git",) + args, cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


def _commit_at(repo, name, body, when: float) -> str:
    """A commit whose COMMITTER instant is `when`. The join keys on `%ct`, so the fixture has to be
    able to place a commit before, inside and after a window -- a repo whose commits are all `now`
    cannot express the defect at all."""
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    _git(repo, "add", name)
    stamp = f"@{when:.0f} +0000"
    env = dict(os.environ, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    subprocess.run(("git", "commit", "-m", f"land {name}"), cwd=repo, check=True,
                   capture_output=True, text=True, env=env)
    return _git(repo, "rev-parse", "HEAD")


#: The draw instant every case below is placed around. A FIXED number, not `time.time()`: every
#: assertion here is about an offset from a draw, and a fixture whose clock moves makes a failure
#: unreproducible on the second run.
DRAWN = 1_700_000_000.0


@pytest.fixture
def lane(tmp_path, monkeypatch):
    """A real repo plus a real ledger, with BOTH of the lane's trees pointed at it.

    Two seams, because the check genuinely asks two different trees: commits are read from
    `PROJECT_DIR` (a linked worktree shares its object store, so any checkout answers alike) and
    working-tree bytes from `seat_continuation.shared_tree_dir()`. They are the same directory
    here and deliberately patched SEPARATELY -- a fixture that patched one and let the other fall
    through to the live repository would grade this machine's uncommitted state, not the fixture's.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    _commit_at(repo, "docs/seed.md", "seed\n", DRAWN - 10_000)

    claims = tmp_path / "claims.json"
    monkeypatch.setattr(dl, "PROJECT_DIR", repo)
    monkeypatch.setattr(dl, "CLAIMS_FILE", claims)
    monkeypatch.setattr(seat_continuation, "shared_tree_dir", lambda *a, **k: repo)
    # The item's prose is the fallback path source; every row below stamps `named_paths` instead,
    # so nothing here reaches back into the live direction record.
    monkeypatch.setattr(dl, "_item_text", lambda fid: "")
    return repo, claims


def _row(claims, focus_id, named_paths, *, drawn=DRAWN, **extra):
    ledger_path = dl._ledger_path(claims)
    ledger = claims_mod._load(ledger_path) if ledger_path.exists() else {}
    ledger[focus_id] = {"first_drawn_at": drawn, "last_drawn_at": drawn,
                        "named_paths": list(named_paths), **extra}
    claims_mod._save(ledger, ledger_path)


def _now():
    """Long enough after the draw that every window below has closed."""
    return DRAWN + dl.CLAIM_STALE_SECONDS + 100_000


# -------------------------------------------------------------------------------------------
# THE PARTITION. Read this one first.
# -------------------------------------------------------------------------------------------

def test_ALL_FOUR_VERDICTS_ARE_REACHABLE_FROM_ONE_FIXTURE(lane):
    """CREDITED, STRANDED, STRAND_CANDIDATE and silence are each taken. One control, whole partition.

    THIS IS THE LEG THE OTHERS CANNOT SUBSTITUTE FOR, and it is written first because this project
    has walked into the trap it guards three times in one afternoon: every test of a check asks
    "does it refuse correctly", and a check that refuses EVERYTHING passes all of them. `tree_verdict`
    returns `None` on six separate routes -- no row, no paths, window still open, already credited,
    git silent, nothing found -- so `None` is overwhelmingly the easy answer, and a regression that
    made it the ONLY answer would leave every other assertion in this file green.

    IT GREW A FOURTH VALUE ON 2026-09-19 RATHER THAN A SECOND CONTROL, and that is the point of
    asserting the partition in one dict: the new disposition has to be reachable, AND every older
    one has to still be reachable beside it, and a leg-per-branch file cannot say the second thing.
    `silent-id` is the one that had to be re-cut -- it used to be silent because nothing matched its
    NAMES, and the whole-tree question would now answer it from another row's bytes. It is silent
    here because its WINDOW is somewhere else in time, which is the only honest way left to be
    silent and is exactly the property the new reading rests on.

    MUTATION: make `tree_verdict` return `None` unconditionally. Every other test in this file
    still passes on its refusal legs; this one fires on the first assertion.
    """
    repo, claims = lane
    now = _now()

    # CREDITED: a commit inside the window on a path the claim named.
    _commit_at(repo, "tools/credited.py", "x = 1\n", DRAWN + 60)
    _row(claims, "credited-id", ["tools/credited.py"])

    # STRANDED: uncommitted bytes on a path the claim NAMED, last touched before the window closed.
    (repo / "tools" / "stranded.py").write_text("never landed\n")
    old = DRAWN + 10
    os.utime(repo / "tools" / "stranded.py", (old, old))
    _row(claims, "stranded-id", ["tools/stranded.py"])

    # STRAND_CANDIDATE: named path git has never heard of and no bytes of its own -- but its window
    # is the same window `stranded-id`'s bytes were written in. This is the 2026-09-18 geometry:
    # the prose predicted one place and the work went somewhere else in the same hours.
    _row(claims, "candidate-id", ["tools/the-prose-guessed-this.py"])

    # SILENT: same absent path, and a window that holds no uncommitted bytes ANYWHERE in the tree.
    _row(claims, "silent-id", ["tools/nothing_here.py"], drawn=DRAWN + 50_000)

    verdicts = {fid: (dl.tree_verdict(fid, now=now, path=claims) or {}).get("verdict")
                for fid in ("credited-id", "stranded-id", "candidate-id", "silent-id")}

    assert verdicts == {"credited-id": dl.CREDITED,
                        "stranded-id": dl.STRANDED,
                        "candidate-id": dl.STRAND_CANDIDATE,
                        "silent-id": None}, (
        "all four answers must be reachable. If every value is None the check has gone "
        "fail-silent and says nothing about any tree; if STRANDED is missing the half the "
        "BLOCKING finding asked for is dead; if CREDITED is missing the 27 landed-but-unbound "
        "rows stay invisible; if STRAND_CANDIDATE is missing the lane is blind again to work that "
        "finished somewhere the item's prose did not predict; and if SILENT is missing the second "
        "question has stopped discriminating and every swept claim now carries a candidate list. "
        "Got: {}".format(verdicts))


# -------------------------------------------------------------------------------------------
# THE CREDIT HALF, and the window edge that is the whole measured defect.
# -------------------------------------------------------------------------------------------

def test_a_commit_that_arrives_AFTER_the_given_window_but_inside_the_gate_deadline_is_CREDITED(lane):
    """The 606-second miss, reproduced at the edge it happened on.

    MUTATION: restore `window_ends = drawn + CLAIM_STALE_SECONDS` -- i.e. drop
    `_landing_grace_seconds()` -- and this fires. That is the exact code that was live while the
    gas-tariff row sat reading `not_done` with an empty evidence string, so the mutation is not
    hypothetical: it is what the tree did yesterday.
    """
    repo, claims = lane
    late = DRAWN + dl.CLAIM_STALE_SECONDS + 606        # the measured gap, to the second
    sha = _commit_at(repo, "simulation/run_phase2b.py", "rolled\n", late)
    _row(claims, "gas-roll", ["simulation/run_phase2b.py"])

    verdict = dl.tree_verdict("gas-roll", now=_now(), path=claims)

    assert verdict and verdict["verdict"] == dl.CREDITED, (
        "a landing 606s past the sweep deadline is still the landing of the turn that held the "
        "claim -- the gate it had to come through takes up to an hour")
    assert verdict["commit"] == sha
    assert verdict["at"] == pytest.approx(late), (
        "the credit must carry the COMMIT's own instant; stamping it with `now` would make a "
        "stale window read fresh")


def test_a_commit_LATER_than_the_gate_deadline_is_REFUSED(lane):
    """The widened edge still has an edge. This is the leg that makes the previous one a bound
    rather than a licence.

    MUTATION: drop the `<= window_ends` comparison, or widen the grace to a day, and this fires.
    Without it the credit half would sweep up whatever the busiest lane committed next onto a
    shared file and report it as this claim's delivery -- the fail-open the item's own `bound_at`
    join exists to prevent, arriving by a different door.
    """
    repo, claims = lane
    too_late = DRAWN + dl.CLAIM_STALE_SECONDS + dl._landing_grace_seconds() + 60
    _commit_at(repo, "tools/somebody_elses.py", "later\n", too_late)
    _row(claims, "ran-out", ["tools/somebody_elses.py"])

    assert dl.tree_verdict("ran-out", now=_now(), path=claims) is None, (
        "a commit later than `surgical_land`'s own kill deadline cannot be the invocation that "
        "held the claim -- the door it had to come through was already dead")


def test_the_grace_is_DERIVED_from_the_landing_doors_own_deadline_and_not_a_chosen_number(lane):
    """The constant answers to a source. A number picked to make the case above pass would be
    load-bearing within a week and unattributable within a month.

    MUTATION: replace `_landing_grace_seconds()` with a literal and this fires the day
    `surgical_land.GATE_TIMEOUT_SECONDS` moves -- which is the point: the two must move together
    or the credit window silently stops matching the door it is derived from.
    """
    from tools import surgical_land

    assert dl._landing_grace_seconds() == float(surgical_land.GATE_TIMEOUT_SECONDS)


def test_a_commit_ALREADY_BOUND_to_another_row_is_never_credited_twice(lane):
    """The discriminator that makes "unbound" mean something. Untouched by the window change, and
    graded here because widening an edge is the fail-open direction and this is what holds it.

    MUTATION: drop the `when in bound_at` test and this fires -- both rows claim one commit, and
    every claim whose paths overlap a busy file reads as delivered forever.
    """
    repo, claims = lane
    when = DRAWN + 60
    _commit_at(repo, "tools/shared.py", "shared\n", when)
    _row(claims, "the-real-one", ["tools/shared.py"],
         last_landing_at=when, last_landing_paths=["tools/shared.py"], drawn=DRAWN - 5_000)
    _row(claims, "the-bystander", ["tools/shared.py"])

    assert dl.tree_verdict("the-bystander", now=_now(), path=claims) is None, (
        "a commit another row is already credited with is somebody else's landing by the lane's "
        "own record")


def test_the_CREDIT_IS_WRITTEN_so_the_row_reads_DELIVERED_and_NAMES_THE_COMMIT(lane):
    """The item's done-condition, and the step that turns a reading into a mechanism.

    `_landed_unbound` could NAME a landed-but-unbound commit since 2026-09-16 and could do nothing
    about it: the row kept `last_landing_at: null`, so `drawn_without_landing`, the orientation
    brief and `seat_executor`'s did-anything-move verdict all still read the claim as having
    delivered nothing, and each re-derived the same miss.

    MUTATION: make `credit_from_tree` return the verdict without calling `_remember_landing` and
    this fires on the second assertion -- the verdict is still correct, the store still says the
    work never happened, and every downstream reader still disagrees with git.
    """
    repo, claims = lane
    when = DRAWN + 120
    sha = _commit_at(repo, "simulation/svt_product.py", "rolled\n", when)

    _row(claims, "gas-roll", ["simulation/svt_product.py"])
    assert dl.disposition_of("gas-roll", path=claims)["disposition"] != dl.DELIVERED

    acted = dl.credit_from_tree("gas-roll", now=_now(), path=claims)

    assert acted["bound"] == ["simulation/svt_product.py"], (
        "the paths bound are the commit's own INTERSECTED with what the claim named -- not "
        "everything that rode along in the commit, and not paths no commit moved")
    after = dl.disposition_of("gas-roll", path=claims)
    assert after["disposition"] == dl.DELIVERED, (
        "after the credit the row must READ delivered, not merely be labelled so by a reader "
        "that runs again next time")
    assert dl.last_landing("gas-roll", path=claims)[0] == pytest.approx(when)
    assert sha.startswith(acted["commit"][:9])


def test_an_EMPTY_INTERSECTION_writes_NOTHING_rather_than_falling_back(lane):
    """The one place a plausible fallback would have asserted a movement nothing measured.

    An empty intersection cannot happen while git answers -- the commit was FOUND by
    `git log -- <named paths>` -- so it means `_commit_facts` went silent. Binding the named paths
    anyway would credit the claim with files no commit was shown to touch.

    MUTATION: restore `bound = ... or sorted(named)` and this fires: the row is credited, and the
    paths recorded are the item's PROSE rather than a commit's contents.
    """
    repo, claims = lane
    _commit_at(repo, "tools/real.py", "real\n", DRAWN + 60)
    _row(claims, "silent-git", ["tools/real.py"])

    import background.delivery_lane as mod
    original = mod._commit_facts
    try:
        mod._commit_facts = lambda *a, **k: (0.0, [])
        acted = dl.credit_from_tree("silent-git", now=_now(), path=claims)
    finally:
        mod._commit_facts = original

    assert acted["verdict"] == dl.CREDITED and acted["bound"] == []
    assert dl.last_landing("silent-git", path=claims) == (0.0, []), (
        "no landing may be written when nothing can say which paths moved -- the row keeps its "
        "unnamed miss and the next sweep asks again")


# -------------------------------------------------------------------------------------------
# THE STRAND HALF. The BLOCKING finding's subject.
# -------------------------------------------------------------------------------------------

def test_uncommitted_bytes_OLDER_than_the_window_are_STRANDED(lane):
    """Night one and night two of the finding: a lane that never ran the landing step, and a lane
    that ran it and died inside it. Both leave the same thing behind, and only the tree can say so.

    MUTATION: delete the `_stranded_paths` call from `tree_verdict` and this fires. The finding's
    own point is that a retrospective naming this failure mode did not prevent its recurrence
    twelve hours later -- a rule is not a control.
    """
    repo, claims = lane
    p = repo / "sim" / "weather_world"
    p.mkdir(parents=True)
    (p / "store.json").write_text("nine paths nobody landed\n")
    old = DRAWN + 30
    os.utime(p / "store.json", (old, old))
    _row(claims, "weather-store", ["sim/weather_world/store.json"])

    verdict = dl.tree_verdict("weather-store", now=_now(), path=claims)

    assert verdict and verdict["verdict"] == dl.STRANDED
    assert verdict["paths"] == ["sim/weather_world/store.json"]
    assert "uncommitted" in verdict["evidence"]


def test_FRESH_uncommitted_bytes_are_ANOTHER_LANES_LIVE_WORK_and_are_NOT_alarmed(lane):
    """The mtime discriminator, and the only thing standing between this and a false alarm on
    every single sweep.

    Several lanes edit this tree continuously, so "these paths are dirty" is true almost always and
    means nothing. What is not ordinary is bytes that stopped moving before the window closed: a
    dead invocation's leavings freeze at the instant it died, a live lane's repair does not.

    MUTATION: compare on existence rather than mtime -- `if True` in place of
    `mtime <= window_closed` -- and this fires. Without this leg the alarm pages a seat about
    another lane's in-flight repair, which is how a control of this kind gets ignored, and that
    costs more than the strand it was built to catch.
    """
    repo, claims = lane
    (repo / "docs" / "live_repair.md").write_text("another lane is typing right now\n")
    now = _now()
    os.utime(repo / "docs" / "live_repair.md", (now - 5, now - 5))
    _row(claims, "not-mine", ["docs/live_repair.md"])

    assert dl.tree_verdict("not-mine", now=now, path=claims) is None, (
        "bytes touched since the window closed are somebody's live work; alarming on them is a "
        "false positive on every sweep of a shared tree")


def test_a_CREDITED_claim_whose_leftovers_are_dirty_is_DELIVERED_and_not_STRANDED(lane):
    """Order is not arbitrary: the credit is asked first.

    MUTATION: swap the two halves in `tree_verdict` and this fires -- a turn that landed its work
    and left a scratch file behind gets paged as having stranded it, which is a page about work
    that is already in a ref.
    """
    repo, claims = lane
    _commit_at(repo, "tools/landed.py", "done\n", DRAWN + 60)
    (repo / "tools" / "leftover.txt").write_text("scratch\n")
    old = DRAWN + 10
    os.utime(repo / "tools" / "leftover.txt", (old, old))
    _row(claims, "both-shapes", ["tools/landed.py", "tools/leftover.txt"])

    verdict = dl.tree_verdict("both-shapes", now=_now(), path=claims)

    assert verdict["verdict"] == dl.CREDITED


def test_the_strand_check_asks_the_SHARED_tree_and_not_the_checkout_it_runs_in(lane, monkeypatch):
    """`git status` reports the working tree of the checkout it runs in, and the bytes this half
    looks for are on the shared disk by definition.

    MUTATION: let `_stranded_paths` fall through to `PROJECT_DIR` and this fires -- the shared
    tree below holds the stranded bytes and the tree the process stands in does not, which is the
    exact geometry of every isolated-worktree turn, i.e. every turn that runs here.
    """
    repo, claims = lane
    elsewhere = repo.parent / "linked"
    elsewhere.mkdir()
    _git(repo, "worktree", "add", "-q", str(elsewhere), "-b", "linked")
    (repo / "tools").mkdir(parents=True, exist_ok=True)
    (repo / "tools" / "on_the_shared_disk.py").write_text("stranded\n")
    old = DRAWN + 10
    os.utime(repo / "tools" / "on_the_shared_disk.py", (old, old))
    _row(claims, "from-a-worktree", ["tools/on_the_shared_disk.py"])

    # The process stands in the LINKED worktree; the shared tree is where the bytes are.
    monkeypatch.setattr(dl, "PROJECT_DIR", elsewhere)
    verdict = dl.tree_verdict("from-a-worktree", now=_now(), path=claims)

    assert verdict and verdict["verdict"] == dl.STRANDED, (
        "asking the wrong tree returns a clean status and reads as nothing stranded, which is "
        "the flattering answer")


# -------------------------------------------------------------------------------------------
# THE SECOND QUESTION. The named set is a PREDICTION, and this is what is asked when it is wrong.
# -------------------------------------------------------------------------------------------

def test_the_SVT_geometry_the_named_set_could_not_see_is_published_as_a_CANDIDATE(lane):
    """The measured case, reproduced at its own offsets. `the-svt-household-has-no-route-back-to-a-
    fixed-term` was drawn 2026-09-18 19:04:59 naming three DOCUMENTS, its window closed 20:44:59,
    and the turn's work sat at `simulation/renewals.py` with an mtime of 19:30:21 -- 25.4 minutes
    into the window, and in none of the three names. `_stranded_paths` asked git about the three
    documents, git answered correctly, and the lane published `not_done`.

    (The item that directed this repair put the window at 21:00-22:40. The ledger instants above
    are the measured ones and the prose was wrong by about two hours; what it was right about, and
    what this grades, is the RELATION -- mtime strictly inside the window, path outside every name.)

    MUTATION: delete the `_window_attributable_paths` call from `tree_verdict` and this fires. That
    is the code that was live on the night, so the mutation is not hypothetical: it is what the
    lane did, and the work was re-derived by a later turn.
    """
    repo, claims = lane
    named = ["docs/market_research/switcher_split.md", "docs/staging/WORKER_FINDING_SVT.md",
             "docs/staging/done/SEAT_DECISION_SVT.md"]
    for rel in named:                                   # named, tracked, and CLEAN
        _commit_at(repo, rel, "prose\n", DRAWN - 5_000)

    (repo / "simulation").mkdir(parents=True, exist_ok=True)
    (repo / "simulation" / "renewals.py").write_text("the work, never landed\n")
    written = DRAWN + 25.4 * 60                         # 25.4 minutes into a 100-minute window
    os.utime(repo / "simulation" / "renewals.py", (written, written))
    _row(claims, "svt-row", named)

    verdict = dl.tree_verdict("svt-row", now=_now(), path=claims)

    assert verdict and verdict["verdict"] == dl.STRAND_CANDIDATE
    assert verdict["paths"] == ["simulation/renewals.py"]
    assert verdict["named_paths"] == named, (
        "the candidate must carry BOTH sets: a reader cannot judge a time attribution without "
        "seeing the names it is standing in for")


def test_the_candidate_says_IN_ITS_OWN_PROSE_that_the_attribution_is_BY_TIME(lane):
    """The caveat is the load-bearing half, and it has to be in the published sentence rather than
    in this module's docstrings. Bytes written during a claim's window by ANOTHER lane satisfy the
    query exactly as well as its own do, and a reader who takes the list for a proof will land
    somebody else's work under this claim's name -- which is worse than the silence it replaces.

    MUTATION: drop the caveat clause from `_attributed_by_time` and this fires. The verdict is
    still correct, the paths are still right, and the sentence has become a claim about authorship
    that nothing measured.
    """
    repo, claims = lane
    (repo / "docs" / "somebody_elses_repair.md").write_text("not this claim's work\n")
    written = DRAWN + 600
    os.utime(repo / "docs" / "somebody_elses_repair.md", (written, written))
    _row(claims, "coincidence", ["tools/predicted_nothing.py"])

    evidence = dl.tree_verdict("coincidence", now=_now(), path=claims)["evidence"]

    assert "BY TIME AND NOT BY NAME" in evidence
    assert "another lane's" in evidence, "the alternative explanation must be named, not implied"
    assert "docs/somebody_elses_repair.md@" in evidence, (
        "each candidate carries its own mtime -- a path without one cannot be triaged against a "
        "live lane by the seat reading it")


def test_the_candidate_list_DECLARES_ITS_OWN_TRUNCATION_and_the_count_it_came_from(lane):
    """The silent-cap shape, and the reason it matters HERE more than usual.

    MEASURED on the live ledger the hour this landed: the settled 2026-09-18 SVT window yields 4
    candidates, and two just-closed windows on the same tree yield 28 and 57, because three lanes
    were writing through them. The count IS the strength of the attribution -- four is a list to
    open, fifty-seven is a statement that the window was too busy for a clock to single anything
    out -- so a sentence that prints five paths and not the number they were drawn from has hidden
    the one figure that tells the reader how much to believe it.

    MUTATION: print `found[:5]` without the count, or drop the "oldest N of M" clause, and this
    fires. The verdict is still right and every path in it is still real; what is gone is the
    reader's ability to tell a proof from a coincidence.
    """
    repo, claims = lane
    (repo / "docs" / "busy").mkdir(parents=True)
    for i in range(9):
        p = repo / "docs" / "busy" / f"lane_{i}.md"
        p.write_text("someone was writing\n")
        os.utime(p, (DRAWN + 60 + i, DRAWN + 60 + i))
    _row(claims, "busy-window", ["tools/predicted_nothing.py"])

    evidence = dl.tree_verdict("busy-window", now=_now(), path=claims)["evidence"]

    assert "9 path(s)" in evidence, "the total is the figure that says how much to believe this"
    assert "oldest 5 of 9" in evidence, (
        "five paths printed out of nine, with no sign of the other four, reads as a complete list")
    assert evidence.count("docs/busy/lane_") == 5, (
        "and the cap itself must still hold -- a brief that prints every dirty path in a busy "
        "window is the 347-path wall this reading was cut down from")


def test_bytes_written_BEFORE_THE_DRAW_are_not_attributable_and_this_is_what_makes_it_readable(lane):
    """The lower bound, which is the whole difference from `_stranded_paths` and the only reason
    dropping the pathspec is publishable at all.

    MEASURED on the live tree over that same SVT window, 2026-09-19: 537 dirty entries; **347** of
    them satisfy `mtime <= window_closed` when that discriminator is asked of the whole tree, and
    **4** satisfy `drawn <= mtime <= window_closed`. A 347-path candidate list is a wall of noise
    that would be ignored inside a week, and a control nobody reads is not a control.

    MUTATION: reuse `_stranded_paths`' own `mtime <= window_closed` for the whole-tree question --
    i.e. drop the `drawn <=` half -- and this fires. Note the direction: the mutation makes the
    check report MORE, which is the shape that passes a "does it detect the strand" leg and still
    destroys the reading.
    """
    repo, claims = lane
    (repo / "docs" / "long_before.md").write_text("another lane, hours earlier\n")
    old = DRAWN - 3_600
    os.utime(repo / "docs" / "long_before.md", (old, old))
    _row(claims, "clean-window", ["tools/predicted_nothing.py"])

    assert dl.tree_verdict("clean-window", now=_now(), path=claims) is None, (
        "bytes that had already stopped moving when the claim was handed out cannot be its work; "
        "counting them turns every swept claim into a candidate and the reading into noise")


def test_the_SECOND_question_is_asked_only_when_the_NAMED_set_comes_back_clean(lane):
    """Order, and it is what keeps the strong claim strong. A row whose own named paths are dirty
    is a STRAND -- said with the item's own prose behind it -- and must never be downgraded to a
    coincidence because a louder-looking file happens to share its hours.

    MUTATION: ask the whole-tree question first and this fires. Every genuine strand would be
    published under the candidate's hedged verb ("LOOK") instead of its own ("LAND THESE"), and
    the BLOCKING finding's own remedy would stop being actionable.
    """
    repo, claims = lane
    (repo / "docs" / "mine.md").write_text("this claim's work\n")
    (repo / "docs" / "theirs.md").write_text("somebody else's, same hour\n")
    for rel in ("docs/mine.md", "docs/theirs.md"):
        os.utime(repo / rel, (DRAWN + 30, DRAWN + 30))
    _row(claims, "named-and-dirty", ["docs/mine.md"])

    verdict = dl.tree_verdict("named-and-dirty", now=_now(), path=claims)

    assert verdict["verdict"] == dl.STRANDED
    assert verdict["paths"] == ["docs/mine.md"], (
        "the strand names what the claim named; sweeping the sibling in would attach a coincidence "
        "to a claim that had earned a proof")


def test_a_swept_claim_is_NEVER_published_as_a_GENUINE_MISS_over_a_window_holding_dirty_bytes(lane):
    """THE PROPERTY, and this is the control keyed to it rather than to today's answer.

    "This is a genuine miss and the work may still be undone" is the sentence the orientation brief
    prints and the one that sends a reader off to do the work again. Every clause it rested on was
    about COMMITS on the paths the item's prose NAMED -- so it was being published, unhedged, over
    windows whose own hours held the finished work as uncommitted bytes somewhere else in the tree.
    Work finishing and not leaving the tree is this project's most expensive recurring loss, and
    this is the sentence that made it invisible.

    KEYED TO THE PROPERTY: it does not assert which words replace it, only that the flattering
    verdict cannot be reached while the window has attributable bytes. A leg pinned to today's
    phrasing would go red the day the sentence is improved and stay green the day the reading rots.

    MUTATION: delete the `_window_attributable_paths` call from `_nothing_answered` and this fires
    while `tree_verdict` stays perfectly correct -- the two readers are separate doors to the same
    defect, and the brief's is the one a seat actually reads.
    """
    repo, claims = lane
    (repo / "tools").mkdir(parents=True, exist_ok=True)
    (repo / "tools" / "finished_and_sitting_there.py").write_text("done, never committed\n")
    written = DRAWN + 900
    os.utime(repo / "tools" / "finished_and_sitting_there.py", (written, written))
    _row(claims, "brief-row", ["docs/the_prose_guessed_this.md"])

    evidence = dl.disposition_of("brief-row", path=claims)["evidence"]

    assert "genuine miss" not in evidence, (
        "the brief may not tell a reader to redo work that may be sitting finished in the window "
        "it is describing. Got: {}".format(evidence))
    assert "tools/finished_and_sitting_there.py@" in evidence, (
        "and withholding the sentence is not enough -- the reader needs the path to go and look at")


def test_a_window_with_NOTHING_dirty_in_it_still_earns_the_genuine_miss_sentence(lane):
    """The mirror, and without it the leg above is satisfied by a reading that never says anything.

    A residual that can no longer reach its own conclusion is the fail-silent direction of the same
    defect: every swept claim would carry a hedge, the seat would learn to skip the field, and a
    real miss would be indistinguishable from a maybe.

    MUTATION: make `_nothing_answered` always take the candidate branch -- or make
    `_window_attributable_paths` return the whole dirty tree -- and this fires.
    """
    repo, claims = lane
    _commit_at(repo, "docs/all_clean.md", "nothing outstanding\n", DRAWN - 5_000)
    _row(claims, "a-real-miss", ["docs/all_clean.md"])

    evidence = dl.disposition_of("a-real-miss", path=claims)["evidence"]

    assert "genuine miss" in evidence, (
        "a window with a clean tree behind it IS a miss and the brief must be able to say so. "
        "Got: {}".format(evidence))


def test_a_BROKEN_scan_is_published_as_CANNOT_ANSWER_and_not_as_a_genuine_miss(lane, monkeypatch):
    """The could-not-ask split, one question later. `_git` reports a failed git as `None` and a git
    that matched nothing as `""`, and this module has paid twice for callers that collapsed the two.
    The second question is a new place to make that exact mistake.

    MUTATION: let the `except` fall through to the genuine-miss sentence and this fires -- a scan
    that never ran would license the most expensive reading the brief can publish.
    """
    repo, claims = lane
    _commit_at(repo, "docs/quiet.md", "x\n", DRAWN - 5_000)
    _row(claims, "scan-broke", ["docs/quiet.md"])

    def _boom(*a, **k):
        raise RuntimeError("git status fell over")

    monkeypatch.setattr(dl, "_window_attributable_paths", _boom)
    got = dl.disposition_of("scan-broke", path=claims)

    assert "genuine miss" not in got["evidence"]
    assert could_not_ask(got), (
        "and it must speak the voice this module ALREADY has. `residual_voices` keys "
        "`could_not_ask` on the CANNOT ANSWER marker; a third voice saying the same thing in its "
        "own words is invisible to every consumer of that split, which is the conflation this "
        "residual exists to end. Got: {}".format(got))
    assert "RuntimeError" in got["evidence"], "and it names what went dark"


def test_the_candidate_alarm_says_LOOK_and_the_strand_alarm_says_LAND(lane, monkeypatch):
    """The two verdicts want opposite actions from the reader, and an alarm that told a seat to
    land bytes it had only a coincidence for would make this reading worse than the silence it
    replaces. Separate keys too: one message that fired for both would suppress the other.

    MUTATION: route STRAND_CANDIDATE through the STRANDED alarm and this fires on both assertions.
    """
    repo, claims = lane
    (repo / "docs" / "in_the_window.md").write_text("bytes\n")
    os.utime(repo / "docs" / "in_the_window.md", (DRAWN + 60, DRAWN + 60))
    _row(claims, "paged", ["tools/predicted_nothing.py"])

    sent = {}
    from background import alarm_repetition
    monkeypatch.setattr(alarm_repetition, "escalate",
                        lambda msg, **kw: sent.update(msg=msg, key=kw.get("key")))

    dl._act_on_tree_verdict("paged", now=_now(), path=claims)

    assert sent.get("key") == "delivery-lane-strand-candidate:paged", (
        "sharing the strand's key would let one suppress the other")
    assert "CANDIDATE, not a strand" in sent["msg"] and "not yours to commit" in sent["msg"]


# -------------------------------------------------------------------------------------------
# THE SWEEP, which is what the item said DONE means.
# -------------------------------------------------------------------------------------------

def test_THE_SWEEP_CREDITS_a_landed_but_unbound_claim_and_STILL_RELEASES_IT(lane, monkeypatch):
    """One sweep that reads a landed-but-unbound row as delivered and names the commit.

    The claim is still released, and that is right: the work landed, so there is nothing left to
    hold. What changed is that the record now says so instead of re-offering the work.

    MUTATION: delegate straight to `claims_mod.sweep` again -- the pre-2026-09-17 body -- and this
    fires on the disposition. That version alarmed *"No commit has touched its N claimed path(s)
    in that time"* without ever asking git, which is the same un-asked claim about state as the
    sentence it replaced one rung up.
    """
    repo, claims = lane
    sha = _commit_at(repo, "tools/swept.py", "landed\n", DRAWN + 60)
    _row(claims, "swept-id", ["tools/swept.py"])
    claims_mod.claim("swept-id", note="n", paths=[], path=claims, now=DRAWN)
    monkeypatch.setattr(claims_mod, "_last_commit_time_touching", lambda paths: 0.0)

    freed = dl.sweep_stale(now=_now(), path=claims)

    assert "swept-id" in freed, "a claim that is out of time still goes back in the pool"
    after = dl.disposition_of("swept-id", path=claims)
    assert after["disposition"] == dl.DELIVERED, (
        "the sweep must credit from the tree; leaving it `not_done` is the whole defect")
    assert sha.startswith(dl.last_landing("swept-id", path=claims)[1] and sha[:9])


def test_an_UNREADABLE_tree_check_never_costs_the_sweep_its_actual_JOB(lane, monkeypatch):
    """Returning abandoned claims to the pool is what `sweep_stale` is for. The reading is added.

    MUTATION: drop the try/except around `_act_on_tree_verdict` and this fires -- one claim whose
    prose names an unreadable path takes down the sweep for every other claim, and the lane stops
    recycling work entirely on a bookkeeping failure.
    """
    repo, claims = lane
    _row(claims, "boom-id", ["tools/whatever.py"])
    claims_mod.claim("boom-id", note="n", paths=[], path=claims, now=DRAWN)
    monkeypatch.setattr(claims_mod, "_last_commit_time_touching", lambda paths: 0.0)

    def _boom(*a, **k):
        raise RuntimeError("git fell over")

    monkeypatch.setattr(dl, "tree_verdict", _boom)

    assert dl.sweep_stale(now=_now(), path=claims) == ["boom-id"]


def test_a_window_that_is_STILL_OPEN_is_never_disposed_of(lane):
    """A claim inside its own window has not failed at anything yet.

    MUTATION: drop the `stamp - drawn < CLAIM_STALE_SECONDS` guard and this fires -- a live turn
    that has just landed its first increment gets credited and read as finished while it is still
    working, and the claim's remaining time is spent on a row the brief already calls delivered.
    """
    repo, claims = lane
    _commit_at(repo, "tools/in_flight.py", "wip\n", DRAWN + 60)
    _row(claims, "still-going", ["tools/in_flight.py"])

    assert dl.tree_verdict("still-going", now=DRAWN + 100, path=claims) is None


def test_the_strand_verdict_carries_the_AGE_the_reader_needs_to_act(lane):
    """"We cannot tell" is a result and so is "these bytes are eleven hours old". A strand alarm
    without an age cannot be triaged against a live lane by the seat reading it.

    MUTATION: drop `oldest_age_hours` and this fires. It is a separable defect from the strand
    detection itself -- the check can be right and still tell the reader nothing actionable.
    """
    repo, claims = lane
    (repo / "docs" / "left.md").write_text("bytes\n")
    # Written 100s into the turn and never touched again -- the shape a dead invocation leaves.
    # The age is therefore measured from THERE, not from the window's close: what the reader has
    # to triage is how long the bytes have sat, and a file cannot be stranded and recent at once.
    written = DRAWN + 100
    now = _now()
    os.utime(repo / "docs" / "left.md", (written, written))
    _row(claims, "aged", ["docs/left.md"])

    verdict = dl.tree_verdict("aged", now=now, path=claims)

    assert verdict["oldest_age_hours"] == pytest.approx((now - written) / 3600.0, abs=0.2)
    assert verdict["oldest_age_hours"] > 1.0, (
        "an age that rounds to zero tells the reader nothing, and would pass an assertion "
        "comparing it against itself")


def test_the_two_halves_read_the_SAME_path_set(lane):
    """One check, not two. A claim credited against one path set and alarmed against another can
    report both answers about itself, and the pair would disagree without either being wrong.

    MUTATION: give `_stranded_paths` its own extraction (say, `_paths_named_in` while the credit
    half reads `named_paths`) and this fires: the stamped list and the prose list differ here on
    purpose, exactly as they do for a re-drawn row whose item was rewritten.
    """
    repo, claims = lane
    _row(claims, "one-set", ["tools/stamped.py"])
    ledger = claims_mod._load(dl._ledger_path(claims))

    assert dl._claim_paths("one-set", ledger["one-set"]) == ["tools/stamped.py"], (
        "the stamped `named_paths` is the window actually being judged; falling through to the "
        "item's current prose would grade a re-drawn row against the wrong window")
    assert dl._claim_paths("never-drawn", {}) == [], (
        "an empty set must mean CANNOT ANSWER, and both halves must treat it that way -- neither "
        "may read it as `nothing to see`")


def test_time_is_never_read_from_the_WALL_CLOCK_inside_the_check(lane):
    """Every entry point takes `now`. A check that reached for `time.time()` internally could not
    be graded at a chosen offset from a draw, and this whole file would become unwritable.

    MUTATION: replace the `now` parameter with `time.time()` in `tree_verdict` and this fires --
    the fixture's draw is in 2023 and every window would read as closed decades ago.
    """
    repo, claims = lane
    _commit_at(repo, "tools/clocked.py", "x\n", DRAWN + 60)
    _row(claims, "clocked", ["tools/clocked.py"])

    assert dl.tree_verdict("clocked", now=DRAWN + 10, path=claims) is None
    assert dl.tree_verdict("clocked", now=_now(), path=claims)["verdict"] == dl.CREDITED
    assert time.time() > DRAWN, "the fixture clock must be in the past for the above to mean anything"
