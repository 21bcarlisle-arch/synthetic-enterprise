"""The stretch log, each test named by the defect it exists to catch.

Director console, 2026-09-06: *"The commits keep the what; the why is lost... a stretch that lands
work without a report is a finding, and the file should be readable on its own months later, so it
names what it was about rather than assuming the reader has the conversation."*
"""
from __future__ import annotations

import subprocess
import time

import pytest

from tools import stretch_log as sl


@pytest.fixture()
def log(tmp_path, monkeypatch):
    monkeypatch.setattr(sl, "LOG", tmp_path / "SEAT_STRETCH_LOG.md")
    monkeypatch.setattr(sl, "PROJECT", tmp_path)
    return sl.LOG


def test_a_subject_that_leans_on_the_conversation_is_refused(log):
    """THE DEFECT THE DIRECTOR NAMED. A report written inside a conversation reads perfectly at the
    time and is unusable six months later, because the reader has none of it. "As discussed" names
    nothing."""
    for subject in ("As discussed, the changes we agreed this morning",
                    "Continuing the work from your last message about the queue",
                    "Per your previous instruction, the follow-up items are done"):
        with pytest.raises(ValueError, match="leans on the conversation"):
            sl.append(subject, "body")


def test_a_subject_too_short_to_name_its_subject_is_refused(log):
    """The other half of "readable on its own": a subject line can be free of conversational
    pointers and still say nothing. `Tick fix` passes the phrase check and fails the reader."""
    with pytest.raises(ValueError, match="too short"):
        sl.append("Tick fix", "body")


def test_a_self_contained_subject_is_accepted_and_the_entry_carries_its_head(log):
    sl.append("The worker tick cadence was raised for one allowance window and reverted on a timer",
              "the body of the report")

    text = log.read_text()
    assert "The worker tick cadence was raised" in text
    assert "the body of the report" in text
    assert sl.newest_entry_head() is not None, "an entry with no head stamp cannot be measured"


def test_the_newest_entry_goes_FIRST(log):
    """Newest first, or the file becomes a scroll nobody reaches the end of. Asserted because
    append-to-end is the natural implementation and would read as working."""
    sl.append("The first stretch, about the coverage curves and the sample size they imply", "one")
    sl.append("The second stretch, about mains gas being a meter fact rather than a grid fact", "two")

    text = log.read_text()
    assert text.index("The second stretch") < text.index("The first stretch")


def test_work_landed_with_no_report_is_a_FINDING_and_names_the_commits(log, monkeypatch):
    """THE PROPERTY, and the reason it is a finding rather than a gate: a report is written when a
    piece of work FINISHES, so refusing every commit in between would block the work it describes.

    `--check` must also NAME the commits. A count alone tells the reader a report is owed; the
    subjects tell them what it is owed ABOUT, which is the difference between a nag and a prompt.
    """
    sl.append("A stretch about the premise joint and the correlations it must carry", "body")
    # The stub must answer the RANGE query and the PATH-RESTRICTED one differently -- returning the
    # same text for both means every commit reads as having touched the log and nothing is ever
    # owed. Which is what a single-answer stub did on the first pass.
    monkeypatch.setattr(sl, "_git", lambda *a: "" if "--" in a
                        else "abc1234 land the fitted joint\ndef5678 fix its test")

    rc, msg = sl.check()

    assert rc == 1
    assert "2 commit(s)" in msg
    assert "land the fitted joint" in msg


def test_a_stretch_with_nothing_landed_since_its_report_is_quiet(log, monkeypatch):
    """REACHABILITY OF THE QUIET BRANCH. Without it a check that always fired would satisfy the
    test above while making the finding meaningless.

    IT MUST NOW HOLD THE CLOCK STILL (2026-09-18). The cadence, not the commit count, is what
    decides an entry is owed -- so "nothing landed" is quiet only INSIDE the window, and this test
    became time-dependent the moment that changed. Pinning the epoch is the point rather than a
    workaround: the quiet branch it proves reachable is now "nothing landed AND recently", which is
    a narrower and truer claim than the one it made before.
    """
    sl.append("A stretch about the closed atoms and whether their code actually runs", "body")
    monkeypatch.setattr(sl, "_git", lambda *a: "")
    monkeypatch.setattr(sl, "_entry_epoch", lambda _h: time.time())

    assert sl.check()[0] == 0


