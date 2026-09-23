"""The defect: the stale-copy clock had TWO return values for THREE states, and the third took the
flattering exit.

`judge` and `clock_judge` return `Loss | None`. `None` meant *the clock looked and has no
complaint*. It ALSO meant *a git call this verdict rests on failed and nothing was ever measured* --
because `_git` is `check=False` throughout, a failing `git log` prints nothing, and every reader
turned "nothing" into its own negative: `last_commit_touching` into "no commit has touched this
path", `committed_at` into a DECLARED "git will not answer" that its one caller then read as "the
copy is not older", `distinctive_lines` into "this landing added no evidence". Three causes, one
falsy value, and `refresh_to_head.judge_copy` printed a CONTENT verdict beside a clause asserting
the clock had no objection.

WHAT IS AND IS NOT CLAIMED HERE. The two live refusals of 2026-09-22 that commissioned this -- the
same enactment refused twice, HEAD stable either side, the files byte-identical -- are NOT
attributed to this cause by any test in this file, and were not attributed by the seat that found
them. The claim these legs make is the narrower and checkable one: that the OUTPUT could not have
told you either way, and now can.

EVERY LEG NAMES A WAY THE REPAIR COULD BE USELESS rather than exercising the new state twice. The
two that matter most are the pair: a guard that refuses EVERYTHING passes every test written for
"does it refuse correctly", so `test_a_healthy_clock_still_reaches_every_content_verdict` asserts
the content verdicts are still reachable AND still distinct from each other.

NO STUB STANDS IN FOR GIT ANYWHERE IN THIS FILE, and that was worth the trouble because the whole
subject is what a REAL failing git call does to a verdict -- a patched `_git` proves a patched
`_git`. `_a_checkout_whose_history_CANNOT_BE_READ` makes one loose object unreadable, which is a
degraded checkout git itself reports on (`error: unable to open loose object ... Permission
denied`), and which leaves `git show HEAD:<path>` working while every history walk fails. That
asymmetry is the defect's own shape: the content oracles all answer, the clock cannot run, and
before this repair the tool printed the content answer as though the clock had agreed with it.

THE FIRST INSTRUMENT TRIED HERE WAS WRONG AND IS RECORDED RATHER THAN QUIETLY REPLACED. It passed a
TREE sha as the base, on the belief that `git log <tree>` is `fatal: not a commit`. It is not: it
exits 0 and prints NOTHING, which `last_commit_touching` reads as "no commit has ever touched this
path". So the first draft of these legs was measuring a different fail-silent from the one it named
-- a real one, and one no exception can reach, since there is no failure for `_git_answer` to see.
That shape is unrepaired and is a finding, not something this file should pretend to cover.
"""
from __future__ import annotations

import json
import os
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from tools import refresh_to_head as rth
from tools import stale_copy_refusal as scr


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


LANDED = (
    "def alpha():\n    return 1\n\n\n"
    "def freshly_landed_helper(argument):\n"
    '    """A distinctive line that appears exactly once in this file."""\n'
    "    return argument * 41 + 7\n"
)

#: Carries the landing's distinctive line and adds a name of its own: the clock has NO COMPLAINT
#: about it, and the content oracles have plenty to say. That combination is what makes it the
#: control for "the refusal did not swallow the content verdicts".
HOLDER_APPENDS = LANDED + (
    "\n\ndef my_own_unlanded_function():\n"
    "    return 'work that only exists in this lane and nowhere else'\n"
)

