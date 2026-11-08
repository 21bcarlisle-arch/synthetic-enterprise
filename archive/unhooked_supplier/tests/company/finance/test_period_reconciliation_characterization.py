"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/finance/period_reconciliation.py — period-end revenue/cost
matching and the settlement-variance ledger. This is where a trading period's
gross margin is struck and where post-close adjustments (settlement
differences, meter-read errors, accrual reversals) are booked against it.

All dates are literals passed in explicitly; the module reads no clock.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.finance.period_reconciliation import (
    PeriodReconciliation,
    ReconciliationLedger,
    ReconciliationStatus,
    ReconciliationVariance,
    VarianceType,
)

JAN = dt.date(2024, 1, 1)
JAN_END = dt.date(2024, 1, 31)
FEB = dt.date(2024, 2, 1)
FEB_END = dt.date(2024, 2, 29)


def open_january(ledger, **overrides):
    kw = dict(
        period_id="2024-01", period_start=JAN, period_end=JAN_END,
        billed_revenue_gbp=1_000_000.0, accrued_revenue_gbp=120_000.0,
        wholesale_cost_gbp=700_000.0, network_cost_gbp=180_000.0,
        policy_cost_gbp=90_000.0, operating_cost_gbp=60_000.0,
    )
    kw.update(overrides)
    return ledger.open_period(**kw)


# ---------------------------------------------------------------------------
# ReconciliationVariance
# ---------------------------------------------------------------------------


def test_a_variance_is_adverse_purely_by_sign():
    v = ReconciliationVariance("V1", JAN, VarianceType.SETTLEMENT_DIFFERENCE, -5_000.0, "R2 run")
    assert v.is_adverse is True
    assert v.abs_amount_gbp == 5_000.0


def test_a_zero_variance_is_not_adverse():
    # `< 0` — an exactly-zero variance is classed favourable. Frozen as-is.
    v = ReconciliationVariance("V1", JAN, VarianceType.ACCRUAL_REVERSAL, 0.0, "nil")
    assert v.is_adverse is False


def test_variance_type_does_not_constrain_sign():
    # SURPRISE: nothing ties the sign to the type. A REVENUE_SHORTFALL of
    # +£50,000 — a shortfall that increases margin — is accepted and reported as
    # favourable. The type is a free-text label on an arbitrary signed number.
    v = ReconciliationVariance("V1", JAN, VarianceType.REVENUE_SHORTFALL, 50_000.0, "?")
    assert v.is_adverse is False
    assert v.variance_type is VarianceType.REVENUE_SHORTFALL


def test_a_variance_is_frozen_once_created():
    v = ReconciliationVariance("V1", JAN, VarianceType.COST_OVERRUN, -1.0, "x")
    with pytest.raises(Exception):
        v.amount_gbp = 0.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PeriodReconciliation arithmetic
# ---------------------------------------------------------------------------


def test_the_period_margin_arithmetic_is_a_plain_sum():
    p = PeriodReconciliation(
        period_id="2024-01", period_start=JAN, period_end=JAN_END,
        billed_revenue_gbp=1_000_000.0, accrued_revenue_gbp=120_000.0,
        wholesale_cost_gbp=700_000.0, network_cost_gbp=180_000.0,
        policy_cost_gbp=90_000.0, operating_cost_gbp=60_000.0,
    )
    assert p.total_revenue_gbp == 1_120_000.0
    assert p.total_cost_gbp == 1_030_000.0
    assert p.gross_margin_gbp == 90_000.0
    assert p.total_variance_gbp == 0.0
    assert p.adjusted_margin_gbp == 90_000.0
    assert p.status is ReconciliationStatus.OPEN


def test_accrued_revenue_is_counted_as_revenue_with_no_separate_visibility():
    # Accrued (estimated, unbilled) revenue lands in the same total as cash-
    # billed revenue. A period whose margin is entirely accrual reports the same
    # gross_margin_gbp as one that billed every penny of it.
    all_billed = PeriodReconciliation("A", JAN, JAN_END, 1_120_000.0, 0.0, 700_000.0,
                                      180_000.0, 90_000.0, 60_000.0)
    all_accrued = PeriodReconciliation("B", JAN, JAN_END, 0.0, 1_120_000.0, 700_000.0,
                                       180_000.0, 90_000.0, 60_000.0)
    assert all_billed.gross_margin_gbp == all_accrued.gross_margin_gbp == 90_000.0


def test_variances_move_the_adjusted_margin_but_never_the_gross_margin():
    p = PeriodReconciliation("A", JAN, JAN_END, 1_000_000.0, 0.0, 900_000.0, 0.0, 0.0, 0.0)
    p.add_variance("V1", VarianceType.SETTLEMENT_DIFFERENCE, -25_000.0, "R1 run")
    p.add_variance("V2", VarianceType.METER_READ_ERROR, 4_000.0, "re-read")
    assert p.gross_margin_gbp == 100_000.0
    assert p.total_variance_gbp == -21_000.0
    assert p.adjusted_margin_gbp == 79_000.0


