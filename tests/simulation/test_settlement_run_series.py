"""Tests for simulation/settlement_run_series.py -- the L2 integration that
wires a REAL settled book (simulation/settlement.py::run_settlement) plus the
REAL meter-read estimation model (simulation/meter_reads.py) into the
settlement-run revision timetable.

Two properties are load-bearing for this atom and get their own classes:

  * TestFinalValueNeutrality -- the integration NEVER changes a final settled
    figure. The RF (true-final) value the timetable resolves to is exactly
    the untouched sum of the real settled records, and the settled records
    themselves are not mutated. This is the core risk control for W3_2 L2.

  * TestPointInTimeBlindfold -- a read as-of R1's transaction_time sees the
    R1 estimate, NOT the RF final; the RF is invisible before its own
    publication date; nothing is knowable before delivery.
"""
import copy
import datetime as dt

import pytest

from company.interfaces.bitemporal_event_log import BitemporalEventLog
from simulation.meter_reads import generate_meter_read_log, meter_type_for_customer
from simulation.settlement import run_settlement
from simulation.settlement_run_series import (
    bills_from_settled_records,
    build_settlement_revision_log,
)
from simulation.settlement_timetable import emit_settlement_timetable


def _dt(d: dt.date) -> dt.datetime:
    return dt.datetime.combine(d, dt.time(0, 0))


# ---------------------------------------------------------------------------
# End-to-end fixture: real generators only (run_settlement + meter_reads).
# ---------------------------------------------------------------------------

def _seasonal_shape(kwh_per_period_by_month: dict[int, float]):
    """A consumption shape that varies (mildly) by calendar month, so the
    meter-read model's trailing-average estimate genuinely differs from the
    true value in later months -- a real, non-degenerate revision gap."""
    def shape_fn(date_str: str) -> list[float]:
        month = int(date_str[5:7])
        return [kwh_per_period_by_month[month]] * 48
    return shape_fn


def _price_records(dates: list[str], price: float = 60.0) -> list[dict]:
    return [
        {"settlementDate": d, "settlementPeriod": p, "systemSellPrice": price}
        for d in dates
        for p in range(1, 49)
    ]


def _daterange(start: dt.date, end: dt.date) -> list[str]:
    out, cur = [], start
    while cur <= end:
        out.append(cur.isoformat())
        cur += dt.timedelta(days=1)
    return out


def _build_real_book():
    """Run the REAL settlement generator + REAL meter-read model over a small
    multi-month, multi-customer book and return (settled_records,
    meter_read_log, dominant_meter_type)."""
    start = dt.date(2022, 1, 1)
    end = dt.date(2022, 4, 30)
    dates = _daterange(start, end)
    # Mild month-to-month variation (~1.5% steps) -> in-band non-HH revisions.
    shape = _seasonal_shape({1: 1.00, 2: 1.015, 3: 0.985, 4: 1.005})
    prices = _price_records(dates, price=60.0)

    customers = [
        {"customer_id": f"C{i}", "acquisition_date": "2021-06-01",
         "unit_rate_gbp_per_mwh": 100.0, "metering": "NHH"}
        for i in range(1, 9)
    ]
    settled = run_settlement(
        customers=customers,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        consumption_shape=shape,
        system_price_records=prices,
    )

    meter_types = {c["customer_id"]: meter_type_for_customer(c) for c in customers}
    bills = bills_from_settled_records(settled)
    meter_log = generate_meter_read_log(bills, meter_types)
    return settled, meter_log


def _true_value_by_month(settled_records, value_field="revenue_gbp"):
    out = {}
    for rec in settled_records:
        out.setdefault(rec["settlement_date"][:7], 0.0)
        out[rec["settlement_date"][:7]] += rec[value_field]
    return out


class TestFinalValueNeutrality:
    def test_rf_equals_untouched_true_settled_per_month(self):
        settled, meter_log = _build_real_book()
        expected = _true_value_by_month(settled, "revenue_gbp")

        _, events_by_month = build_settlement_revision_log(
            settled, meter_log, value_field="revenue_gbp",
            allow_out_of_band=True,  # neutrality is band-independent; see class docstring
        )

        assert set(events_by_month) == set(expected)
        for mkey, events in events_by_month.items():
            rf = next(e for e in events if e.run == "RF")
            assert rf.value == pytest.approx(expected[mkey]), mkey

    def test_total_rf_equals_total_settled_revenue(self):
        settled, meter_log = _build_real_book()
        total_settled = sum(r["revenue_gbp"] for r in settled)

        _, events_by_month = build_settlement_revision_log(
            settled, meter_log, allow_out_of_band=True,
        )
        total_rf = sum(
            e.value for events in events_by_month.values() for e in events if e.run == "RF"
        )
        assert total_rf == pytest.approx(total_settled)

    def test_settled_records_are_not_mutated(self):
        settled, meter_log = _build_real_book()
        before = copy.deepcopy(settled)
        build_settlement_revision_log(settled, meter_log, allow_out_of_band=True)
        assert settled == before

    def test_a_real_estimation_gap_actually_occurs(self):
        """Guard against a silently degenerate (initial == final everywhere)
        integration: with a varying shape and traditional meters, at least one
        month must carry a genuine revision (initial != RF)."""
        settled, meter_log = _build_real_book()
        _, events_by_month = build_settlement_revision_log(
            settled, meter_log, allow_out_of_band=True,
        )
        gaps = []
        for events in events_by_month.values():
            initial = next(e for e in events if e.run == "initial").value
            rf = next(e for e in events if e.run == "RF").value
            gaps.append(abs(rf - initial))
        assert max(gaps) > 0.0, "no month carried a real revision gap"


