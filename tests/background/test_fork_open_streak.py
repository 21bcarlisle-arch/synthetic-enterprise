"""The fork with origin stood open 22.4 hours and paged nobody.

THE DEFECT, measured 2026-09-26 from `docs/observability/reconcile-watch-log.md`: 314 fork
verdicts in 39 hours, 10 of them settled, and the verdict line went to `_log` and nowhere else.
While it stood, the shared tree was 32 behind, the publisher's recorded cause was `behind_origin`
and the site was dark. The reconciler was not broken -- it refused a conflict, correctly, and a
conflict is by design a judgement for a person. Nothing told the person.

Every control below names the mutation that must red it. The first one is the load-bearing one:
the streak is keyed to the PROPERTY (the fork did not close) and not to the status string, because
the real 203-tick streak carried five different statuses interleaved and a status-keyed counter
resets every few ticks, can never fire, and looks like a working detector the whole time.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import background.fork_open_streak as F
import background.reconcile_watch as W

T0 = datetime(2026, 9, 26, 0, 0, tzinfo=timezone.utc)


def _line(minute: int, status: str, settled: bool, behind: int = 32, ahead: int = 3) -> str:
    at = (T0 + timedelta(minutes=minute)).strftime("%Y-%m-%d %H:%M")
    return "- [{} UTC] fork with origin ({} behind, {} ahead) -> {} [{}]: detail".format(
        at, behind, ahead, status, "settled" if settled else "STILL OPEN")


def _run(lines, *, now_minute, state=None):
    """One pass with everything injected. Returns `(page_text_or_None, pages_sent)`."""
    sent = []
    text = F.check(notify=lambda msg, **kw: sent.append((msg, kw)),
                   now=T0 + timedelta(minutes=now_minute), lines=lines,
                   state=state if state is not None else {})
    return text, sent


# ── THE STREAK IS THE PROPERTY, NOT THE STATUS ──────────────────────────────────────────────
def test_the_streak_survives_the_status_CHANGING_under_it():
    """THE MEASURED SHAPE. The live 203-tick streak was
    `{GATE_RUNNING: 78, NOT_ADVANCED: 60, ERROR: 32, REFUSED_CONFLICT: 32, REFUSED_GATE: 1}` --
    five statuses, one unbroken failure to close. This is the whole reason the detector exists.

    MUTATION (must fire): break the streak when `status` changes -- e.g. add
    `if row["status"] != run[-1]["status"]: break` to `open_streak`'s walk. The streak collapses
    to 1 tick, the page never goes out, and nothing else in this file reds.
    """
    statuses = ["GATE_RUNNING", "REFUSED_CONFLICT", "ERROR", "NOT_ADVANCED", "GATE_RUNNING",
                "REFUSED_CONFLICT", "ERROR", "NOT_ADVANCED", "GATE_RUNNING", "REFUSED_CONFLICT",
                "ERROR", "NOT_ADVANCED", "GATE_RUNNING", "REFUSED_CONFLICT", "ERROR"]
    lines = [_line(i * 5, s, settled=False) for i, s in enumerate(statuses)]
    streak = F.open_streak(F.verdicts(lines), T0 + timedelta(minutes=75))

    assert streak["open"] and streak["ticks"] == len(statuses), (
        "the streak broke when the status changed under it, which is the exact shape that made "
        "the 22-hour fork invisible: {}".format(streak))
    assert len(streak["statuses"]) == 4, (
        "the page has to carry WHICH refusals it was, or the reader cannot tell a wedged conflict "
        "from a busy gate: {}".format(streak["statuses"]))
    text, sent = _run(lines, now_minute=75)
    assert text and len(sent) == 1 and "5 x" not in text


def test_a_settled_verdict_ends_the_streak_and_a_later_one_starts_a_NEW_one():
    """The counter-arm to the test above: a detector that never breaks the streak would pass it
    and be a constant alarm. MUTATION: delete the `if row["settled"]: break` and this reds."""
    lines = ([_line(i * 5, "REFUSED_CONFLICT", settled=False) for i in range(20)]
             + [_line(100, "RECONCILED", settled=True)]
             + [_line(105 + i * 5, "GATE_RUNNING", settled=False) for i in range(3)])
    streak = F.open_streak(F.verdicts(lines), T0 + timedelta(minutes=115))
    assert streak["open"] and streak["ticks"] == 3, (
        "a settled verdict did not end the streak, so the count is the whole log: {}".format(
            streak))


# ── THE THRESHOLD, AND BOTH SIDES OF IT IN ONE PASS ─────────────────────────────────────────
def test_BOTH_sides_of_the_threshold_are_reachable_in_one_pass():
    """THE PARTITION CONTROL. A detector that pages at every length passes "it pages", and one
    that pages at none passes "it stays quiet"; only asserting both in the same pass over the
    same mechanism can tell those apart from a working threshold.

    The quiet case is a real one off the record -- self-clearing streaks here ran 5, 25, 30, 35
    and 52 minutes. The loud case is the 497-minute one that needed a person.

    MUTATION (must fire): drop the `< UNATTENDED_MINUTES` test in `page_for` (always pages), or
    invert it (never pages). Either reds one leg of this."""
    short = [_line(i * 5, "GATE_RUNNING", settled=False) for i in range(11)]      # 50 minutes
    long_ = [_line(i * 5, "GATE_RUNNING", settled=False) for i in range(101)]     # 500 minutes

    quiet, quiet_sent = _run(short, now_minute=50)
    loud, loud_sent = _run(long_, now_minute=500)

    assert quiet is None and quiet_sent == [], (
        "a 50-minute streak paged, and every streak that has ever cleared itself here was "
        "shorter than that -- this detector would be ignored within a day: {}".format(quiet))
    assert loud is not None and len(loud_sent) == 1, "a 500-minute open fork did not page"
    assert "500" in loud and "101 ticks" in loud and "32" in loud, (
        "the page must carry how long, how many observations and how far behind, or the reader "
        "has to go and read the log this exists to save them reading: {}".format(loud))


def test_the_threshold_sits_in_the_gap_the_record_actually_has():
    """KEYED TO THE PROPERTY, NOT TO TODAY'S NUMBER. What must hold is that the threshold is
    above every self-clearing streak observed and below every one that needed a person -- the
    measured distribution is 5/25/30/35/52 then 497. A control pinned to `== 60` would go red
    when someone re-measured and MORE honestly moved it, which is backwards.

    MUTATION: set `UNATTENDED_MINUTES = 40` (inside the self-clearing range) or `= 600` (past the
    streak that needed a person) and this reds."""
    self_clearing_max, needed_a_person_min = 52, 497
    assert self_clearing_max < F.UNATTENDED_MINUTES < needed_a_person_min, (
        "the threshold is no longer in the gap between what clears itself and what needs a "
        "person: {}".format(F.UNATTENDED_MINUTES))


# ── TRANSITION-ONLY, AND KEYED TO WHICH STREAK ──────────────────────────────────────────────
def test_it_pages_ONCE_for_a_streak_and_then_stays_quiet_while_it_stands():
    """R5. This fires every five minutes; a page per tick is how an alarm gets muted.

    MUTATION: return the text unconditionally from `page_for`'s open branch, and this reds."""
    lines = [_line(i * 5, "REFUSED_CONFLICT", settled=False) for i in range(101)]
    first, state = F.page_for(F.open_streak(F.verdicts(lines), T0 + timedelta(minutes=500)),
                              {}, T0 + timedelta(minutes=500))
    again, _ = F.page_for(F.open_streak(F.verdicts(lines + [_line(505, "ERROR", settled=False)]),
                                        T0 + timedelta(minutes=505)),
                          state, T0 + timedelta(minutes=505))
    assert first is not None and again is None, (
        "it paged twice for one standing fork: {!r}".format(again))


