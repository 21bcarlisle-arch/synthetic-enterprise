"""R15 on the PROPOSAL side of a `since_field`: an unrecordable proposal did not survive the
guard, it WON.

THE NAMED DEFECT. `guard_episode` screened the PRIOR side of a low-water episode start
(`_is_start_to_remember`, 2026-09-04) and deliberately not the proposal, on the stated ground that
screening the proposal "could turn a data-dependent value into a silent field-clear, which is the
under-reporting the whole class exists to cure". Measured, that ground was backwards. `since_fields`
is LOW-water -- earliest wins -- so `0` is the earliest instant orderable and therefore beat a
healthy 2026 start outright:

    guard_episode({"t": 1.7e9}, {"t": 0}, since_fields=("t",))            -> {"t": 0}
    guard_episode({"t": "2026-09-04T10:00"}, {"t": "1970-01-01T00:00"})   -> {"t": "1970-01-01..."}

and the three carriers that echo their own proposal off disk re-proposed it on every write, so the
1970 was permanent. Screening the proposal is therefore the OPPOSITE of a field-clear: with a start
on the prior side, the prior now stands.

Both directions, per R15:
  * FIRES  -- the unrecordable proposal no longer takes the field, at the guard and at all three
              carriers, and the RUNG 1d page that read one of them no longer clears its bar on it.
  * SILENT -- an honest earlier proposal still wins, an evidenced close still clears, and a
              MISDECLARED proposal still raises. The new screen is asked only of values the guard
              could already order, so it must not have swallowed the type refusal beside it.

Pre-registration and the measurements above:
docs/staging/SEAT_PREREGISTRATION_WHAT_THE_UNSCREENED_PROPOSAL_SIDE_OF_A_SINCE_FIELD_ACTUALLY_DOES_2026-09-04.md
"""
from __future__ import annotations

import json

import pytest

from background.episode_monotonic import EpisodeFieldTypeError, guard_episode

SINCE = ("t",)

GOOD = 1_700_000_000.0        # a 2026-era epoch: an instant something here could have recorded
GOOD_ISO = "2026-09-04T10:00:00+00:00"

#: Values that are ORDERABLE but name no instant anything here recorded. `True` and `NaN` are
#: deliberately NOT in this list -- they are unorderable and were already refused, and the leg
#: below that asserts they still raise is what keeps that true.
NO_START_PROPOSALS = [0, 0.0, -1, -86_400.0, "1970-01-01T00:00:00+00:00", "1969-12-31T23:00:00Z"]


# --------------------------------------------------------------------------- FIRES

@pytest.mark.parametrize("proposal", NO_START_PROPOSALS)
def test_an_unrecordable_proposal_does_not_beat_a_recorded_start(proposal):
    """The headline. Before the screen, every one of these took the field off a live 2026 episode
    and dated it to 1970 -- because on a low-water field the epoch is the strongest value there
    is."""
    prior = GOOD_ISO if isinstance(proposal, str) else GOOD
    out = guard_episode({"t": prior}, {"t": proposal}, since_fields=SINCE)
    assert out["t"] == prior, (
        f"a proposal of {proposal!r} took the field from a recorded start -- the low-water rule is "
        f"now remembering a 1970 nobody recorded, which is the defect this guard exists to cure "
        f"wearing the other coat")


@pytest.mark.parametrize("proposal", NO_START_PROPOSALS)
def test_with_no_start_on_either_side_the_field_says_so(proposal):
    """The durability half. With nothing to remember on the prior side the guard used to write the
    unrecordable proposal straight through, so it was on disk to be re-proposed forever -- and to
    be read as an established episode by the next hand-rolled `isinstance` test that met it. There
    were three of those. `None` is the same fact the value already meant, said in the one spelling
    every reader in this repo understands."""
    for prior in (None, 0, -5, "1970-01-01T00:00:00+00:00"):
        out = guard_episode({"t": prior}, {"t": proposal}, since_fields=SINCE)
        assert out["t"] is None, (
            f"prior={prior!r} proposal={proposal!r} persisted as {out['t']!r}: a value nobody "
            f"recorded is still on disk claiming to be an episode start")


def test_a_carried_forward_zero_cannot_outlive_one_write():
    """The mechanism the three carriers actually ran: read the field, propose it back, write. The
    2026-09-04 measurement of this loop, before the screen, was that `0` survived every round."""
    state = {"t": 0}
    for _ in range(5):
        state = guard_episode(state, {"t": state.get("t")}, since_fields=SINCE)
    assert state["t"] is None, "the echo loop is still refuelling itself from its own bad value"


# --------------------------------------------------------------------------- SILENT

def test_an_honest_earlier_proposal_still_wins():
    """The low-water rule itself, which the screen must not have eaten. This is the whole point of
    the guard: a genuinely earlier start REPLACES a later one."""
    out = guard_episode({"t": 5000.0}, {"t": 1000.0}, since_fields=SINCE)
    assert out["t"] == 1000.0


def test_an_evidenced_close_still_clears_a_recorded_start():
    out = guard_episode({"t": GOOD}, {"t": None}, since_fields=SINCE, episode_closed=True)
    assert out["t"] is None