class TestPointInTimeBlindfold:
    """Controlled inputs with a known, in-band gap so the reveal timeline is
    exact. Book: one customer, one month, true settled revenue 1000.0, a
    delivery-time estimate 3% low (well inside the non-HH +-4% band)."""

    def _build(self):
        settled = [
            {"customer_id": "C1", "settlement_date": "2022-06-15",
             "consumption_kwh": 100.0, "revenue_gbp": 600.0},
            {"customer_id": "C1", "settlement_date": "2022-06-20",
             "consumption_kwh": 100.0, "revenue_gbp": 400.0},
        ]
        # True monthly consumption = 200 kWh; estimate 3% low = 194 kWh.
        meter_log = [
            {"customer_id": "C1", "period_end": "2022-06-30", "meter_type": "traditional",
             "status": "estimated", "estimated_consumption_kwh": 194.0,
             "true_consumption_kwh": 200.0},
        ]
        log, events_by_month = build_settlement_revision_log(
            settled, meter_log, value_field="revenue_gbp", meter_type="non_HH",
        )
        return log, events_by_month["2022-06"]

    def test_initial_is_estimate_scaled_final(self):
        _, events = self._build()
        initial = next(e for e in events if e.run == "initial")
        rf = next(e for e in events if e.run == "RF")
        # ratio = 194/200 = 0.97 -> initial = 1000 * 0.97 = 970.0
        assert initial.value == pytest.approx(970.0)
        assert rf.value == pytest.approx(1000.0)

    def test_before_delivery_nothing_is_knowable(self):
        log, events = self._build()
        delivery = next(e for e in events if e.run == "initial").publication_date
        rec = log.as_known_at(
            _dt(delivery - dt.timedelta(days=1)), "book", "settlement_revenue_gbp",
        )
        assert rec is None

    def test_as_of_r1_sees_r1_estimate_not_final(self):
        log, events = self._build()
        r1 = next(e for e in events if e.run == "R1")
        rec = log.as_known_at(
            _dt(r1.publication_date), "book", "settlement_revenue_gbp",
        )
        assert rec.value == pytest.approx(r1.value)
        # gap = 1000 - 970 = 30; R1 resolves 60% -> 970 + 18 = 988.0
        assert rec.value == pytest.approx(988.0)
        assert rec.value != pytest.approx(1000.0)

    def test_rf_final_invisible_before_its_publication_date(self):
        log, events = self._build()
        rf = next(e for e in events if e.run == "RF")
        r3 = next(e for e in events if e.run == "R3")
        rec = log.as_known_at(
            _dt(rf.publication_date - dt.timedelta(days=1)), "book", "settlement_revenue_gbp",
        )
        # The day before RF publishes, the latest visible figure is R3, never
        # the true final -- the blindfold holds.
        assert rec.value == pytest.approx(r3.value)
        assert rec.value != pytest.approx(1000.0)

    def test_as_of_rf_publication_sees_true_final(self):
        log, events = self._build()
        rf = next(e for e in events if e.run == "RF")
        rec = log.as_known_at(
            _dt(rf.publication_date), "book", "settlement_revenue_gbp",
        )
        assert rec.value == pytest.approx(1000.0)


class TestNoMeterEventDefaultsToNoRevision:
    def test_customer_month_without_a_read_settles_at_true(self):
        settled = [
            {"customer_id": "C9", "settlement_date": "2022-06-15",
             "consumption_kwh": 100.0, "revenue_gbp": 500.0},
        ]
        # Empty meter log -> no estimate for C9 -> ratio 1.0 -> no revision.
        log, events_by_month = build_settlement_revision_log(
            settled, meter_read_log=[], value_field="revenue_gbp",
        )
        events = events_by_month["2022-06"]
        initial = next(e for e in events if e.run == "initial").value
        rf = next(e for e in events if e.run == "RF").value
        assert initial == pytest.approx(rf) == pytest.approx(500.0)