def test_add_variance_stamps_the_period_start_not_the_date_the_variance_arose():
    # SURPRISE: every variance is dated `period_start`, whatever period it was
    # actually discovered or booked in. An RF settlement adjustment landing 28
    # months later is recorded as having occurred on the first day of the period
    # it corrects, so the variance carries no information about WHEN the company
    # learned of it — the whole point of a reconciliation tail.
    p = PeriodReconciliation("A", JAN, JAN_END, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    v = p.add_variance("V1", VarianceType.SETTLEMENT_DIFFERENCE, -1.0, "RF, booked 2026-05")
    assert v.period == JAN


def test_duplicate_variance_ids_are_accepted_and_both_count():
    # DELIBERATELY CORRUPT INPUT: the same variance_id booked twice. SURPRISE:
    # there is no uniqueness check, so a re-submitted settlement adjustment is
    # counted twice against margin with no error and no way to tell from the
    # totals. (Contrast the ledger-side dedup in company/billing/account_ledger.)
    p = PeriodReconciliation("A", JAN, JAN_END, 1_000_000.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    p.add_variance("V1", VarianceType.SETTLEMENT_DIFFERENCE, -10_000.0, "R1")
    p.add_variance("V1", VarianceType.SETTLEMENT_DIFFERENCE, -10_000.0, "R1 again")
    assert len(p.variances) == 2
    assert p.total_variance_gbp == -20_000.0


def test_a_closed_period_still_accepts_new_variances():
    # SURPRISE: `close()` sets a status and nothing else. A RECONCILED period
    # remains fully writable — post-close adjustments silently restate a closed
    # period's margin with no reopen step, no audit trail, and no status change
    # back to OPEN or DISPUTED.
    p = PeriodReconciliation("A", JAN, JAN_END, 1_000_000.0, 0.0, 900_000.0, 0.0, 0.0, 0.0)
    p.close()
    assert p.status is ReconciliationStatus.RECONCILED
    p.add_variance("V1", VarianceType.ACCRUAL_REVERSAL, -50_000.0, "after close")
    assert p.status is ReconciliationStatus.RECONCILED
    assert p.adjusted_margin_gbp == 50_000.0


def test_close_is_idempotent_and_one_way():
    # There is no reopen(); DISPUTED and WRITTEN_OFF exist in the enum but no
    # method in the module ever sets them.
    p = PeriodReconciliation("A", JAN, JAN_END, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    p.close()
    p.close()
    assert p.status is ReconciliationStatus.RECONCILED
    assert set(ReconciliationStatus) == {
        ReconciliationStatus.OPEN, ReconciliationStatus.RECONCILED,
        ReconciliationStatus.DISPUTED, ReconciliationStatus.WRITTEN_OFF,
    }


def test_period_dates_are_never_validated_against_each_other():
    # DELIBERATELY CORRUPT INPUT: period_end BEFORE period_start. Accepted
    # silently; every downstream figure is computed as normal, and the period is
    # filed under period_start's year.
    p = PeriodReconciliation("A", FEB_END, JAN, 1_000.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert p.gross_margin_gbp == 1_000.0
    assert p.period_start.year == 2024


def test_the_variances_list_defaults_are_not_shared_between_periods():
    # `variances: List = None` + __post_init__ — the mutable-default trap is
    # avoided. Frozen so a refactor to `field(default_factory=list)` (or back to
    # a bare `[]` default) is visible.
    a = PeriodReconciliation("A", JAN, JAN_END, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    b = PeriodReconciliation("B", FEB, FEB_END, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    a.add_variance("V1", VarianceType.COST_OVERRUN, -1.0, "x")
    assert b.variances == []


# ---------------------------------------------------------------------------
# ReconciliationLedger
# ---------------------------------------------------------------------------


def test_open_period_returns_the_record_and_files_it():
    led = ReconciliationLedger()
    p = open_january(led)
    assert led.get("2024-01") is p
    assert led.open_periods() == [p]


def test_get_on_an_unknown_period_returns_none_rather_than_raising():
    assert ReconciliationLedger().get("2099-01") is None


def test_duplicate_period_ids_are_accepted_and_get_returns_the_first():
    # DELIBERATELY CORRUPT INPUT: the same period opened twice. SURPRISE: both
    # are stored and both are summed into the annual margin, but `get()` can
    # only ever reach the FIRST. The second period's variances are booked into
    # the annual figures while being unaddressable by period_id.
    led = ReconciliationLedger()
    first = open_january(led)
    second = open_january(led, billed_revenue_gbp=999_999_999.0)
    assert led.get("2024-01") is first
    assert second in led.open_periods()
    assert led.annual_gross_margin_gbp(2024) > 999_000_000.0


def test_annual_gross_margin_sums_adjusted_not_gross_margins():
    # The method is named annual_GROSS_margin_gbp but sums adjusted_margin_gbp,
    # i.e. it is net of variances. Frozen because the name and the number differ.
    led = ReconciliationLedger()
    p = open_january(led)
    p.add_variance("V1", VarianceType.SETTLEMENT_DIFFERENCE, -40_000.0, "R1")
    assert p.gross_margin_gbp == 90_000.0
    assert led.annual_gross_margin_gbp(2024) == 50_000.0


def test_a_period_is_attributed_to_the_year_of_its_start_date_alone():
    # A period spanning a year boundary counts entirely in the starting year.
    led = ReconciliationLedger()
    led.open_period("2023-12", dt.date(2023, 12, 1), dt.date(2024, 1, 31),
                    1_000_000.0, 0.0, 900_000.0, 0.0, 0.0, 0.0)
    assert led.annual_gross_margin_gbp(2023) == 100_000.0
    assert led.annual_gross_margin_gbp(2024) == 0.0


def test_an_empty_year_reports_a_zero_margin_not_an_absence():
    # SURPRISE (fail-open shape): a year with no periods at all is reported as
    # £0.00 annual margin, identical to a year that traded exactly to breakeven.
    # `reconciliation_summary` carries `periods: 0`, but the margin figure alone
    # cannot distinguish "no data" from "no profit".
    led = ReconciliationLedger()
    assert led.annual_gross_margin_gbp(2024) == 0.0
    assert led.reconciliation_summary(2024) == {
        "year": 2024, "periods": 0, "open": 0,
        "annual_gross_margin_gbp": 0.0, "total_variances_gbp": 0.0,
        "variances_by_type": {},
    }


def test_variances_by_type_aggregates_signed_amounts_and_can_net_to_zero():
    # SURPRISE: opposing variances of the same type cancel, so a period with a
    # -£1m and a +£1m settlement difference reports 0.0 for that type — the same
    # value as a period with no settlement variance at all. Gross activity is
    # not recoverable from the summary.
    led = ReconciliationLedger()
    p = open_january(led)
    p.add_variance("V1", VarianceType.SETTLEMENT_DIFFERENCE, -1_000_000.0, "R1")
    p.add_variance("V2", VarianceType.SETTLEMENT_DIFFERENCE, 1_000_000.0, "R2 reversal")
    assert led.variances_by_type(2024) == {"settlement_difference": 0.0}


def test_variances_by_type_keys_are_the_enum_values():
    led = ReconciliationLedger()
    p = open_january(led)
    p.add_variance("V1", VarianceType.METER_READ_ERROR, -1_500.0, "estimated read")
    p.add_variance("V2", VarianceType.ACCRUAL_REVERSAL, -2_500.0, "true-up")
    assert led.variances_by_type(2024) == {
        "meter_read_error": -1_500.0, "accrual_reversal": -2_500.0,
    }


def test_reconciliation_summary_counts_open_periods_within_the_year():
    led = ReconciliationLedger()
    jan = open_january(led)
    led.open_period("2024-02", FEB, FEB_END, 500_000.0, 0.0, 400_000.0, 0.0, 0.0, 0.0)
    jan.add_variance("V1", VarianceType.COST_OVERRUN, -10_000.0, "imbalance")
    jan.close()
    s = led.reconciliation_summary(2024)
    assert s["periods"] == 2
    assert s["open"] == 1
    assert s["annual_gross_margin_gbp"] == 180_000.0   # (90k - 10k) + 100k
    assert s["total_variances_gbp"] == -10_000.0
    assert s["variances_by_type"] == {"cost_overrun": -10_000.0}


def test_open_periods_is_not_year_scoped_but_the_summary_is():
    led = ReconciliationLedger()
    open_january(led)
    led.open_period("2019-01", dt.date(2019, 1, 1), dt.date(2019, 1, 31),
                    1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert len(led.open_periods()) == 2
    assert led.reconciliation_summary(2024)["open"] == 1


def test_rounding_is_applied_at_every_property_so_errors_compound_by_pennies():
    p = PeriodReconciliation("A", JAN, JAN_END,
                             billed_revenue_gbp=0.005, accrued_revenue_gbp=0.005,
                             wholesale_cost_gbp=0.005, network_cost_gbp=0.005,
                             policy_cost_gbp=0.0, operating_cost_gbp=0.0)
    # Each property rounds independently before the next subtracts, so the
    # margin is struck on rounded inputs, not rounded at the end.
    assert p.total_revenue_gbp == 0.01
    assert p.total_cost_gbp == 0.01
    assert p.gross_margin_gbp == 0.0
