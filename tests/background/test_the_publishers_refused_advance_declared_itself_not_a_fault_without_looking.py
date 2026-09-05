"""THE PUBLISHER'S REFUSED ADVANCE DECLARED ITSELF "NOT A FAULT" ABOUT A STATE IT NEVER EXAMINED.

THE DEFECT, from `docs/staging/done/SEAT_FINDING_THE_PATH_THAT_WEDGED_THE_PUBLISHER_WAS_THE_FILE
_THE_LANE_REPAIRING_THE_PUBLISHER_WAS_HOLDING_2026-09-04.md`. `_advance_to_origin_or_say_why`
returned ONE reason for every non-zero `--ff-only` rc:

    git REFUSED the fast-forward (rc=1), which is the guard working and not a fault: <git's tail>

The safety claim behind it is sound -- git will not clobber a lane's edit -- but the sentence
converts it into a verdict that there is nothing here to act on, and **a refusal that declares
itself not-a-fault is a refusal nobody re-reads.** Measured 2026-09-04/05: nine advance attempts,
zero fires, and the single tracked path refusing every one of them was
`background/process_run_complete.py` -- the advance's own source file, held dirty by the lane
repairing the advance. Three separate seats re-derived the blocking paths by hand while that line
said the guard was working.

THE PROPERTY THESE CONTROLS ARE KEYED TO is the one that finding names, and it is deliberately NOT
"the blocking set is empty" -- that is today's answer, and it goes green for the wrong reason the
moment the tree happens to be clean:

    **a refusal to advance must name whether it EXAMINED the holders, and must not report a cause
    it did not establish.**

So `None` ("I could not look") and `[]` ("I looked and nothing collides") must reach the reader as
different findings, and `FF_MODIFIED` (a lane's work, with an owner and a remedy) must not be
rendered in the same reassuring words as `FF_UNTRACKED` (usually a byte-identical twin with nothing
at stake).

WHY THERE IS NO THIRD IMPLEMENTATION HERE, and it is asserted rather than trusted.
`origin_reconcile.paths_blocking_fast_forward` / `_blocking_clause` already ask and answer this
exact question. This module had already paid for the copy-instead-of-call shape at this very
function -- it reused `commits_ahead` and hand-rolled the advance, so the twin-clearing repair that
landed in `advance_shared_tree` never reached it. `test_the_clause_is_the_SIBLINGS_and_not_a_second
_renderer` is the control over that.
"""
from __future__ import annotations

import inspect
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from background import origin_reconcile as orc
from background import process_run_complete as prc


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


def _untracked(path: str) -> dict:
    return {"path": path, "kind": orc.FF_UNTRACKED}


def _verdict(blocking) -> str:
    """The verdict half of the refusal, driven by an injected blocking read."""
    return prc._refused_advance_cause(Path("/nonexistent"), lambda _p: blocking)[0]


def _clause(blocking) -> str:
    return prc._refused_advance_cause(Path("/nonexistent"), lambda _p: blocking)[1]


NOT_A_FAULT = "the guard working and not a fault"


# ── the whole partition in one control, before any leg claims what it does ───────────────────
def test_all_four_readings_are_reachable_and_none_of_them_is_the_only_one():
    """THE REACHABILITY CONTROL, and it comes first for the reason CLAUDE.md gives: every leg below
    asserts what ONE reading says, and a `_refused_advance_cause` that returned a single constant
    string would pass any one of them in isolation.

    Four readings, four distinct verdicts. This project has entered the "rare branch is unreachable
    another way" trap three times in one afternoon through three different doors, so the guard is
    written over the whole partition rather than as a leg per branch.

    MUTATION: collapse any two branches of `_refused_advance_cause` into one return and the
    `len(set(...)) == 4` assertion reds. Return a constant and it reds harder.
    """
    readings = {
        "modified": _verdict([_modified("background/process_run_complete.py")]),
        "untracked": _verdict([_untracked("docs/staging/A_FINDING.md")]),
        "nothing": _verdict([]),
        "unread": _verdict(None),
    }
    assert len(set(readings.values())) == 4, (
        "the four readings a blocking check can return -- a lane's tracked file, an untracked "
        "twin, nothing at all, and 'I could not look' -- must reach the reader as four different "
        "findings, got {}".format(readings))
    assert all(v.strip() for v in readings.values()), \
        "every reading must produce a sentence; an empty verdict is the silence this repairs"


def test_a_dirty_tracked_file_is_NOT_reported_as_the_guard_working():
    """THE REPAIR ITSELF. An `FF_MODIFIED` path is a lane's uncommitted work holding the shared tree
    behind origin -- a wedge with an owner and a named remedy, not a state with nothing to act on.

    MUTATION: delete the `FF_MODIFIED` branch and the reading falls through to the untracked one,
    which carries `NOT_A_FAULT` verbatim -- so the first assertion reds.
    """
    verdict = _verdict([_modified("background/process_run_complete.py")])
    assert NOT_A_FAULT not in verdict, (
        "a tracked file this tree has edited is what actually wedged the publisher for nine "
        "attempts, and calling it 'not a fault' is what stopped four readers acting on it: "
        "{}".format(verdict))
    assert "isolate_hunks" in verdict, \
        "the reading with an owner must carry the command that owner uses to land their hunks " \
        "without waiting -- a refusal that names no remedy is the one nobody re-reads"


