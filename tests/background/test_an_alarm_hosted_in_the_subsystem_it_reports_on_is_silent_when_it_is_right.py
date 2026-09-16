"""The stretch alarm and the product floor, each on a host that is not the thing it reports on.

THE DEFECT (2026-09-16, the director's question after an 88-commit day with no product in it).

Two controls, one shape, and the shape is not "the control was missing" -- both were built, both
ran, and both were correct every time they ran.

**The stretch alarm.** `raise_stretch_report_owed` was written inside
`background/process_run_complete.py` and that publisher was its ONLY caller. The publisher last
succeeded 2026-09-10 02:35 and not again until 2026-09-16 14:41 -- six days, 34 refused publishes,
184 commits landed with no report. The alarm whose whole purpose is to say *the machine has stopped
telling you why* could not run, because it shared a failure domain with the loudest instance of
that. Its silence was indistinguishable from a healthy machine writing its reports.

**The product floor.** `product_machinery_split` measured 7% product share against a 25% floor and
`main()` returned 0. Its one live consumer composed a clause into a `log()` line. The measurement
fired every cycle, said BELOW FLOOR every cycle, and could not fail.

So the controls here are about HOSTING and CHANNEL, not about the arithmetic -- the arithmetic was
already right and already tested. Each of these fails if the alarm is put back inside the publisher,
if the leaf stops paging, or if the floor goes back to being a sentence.
"""
from __future__ import annotations

import inspect

import pytest

from background import process_run_complete as prc
from background import supervisor
from tools import stretch_log


class _Spy:
    def __init__(self):
        self.calls = []

    def __call__(self, message, **kw):
        self.calls.append((message, kw))
        return "spy-send-id"


# --------------------------------------------------------------------------------------
# The stretch alarm lives in the leaf, and the leaf is what pages.
# --------------------------------------------------------------------------------------

def test_the_alarm_itself_is_in_the_leaf_and_not_in_the_publisher():
    """The implementation moved. A future edit that re-inlines it into the publisher fails here.

    Keyed to the PROPERTY -- "the publisher does not itself page" -- rather than to today's line
    count, because a control pinned to the current text goes red when the code is reorganised
    honestly and stays green when the defect comes back under a new shape.
    """
    assert callable(stretch_log.raise_stretch_report_owed)

    publisher_src = inspect.getsource(prc.raise_stretch_report_owed)
    assert "tools.stretch_log" in publisher_src, (
        "the publisher's copy must delegate to the leaf, not hold the alarm"
    )
    assert "notify_fn(" not in publisher_src, (
        "the publisher is paging in its own body again -- that is the defect this file names: "
        "the alarm would go down with the publisher, exactly when it is right"
    )


def test_the_leaf_pages_when_a_report_is_owed_and_escalation_is_earned():
    spy = _Spy()
    logged = []
    result = stretch_log.raise_stretch_report_owed(log_fn=logged.append, notify_fn=spy)

    # The live tree decides whether a report is owed, so assert the MAPPING from verdict to
    # action rather than today's verdict -- this holds whether the log is current or not.
    if result["owed"] and result.get("paged"):
        assert len(spy.calls) == 1
        msg, kw = spy.calls[0]
        assert "stretch" in msg.lower()
        assert kw["transition_key"] == "stretch-log:report-owed", (
            "an auto-keyed page would be a NEW condition every cycle -- 75 escalation documents "
            "standing for one condition, which is what the explicit key exists to stop"
        )
        assert kw["re_escalate_after"] == 24 * 3600, (
            "still owed a day later is a fresh page; without this a state that cannot change "
            "until someone acts is silenced forever by the first send"
        )
        assert logged, "the LISTING still belongs in the log; the page carries the condition"
    else:
        assert not spy.calls, "nothing owed (or below escalation) must not page"


def test_the_leaf_is_silent_when_the_log_is_up_to_date(monkeypatch):
    """The other half of the partition: it must be ABLE to stay quiet, and for the right reason."""
    spy = _Spy()
    monkeypatch.setattr(stretch_log, "check", lambda: (0, "[stretch-log] up to date."))
    result = stretch_log.raise_stretch_report_owed(log_fn=lambda _m: None, notify_fn=spy)
    assert result == {"owed": False, "logged": False, "paged": False}
    assert not spy.calls


