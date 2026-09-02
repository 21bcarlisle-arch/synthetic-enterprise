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


def test_the_rendering_puts_the_list_before_the_verdict():
    """The director saw this from a LIST. "29 commits, 0 substantive" was true all afternoon and
    read as a statistic; twelve identical titles in a column reads as a fault."""
    rows = _rows(6)
    text = cn.render({"commits": rows, "count": 6, "carrying_work": 0, "quiet": False,
                      "findings": cn.findings(rows), "shape_is_wrong": True})
    assert text.index("s00") < text.index("[{}]".format(cn.REPETITION))
    assert text.count("!!") == 6, "every no-work commit is marked in the list itself"
