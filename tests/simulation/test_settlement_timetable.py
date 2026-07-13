"""Tests for simulation/settlement_timetable.py -- the world-side settlement
run revision timetable (W3_2_settlement_timetable). Verifies the
reveal-over-time property on the bitemporal spine: a decision as-of a given
date sees only the settlement figure that had actually been published by
that date in real life, and the RF run resolves exactly to the true value.
"""
import datetime as dt

import pytest

from company.interfaces.bitemporal_event_log import BitemporalEventLog
import company.regulatory.settlement_reconciliation as recon
from simulation import settlement_timetable as st


def _dt(d: dt.date) -> dt.datetime:
    return dt.datetime.combine(d, dt.time(0, 0))


class TestConstantsMatchSharedSource:
    """This module deliberately duplicates (does not import, per
    .claude/rules/epistemic-wall-sim.md) company/regulatory/
    settlement_reconciliation.py's own real, Elexon-anchored constants.
    Tests may import anything (EXEMPT_PATHS) -- use that to guard against
    the two constant sets ever silently drifting apart."""

    def test_months_match(self):
        assert st.R1_MONTHS == recon._R1_MONTHS
        assert st.R2_MONTHS == recon._R2_MONTHS
        assert st.R3_MONTHS == recon._R3_MONTHS
        assert st.RF_MONTHS == recon._RF_MONTHS

    def test_shares_match(self):
        assert st.R1_SHARE == recon._R1_SHARE
        assert st.R2_SHARE == recon._R2_SHARE
        assert st.R3_SHARE == recon._R3_SHARE
        assert st.RF_SHARE == recon._RF_SHARE

    def test_variance_bands_match(self):
        assert st.HH_VARIANCE == recon._HH_RECON_VARIANCE
        assert st.NON_HH_VARIANCE == recon._NON_HH_RECON_VARIANCE

    def test_shares_sum_to_one(self):
        assert abs((st.R1_SHARE + st.R2_SHARE + st.R3_SHARE + st.RF_SHARE) - 1.0) < 1e-9


class TestEmitSettlementTimetable:
    def _emit(self, initial=1000.0, true_final=1004.0, meter_type="HH", **kw):
        log = BitemporalEventLog()
        delivery_date = dt.date(2020, 6, 15)
        events = st.emit_settlement_timetable(
            log,
            entity_id="cust_1",
            fact_type="settlement_value_gbp",
            delivery_date=delivery_date,
            initial_value=initial,
            true_final_value=true_final,
            meter_type=meter_type,
            **kw,
        )
        return log, delivery_date, events

    def test_emits_initial_plus_four_runs(self):
        _, _, events = self._emit()
        assert [e.run for e in events] == ["initial", "R1", "R2", "R3", "RF"]

    def test_publication_dates_are_real_month_offsets(self):
        _, delivery_date, events = self._emit()
        by_run = {e.run: e.publication_date for e in events}
        assert by_run["initial"] == delivery_date
        assert (by_run["R1"].year, by_run["R1"].month) == (2020, 7)
        assert (by_run["R2"].year, by_run["R2"].month) == (2020, 9)
        assert (by_run["R3"].year, by_run["R3"].month) == (2020, 11)
        assert (by_run["RF"].year, by_run["RF"].month) == (2022, 10)

    def test_rf_equals_true_final_value_exactly(self):
        _, _, events = self._emit(initial=1000.0, true_final=1004.0)
        rf = next(e for e in events if e.run == "RF")
        assert rf.value == pytest.approx(1004.0)

    def test_r1_resolves_60_percent_of_gap(self):
        _, _, events = self._emit(initial=1000.0, true_final=1004.0)
        r1 = next(e for e in events if e.run == "R1")
        # gap = 4.0, 60% resolved = 2.4 -> value = 1002.4
        assert r1.value == pytest.approx(1002.4)

    def test_r2_resolves_cumulative_85_percent(self):
        _, _, events = self._emit(initial=1000.0, true_final=1004.0)
        r2 = next(e for e in events if e.run == "R2")
        # cumulative share 0.85, gap 4.0 -> value = 1000 + 3.4 = 1003.4
        assert r2.value == pytest.approx(1003.4)

    def test_out_of_band_gap_raises_by_default(self):
        # HH variance is +-0.5%; a 10% gap is wildly out of band for HH.
        with pytest.raises(ValueError):
            self._emit(initial=1000.0, true_final=1100.0, meter_type="HH")

    def test_out_of_band_gap_allowed_with_override(self):
        _, _, events = self._emit(
            initial=1000.0, true_final=1100.0, meter_type="HH", allow_out_of_band=True,
        )
        rf = next(e for e in events if e.run == "RF")
        assert rf.value == pytest.approx(1100.0)

    def test_non_hh_wider_band_permits_larger_gap(self):
        # 3% gap is within +-4% non-HH band but would fail for HH's +-0.5%.
        _, _, events = self._emit(initial=1000.0, true_final=1030.0, meter_type="non_HH")
        rf = next(e for e in events if e.run == "RF")
        assert rf.value == pytest.approx(1030.0)