def test_an_untracked_twin_IS_still_reported_as_the_guard_working():
    """THE OTHER SIDE, and it is what stops the repair from being 'call everything a fault'.

    An untracked path origin also adds is usually byte-identical, and then nobody's work is at
    stake at all. A version that alarmed on every refusal would pass the test above and be exactly
    as useless in the opposite direction.

    MUTATION: make the `FF_MODIFIED` branch fire for any non-empty `blocking` and this reds.
    """
    verdict = _verdict([_untracked("docs/staging/A_FINDING.md")])
    assert NOT_A_FAULT in verdict
    assert "isolate_hunks" not in verdict, \
        "nothing is held by a lane here, so pointing the reader at the hunk-isolating door sends " \
        "them to a door with nothing behind it"


def test_a_modified_path_beside_a_twin_reads_as_the_wedge_and_not_as_the_twin():
    """THE MIXED SET, which is the state actually measured on the shared tree on 2026-09-04: one
    `FF_MODIFIED` and one -- later six -- lossless `FF_UNTRACKED` twins.

    The tracked path survives every twin removal, so it is what the verdict must be about. A reader
    told "untracked twins, nothing at stake" about this set clears six files and advances nothing,
    which is the deletion-bought-for-no-advance that `advance_shared_tree` declines by design.

    MUTATION: test `blocking[0]["kind"]` instead of `any(...)` and the twin-first ordering here
    reds.
    """
    verdict = _verdict([_untracked("docs/staging/A_FINDING.md"),
                        _modified("background/process_run_complete.py")])
    assert NOT_A_FAULT not in verdict, \
        "one tracked collision holds the fast-forward no matter how many twins are cleared, so " \
        "the mixed set must read as the wedge"


def test_could_not_look_and_nothing_collides_are_never_the_same_finding():
    """FAIL-CLOSED, keyed to the REASON and not to the values -- which is the shape a mutation
    already caught once in this repo's sibling control.

    `None` is "I could not look" and `[]` is "I looked and nothing collides". Both are refusals,
    both are non-advancing, and a verdict that renders them alike is exactly how a fail-open reads
    as a clean bill. Neither may borrow the reassuring wording, because neither established that
    the refusal was harmless.

    MUTATION: delete the `blocking is None` branch and `None` -- being falsy -- falls through to
    the `[]` reading by the other route, producing the same sentence. The final assertion reds;
    an assertion over `advanced`/booleans alone would not fire at all.
    """
    unread, nothing = _verdict(None), _verdict([])
    assert unread != nothing
    assert "NOT established" in unread, \
        "an unexamined state must say it was unexamined, in the words the reader acts on"
    assert NOT_A_FAULT not in unread and NOT_A_FAULT not in nothing, \
        "neither reading examined a holder that proved harmless, so neither may claim it"


def test_the_clause_is_the_SIBLINGS_and_not_a_second_renderer():
    """NO THIRD COPY. The rendered clause must be `origin_reconcile._blocking_clause`'s own output,
    byte for byte -- not a lookalike that will drift away from it the next time the sibling learns
    something.

    This is the defect this module has already committed at this exact function: it reused
    `commits_ahead` and hand-rolled the advance, and when the twin-clearing repair landed in
    `advance_shared_tree` it reached the reconciler's two legs and not this one. Nothing went red.

    MUTATION: re-render the paths locally (`"; ".join(b["path"] for b in blocking)`) and the
    equality reds while every behavioural test above still passes.
    """
    for blocking in ([_modified("a.py")], [_untracked("b.md")],
                     [_modified("a.py"), _untracked("b.md")], [], None):
        assert _clause(blocking) == orc._blocking_clause(blocking), \
            "the clause must BE the sibling's, not resemble it -- blocking={}".format(blocking)


def test_a_blocking_read_that_raises_costs_the_verdict_and_never_gits_own_words():
    """The naming of the cause is an ENRICHMENT of a refusal that already had an answer. If it
    fails, the refusal must survive it -- a recovery path that turns a refusal into a crash is the
    shape `_advance_to_origin_or_say_why`'s own broad except exists to refuse.

    MUTATION: drop the `try/except` in `_refused_advance_cause` and this raises instead of
    returning, reding the call itself.
    """
    def _explode(_project):
        raise RuntimeError("git went away")

    verdict, clause = prc._refused_advance_cause(Path("/nonexistent"), _explode)
    assert "NOT established" in verdict and "RuntimeError" in verdict, \
        "a naming attempt that failed must say so and say why, not fall back to the reassuring " \
        "wording it could not justify"
    assert NOT_A_FAULT not in verdict
    assert clause == ""