def test_the_leaf_pages_on_a_manufactured_owed_state(monkeypatch):
    """Proves the paging branch is REACHABLE, not merely that the quiet branch is correct.

    A guard that refuses everything passes every test asking whether it refuses correctly. This is
    the leg that would have caught the six-day silence if the host had been sound.
    """
    spy = _Spy()
    monkeypatch.setattr(stretch_log, "check", lambda: (1, "[stretch-log] 184 commit(s) owed"))
    monkeypatch.setattr(stretch_log, "owed", lambda: {
        "owed": True, "escalate": True, "commits": 184, "hours": 139.0,
        "reason": "139h since the last report; and 184 commits since the last report"})
    monkeypatch.setattr(stretch_log, "newest_entry_head", lambda: "deadbeef")

    result = stretch_log.raise_stretch_report_owed(log_fn=lambda _m: None, notify_fn=spy)
    assert result["paged"] is True
    assert len(spy.calls) == 1
    assert spy.calls[0][1]["state"] == "deadbeef", (
        "the STATE is the newest entry's head stamp, so writing a report clears the alarm by "
        "construction rather than by anyone remembering to"
    )


def test_the_supervisor_tick_is_a_second_host_for_the_alarm():
    """Two independent hosts, because neither one's outage may be the alarm's outage.

    This is the whole repair. The publisher keeps its call -- publishing IS when a piece of work
    finishes -- but the tick, which ran through all six days of the wedge, now calls it too.
    """
    ladder_src = inspect.getsource(supervisor._self_refill_draw_ladder)
    assert "raise_stretch_report_owed" in ladder_src, (
        "the tick has stopped hosting the stretch alarm -- the publisher is its only host again, "
        "which is the 10--16 September silence restored"
    )
    assert "from background.process_run_complete import" not in ladder_src, (
        "ASK THE LEAF, NOT THE PUBLISHER (supervisor.py ~line 167): importing the publish path "
        "here enrols the whole harness suite in the publish gate"
    )


# --------------------------------------------------------------------------------------
# The product floor pages on a crossing instead of composing a sentence.
# --------------------------------------------------------------------------------------

def _fake_split(*, share, classified=95, enough=True, below=None):
    return {
        "window": 100, "product": round(share * classified), "machinery": classified,
        "neither": 5, "classified": classified, "product_share": share,
        "enough_to_judge": enough,
        "below_floor": (share < 0.25) if below is None else below,
        "floor": 0.25,
    }


@pytest.mark.parametrize("share,expected_state", [(0.07, "below"), (0.40, "ok")])
def test_the_floor_pages_on_both_crossings(monkeypatch, share, expected_state):
    """Below floor AND recovery both send, and they are DIFFERENT states so the key transitions.

    Recovery pages deliberately: a control that only ever speaks bad news teaches its reader that
    silence is good news, and this project's evidence is that silence is the default state of a
    broken control.
    """
    import tools.product_machinery_split as pms
    monkeypatch.setattr(pms, "split", lambda window=100: _fake_split(share=share))
    spy = _Spy()
    sent = supervisor._page_product_floor_crossing(notify_fn=spy)

    assert sent == "spy-send-id"
    assert len(spy.calls) == 1
    msg, kw = spy.calls[0]
    assert kw["state"] == expected_state
    assert kw["transition_key"] == "product-machinery:floor", (
        "one key for one condition -- a share wobbling 6%-8% below the floor must be ONE page, "
        "not a fresh one every tick, or this becomes the treadmill the canon forbids"
    )
    assert kw["re_escalate_after"] == 24 * 3600, (
        "a floor that pages once and then goes quiet is the failure this exists to end"
    )
    if expected_state == "below":
        assert "BELOW FLOOR" in msg and "7%" in msg


def test_the_floor_is_silent_on_a_sample_too_thin_to_judge(monkeypatch):
    """'Not enough work to judge' and 'the ratio is fine' are different states, and neither pages.

    Fails closed toward silence here on purpose: a floor that pages on a fresh clone with nine
    commits in it is a floor nobody leaves switched on.
    """
    import tools.product_machinery_split as pms
    monkeypatch.setattr(pms, "split",
                        lambda window=100: _fake_split(share=0.07, classified=3, enough=False))
    spy = _Spy()
    assert supervisor._page_product_floor_crossing(notify_fn=spy) is None
    assert not spy.calls


def test_the_floor_check_cannot_take_down_the_draw(monkeypatch):
    """A measurement that refuses must not become a gate on choosing work.

    The mirror of the fail-closed rule, and the right way round for THIS control: an unreadable
    split is a finding about the split, never a reason the tick draws nothing.
    """
    import tools.product_machinery_split as pms

    def _boom(window=100):
        raise RuntimeError("git unavailable")

    monkeypatch.setattr(pms, "split", _boom)
    spy = _Spy()
    assert supervisor._page_product_floor_crossing(notify_fn=spy) is None
    assert not spy.calls


def test_the_tick_asks_the_floor_every_cycle():
    """Canon 2026-09-05 §4: the ratio itself becomes a finding when it goes wrong.

    An unwired mechanism has no red state -- an ARMED function nobody calls reads as
    running-and-finding-nothing, which is precisely how 7% stood for days.
    """
    ladder_src = inspect.getsource(supervisor._self_refill_draw_ladder)
    assert "_page_product_floor_crossing()" in ladder_src