class TestRevealOverTimeProperty:
    """The core point-in-time guarantee this atom exists to prove: a
    decision made as-of a given real date sees exactly the settlement
    figure that had actually been published in real life by that date --
    never an earlier revision it should have superseded, never a later one
    it could not yet have known."""

    def _build(self):
        log = BitemporalEventLog()
        delivery_date = dt.date(2020, 6, 15)
        events = st.emit_settlement_timetable(
            log,
            entity_id="cust_1",
            fact_type="settlement_value_gbp",
            delivery_date=delivery_date,
            initial_value=1000.0,
            true_final_value=1004.0,
            meter_type="HH",
        )
        return log, delivery_date, events

    def test_before_r1_sees_only_initial_figure(self):
        log, delivery_date, _ = self._build()
        # One week after delivery -- well before R1 (~1 month later).
        as_of = _dt(delivery_date + dt.timedelta(days=7))
        rec = log.as_known_at(as_of, "cust_1", "settlement_value_gbp", delivery_date)
        assert rec.value == pytest.approx(1000.0)

    def test_after_r2_sees_r2_revised_figure(self):
        log, delivery_date, events = self._build()
        r2 = next(e for e in events if e.run == "R2")
        # A few days after R2's own publication date.
        as_of = _dt(r2.publication_date + dt.timedelta(days=3))
        rec = log.as_known_at(as_of, "cust_1", "settlement_value_gbp", delivery_date)
        assert rec.value == pytest.approx(r2.value)
        # And strictly between R2 and R3, still shows R2 (not yet the final value).
        assert rec.value != pytest.approx(1004.0)

    def test_final_rf_figure_equals_true_value(self):
        log, delivery_date, events = self._build()
        rf = next(e for e in events if e.run == "RF")
        as_of = _dt(rf.publication_date + dt.timedelta(days=1))
        rec = log.as_known_at(as_of, "cust_1", "settlement_value_gbp", delivery_date)
        assert rec.value == pytest.approx(1004.0)

    def test_as_of_each_runs_own_publication_date_returns_that_runs_value(self):
        """The reveal-over-time property, exhaustively: querying exactly
        as-of each run's own publication date returns that run's revision
        (transaction_time <= decision_time is inclusive)."""
        log, delivery_date, events = self._build()
        for event in events:
            as_of = _dt(event.publication_date)
            rec = log.as_known_at(as_of, "cust_1", "settlement_value_gbp", delivery_date)
            assert rec.value == pytest.approx(event.value), (
                f"run {event.run}: expected {event.value}, got {rec.value}"
            )

    def test_query_strictly_before_publication_does_not_see_that_runs_value(self):
        log, delivery_date, events = self._build()
        r3 = next(e for e in events if e.run == "R3")
        r2 = next(e for e in events if e.run == "R2")
        as_of = _dt(r3.publication_date - dt.timedelta(days=1))
        rec = log.as_known_at(as_of, "cust_1", "settlement_value_gbp", delivery_date)
        assert rec.value == pytest.approx(r2.value)

    def test_nothing_knowable_before_delivery_date_itself(self):
        log, delivery_date, _ = self._build()
        as_of = _dt(delivery_date - dt.timedelta(days=1))
        rec = log.as_known_at(as_of, "cust_1", "settlement_value_gbp", delivery_date)
        assert rec is None