def test_the_logs_OWN_commit_does_not_count_and_is_excluded_BY_PATH(log, monkeypatch):
    """A control that can only ever be red -- and the first version got the exclusion wrong in a way
    that shipped.

    It filtered commit SUBJECTS containing "stretch log". Its own landing commit was titled "the
    why, kept: stretch reports land in a committed file on the mirror", which says "stretch
    reports", so it slipped through and the log reported itself as unreported the moment it shipped.
    A grep for a concept's NAME is blind to the thing itself.

    Excluded by PATH now: whatever the commit is called, if it touched the log it is the report,
    not work awaiting one. This drives the two `git log` shapes the function issues -- the range,
    then the range restricted to the log's path -- so a title that mentions nothing still counts.
    """
    sl.append("A stretch about the use-case register and how it sequences against the stages", "b")

    def fake_git(*args):
        if "--" in args:                       # the path-restricted query
            return "aaa1111"
        return "aaa1111 the why, kept: reasoning lands somewhere durable\nbbb2222 an unrelated fix"

    monkeypatch.setattr(sl, "_git", fake_git)
    rc, msg = sl.check()

    assert rc == 1, "the unrelated commit still owes a report"
    assert "1 commit(s)" in msg, msg
    assert "an unrelated fix" in msg
    assert "the why, kept" not in msg, "the log's own commit must be excluded by path"


def test_a_missing_log_is_a_finding_rather_than_silence(log):
    """FAIL-CLOSED on absence. An empty state that reported "up to date" would be the fail-silent
    shape: no log and no complaint reads identically to a log that is current."""
    rc, msg = sl.check()

    assert rc == 1
    assert "no log exists" in msg


def test_an_entry_without_a_head_stamp_is_unmeasurable_and_says_so(log):
    """The staleness measure is keyed to the head each entry was written at. An entry lacking one
    must refuse to report freshness rather than assume it -- an unavailable check is a FAILED
    check."""
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("# Delivery-seat stretch log\n\n---\n\n## 2026-09-06 — a subject with no stamp\n\nbody\n")

    rc, msg = sl.check()

    assert rc == 1
    assert "unmeasurable" in msg


def test_a_head_stamp_this_tree_cannot_RESOLVE_is_red_and_not_up_to_date(log, monkeypatch):
    """THE SILENT GREEN, found 2026-09-10 while diagnosing the three-day silence.

    `_git` returned `""` for a FAILED git command and `""` for one that legitimately produced no
    output, and nothing downstream could tell them apart. The head stamp names a commit; if that
    commit is not reachable -- written in a worktree whose landing never promoted, on a branch since
    rewritten, in a fresh clone -- `git log <stamp>..HEAD` exits 128. The old code read that as zero
    commits and printed **"up to date"**, forever, with no report ever written.

    Not hypothetical in this project: stretch entries are written in linked worktrees and reach the
    shared tree only if `promote_worktree_landing` succeeds. One refusal and the control goes green
    for good.

    MUTATION: restore `return done.stdout.strip() if rc == 0 else ""` and this returns rc 0.
    """
    sl.append("A stretch about the fitted joint and the correlations it has to carry", "body")
    monkeypatch.setattr(sl, "_git", lambda *a: None)   # git refused, whatever was asked

    rc, msg = sl.check()

    assert rc == 1, "an unresolvable head stamp reported the log as up to date"
    assert "not reachable" in msg and "UNMEASURABLE" in msg
    assert "[stretch-log] up to date." not in msg, "the green verdict survived an unreadable input"


def test_an_unreachable_stamp_ESCALATES_rather_than_reading_as_a_small_gap(log, monkeypatch):
    """The same defect at the escalation seam. `owed()` derives its thresholds from a commit count
    and an age, and BOTH are unavailable when the stamp will not resolve. Defaulting either to zero
    would turn "I could not look" into "nothing much is owed"."""
    sl.append("A stretch about the space-filling sample and what it rejects on", "body")
    monkeypatch.setattr(sl, "_git", lambda *a: None)

    v = sl.owed()

    assert v["owed"] and v["escalate"]
    assert v["commits"] is None and v["hours"] is None
    assert "unreachable" in v["reason"]


def test_an_ordinary_gap_is_owed_but_does_not_escalate(log, monkeypatch):
    """REACHABILITY OF THE NON-ESCALATING BRANCH, and the whole reason there is a threshold.

    Every gap is "owed" almost all of the time -- that is the machine working, because a report is
    written when a piece of work FINISHES. If `escalate` were simply `owed`, the repair would page
    on every publish cycle and earn itself exactly the reader the run log had.
    """
    sl.append("A stretch about the billing axes and which of them the sample spans", "body")
    monkeypatch.setattr(sl, "_git", lambda *a: (
        "" if "--" in a else "\n".join(f"c{i:06x} a landing" for i in range(5))))
    monkeypatch.setattr(sl, "_entry_epoch", lambda h: 1_000_000.0)

    v = sl.owed(now=1_000_000.0 + 3600)   # five commits, one hour

    assert v["owed"] is True
    assert v["escalate"] is False, "an ordinary between-pieces gap must not page"


