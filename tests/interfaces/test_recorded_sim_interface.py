"""RecordedSimInterface + composition + capture-tool + gap + publish-refusal
tests — ARCH1_internal_seams, docs/design/ARCH1_FRAME.md §4/§5/§6/§8.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.interfaces.recorded_sim_interface import (
    GapMeasurement,
    NotKnowableYet,
    ObservableTrace,
    RecordedRunPublishRefused,
    RecordedSimInterface,
    ReplayStatus,
    canonical_request_key,
    fitness_gap,
    refuse_publish_if_recorded,
)
from company.interfaces.sim_interface import (
    LiveSimInterface,
    SimInterface,
    StubSimInterface,
    build_sim_interface,
)
from tools.observable_trace_capture import (
    ForwardPriceQuery,
    build_queries,
    capture_trace,
)

FUEL = "electricity"
DELIVERY = "2020-07-01"
TERM = 12
KEY = canonical_request_key("forward_price.v1", FUEL, DELIVERY, TERM)


def _capture_stub_trace(as_of=dt.datetime(2019, 1, 1)):
    """A small deterministic trace captured from a StubSimInterface (get_forward_
    price -> 120.0 for electricity)."""
    stub = StubSimInterface()
    queries = [ForwardPriceQuery(FUEL, DELIVERY, as_of=as_of, term_months=TERM)]
    return capture_trace(stub, queries)


# ---------------------------------------------------------------------------
# Protocol / drop-in compatibility
# ---------------------------------------------------------------------------
def test_is_a_siminterface():
    mock = RecordedSimInterface(ObservableTrace())
    assert isinstance(mock, SimInterface)


def test_exogenous_replayed_after_clock_set():
    trace = _capture_stub_trace(as_of=dt.datetime(2019, 1, 1))
    mock = RecordedSimInterface(trace, as_of=dt.datetime(2020, 1, 1))
    assert mock.get_forward_price(FUEL, DELIVERY, term_months=TERM) == 120.0


# ---------------------------------------------------------------------------
# BLINDFOLD at the typed-method level: no clock set -> FAIL CLOSED (NotKnowableYet
# raised, never a leaked price). And a clock BEFORE the observed_at -> refused.
# ---------------------------------------------------------------------------
def test_no_clock_fails_closed():
    trace = _capture_stub_trace(as_of=dt.datetime(2019, 1, 1))
    mock = RecordedSimInterface(trace)  # no as_of
    with pytest.raises(NotKnowableYet):
        mock.get_forward_price(FUEL, DELIVERY, term_months=TERM)


def test_clock_before_observed_at_fails_closed():
    trace = _capture_stub_trace(as_of=dt.datetime(2021, 1, 1))
    mock = RecordedSimInterface(trace, as_of=dt.datetime(2020, 1, 1))  # before capture
    with pytest.raises(NotKnowableYet):
        mock.get_forward_price(FUEL, DELIVERY, term_months=TERM)


def test_set_as_of_returns_self_and_updates_clock():
    trace = _capture_stub_trace(as_of=dt.datetime(2019, 1, 1))
    mock = RecordedSimInterface(trace)
    assert mock.set_as_of(dt.datetime(2020, 1, 1)) is mock
    assert mock.get_forward_price(FUEL, DELIVERY, term_months=TERM) == 120.0


# ---------------------------------------------------------------------------
# ENDOGENOUS methods run the live fixed-world delegate (company's own book).
# ---------------------------------------------------------------------------
def test_endogenous_delegated_to_live_path():
    mock = RecordedSimInterface(ObservableTrace())
    # churn estimate is a company observable model (enriched_churn_estimate);
    # it must produce a real number, not touch the trace.
    p = mock.get_churn_estimate("acc-1", 100.0, 130.0, 2.0, 3500.0)
    assert 0.0 <= p <= 0.95
    assert mock.get_customer_status("acc-1") == "active"


def test_notify_writes_go_to_delegate():
    endo = StubSimInterface()
    mock = RecordedSimInterface(ObservableTrace(), endogenous=endo)
    mock.notify_churn("acc-1", "2020-01-01")
    mock.notify_acquisition("acc-2", "2020-02-01")
    assert len(endo.churn_notifications) == 1
    assert len(endo.acquisition_notifications) == 1


def test_endogenous_draws_no_exogenous_price_history():
    # The whole memory win: the mock answers get_forward_price WITHOUT loading
    # the multi-GB sim price history. Its endogenous delegate is a StubSimInterface
    # (kilobytes), never a LiveSimInterface, and its exogenous path is pure replay.
    trace = _capture_stub_trace()
    mock = RecordedSimInterface(trace, as_of=dt.datetime(2020, 1, 1))
    assert isinstance(mock.endogenous_delegate, StubSimInterface)
    assert not isinstance(mock.endogenous_delegate, LiveSimInterface)


# ---------------------------------------------------------------------------
# Composition hook: build_sim_interface() reads SIM_RECORDED_TRACE (env-var only,
# zero edit to tournament_runner.py — §4).
# ---------------------------------------------------------------------------
def test_build_sim_interface_reads_env_var(tmp_path, monkeypatch):
    trace = _capture_stub_trace()
    path = tmp_path / "trace.jsonl"
    trace.save(path)
    monkeypatch.setenv("SIM_RECORDED_TRACE", str(path))
    iface = build_sim_interface()
    assert isinstance(iface, RecordedSimInterface)


def test_build_sim_interface_unset_returns_stub(monkeypatch):
    monkeypatch.delenv("SIM_RECORDED_TRACE", raising=False)
    assert isinstance(build_sim_interface(), StubSimInterface)
    assert isinstance(build_sim_interface(live=True), LiveSimInterface)


# ---------------------------------------------------------------------------
# L2 composition point: the memory-cap path admits N>1 workers when the caller
# passes the mock's low per-life RSS. Exercises tournament_runner's cap WITHOUT
# editing it (import-only).
# ---------------------------------------------------------------------------
def test_memory_cap_admits_more_workers_with_mock_rss():
    from tools.tournament_runner import memory_safe_worker_cap

    avail = 8 * 1024 * 1024 * 1024  # 8 GiB, the box in the profile
    full_life = 6_000 * 1024 * 1024  # ~5.67 GB reconstruct-the-world life
    mock_life = 512 * 1024 * 1024    # sub-GB recorded-replay life

    full_workers = memory_safe_worker_cap(full_life, available_bytes=avail)
    mock_workers = memory_safe_worker_cap(mock_life, available_bytes=avail)

    assert full_workers == 1              # memory-bound: the throttle the mock lifts
    assert mock_workers > 1               # the mock unthrottles parallelism
    assert mock_workers > full_workers


# ---------------------------------------------------------------------------
# COUPLED_TRIAD gap-measurement point defined (§6). The gap IS the score.
# ---------------------------------------------------------------------------
def test_fitness_gap_measurement_point():
    mock_fit = {"total_net_gbp": 1_000_000.0}
    full_fit = {"total_net_gbp": 1_050_000.0}
    g = fitness_gap("variant-A", mock_fit, full_fit)
    assert isinstance(g, GapMeasurement)
    assert g.gap == pytest.approx(50_000.0)
    assert g.relative_gap == pytest.approx(50_000.0 / 1_050_000.0)


def test_fitness_gap_zero_when_identical():
    fit = {"total_net_gbp": 42.0}
    assert fitness_gap("v", fit, fit).gap == 0.0
    assert fitness_gap("v", fit, fit).relative_gap == 0.0


# ---------------------------------------------------------------------------
# Publish-refusal WALL (§4, R15 fail-closed) + MUTATION: a recorded run may never
# reach a publish path. If the guard is removed, this raises no error and the
# test fails.
# ---------------------------------------------------------------------------
def test_publish_refused_MUTATION_when_recorded():
    with pytest.raises(RecordedRunPublishRefused):
        refuse_publish_if_recorded({"SIM_RECORDED_TRACE": "/some/trace.jsonl"})


def test_publish_allowed_when_not_recorded():
    refuse_publish_if_recorded({})  # no exception


# ---------------------------------------------------------------------------
# Capture tool: deterministic, records only observable return values.
# ---------------------------------------------------------------------------
def test_capture_records_only_return_values():
    trace = _capture_stub_trace()
    (rec,) = trace.records()
    assert rec.request_type == "forward_price.v1"
    assert rec.status is ReplayStatus.OK
    assert rec.payload == 120.0            # the observable price float, nothing else
    assert rec.observed_at == dt.datetime(2019, 1, 1)
    assert rec.valid_time == dt.date(2020, 7, 1)


def test_capture_is_deterministic(tmp_path):
    stub = StubSimInterface()
    queries = build_queries(
        ["electricity", "gas"],
        [dt.datetime(2019, 1, 1)],
        ["2020-07-01"],
        [12, 24],
    )
    p1 = tmp_path / "a.jsonl"
    p2 = tmp_path / "b.jsonl"
    capture_trace(stub, queries, out_path=p1)
    capture_trace(StubSimInterface(), queries, out_path=p2)
    assert p1.read_text() == p2.read_text()  # byte-identical re-capture


def test_capture_to_disk_then_replay(tmp_path):
    stub = StubSimInterface()
    queries = [ForwardPriceQuery(FUEL, DELIVERY, as_of=dt.datetime(2019, 1, 1), term_months=TERM)]
    path = tmp_path / "trace.jsonl"
    capture_trace(stub, queries, out_path=path)
    mock = RecordedSimInterface.from_path(path, as_of=dt.datetime(2020, 1, 1))
    assert mock.get_forward_price(FUEL, DELIVERY, term_months=TERM) == 120.0
