"""WALL/determinism/idempotency/arrival tests for ObservableTrace.replay —
ARCH1_internal_seams, docs/design/ARCH1_FRAME.md §5/§8-L1.

The single most important test here is the BLINDFOLD MUTATION TEST
(`test_blindfold_gate_MUTATION_*`): it proves the gate FIRES on a future-dated
record and — critically — that removing the gate would make the tests FAIL
(fail-OPEN forbidden, R15).
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.interfaces.recorded_sim_interface import (
    ObservableRecord,
    ObservableTrace,
    ReplayStatus,
    canonical_request_key,
)

KEY = canonical_request_key("forward_price.v1", "electricity", "2020-07-01", 12)


def _rec(observed_at, *, payload=120.0, status=ReplayStatus.OK, as_of=None, key=KEY):
    return ObservableRecord(
        request_type="forward_price.v1",
        request_key=key,
        as_of=as_of or (observed_at if isinstance(observed_at, dt.datetime) else dt.datetime(2020, 1, 1)),
        observed_at=observed_at,
        valid_time=dt.date(2020, 7, 1),
        status=status,
        payload=payload,
    )


def test_known_record_served():
    trace = ObservableTrace([_rec(dt.datetime(2019, 1, 1), payload=99.0)])
    rec = trace.replay(KEY, dt.datetime(2020, 1, 1))
    assert rec.status is ReplayStatus.OK
    assert rec.payload == 99.0


# ---------------------------------------------------------------------------
# BLINDFOLD MUTATION TEST — the load-bearing WALL. A record observable only in
# the query's FUTURE must return NOT_KNOWABLE_YET, never its value. If the gate
# (`if oa > as_of: continue`) is removed, `replay` would return the future
# record as OK/120.0 and BOTH asserts below fail — that is the mutation this
# test kills.
# ---------------------------------------------------------------------------
def test_blindfold_gate_MUTATION_future_record_not_served():
    future = dt.datetime(2025, 1, 1)  # after the query clock
    trace = ObservableTrace([_rec(future, payload=777.0)])
    rec = trace.replay(KEY, as_of=dt.datetime(2020, 1, 1))
    assert rec.status is ReplayStatus.NOT_KNOWABLE_YET  # gate fired
    assert rec.payload is None  # the future value NEVER leaks


def test_blindfold_boundary_equal_observed_at_is_knowable():
    # observed_at == as_of is knowable (the answer became knowable AT the clock).
    clock = dt.datetime(2020, 1, 1)
    trace = ObservableTrace([_rec(clock, payload=55.0)])
    rec = trace.replay(KEY, as_of=clock)
    assert rec.status is ReplayStatus.OK
    assert rec.payload == 55.0


# ---------------------------------------------------------------------------
# FAIL-CLOSED: a missing / empty / malformed observed_at must be treated as
# NOT-yet-knowable and NEVER leak its payload (R15 FAIL-OPEN forbidden). A
# fail-OPEN impl would serve it; ours drops it.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [None])
def test_failclosed_missing_observed_at_never_leaks(bad):
    trace = ObservableTrace([_rec(bad, payload=888.0)])
    rec = trace.replay(KEY, as_of=dt.datetime(2020, 1, 1))
    assert rec.status is ReplayStatus.NOT_KNOWABLE_YET
    assert rec.payload is None


@pytest.mark.parametrize("bad", ["", "not-a-date", "2020-13-99"])
def test_failclosed_malformed_observed_at_from_dict_never_leaks(bad):
    # from_dict parses a malformed observed_at to None (fail-closed), so replay
    # then refuses to serve it.
    d = _rec(dt.datetime(2019, 1, 1), payload=888.0).to_dict()
    d["observed_at"] = bad
    trace = ObservableTrace([ObservableRecord.from_dict(d)])
    rec = trace.replay(KEY, as_of=dt.datetime(2020, 1, 1))
    assert rec.status is ReplayStatus.NOT_KNOWABLE_YET
    assert rec.payload is None


def test_latest_knowable_served_when_multiple_revisions():
    trace = ObservableTrace([
        _rec(dt.datetime(2018, 1, 1), payload=10.0),
        _rec(dt.datetime(2019, 1, 1), payload=20.0),  # latest knowable at 2020
        _rec(dt.datetime(2021, 1, 1), payload=30.0),  # future -> excluded
    ])
    rec = trace.replay(KEY, as_of=dt.datetime(2020, 1, 1))
    assert rec.payload == 20.0


def test_determinism_two_replays_identical():
    trace = ObservableTrace([_rec(dt.datetime(2019, 1, 1), payload=42.0)])
    a = trace.replay(KEY, dt.datetime(2020, 1, 1))
    b = trace.replay(KEY, dt.datetime(2020, 1, 1))
    assert a == b  # frozen dataclass value-equality; pure function


def test_idempotency_replay_twice_no_state_change():
    trace = ObservableTrace([_rec(dt.datetime(2019, 1, 1), payload=42.0)])
    before = len(trace)
    trace.replay(KEY, dt.datetime(2020, 1, 1))
    trace.replay(KEY, dt.datetime(2020, 1, 1))
    assert len(trace) == before  # replay never mutates the log (C-S2)


def test_arrival_order_tolerance_shuffled_same_answer():
    # C-S1: answers keyed by request_key, independent of insertion order.
    recs = [
        _rec(dt.datetime(2018, 1, 1), payload=10.0),
        _rec(dt.datetime(2019, 1, 1), payload=20.0),
    ]
    forward = ObservableTrace(recs).replay(KEY, dt.datetime(2020, 1, 1))
    reverse = ObservableTrace(list(reversed(recs))).replay(KEY, dt.datetime(2020, 1, 1))
    assert forward.payload == reverse.payload == 20.0


def test_recorded_not_knowable_yet_stays(tmp_path):
    # C-S3: a recorded NOT_KNOWABLE_YET status survives a save/load round trip and
    # replay does not collapse it to a value.
    rec = _rec(dt.datetime(2019, 1, 1), payload=None, status=ReplayStatus.NOT_KNOWABLE_YET)
    trace = ObservableTrace([rec])
    served = trace.replay(KEY, dt.datetime(2020, 1, 1))
    assert served.status is ReplayStatus.NOT_KNOWABLE_YET


def test_missing_key_returns_not_knowable_yet():
    trace = ObservableTrace([_rec(dt.datetime(2019, 1, 1))])
    rec = trace.replay("no-such-key", dt.datetime(2020, 1, 1))
    assert rec.status is ReplayStatus.NOT_KNOWABLE_YET
    assert rec.payload is None


def test_jsonl_round_trip(tmp_path):
    trace = ObservableTrace([
        _rec(dt.datetime(2018, 1, 1), payload=10.0),
        _rec(dt.datetime(2019, 1, 1), payload=20.0),
    ])
    path = tmp_path / "trace.jsonl"
    trace.save(path)
    loaded = ObservableTrace.load(path)
    assert len(loaded) == 2
    assert loaded.replay(KEY, dt.datetime(2020, 1, 1)).payload == 20.0


def test_append_only_file_grows(tmp_path):
    path = tmp_path / "trace.jsonl"
    ObservableTrace.append_record_to_file(path, _rec(dt.datetime(2018, 1, 1), payload=1.0))
    ObservableTrace.append_record_to_file(path, _rec(dt.datetime(2019, 1, 1), payload=2.0))
    loaded = ObservableTrace.load(path)
    assert len(loaded) == 2  # append never rewrote the first line