#: Contains NOT ONE of the landing's distinctive lines: the clock COMPLAINS, with `predates_landing`.
PREDATES_THE_LANDING = (
    "def alpha():\n"
    '    """an alternative wording of exactly the same behaviour, and nothing else"""\n'
    "    return 1\n"
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo with a landing in its history. The subject is what git says and does not
    say; a fake git would be a fake more permissive than its subject, which is how a fail-open goes
    green."""
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "m.py").write_text("def alpha():\n    return 1\n")
    (root / "report.json").write_text(json.dumps({"headline": 1, "rows": [{"v": 2}]}))
    _run(root, "add", "m.py", "report.json")
    _run(root, "commit", "-qm", "base")
    (root / "m.py").write_text(LANDED)
    (root / "report.json").write_text(json.dumps({"headline": 9, "rows": [{"v": 8}], "extra": 3}))
    _run(root, "add", "m.py", "report.json")
    _run(root, "commit", "-qm", "the landing")
    return root


@contextmanager
def _a_checkout_whose_history_CANNOT_BE_READ(root: Path):
    """A real degraded repository: the base commit's loose object is made unreadable.

    WHAT IT DOES AND DOES NOT BREAK is the entire reason this is the instrument. `git show
    HEAD:<path>` needs the HEAD commit, its tree and the blob -- all intact -- so `blob_at` and
    every content oracle downstream of it answer normally. Every HISTORY walk (`git log ... --
    <path>`, `git log -1 --format=%ct`, `git diff <c>^ <c>`) must reach the parent and fails with
    rc 128. That is the clock, and only the clock, unable to run on a checkout that otherwise looks
    fine -- which is what "fail-closed on bytes, fail-silent on cause" described.

    SKIPPED RATHER THAN SILENTLY VACUOUS where the mode does not bite (running as root, or a
    filesystem that ignores it). A test whose injected failure did not happen measures the healthy
    path and reports it as the broken one."""
    base = _run(root, "rev-parse", "HEAD~1").strip()
    blob = root / ".git" / "objects" / base[:2] / base[2:]
    if not blob.exists():
        pytest.skip("the base commit is packed, so there is no loose object to make unreadable")
    original = blob.stat().st_mode
    os.chmod(blob, 0o000)
    try:
        probe = subprocess.run(["git", "log", "-1", "--format=%ct", "HEAD"], cwd=str(root),
                               capture_output=True, text=True, check=False)
        if probe.returncode == 0:
            pytest.skip("this process can read the object regardless of its mode (root?), so the "
                        "failure this leg is about was never injected")
        yield
    finally:
        os.chmod(blob, original)


# ------------------------------------------------------ the three answers, and that they differ


def test_the_clock_has_THREE_answers_and_no_two_of_them_collapse(repo: Path) -> None:
    """THE PARTITION CONTROL, and it asserts DISTINCTNESS rather than three separate memberships.

    A per-answer leg (`this shape gives COMPLAINT`, `that shape gives NO_COMPLAINT`, ...) passes
    unchanged if two of the three shapes start returning the SAME state -- which is precisely the
    defect: three causes, one value. Asserting the set has three members is the only form that
    reds on a collapse, whichever pair collapses."""
    head_text = _run(repo, "show", "HEAD:m.py")

    (repo / "m.py").write_text(PREDATES_THE_LANDING)
    complaint = scr.opinion(repo, "m.py", head_text, PREDATES_THE_LANDING)
    (repo / "m.py").write_text(HOLDER_APPENDS)
    no_complaint = scr.opinion(repo, "m.py", head_text, HOLDER_APPENDS)
    with _a_checkout_whose_history_CANNOT_BE_READ(repo):
        # THE SAME COPY AND THE SAME ARGUMENTS as `no_complaint` above, so the only thing that
        # moved is whether git could answer. Any other difference would let a reader attribute the
        # third state to the fixture instead of to the failure.
        unanswered = scr.opinion(repo, "m.py", head_text, HOLDER_APPENDS)

    assert len({o.answer for o in (complaint, no_complaint, unanswered)}) == 3, (
        "two of the clock's three states share a value ({}, {}, {}) -- which is the defect "
        "itself, whichever pair it is".format(
            complaint.answer, no_complaint.answer, unanswered.answer))
    assert complaint.answer == scr.COMPLAINT and complaint.loss is not None
    assert no_complaint.answer == scr.NO_COMPLAINT and no_complaint.loss is None
    assert unanswered.answer == scr.COULD_NOT_ANSWER and unanswered.loss is None


def test_the_unanswered_state_carries_the_call_that_failed_so_it_can_be_re_run(repo: Path) -> None:
    """A refusal that does not name its reason is how you never discover the refusal was wrong --
    and this one's whole content is a reason, so a cause the reader cannot act on is the same
    silence in a longer sentence. Git's own stderr is what says WHICH object could not be read."""
    head_text = _run(repo, "show", "HEAD:m.py")
    with _a_checkout_whose_history_CANNOT_BE_READ(repo):
        verdict = scr.opinion(repo, "m.py", head_text, HOLDER_APPENDS)
    assert verdict.unanswered
    assert "git log" in verdict.cause and "rc=" in verdict.cause, (
        "the cause does not name the call that failed, so the reader cannot run it: "
        + verdict.cause)
    assert "loose object" in verdict.cause, (
        "git's own stderr was dropped, so the cause names a call but not why it failed: "
        + verdict.cause)


def test_the_printable_rule_is_never_no_complaint_for_a_question_nobody_answered(
        repo: Path) -> None:
    """`Opinion.rule` EXISTS BECAUSE EVERY CALLER SPELLED THE SAME WRONG EXPRESSION. `"no complaint"
    if clock is None else clock.rule` appeared three times in `judge_copy` alone, and it is right
    for two of three states. This pins the string a reader is shown, because the string is what the
    operator acted on when they re-ran the door three times."""
    head_text = _run(repo, "show", "HEAD:m.py")
    with _a_checkout_whose_history_CANNOT_BE_READ(repo):
        assert scr.opinion(repo, "m.py", head_text, HOLDER_APPENDS).rule == scr.UNANSWERED
    assert scr.opinion(repo, "m.py", head_text, HOLDER_APPENDS).rule == "no complaint"


# ------------------------------------------------------------- the readers, one cause at a time


def test_committed_at_refuses_rather_than_returning_the_none_that_also_meant_a_measured_no(
        repo: Path) -> None:
    """The DECLARED fail-silent, and the reason it is worth its own leg: the docstring said "or
    `None` if git will not answer", so this was documented and still wrong -- `taken_before` reads
    it as `landed is not None`, and a "cannot tell" and a "no" collapse at the first truth test
    after them.

    THE CAUSE IS ASSERTED AND NOT JUST THE RAISE, because the raise alone is EQUIVALENT under a
    mutation that matters. Reverting this function's git read to the old tolerant `_git(...).stdout`
    still ends in a `ClockUnanswered`, via the `isdigit` guard a line later -- so a leg that only
    asked `pytest.raises` stayed green on the change it was written for, measured 2026-09-23. What
    the two versions do NOT share is what the refusal SAYS: git's own `fatal: bad object ...` is
    lost, and all the reader is told is that something returned the empty string. On a door whose
    whole repair is "name the failing call", that difference is the repair."""
    assert scr.committed_at(repo, "HEAD") > 0
    with pytest.raises(scr.ClockUnanswered) as raised:
        scr.committed_at(repo, "0" * 40)
    assert "git log" in str(raised.value) and "bad object" in str(raised.value), (
        "the refusal does not carry git's own reason, so it names a symptom and not a cause: "
        + str(raised.value))


def test_distinctive_lines_does_not_report_NO_EVIDENCE_for_a_rev_git_cannot_resolve(
        repo: Path) -> None:
    """The SILENT one, one rev deeper than the others. `rev-parse --verify <c>^` fails identically
    for "this is a root commit" and for "this is not a commit", and the first is answered `()` --
    *there was no before, so there is no evidence* -- which is a sentence about the repository, not
    about the caller's typo.

    THE ROOT-COMMIT LEG IS HERE TOO, because a fix that raised on both would be a control that
    refuses everything: the honest empty answer must survive."""
    root_commit = _run(repo, "rev-list", "--max-parents=0", "HEAD").strip()
    assert scr.distinctive_lines(repo, "m.py", root_commit) == (), (
        "the commit that CREATED the file still has no 'before', and that is an answer")
    assert scr.distinctive_lines(repo, "m.py", "HEAD"), "the landing's own evidence went missing"
    with pytest.raises(scr.ClockUnanswered):
        scr.distinctive_lines(repo, "m.py", "0" * 40)


def test_last_commit_touching_tells_a_path_nobody_landed_from_a_ref_that_does_not_resolve(
        repo: Path) -> None:
    """Both were `None`. One is a fact about the tree and the other is a failed question, and the
    caller (`if not commit: return None`) could not tell them apart."""
    assert scr.last_commit_touching(repo, "never_existed.py") is None
    assert scr.last_commit_touching(repo, "m.py") is not None
    with pytest.raises(scr.ClockUnanswered):
        scr.last_commit_touching(repo, "m.py", upto="refs/heads/no_such_branch")


# --------------------------------------------------------------- the door, which is the subject


def test_refresh_to_head_renders_the_unanswered_clock_as_its_OWN_refusal(repo: Path) -> None:
    """THE HALF OF THE DIRECTION THIS FILE EXISTS FOR: *make `refresh_to_head` render the second as
    its own refusal rather than as a content verdict*.

    The live symptom was a grade about the copy's CONTENT -- "supplies 2706 JSON leaves origin/main
    does not have ... decide which document wins and land it deliberately" -- printed for a copy
    whose clock had never been read, with a clause beside it naming the stale-copy verdict as "no
    complaint". So this asserts both halves: the state is the new one, AND the content sentences
    are absent. Asserting only the state would pass a version that printed the new name on top of
    the old paragraph."""
    (repo / "m.py").write_text(HOLDER_APPENDS)
    with _a_checkout_whose_history_CANNOT_BE_READ(repo):
        verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.CLOCK_UNANSWERED, verdict.reason
    assert verdict.refused
    # THE SENTENCES THE OTHER STATES PRINT, named individually rather than by searching for the
    # string "no complaint" -- this refusal SAYS "unknown is not 'no complaint'" on purpose, and a
    # substring test would forbid the tool from explaining itself. These three are the claims:
    # `NOT_SUPERSEDED`'s positive assertion, `SUPPLIES_NEW`'s content grade, and the clause that
    # printed the clock's verdict as `[no complaint]` in the live instance.
    assert "has NO complaint" not in verdict.reason, (
        "the refusal still asserts the clock looked and had no objection")
    assert "supplies" not in verdict.reason.lower(), (
        "a content grade is printed for a copy nothing has measured")
    assert "DOES NOT REACH THIS COPY" not in verdict.reason
    assert "isolate_hunks" not in verdict.reason and "--base-wins" not in verdict.reason, (
        "a door is named for a copy nothing has measured -- which is the guess the bare `None` "
        "was already making, and one of those doors overwrites bytes")
    assert "git log" in verdict.reason, "the failing call is not on the surface"


def test_a_DATA_path_gets_the_same_refusal_and_not_the_leaf_count_that_was_published(
        repo: Path) -> None:
    """The live instance was a `.json`, and the data branch is a SEPARATE run of the same mistake:
    it reached `json_leaf_delta` and reported a leaf count for a copy whose clock had not been
    read. The single consult site is placed above both branches for exactly this reason, and this
    leg is what would red if it were moved back down into one of them."""
    (repo / "report.json").write_text(json.dumps({"headline": 1, "rows": [{"v": 2}], "mine": 5}))
    with _a_checkout_whose_history_CANNOT_BE_READ(repo):
        verdict = rth.judge_copy(repo, "report.json")
    assert verdict.state == rth.CLOCK_UNANSWERED, verdict.reason
    assert not verdict.gains and not verdict.edited, (
        "a content delta was computed and published for a path the clock never looked at")
    assert "JSON key path" not in verdict.reason and "leaf" not in verdict.reason


def test_a_healthy_clock_still_reaches_every_content_verdict(repo: Path) -> None:
    """THE CONTROL THAT STOPS THIS BEING A GUARD THAT REFUSES EVERYTHING.

    Every leg above asks "does it refuse correctly", and a refusal that fires on all inputs passes
    all of them. The consult site added to `judge_copy` runs on EVERY path, before every content
    branch, so an over-broad `unanswered` would have swallowed the tool whole and every test in
    this file would still be green.

    DISTINCTNESS AGAIN, not three memberships: the three shapes must still land in three different
    states, which is the property that a single absorbing state destroys."""
    (repo / "m.py").write_text(HOLDER_APPENDS)
    holder = rth.judge_copy(repo, "m.py")
    (repo / "m.py").write_text(PREDATES_THE_LANDING)
    rival = rth.judge_copy(repo, "m.py")
    (repo / "report.json").write_text(json.dumps({"headline": 1, "rows": [{"v": 2}]}))
    data = rth.judge_copy(repo, "report.json")

    states = [holder.state, rival.state, data.state]
    assert rth.CLOCK_UNANSWERED not in states, (
        "the new refusal fires on a healthy repository, so it is a guard that refuses everything "
        "and every other leg in this file measures nothing: {}".format(states))
    assert len(set(states)) == 3, (
        "three different copies reached the same verdict on a healthy clock: {}".format(states))
    assert holder.state == rth.SUPPLIES_NEW and holder.gains
    assert rival.state == rth.REFRESHABLE


# ------------------------------------------------------------------- the commit gate's own side


def test_violations_refuses_a_path_whose_clock_could_not_answer_and_names_no_door(
        repo: Path) -> None:
    """FAIL-CLOSED, which is this module's own doctrine for `Unparseable` and true here for the
    same reason: an unavailable check is a failed check. The second assertion is the one that
    matters -- both doors this module can name are keyed to evidence the clock was supposed to
    supply, so naming one would be the same guess in a louder voice."""
    head = _run(repo, "rev-parse", "HEAD").strip()
    (repo / "m.py").write_text(HOLDER_APPENDS)
    with _a_checkout_whose_history_CANNOT_BE_READ(repo):
        losses = scr.violations(repo, head, head, ["m.py"])
    assert [loss.rule for loss in losses] == [scr.UNANSWERED], [loss.rule for loss in losses]
    rendered = losses[0].render()
    assert "git log" in rendered and "COULD NOT ANSWER" in rendered
    assert "isolate_hunks" not in rendered and "refresh_to_head" not in rendered
    assert scr.refusal_text(losses), "the refusal does not render at all"


def test_violations_still_passes_a_clean_path_and_still_catches_a_stale_one(repo: Path) -> None:
    """The mirror of the leg above, and the reason it is here rather than assumed: `violations()`
    is the commit gate for every lane in this tree, so a change that made it refuse a healthy path
    would red every commit in the repository -- and would be indistinguishable, from inside the
    tests above, from the repair working."""
    head = _run(repo, "rev-parse", "HEAD").strip()
    base = _run(repo, "rev-parse", "HEAD~1").strip()
    assert scr.violations(repo, base, head, ["m.py"]) == [], (
        "the landing itself is refused, so no commit could ever be made")
    stale = scr.violations(repo, head, base, ["m.py"])
    assert [loss.rule for loss in stale] == [scr.PREDATES], [loss.rule for loss in stale]