def test_a_SECOND_fork_after_a_clear_pages_again():
    """THE DEFECT A BOOLEAN `already_paged` WOULD HAVE. "Still the same fork" and "it closed and
    a new one opened" are different events and the second must page. The state is keyed to the
    streak's START stamp, which tells them apart for free.

    MUTATION: make `page_for` store `{"paged_for_since": True}` instead of the stamp, and the
    second fork below goes silent."""
    first_fork = [_line(i * 5, "REFUSED_CONFLICT", settled=False) for i in range(101)]
    _, state = F.page_for(F.open_streak(F.verdicts(first_fork), T0 + timedelta(minutes=500)),
                          {}, T0 + timedelta(minutes=500))
    closed = first_fork + [_line(505, "RECONCILED", settled=True)]
    cleared, state = F.page_for(F.open_streak(F.verdicts(closed), T0 + timedelta(minutes=505)),
                                state, T0 + timedelta(minutes=505))
    second = closed + [_line(510 + i * 5, "REFUSED_CONFLICT", settled=False) for i in range(101)]
    text, _ = F.page_for(F.open_streak(F.verdicts(second), T0 + timedelta(minutes=1010)),
                         state, T0 + timedelta(minutes=1010))
    assert "CLEARED" in (cleared or ""), "the close of a paged fork was not reported"
    assert text is not None and "CLEARED" not in text, (
        "a second fork, after a clear, did not page: {!r}".format(text))


