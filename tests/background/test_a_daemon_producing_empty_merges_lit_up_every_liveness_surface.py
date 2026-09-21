"""29 EMPTY MERGES IN THREE HOURS LOOKED LIKE HEALTH ON EVERY SURFACE THIS MACHINE HAS.

Director, 2026-09-02:

    "Twelve identical titles in an hour was visible at a human glance and invisible to you by
     construction, because nothing asks whether a commit carries any work -- so a daemon producing
     empty merges lit up every liveness surface you have."

`background/origin_reconcile` merged origin into a stale local HEAD and pushed, once every 6m20s
from 15:47 to 19:01. Each commit's tree was byte-identical to its second parent: no content
changed, ever. Three surfaces read that as work:

  * `deadmans_switch._is_non_progress_commit` -- a DENYLIST of subject prefixes. The subject
    matched none, so the liveness clock was refreshed 29 times and the STALL alarm never fired.
  * `delivery_seat.commits_since` -- classifies by FILENAME, and `git log --name-only` prints no
    filenames for a merge. So `substantive_count` was 0, `is_material` read the stretch as empty,
    and the seat SKIPPED orienting: a machine at full tilt and a machine asleep produced the
    identical brief.
  * the gate and the publish path, which counted and receipted those commits without once asking
    what was in them.

The rule these tests hold is structural, so no future subject line can walk past it:

    a commit carries work IFF its tree differs from EVERY one of its parents' trees.
"""
from __future__ import annotations

import subprocess

import pytest

from background import commit_narrative as cn


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "r"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    (r / "a.md").write_text("one\n")
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "real work")
    return r


def _subjects(rows):
    return [r["subject"] for r in rows]