def test_each_escalation_leg_can_carry_the_verdict_ALONE(log, monkeypatch):
    """THE TWO LEGS ARE AN OR, AND EACH IS LOAD-BEARING.

    Thresholds measured against this log's own history rather than chosen: eleven stamped entries
    give ten gaps of 1, 2, 2, 5, 8, 9, 20, 29, 37, 70 commits, and a longest silence of 16.7h. So
    80 commits and 24h both sit above everything the log has ever done, and neither would have
    fired on any historical stretch.

    A machine that lands nothing for three days owes a report as much as one that lands three
    hundred commits in an afternoon, so a single AND leg would miss one of them entirely.
    """
    sl.append("A stretch about the weather cells and how much granularity Britain needs", "body")
    monkeypatch.setattr(sl, "_entry_epoch", lambda h: 0.0)

    # TIME ONLY: three days quiet, four commits.
    monkeypatch.setattr(sl, "_git", lambda *a: (
        "" if "--" in a else "\n".join(f"c{i:06x} x" for i in range(4))))
    v_time = sl.owed(now=3 * 24 * 3600)
    assert v_time["escalate"] and "since the last report" in v_time["reason"]
    assert "commits since" not in v_time["reason"], "the count leg fired on four commits"

    # COUNT ONLY: two hundred commits inside an hour.
    monkeypatch.setattr(sl, "_git", lambda *a: (
        "" if "--" in a else "\n".join(f"c{i:06x} x" for i in range(200))))
    v_count = sl.owed(now=3600)
    assert v_count["escalate"] and "200 commits since" in v_count["reason"]
    assert "h since the last report" not in v_count["reason"], "the age leg fired at one hour"


def test_the_page_text_does_not_carry_the_rotating_commit_list(log, monkeypatch):
    """ALARM IDENTITY IS THE DECLARED KEY, and prose is not normalised out of it.

    `alarm_repetition.normalise()` strips numbers, elapsed times and hashes; it does not strip
    sentences. A page carrying twelve commit subjects would be a different condition every cycle --
    the shape that once put 28 documents behind 2 conditions. The listing belongs in `--check`,
    which the run log keeps; the page carries the condition.
    """
    sl.append("A stretch about the demand vector and what a claim declares it reduces over", "body")
    monkeypatch.setattr(sl, "_git", lambda *a: (
        "" if "--" in a else "abc1234 land the fitted joint\ndef5678 fix its test"))
    monkeypatch.setattr(sl, "_entry_epoch", lambda h: 0.0)

    page = sl.alarm_message(sl.owed(now=10 * 24 * 3600))

    assert "land the fitted joint" not in page
    assert "abc1234" not in page
    assert "stretch report" in page.lower()


def test_the_live_log_is_published_where_the_advisor_reads():
    """The director asked for "somewhere my advisor reads without being told". `docs/` is the tree
    the GitHub Pages mirror publishes and the channel the advisor fetches; `site/` is Cloudflare and
    a different audience. A log written to the wrong tree is a log nobody sees.

    Asserted against the real path, not the fixture's, because this is a fact about where the
    module points in production.
    """
    rel = sl.LOG.resolve().relative_to(sl.PROJECT.resolve())

    assert rel.parts[0] == "docs", f"the log must live under docs/ to reach the mirror, not {rel}"


def test_the_live_log_exists_and_carries_at_least_one_entry():
    """REACHABILITY against the live tree: the mechanism is worthless if nothing ever writes to it,
    and a tool whose output does not exist is the shape this project keeps finding."""
    from pathlib import Path

    live = Path(sl.__file__).resolve().parent.parent / "docs" / "status" / "SEAT_STRETCH_LOG.md"

    assert live.is_file(), "the stretch log does not exist in the live tree"
    assert live.read_text(encoding="utf-8").count("\n## ") >= 1, "the live log has no entries"


def test_the_check_runs_THE_WAY_A_HOOK_WOULD_RUN_IT():
    """Fourth module this week where a script entry point could be dead while every test is green:
    pytest fixes `sys.path` before any test can import the module, so an import-path defect is
    invisible to all of them."""
    import os
    import sys as _sys

    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "m = runpy.run_path('tools/stretch_log.py', run_name='probe');"
         "print(m['check']()[0])"],
        cwd=str(sl.PROJECT), capture_output=True, text=True, timeout=180,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() in ("0", "1"), done.stderr