def test_an_absent_proposal_still_keeps_an_open_episode():
    """Unchanged: a failure that proposes nothing must not clear a start. The new screen routes
    the numeric form of that same assertion to this same answer, and must not have moved this one."""
    out = guard_episode({"t": GOOD}, {"t": None}, since_fields=SINCE)
    assert out["t"] == GOOD


@pytest.mark.parametrize("proposal", ["banana", True, float("nan"), float("inf"), [], {}])
def test_a_misdeclared_proposal_still_raises_and_is_not_silently_cleared(proposal):
    """THE THING THIS CHANGE COULD HAVE BROKEN, and the reason the screen is asked only of values
    `_episode_key` could already order.

    `EpisodeFieldTypeError` on a proposal the guard cannot order is a deterministic property of the
    CALL SITE -- it is the only thing standing between "wired this field in" and a no-op that
    reviews as protection. A screen that swallowed these into a quiet field-clear would delete that
    signal and would be indistinguishable, in every other test in this file, from the change that
    was wanted."""
    with pytest.raises(EpisodeFieldTypeError):
        guard_episode({"t": GOOD}, {"t": proposal}, since_fields=SINCE)


def test_the_proposal_screen_did_not_swallow_the_guard_it_lives_in():
    """REACHABILITY / null control over the whole partition, in ONE place.

    `_asserts_no_start` returning True unconditionally would pass every FIRES leg above while
    deleting the guard: every proposal would become a clear, and the prior would win forever --
    including over an honest earlier start, which is the ONE move the guard exists to allow.
    Returning False unconditionally restores the defect. So assert all four outcomes are distinct
    and each attainable from here."""
    prior_stands = guard_episode({"t": GOOD}, {"t": 0}, since_fields=SINCE)["t"]
    clears = guard_episode({"t": 0}, {"t": 0}, since_fields=SINCE)["t"]
    earlier_wins = guard_episode({"t": 5000.0}, {"t": 1000.0}, since_fields=SINCE)["t"]
    later_loses = guard_episode({"t": 1000.0}, {"t": 5000.0}, since_fields=SINCE)["t"]

    assert prior_stands == GOOD
    assert clears is None
    assert earlier_wins == 1000.0, "every proposal is being read as a clear -- the guard is a no-op"
    assert later_loses == 1000.0
    assert len({prior_stands, clears, earlier_wins}) == 3


# --------------------------------------------------------------------------- WIRED, not just built

def test_the_producer_carrier_no_longer_adopts_a_value_that_is_not_a_start(tmp_path):
    """`sim_runner.record_run_outcome` screened its adoption with `isinstance(first, (int, float))`
    -- which accepts `0` (a truncated write) and `True` (an int in Python). Both were adopted and
    persisted. It asks `recorded_instant_seconds` now, which is what the field's own module asks."""
    now = 1_788_000_000.0
    for bad in (0, -1, True, None, "banana"):
        p = tmp_path / f"producer_{bad!r}.json"
        p.write_text(json.dumps({"last_result": "failed", "consecutive_failures": 3,
                                 "first_failure_ts": bad, "last_failure_ts": now - 60}))
        from background import sim_runner
        st = sim_runner.record_run_outcome(ok=False, detail="x", state_path=p, now=now)
        assert st["first_failure_ts"] == now, (
            f"a persisted {bad!r} was adopted as the streak start -- RUNG 1d measures the outage "
            f"from this field")


def test_the_producer_carrier_still_remembers_a_real_streak_start(tmp_path):
    """The SILENT leg of the one above: the whole reason that field is preserved across failures is
    that re-stamping it every round pins the measured age near zero and the rung never fires."""
    now = 1_788_000_000.0
    started = now - 9_999
    p = tmp_path / "producer_good.json"
    p.write_text(json.dumps({"last_result": "failed", "consecutive_failures": 3,
                             "first_failure_ts": started, "last_failure_ts": now - 60}))
    from background import sim_runner
    st = sim_runner.record_run_outcome(ok=False, detail="x", state_path=p, now=now)
    assert st["first_failure_ts"] == started


def _rung_1d(tmp_path, first_ts, now):
    from background import supervisor
    p = tmp_path / f"state_{first_ts!r}.json"
    p.write_text(json.dumps({"last_result": "failed", "consecutive_failures": 4,
                             "first_failure_ts": first_ts, "last_failure_ts": now - 60,
                             "detail": "synthetic"}))
    reports = tmp_path / "reports"
    reports.mkdir(exist_ok=True)
    return supervisor._producer_starved_active(
        now=now, state_path=p, reports_dir=reports,
        hold_flag=tmp_path / "no_such_hold", oom_clause_fn=lambda: None)