def test_the_all_clear_only_goes_out_to_someone_who_was_told_there_was_a_problem():
    """MUTATION: page the clear unconditionally, and this reds -- every short streak's ordinary
    close would then buzz a phone."""
    closed = ([_line(i * 5, "GATE_RUNNING", settled=False) for i in range(3)]
              + [_line(20, "FAST_FORWARDED", settled=True)])
    text, sent = _run(closed, now_minute=20)
    assert text is None and sent == [], "an unremarkable close paged: {!r}".format(text)


# ── FAIL-CLOSED: A STOPPED WATCHER IS NOT A CLOSED FORK ─────────────────────────────────────
def test_a_log_that_stopped_being_written_pages_as_STALE_and_never_as_an_all_clear():
    """The two causes of "no recent STILL OPEN line" are "the fork closed" and "the timer
    stopped", and they are indistinguishable from the log alone. Reading the second as the first
    is the fail-silent direction, and it is the direction a naive `if not open: fine` takes.

    MUTATION: drop the `stale` branch in `page_for`, and this reds while nothing else does."""
    lines = ([_line(i * 5, "GATE_RUNNING", settled=False) for i in range(3)]
             + [_line(20, "RECONCILED", settled=True)])
    text, sent = _run(lines, now_minute=20 + F.STALE_MINUTES + 5)
    assert text is not None and "NO FORK VERDICT" in text, (
        "a watcher that stopped writing read as a closed fork: {!r}".format(text))
    assert sent and sent[0][1]["headers"]["X-Tags"] == "rotating_light", (
        "the stale page went out tagged as good news")


def test_an_empty_log_is_stale_and_not_a_clean_bill_of_health():
    """A denominator of zero. MUTATION: return `{"open": False, "stale": False}` for no rows."""
    streak = F.open_streak(F.verdicts([]), T0)
    assert streak["stale"] and not streak["open"], streak


# ── THE PARSE IS A PREDICTION ABOUT ANOTHER MODULE'S OUTPUT ─────────────────────────────────
def test_the_regex_matches_a_line_THE_HOST_ITSELF_WROTE_not_a_hand_typed_copy(tmp_path,
                                                                              monkeypatch):
    """A detector that reads another module's log is only verified by reading a line that module
    actually produced. A hand-typed fixture agrees with itself forever and goes silent the day
    the producer's format moves -- and the silence looks exactly like a closed fork.

    So this drives the REAL `_reconcile_the_fork` through the REAL `_log` and parses what lands
    on disk. MUTATION: change the host's line format (its `"fork with origin ({} behind, ...)"`)
    and this reds, which is the only thing that will."""
    log = tmp_path / "reconcile-watch-log.md"
    monkeypatch.setattr(W, "LOG_FILE", log)
    line = W._reconcile_the_fork(
        state_fn=lambda _p: (32, 3),
        reconcile_fn=lambda _p: {"status": "REFUSED_CONFLICT", "detail": "1 conflicted path(s)"},
        subject_fn=lambda: Path("/somewhere"))
    W._log(line)
    rows = F.verdicts(log.read_text().splitlines())

    assert len(rows) == 1, (
        "the host's own fork line did not parse as a verdict -- the detector is reading a format "
        "that no longer exists: {!r}".format(log.read_text()))
    assert rows[0]["settled"] is False and rows[0]["behind"] == 32 and rows[0]["ahead"] == 3, rows

    settled_line = W._reconcile_the_fork(
        state_fn=lambda _p: (5, 0),
        reconcile_fn=lambda _p: {"status": "FAST_FORWARDED", "detail": "d"},
        subject_fn=lambda: Path("/somewhere"))
    W._log(settled_line)
    rows = F.verdicts(log.read_text().splitlines())
    assert [r["settled"] for r in rows] == [False, True], (
        "the settled/STILL OPEN tag the whole streak is keyed to did not survive the round trip: "
        "{}".format(rows))


