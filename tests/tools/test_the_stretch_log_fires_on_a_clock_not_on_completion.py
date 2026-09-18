"""A stretch that landed NOTHING owes a report. That is the whole of this file.

THE DEFECT (director, 2026-09-18, and he named the mechanism before I found it):

    "The stretch log writes when a stretch completes. A day of machinery -- reds, merges, publisher
     fixes -- never completes a stretch, so nothing gets written, so you never have to state what
     the stretch achieved. A machine that never says what it achieved can't notice when it achieved
     nothing. That's the self-correction loop broken exactly where reflection would happen, and
     it's why the log records the wins and misses the drift."

It was two lines in `owed()`:

    if n == 0:
        return {"owed": False, ..., "reason": "up to date"}

so a stretch that landed nothing was reported as up to date, and the state most worth reading was
the one state that could never be reported. The constants above it had *already* written down the
intent -- *"a machine that lands nothing for three days owes a report as much as one that lands
three hundred commits in an afternoon"* -- and the code one screen down made that sentence false
for as long as it had been written. **A comment stating the property is not the property.**

These legs are about WHEN an entry is owed, never about what it says. They are deliberately blind
to the body: the log's content has its own controls (`validate_subject`), and a test that graded
prose here would be grading the writer rather than the trigger.
"""
from __future__ import annotations

import tools.stretch_log as sl

#: An entry written this instant, at a head the tree can resolve.
FRESH_HOURS = 0.5


def _hold_git_still(monkeypatch, tmp_path, *, commits: int, epoch=1_000_000.0) -> None:
    """Patch the four seams `owed()` reads, so what is under test is the DECISION.

    `sl.LOG` is repointed at a REAL temp file rather than stubbing `Path.is_file` -- that attribute
    is read-only on a PosixPath, and trying it is what made the first draft of this file error in
    every leg at once.
    """
    log = tmp_path / "SEAT_STRETCH_LOG.md"
    log.write_text("# log\n\n## 2026-01-01 — x\n\n<!-- head: deadbeefcafe -->\n")
    monkeypatch.setattr(sl, "LOG", log)
    monkeypatch.setattr(sl, "newest_entry_head", lambda: "deadbeefcafe")
    monkeypatch.setattr(sl, "commits_since_last_entry",
                        lambda: (commits, [f"c{i}" for i in range(commits)]))
    monkeypatch.setattr(sl, "_entry_epoch", lambda _h: epoch)


def _verdict(monkeypatch, tmp_path, *, hours: float, commits: int) -> dict:
    _hold_git_still(monkeypatch, tmp_path, commits=commits)
    return sl.owed(now=1_000_000.0 + hours * 3600.0)


def test_a_stretch_that_landed_nothing_owes_a_report(monkeypatch, tmp_path):
    """The entry the director says he most needs, and the one the old code could not ask for."""
    v = _verdict(monkeypatch, tmp_path, hours=sl.CADENCE_HOURS + 1.0, commits=0)
    assert v["owed"] is True, (
        "a stretch past the cadence that landed nothing was reported as needing no entry -- this "
        "is the exact state a day of machinery produces, and the exact state that must be written"
    )
    assert v["escalate"] is True
    assert v["nothing_landed"] is True, "the writer must be told WHICH entry this is"
    assert "cadence" in v["reason"]


def test_inside_the_cadence_an_ordinary_stretch_does_not_escalate(monkeypatch, tmp_path):
    """The other half of the partition. A trigger that always fires is as useless as one that never does.

    OWED AND ESCALATE ARE DIFFERENT QUESTIONS and this leg is about the second. Twelve commits an
    hour ago is owed -- there is something to write -- and must not PAGE, or the alarm fires on
    every publish cycle and earns the reader the run log had. The first draft of this leg asserted
    `owed is False`, which would have made an ordinary landing invisible.
    """
    v = _verdict(monkeypatch, tmp_path, hours=FRESH_HOURS, commits=12)
    assert v["owed"] is True, "twelve commits landed; there is something to write"
    assert v["escalate"] is False, "an ordinary between-pieces gap must not page"
    assert v["nothing_landed"] is False

    # And the genuinely quiet state: nothing landed, inside the window.
    quiet = _verdict(monkeypatch, tmp_path, hours=FRESH_HOURS, commits=0)
    assert quiet["owed"] is False and quiet["escalate"] is False
    assert "inside the" in quiet["reason"]


