"""THE FINDING FIRED 75 TIMES AND NOBODY SAW ONE OF THEM.

Director, 2026-09-10: *"Three days, 100 commits, and no stretch report since 7 September -- the
mechanism you built to stop exactly this has silently stopped. Third instance of that class."*

It had not stopped. `tools/stretch_log.check()` ran on every publish cycle across those three days
and returned rc 1 every time, correctly, naming the commits. Every one of those findings went to
`log()`, which appends to `docs/observability/sim-runner-log.md` -- 250,269 lines of routine
progress chatter. **The mechanism was loud; its channel had no reader.**

That is the class, and it is not "an unwired mechanism has no red state" (this one had one) nor
"a control keyed to a structure that moved" (nothing moved). It is a third shape: a finding written
where the routine output goes is routine output.

This file holds the CONSUMER. The instrument's own properties are in
`tests/tools/test_stretch_log.py`.
"""
from __future__ import annotations

import pytest

import background.process_run_complete as prc
from tools import stretch_log as sl


class _Spy:
    def __init__(self):
        self.calls = []

    def __call__(self, message, **kw):
        self.calls.append((message, kw))
        return "sent:test"


def _owed(escalate, reason="253 commits since the last report", commits=253, hours=68.0):
    return {"owed": True, "escalate": escalate, "commits": commits,
            "hours": hours, "reason": reason}


def test_an_escalating_gap_reaches_the_alarm_channel_and_not_only_the_run_log(monkeypatch):
    """THE DEFECT ITSELF. Three days of owed reports produced 75 log lines and zero pages.

    MUTATION: delete the `notify_fn(...)` call in `raise_stretch_report_owed` and this fails while
    the log line -- the only thing that existed before -- still happens. That is precisely the state
    the director found.
    """
    monkeypatch.setattr(sl, "check", lambda: (1, "[stretch-log] 253 commit(s) ...\n    abc land it"))
    monkeypatch.setattr(sl, "owed", lambda: _owed(escalate=True))
    monkeypatch.setattr(sl, "newest_entry_head", lambda: "39a410f0d46c")
    logged, spy = [], _Spy()

    out = prc.raise_stretch_report_owed(log_fn=logged.append, notify_fn=spy)

    assert out["paged"] is True
    assert len(spy.calls) == 1, "the finding did not reach the alarm channel"
    assert logged, "the run-log listing was dropped -- it says what the report is owed ABOUT"


def test_an_ordinary_between_pieces_gap_does_not_page(monkeypatch):
    """REACHABILITY OF THE QUIET BRANCH, and the reason the threshold exists at all.

    A report is written when a piece of work FINISHES, so a handful of commits with no entry yet is
    the machine working, not a defect. Without this leg the repair pages on every publish cycle
    forever, which is how an alarm channel acquires no reader in the first place -- and this test
    is what stops the fix from recreating the disease one level up.
    """
    monkeypatch.setattr(sl, "check", lambda: (1, "[stretch-log] 3 commit(s) ..."))
    monkeypatch.setattr(sl, "owed", lambda: _owed(escalate=False, commits=3, hours=2.0,
                                                  reason="3 commit(s) owed, inside the ordinary range"))
    logged, spy = [], _Spy()

    out = prc.raise_stretch_report_owed(log_fn=logged.append, notify_fn=spy)

    assert out["owed"] is True and out["paged"] is False
    assert spy.calls == []
    assert logged, "the finding must still be visible in the run log even when it does not page"


def test_up_to_date_is_silent_on_both_channels(monkeypatch):
    monkeypatch.setattr(sl, "check", lambda: (0, "[stretch-log] up to date."))
    logged, spy = [], _Spy()

    out = prc.raise_stretch_report_owed(log_fn=logged.append, notify_fn=spy)

    assert out == {"owed": False, "logged": False, "paged": False}
    assert logged == [] and spy.calls == []


