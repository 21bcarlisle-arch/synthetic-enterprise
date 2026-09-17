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

def test_ALL_THREE_VERDICTS_ARE_REACHABLE_FROM_ONE_FIXTURE(lane):
    """CREDITED, STRANDED and silence are each taken. One control over the whole partition.

    THIS IS THE LEG THE OTHERS CANNOT SUBSTITUTE FOR, and it is written first because this project
    has walked into the trap it guards three times in one afternoon: every test of a check asks
    "does it refuse correctly", and a check that refuses EVERYTHING passes all of them. `tree_verdict`
    returns `None` on six separate routes -- no row, no paths, window still open, already credited,
    git silent, nothing found -- so `None` is overwhelmingly the easy answer, and a regression that
    made it the ONLY answer would leave every other assertion in this file green.

    MUTATION: make `tree_verdict` return `None` unconditionally. Every other test in this file
    still passes on its refusal legs; this one fires on the first assertion.
    """
    repo, claims = lane
    now = _now()

    # CREDITED: a commit inside the window on a path the claim named.
    _commit_at(repo, "tools/credited.py", "x = 1\n", DRAWN + 60)
    _row(claims, "credited-id", ["tools/credited.py"])

    # STRANDED: uncommitted bytes, last touched before the window closed.
    (repo / "tools" / "stranded.py").write_text("never landed\n")
    old = DRAWN + 10
    os.utime(repo / "tools" / "stranded.py", (old, old))
    _row(claims, "stranded-id", ["tools/stranded.py"])

    # SILENT: a path git has never heard of and no bytes on disk.
    _row(claims, "silent-id", ["tools/nothing_here.py"])

    verdicts = {fid: (dl.tree_verdict(fid, now=now, path=claims) or {}).get("verdict")
                for fid in ("credited-id", "stranded-id", "silent-id")}

    assert verdicts == {"credited-id": dl.CREDITED,
                        "stranded-id": dl.STRANDED,
                        "silent-id": None}, (
        "all three answers must be reachable. If every value is None the check has gone "
        "fail-silent and says nothing about any tree; if STRANDED is missing the half the "
        "BLOCKING finding asked for is dead; if CREDITED is missing the 27 landed-but-unbound "
        "rows stay invisible. Got: {}".format(verdicts))


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