def test_the_clock_is_sufficient_on_its_own_whatever_the_commit_count(monkeypatch, tmp_path):
    """Past the cadence is owed at ANY commit count, including zero. That is what "on time" means.

    IT DOES NOT SAY THE CLOCK IS THE ONLY TRIGGER, and the first draft of this leg did -- it
    asserted that 500 commits inside the window owed nothing, and went red, because the commit leg
    is deliberately kept as a SECOND reason ("OR, not AND", the constant's own comment). The
    property the defect was about is that the clock is SUFFICIENT: a stretch that landed nothing
    used to be exempt, and now is not. Asserting more than the design says is how a control ends up
    arguing with its own subject.
    """
    past = sl.CADENCE_HOURS + 2.0
    assert _verdict(monkeypatch, tmp_path, hours=past, commits=0)["owed"] is True
    assert _verdict(monkeypatch, tmp_path, hours=past, commits=500)["owed"] is True

    # And inside the window the clock does not fire on its own -- an ordinary quiet stretch.
    quiet = _verdict(monkeypatch, tmp_path, hours=FRESH_HOURS, commits=0)
    assert quiet["owed"] is False
    assert "inside the" in quiet["reason"]

    # A BURST inside the window is owed, by the other leg, and the reason must say which.
    burst = _verdict(monkeypatch, tmp_path, hours=FRESH_HOURS, commits=500)
    assert burst["owed"] is True
    assert "commits since the last report" in burst["reason"]
    assert "cadence" not in burst["reason"], (
        "the clock is not what carried this one, and a reason naming the wrong leg tells the "
        "writer to write the wrong entry"
    )


def test_a_burst_inside_the_window_still_names_itself_when_the_window_passes(monkeypatch, tmp_path):
    """"Nothing to report" and "too much to report" are different entries, and both are owed.

    The commit leg is kept for exactly this: past the cadence with 500 commits, the reason must say
    so, or the writer cannot tell which of the two reports to write.
    """
    v = _verdict(monkeypatch, tmp_path, hours=sl.CADENCE_HOURS + 1.0, commits=sl.ESCALATE_AFTER_COMMITS + 1)
    assert v["owed"] is True
    assert v["nothing_landed"] is False
    assert "commits since the last report" in v["reason"]
    assert "cadence" in v["reason"], "both legs must be named, not just the louder one"


def test_the_cadence_is_hours_and_not_a_day():
    """Keyed to the director's words -- "every few hours" -- so a drift back to daily reds here.

    A 24h cadence is what this had, and under it a full day of machinery reported nothing once.
    """
    assert 1.0 <= sl.CADENCE_HOURS <= 6.0, (
        f"the cadence is {sl.CADENCE_HOURS}h. The instruction was 'every few hours, whatever state "
        "the work is in'; at a day, a day of drift produces one entry and can hide inside it."
    )


def test_an_unreadable_clock_is_owed_rather_than_quiet(monkeypatch, tmp_path):
    """Fails closed. "I could not tell how long it has been" must never read as "recently"."""
    _hold_git_still(monkeypatch, tmp_path, commits=0, epoch=None)
    v = sl.owed(now=1_000_000.0)
    assert v["owed"] is True and v["escalate"] is True
    assert "unreadable" in v["reason"]


def test_check_tells_the_writer_that_nothing_landed_is_an_entry(monkeypatch, tmp_path):
    """The message is the interface. It used to say "up to date"; it must now ask for the entry."""
    _hold_git_still(monkeypatch, tmp_path, commits=0)
    monkeypatch.setattr(sl, "owed", lambda *a, **k: {
        "owed": True, "escalate": True, "commits": 0,
        "hours": sl.CADENCE_HOURS + 1.0, "nothing_landed": True, "reason": "past the cadence"})
    rc, message = sl.check()
    assert rc == 1
    assert "NOTHING HAS LANDED" in message
    assert "not an exemption" in message, (
        "the message must say an empty stretch is an entry; 'up to date' is what let a day of "
        "machinery pass unwritten"
    )
