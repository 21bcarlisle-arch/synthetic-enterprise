"""The phone watchdog pages on the director's two kinds only, under his limits (ruling, 4 Nov).

Each test names the defect it catches. The first one shows every branch CAN be taken, so a
watchdog that never pages cannot pass the refusal tests below it."""
from datetime import date, datetime

from background import phone_watchdog as w

FAIL = ("- [2026-11-03 {t} UTC] invocation pid=1 exited (rc=1) -- it said: Failed to "
        "authenticate: OAuth session expired and could not be refreshed")
OK = "- [2026-11-04 {t} UTC] invocation pid=2 exited (rc=0)"
FAILING = "\n".join([OK.format(t="09:00:00").replace("11-04", "11-03"),
                     FAIL.format(t="09:16:14"), "- [2026-11-03 09:20 UTC] SPAWNED x",
                     FAIL.format(t="09:26:10")])


def _at(day, hour, minute=0):
    return datetime(2026, 11, day, hour, minute, tzinfo=w.UK).timestamp()


def _incidents(now, log=FAILING, lanes=("worker-tick.timer",), commit=None, today=date(2026, 11, 3)):
    return w.open_incidents(now, tick_log=log, work_commit_epoch=commit if commit is not None else now,
                            lanes=list(lanes), today=today)


def test_every_kind_can_page():
    """MUTANT: an always-closed detector (or a decide() that never sends) passes every refusal."""
    now = _at(3, 10)
    kinds = {**_incidents(now), **_incidents(now, log="", lanes=(), commit=now - 4 * 3600),
             **_incidents(now, log="", today=date(2027, 10, 30))}
    assert {"auth", "stopped", "expiry-30", "expiry-7"} <= set(kinds)
    out, _, _ = w.decide({}, {"auth": kinds["auth"]}, now)
    assert len(out) == 1 and "cannot sign in" in out[0] and "claude setup-token" in out[0]


def test_the_auth_incident_starts_at_the_first_failure_and_one_clean_exit_ends_it():
    """MUTANT: keying on any failure in the log (not the latest exit) never closes the incident."""
    assert w._uk(w.auth_failing_since(FAILING)) == "Tue 3 Nov 09:16"
    assert w.auth_failing_since(FAILING + "\n" + OK.format(t="08:20:00")) is None
    assert w.auth_failing_since("") is None


def test_a_live_lane_or_a_recent_commit_is_not_a_stopped_machine():
    """MUTANT: paging on silence alone pages for quiet that needs no action from him."""
    now = _at(3, 12)
    assert "stopped" not in _incidents(now, log="", commit=now - 10 * 3600)            # timer alive
    assert "stopped" not in _incidents(now, log="", lanes=(), commit=now - 3600)       # too recent
    assert "stopped" not in w.open_incidents(now, tick_log="", work_commit_epoch=now - 9e4,
                                             lanes=None, today=date(2026, 11, 3))  # unreadable


def test_once_per_incident_one_reminder_after_twelve_hours_and_one_all_clear():
    """MUTANT: re-sending each run, or reminding twice, is the spam he ruled out."""
    t0 = _at(3, 9, 30)
    inc = _incidents(t0)
    out, s, _ = w.decide({}, inc, t0)
    assert len(out) == 1
    for h in (1, 6, 11):
        assert w.decide(s, inc, t0 + h * 3600)[0] == []
    out, s, _ = w.decide(s, inc, t0 + 12 * 3600)
    assert len(out) == 1 and out[0].startswith("Still open")
    assert w.decide(s, inc, t0 + 25 * 3600)[0] == []   # 10:30 next day: waking, under cap
    out, s, _ = w.decide(s, {}, _at(4, 8, 30))
    assert len(out) == 1 and out[0].startswith("Recovered") and s["incidents"] == {}


def test_nothing_between_22_and_07_and_the_held_alert_goes_at_seven():
    """MUTANT: an overnight incident paging at 02:00, or being dropped instead of held."""
    night = _at(3, 23)
    inc = _incidents(night)
    out, s, _ = w.decide({}, inc, night)
    assert out == [] and s["incidents"]["auth"]["phoned_at"] is None
    assert w.decide(s, inc, _at(4, 6, 59))[0] == []
    assert len(w.decide(s, inc, _at(4, 7))[0]) == 1


def test_no_more_than_three_in_any_24_hours_and_the_rest_go_to_the_status_page():
    """MUTANT: a per-incident cap, or a cap that drops the message instead of posting it."""
    now = _at(3, 12)
    state = {"sent": [now - 3600, now - 7200, now - 10800]}
    out, s, status = w.decide(state, _incidents(now), now)
    assert out == [] and s["incidents"]["auth"]["capped"]
    assert any("cap" in line and "cannot sign in" in line for line in status)
    assert w.decide({"sent": [now - 25 * 3600] * 3}, _incidents(now), now)[0] != []


def test_each_expiry_warning_goes_once_and_never_clears():
    """MUTANT: a threshold that re-fires daily from day 30 to day 0."""
    now = _at(3, 12)
    inc = _incidents(now, log="", today=date(2027, 10, 10))
    out, s, _ = w.decide({}, inc, now)
    assert len(out) == 1 and "4 Nov 2027" in out[0] and s["done_once"] == ["expiry-30"]
    assert w.decide(s, inc, now + 86400)[0] == []
    out, s, _ = w.decide(s, _incidents(now, log="", today=date(2027, 10, 29)), now + 2 * 86400)
    assert len(out) == 1 and "(6 days)" in out[0]


def test_a_message_is_two_plain_lines():
    """MUTANT: an internal code or a three-paragraph page."""
    for inc in _incidents(_at(3, 10), lanes=(), commit=_at(3, 1)).values():
        lines = w._alert_text(inc).splitlines()
        assert len(lines) == 2 and lines[1].startswith("Fix: ")
        assert "[" not in lines[0] and "_" not in lines[0]