@pytest.mark.parametrize("bad", [0, -1, True])
def test_rung_1d_does_not_clear_its_thirty_minute_bar_on_a_stamp_nobody_recorded(tmp_path, bad):
    """THE PRIORITY ZERO PAGE, and the fifth hand-roll of one question.

    `outage = (now - first_ts) if isinstance(first_ts, (int, float)) else 0.0` gave 496,815 hours
    for every value here -- measured. The silly figure in the prose is not the harm. The harm is
    that `outage > PRODUCER_STARVED_MIN_AGE_SECONDS` was then satisfied by the broken stamp ALONE,
    so a producer that had failed three times in two minutes paged the director at priority zero
    as a 30-minute starvation. An outage nobody recorded is not an outage over the bar."""
    import time
    assert _rung_1d(tmp_path, bad, time.time()) is None, (
        f"first_failure_ts={bad!r} still reaches the priority-zero draw")


def test_rung_1d_still_fires_on_a_real_producer_outage(tmp_path):
    """The SILENT leg. A rung that could only stay quiet is as ignored as a blind one, and
    suppressing a real starvation is the failure this rung was built for (2026-08-17)."""
    import re
    import time
    now = time.time()
    msg = _rung_1d(tmp_path, now - 4 * 3600, now)
    assert msg is not None, "the real producer outage no longer draws"
    assert re.search(r"over 4\.0h", msg), msg


def test_the_ntfy_carrier_restamps_and_its_rendered_string_is_never_inherited(tmp_path,
                                                                              monkeypatch):
    """The director's ONLY channel. Its proposal was `previous.get("since_epoch", now)`, echoed
    straight off disk, and its rendered `since` was echoed the same way -- so a persisted
    `{since_epoch: 0, since: "1970-01-01T00:00:00Z"}` survived a failure write with BOTH fields
    intact. ONE NAME, ONE NUMBER: the string is derived from the carrier or it is None."""
    from background import ntfy_utils
    state_file = tmp_path / "delivery_state.json"
    state_file.write_text(json.dumps({"delivered": False, "since": "1970-01-01T00:00:00Z",
                                      "since_epoch": 0, "consecutive_failures": 5}))
    monkeypatch.setattr(ntfy_utils, "DELIVERY_STATE_FILE", state_file)
    monkeypatch.setattr(ntfy_utils, "DELIVERY_LOG_FILE", tmp_path / "delivery_log.md")

    ntfy_utils.record_delivery_outcome(False, "synthetic drop")

    out = json.loads(state_file.read_text())
    assert out["since_epoch"] > 0, "the persisted zero is still the deafness episode's start"
    assert not str(out["since"]).startswith("1970"), (
        "the rendered start was inherited from disk rather than derived from the carrier beside it")


def test_the_ntfy_rendered_string_refuses_to_assert_a_start_the_carrier_does_not_have(
        tmp_path, monkeypatch):
    """THE BACKSTOP LEG, INJECTED because today's data cannot reach it.

    With the proposal screened above, `guard_episode` can only hand this call site a recorded
    instant, so `state["since"] = ... if _guarded_epoch is not None else None` has an unreachable
    `else`. A mutation that changed that `else` to re-inherit `previous`'s string survived the
    whole suite -- an EQUIVALENCE, not a missing test, and the rule says establish which rather
    than assume the flattering one.

    Establishing it is not the same as leaving it unprovable. The condition is injected: an
    upstream regression that let an unrecordable carrier through must NOT produce a rendered start
    beside it, and this is the leg that says so. It is the whole finding, one field over."""
    from background import episode_monotonic, ntfy_utils
    state_file = tmp_path / "delivery_state.json"
    state_file.write_text(json.dumps({"delivered": False, "since": "1970-01-01T00:00:00Z",
                                      "since_epoch": 0, "consecutive_failures": 5}))
    monkeypatch.setattr(ntfy_utils, "DELIVERY_STATE_FILE", state_file)
    monkeypatch.setattr(ntfy_utils, "DELIVERY_LOG_FILE", tmp_path / "delivery_log.md")
    monkeypatch.setattr(episode_monotonic, "guard_episode",
                        lambda prev, new, **kw: dict(new, since_epoch=0))

    ntfy_utils.record_delivery_outcome(False, "synthetic drop")

    out = json.loads(state_file.read_text())
    assert out["since"] is None, (
        f"the carrier holds {out['since_epoch']!r} -- no recorded start -- and the rendered field "
        f"beside it says {out['since']!r}. One name, one number: it may be derived or absent, "
        f"never inherited")


def test_the_ntfy_carrier_still_remembers_a_long_open_deafness_episode(tmp_path, monkeypatch):
    """The SILENT leg, and the one that matters most: this whole class exists because a 25-hour
    outage paged as "paused 30 seconds ago". The screen must not have re-opened that."""
    import time

    from background import ntfy_utils
    started = time.time() - 25 * 3600
    state_file = tmp_path / "delivery_state.json"
    state_file.write_text(json.dumps({"delivered": False, "since": "2026-09-03T09:00:00Z",
                                      "since_epoch": started, "consecutive_failures": 5}))
    monkeypatch.setattr(ntfy_utils, "DELIVERY_STATE_FILE", state_file)
    monkeypatch.setattr(ntfy_utils, "DELIVERY_LOG_FILE", tmp_path / "delivery_log.md")

    ntfy_utils.record_delivery_outcome(False, "synthetic drop")

    out = json.loads(state_file.read_text())
    assert out["since_epoch"] == started, "a 25-hour deafness episode was restamped to now"