def test_the_near_miss_lines_THE_SAME_LEG_WRITES_are_not_counted_as_verdicts():
    """This log carries the drift reconcile, the seat sweeps, the boot-sha report -- and, from
    the fork leg itself, three lines that are ABOUT the fork and are not verdicts of it. The
    UNREADABLE one is the dangerous shape: it carries the words, a bracket and two numbers, and
    differs only in punctuation.

    THE UNREADABLE LINE IS CORRECTLY NOT A VERDICT, and that is a decision rather than an
    oversight. "git would not answer" is not an observation that the fork is open, so it must
    neither extend a streak nor break one. A run of them simply stops fresh verdicts arriving,
    which is exactly the state `STALE` exists to page -- fail-closed, by the route already built.

    MUTATION (must fire): read the tag as settled when it is absent -- `m["tag"] != "STILL OPEN"`
    with no alternation to fail on -- and seven controls here red.

    AND A CORRECTION, kept beside the claim it replaces: the first draft of this test said the
    mutation was "loosen the prefix to `fork` anywhere in the line". That mutation is GREEN, and
    it is green because it is an EQUIVALENCE, not because a control is missing -- what excludes
    every line below is the `(N behind, M ahead) -> STATUS [tag]` shape after the prefix, and the
    prefix carries no work the shape does not already do. Left written down because the flattering
    reading of a green mutation is that the code is fine, and it was not established until the
    mutation was run twice."""
    noise = ["- [2026-09-26 12:34 UTC] reconcile DRIFT (9 alarm(s)); unchanged -> log only",
             "- [2026-09-26 12:34 UTC] fork reconcile failed (reconcile continues): Boom()",
             "- [2026-09-26 12:34 UTC] fork with origin UNREADABLE (behind=None, ahead=3); "
             "not acting on a state that was not observed",
             "- [2026-09-26 12:34 UTC] fork with origin NOT ATTEMPTED: the shared tree could "
             "not be established",
             "  tests/tools/test_level_zero_contradicted_by_its_own_controls.py"]
    assert F.verdicts(noise) == []


@pytest.mark.parametrize("minutes,expect_rc", [(50, 0), (500, 1)])
def test_the_human_door_answers_rc_1_only_when_a_person_is_actually_needed(minutes, expect_rc,
                                                                          monkeypatch, tmp_path):
    """`--check` is what a seat runs by hand, so its rc is a claim. MUTATION: `return 0` always."""
    log = tmp_path / "reconcile-watch-log.md"
    log.write_text("\n".join(
        _line(i * 5, "REFUSED_CONFLICT", settled=False) for i in range(minutes // 5 + 1)))
    monkeypatch.setattr(F, "LOG_FILE", log)
    monkeypatch.setattr(F, "STALE_MINUTES", 10 ** 9)
    assert F.main(["--check"]) == expect_rc


def test_an_OPEN_fork_nobody_has_observed_recently_says_BOTH_things():
    """The two conditions are independent and this is the overlap: the fork is open, and the
    newest verdict about it is older than the watcher's own cadence allows. Either fact alone
    misleads -- the counts without their age invite action on a stale picture, and the staleness
    without the counts throws away the only evidence there is.

    MUTATION (must fire): drop the `if streak["stale"]:` clause from the open branch, and this
    reds while `test_a_log_that_stopped_being_written_pages_as_STALE...` stays green -- they are
    different states and only one of them is reachable in that test."""
    lines = [_line(i * 5, "REFUSED_CONFLICT", settled=False) for i in range(101)]
    text, _ = F.page_for(
        F.open_streak(F.verdicts(lines), T0 + timedelta(minutes=500 + F.STALE_MINUTES + 5)),
        {}, T0 + timedelta(minutes=500 + F.STALE_MINUTES + 5))
    assert text and "OPEN 500 MINUTES" in text and "LAST OBSERVATION" in text, (
        "an open-and-unobserved fork was paged as one or the other: {!r}".format(text))
