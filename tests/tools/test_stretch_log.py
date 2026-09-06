"""The stretch log, each test named by the defect it exists to catch.

Director console, 2026-09-06: *"The commits keep the what; the why is lost... a stretch that lands
work without a report is a finding, and the file should be readable on its own months later, so it
names what it was about rather than assuming the reader has the conversation."*
"""
from __future__ import annotations

import subprocess

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
    test above while making the finding meaningless."""
    sl.append("A stretch about the closed atoms and whether their code actually runs", "body")
    monkeypatch.setattr(sl, "_git", lambda *a: "")

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
