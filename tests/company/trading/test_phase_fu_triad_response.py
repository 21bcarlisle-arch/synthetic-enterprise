"""Tests for Triad Demand Response Book (Phase FU)."""
import datetime as dt
import pytest
from company.trading.triad_response_book import (
    TriadDemandEvent,
    TriadDemandResponseBook,
    TriadResponseOutcome,
    _DEFAULT_TNUOS_RATE_GBP_PER_KW,
    _FULL_RESPONSE_REDUCTION_PCT,
    _PARTIAL_RESPONSE_REDUCTION_PCT,
)

DATE = dt.date(2023, 1, 10)
SEASON = "2022/23"


def make_event(
    cid="C_IC1",
    baseline=2.0,
    actual=2.0,
    alerted=True,
    triad_num=1,
    rate=_DEFAULT_TNUOS_RATE_GBP_PER_KW,
):
    return TriadDemandEvent(
        customer_id=cid,
        triad_season=SEASON,
        triad_number=triad_num,
        settlement_date=DATE,
        settlement_period=34,
        baseline_demand_mw=baseline,
        actual_demand_mw=actual,
        was_alerted=alerted,
        tnuos_rate_gbp_per_kw=rate,
    )


class TestTriadDemandEvent:
    def test_demand_reduction_positive(self):
        e = make_event(baseline=2.0, actual=1.5)
        assert e.demand_reduction_mw == pytest.approx(0.5)

    def test_demand_reduction_no_negative(self):
        e = make_event(baseline=1.0, actual=1.5)
        assert e.demand_reduction_mw == pytest.approx(0.0)

    def test_reduction_pct_calculation(self):
        e = make_event(baseline=2.0, actual=1.4)
        assert e.reduction_pct == pytest.approx(30.0)

    def test_reduction_pct_zero_baseline(self):
        e = make_event(baseline=0.0, actual=0.0)
        assert e.reduction_pct == pytest.approx(0.0)

    def test_outcome_full_response(self):
        e = make_event(baseline=2.0, actual=1.5, alerted=True)
        assert e.outcome == TriadResponseOutcome.FULL_RESPONSE

    def test_outcome_partial_response(self):
        e = make_event(baseline=2.0, actual=1.85, alerted=True)
        assert e.outcome == TriadResponseOutcome.PARTIAL_RESPONSE

    def test_outcome_no_response(self):
        e = make_event(baseline=2.0, actual=2.0, alerted=True)
        assert e.outcome == TriadResponseOutcome.NO_RESPONSE

    def test_outcome_not_alerted(self):
        e = make_event(baseline=2.0, actual=1.0, alerted=False)
        assert e.outcome == TriadResponseOutcome.NOT_ALERTED

    def test_tnuos_saving_calculation(self):
        e = make_event(baseline=2.0, actual=1.5, rate=80.0)
        # reduction = 0.5 MW = 500 kW; saving = 500 * 80 = 40000
        assert e.tnuos_saving_gbp == pytest.approx(40_000.0)

    def test_tnuos_saving_zero_when_no_reduction(self):
        e = make_event(baseline=2.0, actual=2.0)
        assert e.tnuos_saving_gbp == pytest.approx(0.0)

    def test_event_summary_is_string(self):
        assert isinstance(make_event().event_summary(), str)

    def test_frozen(self):
        e = make_event()
        with pytest.raises((AttributeError, TypeError)):
            e.actual_demand_mw = 0.0


class TestTriadDemandResponseBook:
    def test_record_returns_event(self):
        book = TriadDemandResponseBook()
        e = make_event()
        assert book.record_event(e) is e

    def test_events_for_customer_filters(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(cid="C_IC1"))
        book.record_event(make_event(cid="C_IC2"))
        assert len(book.events_for_customer("C_IC1")) == 1

    def test_events_for_season_filters(self):
        book = TriadDemandResponseBook()
        e1 = make_event()
        e2 = TriadDemandEvent(
            customer_id="C_IC1", triad_season="2023/24", triad_number=1,
            settlement_date=DATE, settlement_period=34,
            baseline_demand_mw=2.0, actual_demand_mw=1.5, was_alerted=True,
        )
        book.record_event(e1)
        book.record_event(e2)
        assert len(book.events_for_season(SEASON)) == 1

    def test_full_response_events_filtered(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(baseline=2.0, actual=1.5))  # full
        book.record_event(make_event(baseline=2.0, actual=2.0))  # no response
        assert len(book.full_response_events()) == 1

    def test_no_response_events_filtered(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(baseline=2.0, actual=2.0))  # no response
        book.record_event(make_event(baseline=2.0, actual=1.5))  # full
        assert len(book.no_response_events()) == 1

    def test_total_demand_reduction_for_season(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(baseline=2.0, actual=1.5))  # 0.5 MW reduction
        book.record_event(make_event(baseline=3.0, actual=2.5))  # 0.5 MW reduction
        assert book.total_demand_reduction_mw_for_season(SEASON) == pytest.approx(1.0)

    def test_total_tnuos_saving(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(baseline=2.0, actual=1.5, rate=80.0))  # 500kW * 80
        book.record_event(make_event(baseline=3.0, actual=2.0, rate=80.0))  # 1000kW * 80
        assert book.total_tnuos_saving_gbp() == pytest.approx(120_000.0)

    def test_response_rate_pct_full(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(baseline=2.0, actual=1.5, alerted=True))  # full
        book.record_event(make_event(baseline=2.0, actual=2.0, alerted=True))  # no
        assert book.response_rate_pct() == pytest.approx(50.0)

    def test_response_rate_pct_no_alerted(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(alerted=False))
        assert book.response_rate_pct() == pytest.approx(0.0)

    def test_top_responders_ordering(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event(cid="C_IC1", baseline=2.0, actual=1.5, rate=80.0))  # 40k
        book.record_event(make_event(cid="C_IC2", baseline=3.0, actual=2.0, rate=80.0))  # 80k
        book.record_event(make_event(cid="C_IC3", baseline=1.0, actual=0.5, rate=80.0))  # 40k
        top = book.top_responders(n=2)
        assert top[0] == "C_IC2"

    def test_demand_response_summary_is_string(self):
        book = TriadDemandResponseBook()
        book.record_event(make_event())
        assert isinstance(book.demand_response_summary(), str)

    def test_empty_book_summary(self):
        book = TriadDemandResponseBook()
        summary = book.demand_response_summary()
        assert "no events" in summary

    def test_empty_book_totals_zero(self):
        book = TriadDemandResponseBook()
        assert book.total_tnuos_saving_gbp() == pytest.approx(0.0)
        assert book.response_rate_pct() == pytest.approx(0.0)