# ── and the refusal a reader actually sees carries all of it, against real git ───────────────
def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=120)


@pytest.fixture
def unlocked(monkeypatch):
    """The advance takes the SHARED tree lock, contended by a live daemon. Neutralised here exactly
    as the sibling advance suite does; the lock is asserted structurally over there, so removing it
    from the code still fails a control."""
    @contextmanager
    def _no_lock():
        yield

    monkeypatch.setattr(prc, "tree_lock", _no_lock)


@pytest.fixture
def wedged(tmp_path):
    """A real clone that is genuinely behind a real origin and genuinely cannot fast-forward,
    because a tracked file origin also changes is edited here.

    Real git because the property is git's own `--ff-only` refusal: a stubbed runner asserting
    against a stubbed refusal would be a tautology, and this is the tree the 2026-09-04 measurement
    was taken on, in miniature.
    """
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin))

    local = tmp_path / "local"
    _git(tmp_path, "clone", str(origin), str(local))
    _git(local, "config", "user.email", "seat@example.invalid")
    _git(local, "config", "user.name", "seat")
    (local / "shared.py").write_text("A\n")
    _git(local, "add", "shared.py")
    _git(local, "commit", "-m", "A")
    _git(local, "push", "origin", "HEAD:main")

    other = tmp_path / "other"
    _git(tmp_path, "clone", str(origin), str(other))
    _git(other, "config", "user.email", "seat@example.invalid")
    _git(other, "config", "user.name", "seat")
    (other / "shared.py").write_text("A\nB\n")
    _git(other, "add", "shared.py")
    _git(other, "commit", "-m", "B")
    _git(other, "push", "origin", "HEAD:main")

    # This lane's uncommitted edit to the very path origin changes -- the FF_MODIFIED wedge.
    (local / "shared.py").write_text("A\nthis lane was here\n")
    return local


def test_the_tree_really_refuses_before_anything_is_claimed_about_the_refusal(wedged, unlocked):
    """THE REACHABILITY LEG for the real-git half. Without it the two tests below could pass
    against a tree that advances cleanly and never produces a refusal at all."""
    result = prc._advance_to_origin_or_say_why(wedged)
    assert result["advanced"] is False
    assert "REFUSED" in result["reason"]
    assert orc.commits_ahead(wedged) == 0, \
        "the fixture must refuse on the COLLISION, not on a fork of its own -- otherwise the " \
        "refusal never reaches the branch under test"


def test_the_refusal_names_the_path_the_remedy_and_gits_own_words(wedged, unlocked):
    """THE WHOLE SENTENCE A READER GETS, assembled from real git against a real wedge.

    Three things have to survive together, and the finding says why each was missing: the PATH
    (four seats re-derived it by hand), the REMEDY (the reading with an owner needs a door), and
    GIT'S OWN TAIL (the clause is derived from it, so dropping it would leave the derivation
    unfalsifiable).

    MUTATION: drop `_clause` from the format string and the path assertion reds; drop
    `stderr_tail(ff.stderr)` and the last one does.
    """
    reason = prc._advance_to_origin_or_say_why(wedged)["reason"]

    assert "shared.py" in reason, \
        "git names only its first colliding path and the clause names them all with their kinds " \
        "-- a refusal that names none is what sent four readers to rediscover them by hand"
    assert orc.FF_MODIFIED in reason, \
        "the KIND is what decides who clears it, so it travels with the path"
    assert NOT_A_FAULT not in reason, \
        "this is a real dirty-tree collision, which is the one reading the old sentence was " \
        "wrong about"
    assert "isolate_hunks" in reason
    assert "overwritten" in reason, \
        "git's own words are the ground truth the clause is derived from and must not be " \
        "replaced by it"


def test_a_tree_that_CAN_advance_never_reaches_the_refusal_at_all(wedged, unlocked):
    """THE NULL CONTROL over the real-git half. With the collision removed the same call advances,
    so the refusal above was attainable AND avoidable -- which is what makes it evidence rather
    than a property of the fixture."""
    _git(wedged, "checkout", "--", "shared.py")
    result = prc._advance_to_origin_or_say_why(wedged)
    assert result["advanced"] is True, \
        "nothing collides now, so the advance must go through -- if it cannot, every refusal " \
        "asserted above is graded against a function that can only say no"
    assert "REFUSED" not in result["reason"]


def test_the_advance_still_takes_the_blocking_read_from_the_sibling_by_default():
    """The injected `blockers_fn` is a test seam, and a seam that is the ONLY route to the code
    means production runs something else. This asserts the default really is the sibling's
    function, so every behavioural control above is about the code that actually runs.

    MUTATION: change the default to a local stub returning `[]` and this reds.
    """
    src = inspect.getsource(prc._refused_advance_cause)
    assert "from background.origin_reconcile import" in src
    assert "paths_blocking_fast_forward" in src and "_blocking_clause" in src
    assert "blockers_fn or paths_blocking_fast_forward" in src, \
        "the injected reader may only OVERRIDE the sibling's, never replace it as the default"