# ── the rule, on each of the four shapes ────────────────────────────────────────────────────
def test_an_ordinary_commit_carries_work(repo):
    (repo / "a.md").write_text("two\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "changed a file")
    assert cn.read_commits(repo)[0]["carries_work"] is True


def test_an_empty_commit_carries_none(repo):
    _git(repo, "commit", "-q", "--allow-empty", "-m", "nothing at all")
    assert cn.read_commits(repo)[0]["carries_work"] is False


def test_a_merge_that_resolved_something_carries_work(repo):
    """A real merge's tree differs from BOTH parents, because it is neither side alone."""
    _git(repo, "checkout", "-q", "-b", "other")
    (repo / "theirs.md").write_text("theirs\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "theirs")
    _git(repo, "checkout", "-q", "main")
    (repo / "ours.md").write_text("ours\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "ours")
    assert _git(repo, "merge", "--no-ff", "-m", "a real merge", "other").returncode == 0
    row = cn.read_commits(repo)[0]
    assert row["subject"] == "a real merge"
    assert row["carries_work"] is True


def test_THE_NO_OP_MERGE_CARRIES_NOTHING(repo):
    """THE 29. A merge whose tree equals one parent's recorded topology and no content.

    Reproduced exactly: the second parent is ahead, the first parent is a stale HEAD with nothing
    of its own, so the merge result IS the second parent's tree. `git merge --no-ff` builds one.

    MUTATION: compare only against the FIRST parent and this passes on the defect -- the tree
    differs from `main`, so a first-parent-only rule calls 29 no-ops "work".
    """
    _git(repo, "checkout", "-q", "-b", "other")
    (repo / "theirs.md").write_text("theirs\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "theirs")
    _git(repo, "checkout", "-q", "main")
    assert _git(repo, "merge", "--no-ff", "-m",
                "merge origin/main: automatic reconciliation", "other").returncode == 0
    row = cn.read_commits(repo)[0]
    assert row["carries_work"] is False, (
        "a merge whose tree is byte-identical to a parent's changed nothing about the repository")


def test_an_unreadable_parent_is_UNKNOWN_and_not_reassurance():
    """`fail_closed_on_unreadable_input`: "could not read it" and "it changed nothing" are
    different answers, and only one of them is a defect report. Neither may be silently the other.
    """
    row = {"sha": "c", "parents": ["gone"]}
    assert cn._carries_work(row, {"c": "t1"}) is None
    assert cn._carries_work({"sha": "c", "parents": []}, {}) is None


# ── the shape findings ──────────────────────────────────────────────────────────────────────
def _rows(n, subject="merge origin/main: automatic reconciliation", work=False, step=380):
    return [{"sha": "s%02d" % i, "short": "s%02d" % i, "subject": subject,
             "epoch": 1_000_000 - i * step, "carries_work": work, "parents": ["p"], "tree": "t"}
            for i in range(n)]


def test_a_run_of_identical_subjects_is_a_finding():
    """The thing the director saw at a glance: twelve identical titles in a column."""
    found = {f["kind"] for f in cn.findings(_rows(6))}
    assert cn.REPETITION in found


def test_two_identical_subjects_are_not_a_finding():
    """Two people naming a thing the same way happens. A control that fired on it would be
    ignored by the time it was right."""
    assert not [f for f in cn.findings(_rows(2)) if f["kind"] == cn.REPETITION]


def test_a_stretch_that_changed_nothing_is_a_finding_even_with_varied_subjects():
    """REPETITION and NO_WORK are separate diagnoses. A loop that varied its message -- a commit
    counter in the subject, say -- would defeat the first and must not defeat the second."""
    rows = [dict(r, subject="merge {}".format(i)) for i, r in enumerate(_rows(5))]
    kinds = {f["kind"] for f in cn.findings(rows)}
    assert cn.NO_WORK in kinds and cn.REPETITION not in kinds


def test_a_regular_cadence_is_named_as_a_timer():
    """Naming the CADENCE is what turns "lots of similar commits" into "a daemon is looping" --
    it tells the reader what to go and look for. 384s was the real one."""
    metronome = [f for f in cn.findings(_rows(6, step=384)) if f["kind"] == cn.METRONOME]
    assert metronome and 370 < metronome[0]["interval_seconds"] < 400


def test_irregular_arrivals_are_not_called_a_timer():
    rows = _rows(6)
    for i, gap in enumerate((0, 30, 900, 60, 4000, 120)):
        rows[i]["epoch"] = 1_000_000 - sum((0, 30, 900, 60, 4000, 120)[:i + 1]) - gap
    assert not [f for f in cn.findings(rows) if f["kind"] == cn.METRONOME]


def test_real_work_produces_no_finding_at_all():
    """The floor under the whole instrument: it must be silent on a normal stretch."""
    rows = [dict(r, subject="a real change %d" % i, carries_work=True)
            for i, r in enumerate(_rows(10))]
    assert cn.findings(rows) == []


def test_a_finding_always_names_its_commits():
    """Director's standing rule, from the 830: a count with no named subject is *"nothing to fix,
    only a number to worry about."* A shape finding with no shas is the same defect renamed."""
    for finding in cn.findings(_rows(6)):
        assert finding["commits"], finding["kind"]


def test_quiet_is_not_the_same_answer_as_spinning():
    """No commits at all has its own causes -- a stopped daemon, a wedged gate, a night off. A
    loop alarm that fired on silence would cry wolf on every idle stretch.

    MUTATION: report `shape_is_wrong` when `count == 0` and this fails.
    """
    state = {"commits": [], "count": 0, "carrying_work": 0, "quiet": True,
             "findings": cn.findings([]), "shape_is_wrong": False}
    assert state["quiet"] and not state["shape_is_wrong"]
    assert "quiet" in cn.render(state)


# ── the second shape: a commit whose only content is the proof it is alive ──────────────────
def _heartbeat(repo, n, surface):
    """`n` commits touching ONLY the declared liveness surface, each with its OWN subject.

    The distinct subjects are the point, not decoration: the real publisher stamps its own
    publishing hash into the message, which is exactly why REPETITION never saw these.
    """
    for i in range(n):
        for rel in surface:
            path = repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"beat": %d}\n' % i)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm",
             "chore(liveness): publish heartbeat while sim output unchanged (git=%09d)" % i)


def test_A_STRETCH_OF_HEARTBEAT_AND_ONE_REAL_COMMIT_IS_READ_APART_FROM_A_GENUINE_ONE(repo,
                                                                                     monkeypatch):
    """THE WHOLE PARTITION IN ONE ASSERTION, which is the only shape that can catch the failure
    that actually threatens this leg.

    A guard that calls EVERY stretch empty satisfies every per-branch test written for the
    heartbeat case -- it would report the spinning stretch perfectly and be catastrophically
    wrong on the quiet-but-productive one. So both sides are asserted together, in one test, and
    neither can be dropped to make the other pass.

    MEASURED, not supposed (2026-09-19, this tree, last 60 commits): twelve heartbeats read as
    WORK and `shape_is_wrong` was False. That is the reading this control refuses.
    """
    from background.process_run_complete import LIVENESS_SURFACE_FILES as surface
    monkeypatch.chdir(repo)

    _heartbeat(repo, 5, surface)
    (repo / "a.md").write_text("genuinely different\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "a real change")
    spinning = cn.narrative(repo, limit=20)

    # SIDE ONE: the machine committed six times and did one thing.
    assert spinning["carrying_work"] == 2, (
        "only the real change and the repo's own first commit carry work; got {}".format(
            spinning["rendered"] if "rendered" in spinning else spinning["carrying_work"]))
    assert spinning["liveness_only"] == 5
    assert spinning["shape_is_wrong"] is True, "a stretch that is five-sixths heartbeat is wrong"
    assert any(f["kind"] == cn.LIVENESS_ONLY for f in spinning["findings"])

    # SIDE TWO: the same instrument on real work must stay silent, or it says nothing at all.
    genuine = _stretch_of_real_commits(repo)
    assert genuine["liveness_only"] == 0
    assert genuine["carrying_work"] == genuine["count"] > 3
    assert genuine["shape_is_wrong"] is False, (
        "a guard that calls every stretch empty is worse than the defect it replaces")


def _stretch_of_real_commits(repo):
    """Four ordinary commits with distinct content, read by the same narrative()."""
    for i in range(4):
        (repo / ("work%d.md" % i)).write_text("content %d\n" % i)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "real work number %d" % i)
    return cn.narrative(repo, limit=4)


def test_a_heartbeat_commit_is_not_called_empty_for_the_WRONG_REASON(repo):
    """NO_WORK's sentence asserts a mechanism -- "its tree is identical to a parent's" -- and that
    is FALSE of a heartbeat, whose tree genuinely differs. A finding that explains itself wrongly
    teaches the reader to stop believing findings.

    MUTATION: collapse `empty_because` to a single value and the run's sentence asserts the
    tree-equality of commits whose trees differ.
    """
    from background.process_run_complete import LIVENESS_SURFACE_FILES as surface
    _heartbeat(repo, 4, surface)
    rows = cn.read_commits(repo, limit=4)
    assert [r["empty_because"] for r in rows] == [cn.LIVENESS_SURFACE_ONLY] * 4
    detail = [f for f in cn.findings(rows) if f["kind"] == cn.NO_WORK][0]["detail"]
    assert "liveness surface" in detail
    assert "identical to one of its own parents" not in detail, (
        "that clause is true of an empty commit and false of a heartbeat")


def test_THE_SURFACE_IS_THE_PRODUCERS_DECLARATION_AND_NOT_A_COPY_OF_TODAYS_TWO_NAMES(repo,
                                                                                     monkeypatch):
    """KEYED TO THE PROPERTY. The day a third liveness file is added, the publisher must declare
    it there in order to publish it at all -- and this reader must pick it up WITHOUT being edited.

    MUTATION: hard-code the pair in `commit_narrative` and this fails, which is the whole point.
    A private second copy of a list that lives somewhere else is this project's most-repaid defect.
    """
    import background.process_run_complete as prc
    third = "docs/observability/a_third_liveness_file.json"
    monkeypatch.setattr(prc, "LIVENESS_SURFACE_FILES",
                        tuple(prc.LIVENESS_SURFACE_FILES) + (third,))
    path = repo / third
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "chore(liveness): a file this reader has never heard of")
    assert cn.read_commits(repo, limit=1)[0]["carries_work"] is False


def test_A_MERGE_IS_NEVER_LIVENESS_BY_DEFAULT_THOUGH_DIFF_TREE_PRINTS_IT_WITH_NO_PATHS(repo):
    """THE FAIL-OPEN THIS LEG NEARLY SHIPPED WITH. `git diff-tree --stdin` prints a merge's sha
    with NO PATHS UNDER IT, so a naive `paths <= surface` reads every merge as liveness-only --
    an empty set is a subset of everything. That would have silently zeroed the work count of
    every merge in the tree while looking like a tightening.

    MUTATION: let `_is_liveness_only` accept an empty path set and this fails.
    """
    assert cn._is_liveness_only(set(), frozenset({"a"})) is False
    _git(repo, "checkout", "-q", "-b", "other")
    (repo / "theirs.md").write_text("theirs\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "theirs")
    _git(repo, "checkout", "-q", "main")
    (repo / "ours.md").write_text("ours\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "ours")
    assert _git(repo, "merge", "--no-ff", "-m", "a real merge", "other").returncode == 0
    assert cn.read_commits(repo, limit=1)[0]["carries_work"] is True


def test_AN_UNREADABLE_SURFACE_DECLARATION_DOES_NOT_CLEAR_THE_STRETCH(repo, monkeypatch):
    """`fail_closed_on_unreadable_input` again. If the declaration cannot be read, the honest
    answer is "these commits were NOT separated from work", not a clean bill.

    MUTATION: return an empty surface silently instead of None and this fails -- the stretch reads
    clean and the reader is never told the leg did not run.

    IT MUST DRIVE THE REAL `_liveness_surface`. An earlier draft of this test monkeypatched that
    function to return None and passed under exactly the mutation it names, because it never ran
    a line of the code it was written about. So the import is broken HERE instead, and the empty
    declaration is asserted separately: `frozenset()` is falsy but is NOT None, and the difference
    is the whole finding -- an empty surface reports the declaration as KNOWN and clears the
    stretch, which is the flattering answer wearing a fail-closed's clothes.
    """
    import sys

    import background.process_run_complete as prc  # bound BEFORE the import is broken

    monkeypatch.setitem(sys.modules, "background.process_run_complete", None)
    assert cn._liveness_surface() is None, "a declaration that cannot be imported is UNKNOWN"

    monkeypatch.undo()
    monkeypatch.setattr(prc, "LIVENESS_SURFACE_FILES", ())
    assert cn._liveness_surface() is None, (
        "an EMPTY declaration is 'we do not know the surface', never 'the surface is nothing'")

    monkeypatch.setattr(cn, "_liveness_surface", lambda: None)
    (repo / "a.md").write_text("two\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "changed a file")
    rows = cn.read_commits(repo, limit=4)
    assert all(r["liveness_surface_known"] is False for r in rows)
    unreadable = [f for f in cn.findings(rows) if f["kind"] == cn.UNREADABLE]
    assert unreadable and "not cleared" in unreadable[0]["detail"]


def test_the_rendering_puts_the_list_before_the_verdict():
    """The director saw this from a LIST. "29 commits, 0 substantive" was true all afternoon and
    read as a statistic; twelve identical titles in a column reads as a fault."""
    rows = _rows(6)
    text = cn.render({"commits": rows, "count": 6, "carrying_work": 0, "quiet": False,
                      "findings": cn.findings(rows), "shape_is_wrong": True})
    assert text.index("s00") < text.index("[{}]".format(cn.REPETITION))
    assert text.count("!!") == 6, "every no-work commit is marked in the list itself"