def test_the_page_is_keyed_to_the_CONDITION_and_not_to_its_rotating_commit_list(monkeypatch):
    """28 DOCUMENTS THAT WERE 2 CONDITIONS, one channel over, and the same cause.

    `notify`'s auto-key runs the message through `alarm_repetition.normalise()`, which strips
    numbers, elapsed times and hashes out of an alarm's identity -- but NOT prose. The check's
    message carries twelve commit subjects that change on every cycle, so an auto-keyed page would
    be a new condition each time: no suppression, no escalation, and one staged finding document
    per publish. Seventy-five of them, for one condition.

    MUTATION: drop `transition_key=` and this fails. Drop the explicit `state=` and the escalation
    still works but nothing clears it when a report is written.
    """
    monkeypatch.setattr(sl, "check", lambda: (1, "[stretch-log] 253 commit(s) ..."))
    monkeypatch.setattr(sl, "owed", lambda: _owed(escalate=True))
    monkeypatch.setattr(sl, "newest_entry_head", lambda: "39a410f0d46c")
    spy = _Spy()

    prc.raise_stretch_report_owed(log_fn=lambda _m: None, notify_fn=spy)

    message, kw = spy.calls[0]
    assert kw["transition_key"] == "stretch-log:report-owed"
    assert kw["state"] == "39a410f0d46c", (
        "the state must be the newest entry's head stamp, so WRITING A REPORT clears the alarm "
        "by construction rather than by anyone remembering to")
    assert kw["kind"] == "real_alarm"
    assert kw["re_escalate_after"] == 24 * 3600
    assert "abc" not in message and "commit(s) have landed" not in message, (
        "the rotating commit listing must stay OUT of the page text or the condition's identity "
        "changes every cycle")


def test_writing_a_report_changes_the_state_so_the_alarm_clears_itself(monkeypatch):
    """THE CLEARING LEG. An alarm nobody can clear is an alarm everyone learns to ignore."""
    monkeypatch.setattr(sl, "check", lambda: (1, "[stretch-log] 253 commit(s) ..."))
    monkeypatch.setattr(sl, "owed", lambda: _owed(escalate=True))
    spy = _Spy()

    monkeypatch.setattr(sl, "newest_entry_head", lambda: "aaaaaaaaaaaa")
    prc.raise_stretch_report_owed(log_fn=lambda _m: None, notify_fn=spy)
    monkeypatch.setattr(sl, "newest_entry_head", lambda: "bbbbbbbbbbbb")
    prc.raise_stretch_report_owed(log_fn=lambda _m: None, notify_fn=spy)

    assert spy.calls[0][1]["state"] != spy.calls[1][1]["state"]


def test_the_real_notify_accepts_what_this_caller_passes():
    """A CALLER THAT PASSES A KIND OR topic_class THE CONTRACT REJECTS RAISES INSIDE A `try:` THAT
    SWALLOWS IT, and the finding is silent again through a brand-new door.

    `notify` raises ValueError on an unknown `kind`, and the publish step wraps this whole call in
    `except Exception: log(...)`. So the two enumerations are checked against the real module here
    rather than against a spy that accepts anything.
    """
    import inspect

    from background import notify as notify_mod

    assert "real_alarm" in notify_mod.KINDS, notify_mod.KINDS
    params = inspect.signature(notify_mod.notify).parameters
    for arg in ("kind", "transition_key", "state", "re_escalate_after", "topic_class"):
        assert arg in params, f"notify has no {arg} parameter -- this caller would raise"
    # `action_needed` is an INSTANT class. The deferrable classes are BATCHED into the periodic
    # digest, which is another quiet channel, and a three-day silence is not digest material.
    assert "action_needed" in (notify_mod.notify.__doc__ or "")


@pytest.mark.parametrize("verdict_reason", [
    "the log file does not exist",
    "the newest entry carries no head stamp",
    "the head stamp is unreachable: ...",
])
def test_an_unmeasurable_gap_pages_rather_than_going_quiet(monkeypatch, verdict_reason):
    """FAIL-CLOSED AT THE CONSUMER TOO. Three ways the gap becomes unmeasurable, and all three used
    to be indistinguishable from "nothing is owed" somewhere along this path."""
    monkeypatch.setattr(sl, "check", lambda: (1, "[stretch-log] unmeasurable"))
    monkeypatch.setattr(sl, "owed", lambda: {"owed": True, "escalate": True, "commits": None,
                                             "hours": None, "reason": verdict_reason})
    monkeypatch.setattr(sl, "newest_entry_head", lambda: None)
    spy = _Spy()

    out = prc.raise_stretch_report_owed(log_fn=lambda _m: None, notify_fn=spy)

    assert out["paged"] is True
    assert verdict_reason.rstrip(". ") in spy.calls[0][0]
