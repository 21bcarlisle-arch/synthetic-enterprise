"""Tests for simulation/settlement_timetable.py -- the world-side settlement
run revision timetable (W3_2_settlement_timetable). Verifies the
reveal-over-time property on the bitemporal spine: a decision as-of a given
date sees only the settlement figure that had actually been published by
that date in real life, and the RF run resolves exactly to the true value.
"""
import datetime as dt

import pytest
from dateutil.relativedelta import relativedelta

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
        """DERIVED FROM THE CONSTANTS, not from four literal months.

        These read `(2020, 7) / (2020, 9) / (2020, 11) / (2022, 10)` until 2026-08-29 -- the
        offsets 1/3/5/28, every one of them wrong, and RF's naming DF's 28-month dispute lag.
        Correcting the constants against Elexon's own timetable turned this control red for
        being RIGHT, which is the signature of a test pinned to today's answer. It now asserts
        that each run lands `<RUN>_MONTHS` after delivery, which is the property, and it stays
        true through the next correction (MHHS takes the process to four months as meters
        migrate from September 2025).
        """
        _, delivery_date, events = self._emit()
        by_run = {e.run: e.publication_date for e in events}
        assert by_run["initial"] == delivery_date
        for run, months in (("R1", st.R1_MONTHS), ("R2", st.R2_MONTHS),
                            ("R3", st.R3_MONTHS), ("RF", st.RF_MONTHS)):
            expected = delivery_date + relativedelta(months=months)
            assert (by_run[run].year, by_run[run].month) == (expected.year, expected.month), (
                f"{run} is published {months} months after the Settlement Date"
            )
        # NON-VACUITY: the four must be DISTINCT and ordered, or a constants file of zeroes
        # would satisfy every assertion above.
        dates = [by_run[r] for r in ("initial", "R1", "R2", "R3", "RF")]
        assert dates == sorted(dates) and len(set(dates)) == 5

    def test_rf_equals_true_final_value_exactly(self):
        _, _, events = self._emit(initial=1000.0, true_final=1004.0)
        rf = next(e for e in events if e.run == "RF")
        assert rf.value == pytest.approx(1004.0)

    def test_r1_resolves_its_declared_share_of_the_gap(self):
        """The share is READ, not restated. This was `test_r1_resolves_60_percent_of_gap` and
        asserted 1002.4, both of which encoded a 0.60 that Elexon's own curve puts at 0.31."""
        _, _, events = self._emit(initial=1000.0, true_final=1004.0)
        r1 = next(e for e in events if e.run == "R1")
        assert r1.value == pytest.approx(1000.0 + 4.0 * st.R1_SHARE)
        assert 0.0 < st.R1_SHARE < 1.0, "vacuous: a share of 0 or 1 makes the line above trivial"

    def test_r2_resolves_the_CUMULATIVE_share_and_not_its_own(self):
        """The property that distinguishes a cumulative curve from a per-run one: R2's value
        carries R1's share as well as its own. Named for that rather than for the number."""
        _, _, events = self._emit(initial=1000.0, true_final=1004.0)
        r2 = next(e for e in events if e.run == "R2")
        cumulative = st.R1_SHARE + st.R2_SHARE
        assert r2.value == pytest.approx(1000.0 + 4.0 * cumulative)
        assert cumulative > st.R2_SHARE, "vacuous: R1 must contribute, or this is not cumulative"

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

    # --- R15 fail-open / NaN-blind guard (red-team, 2026-07-27) --------------
    # The variance-band plausibility check is a bare magnitude comparison
    # (abs(gap) > band). abs(nan) > band and abs(inf) > inf are both False, so
    # without an explicit non-finite reject a NaN/inf input sails through the
    # control and the function emits all-NaN/inf settlement revisions silently
    # (the "initial" record stays valid; every revision and every bitemporal
    # query after R1 returns NaN). These assert the guard fires on that defect.

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_initial_value_raises(self, bad):
        with pytest.raises(ValueError, match="not finite"):
            self._emit(initial=bad, true_final=1004.0)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_true_final_value_raises(self, bad):
        with pytest.raises(ValueError, match="not finite"):
            self._emit(initial=1000.0, true_final=bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_rejected_even_with_out_of_band_override(self, bad):
        # allow_out_of_band bypasses the band check but must NOT bypass the
        # non-finite reject -- an infinite/NaN figure is never a valid stress
        # case, only a bug.
        with pytest.raises(ValueError, match="not finite"):
            self._emit(initial=1000.0, true_final=bad, allow_out_of_band=True)

    def test_non_finite_never_reaches_the_log(self):
        # Belt-and-braces: nothing gets persisted when the input is non-finite.
        import math

        from company.interfaces.bitemporal_event_log import BitemporalEventLog
        log = BitemporalEventLog()
        with pytest.raises(ValueError):
            st.emit_settlement_timetable(
                log,
                entity_id="cust_1",
                fact_type="settlement_value_gbp",
                delivery_date=dt.date(2020, 6, 15),
                initial_value=1000.0,
                true_final_value=math.nan,
                meter_type="HH",
            )
        rec = log.as_known_at(
            _dt(dt.date(2099, 1, 1)), "cust_1", "settlement_value_gbp", dt.date(2020, 6, 15)
        )
        assert rec is None


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
