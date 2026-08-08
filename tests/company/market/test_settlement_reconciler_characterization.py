"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/market/settlement_reconciler.py — the M1 Elexon settlement
interface. Every half-hourly BSC settlement statement the company receives is
reconciled here against its own billed revenue; this is the control that is
supposed to catch the company being charged for energy it did not sell.

All inputs are fixed literals; no randomness and no wall-clock reads. The
module takes no dates of its own — `period` is an opaque string — so there is
no time-dependent path to work around.
"""
from __future__ import annotations

import pytest

from company.market.settlement_reconciler import (
    IMBALANCE_FLAG_THRESHOLD_GBP,
    IMBALANCE_REPORT_THRESHOLD_PCT,
    SettlementStatement,
    imbalance_summary,
    receive_settlement,
    reconcile_against_bill,
    reconcile_period_batch,
)

P1 = "2024-01-15T00:00:00"
P2 = "2024-01-15T00:30:00"


def stmt(cost, customer_id="C1", period=P1, volume_kwh=1000.0, ssp=100.0, hedge=0.0):
    return receive_settlement(
        period=period,
        customer_id=customer_id,
        volume_kwh=volume_kwh,
        ssp_gbp_per_mwh=ssp,
        net_settlement_cost_gbp=cost,
        hedge_pnl_gbp=hedge,
    )


# ---------------------------------------------------------------------------
# receive_settlement: the pure constructor
# ---------------------------------------------------------------------------


def test_receive_settlement_is_a_verbatim_constructor():
    s = receive_settlement(P1, "C1", 1000.0, 100.0, 100.0, 5.0)
    assert isinstance(s, SettlementStatement)
    assert (s.period, s.customer_id, s.volume_kwh) == (P1, "C1", 1000.0)
    assert (s.ssp_gbp_per_mwh, s.net_settlement_cost_gbp, s.hedge_pnl_gbp) == (100.0, 100.0, 5.0)


def test_receive_settlement_does_not_check_the_statements_own_arithmetic():
    # SURPRISE: 1,000 kWh at £100/MWh is £100 of energy, but the statement says
    # £3.00 and is accepted verbatim. `receive_settlement` validates nothing —
    # volume x SSP is never compared against net_settlement_cost_gbp, here or
    # anywhere else in the module. A statement that is internally impossible is
    # indistinguishable from a correct one.
    s = receive_settlement(P1, "C1", volume_kwh=1000.0, ssp_gbp_per_mwh=100.0,
                           net_settlement_cost_gbp=3.0)
    assert s.net_settlement_cost_gbp == 3.0
    assert s.volume_kwh * s.ssp_gbp_per_mwh / 1000.0 == 100.0  # what it should have been


def test_negative_volume_and_negative_price_are_accepted():
    s = receive_settlement(P1, "C1", volume_kwh=-500.0, ssp_gbp_per_mwh=-40.0,
                           net_settlement_cost_gbp=0.0)
    assert (s.volume_kwh, s.ssp_gbp_per_mwh) == (-500.0, -40.0)


# ---------------------------------------------------------------------------
# reconcile_against_bill — the reconciliation control itself
# ---------------------------------------------------------------------------


def test_a_clean_reconciliation_is_not_flagged():
    r = reconcile_against_bill(stmt(100.0), billed_revenue_gbp=105.0)
    assert r == {
        "period": P1,
        "customer_id": "C1",
        "billed_revenue_gbp": 105.0,
        "net_settlement_cost_gbp": 100.0,
        "imbalance_gbp": 5.0,
        "imbalance_pct": 5.0,
        "flagged": False,
    }


def test_the_pct_test_is_strictly_greater_than_so_exactly_five_pct_passes():
    # 5.0% is not > 5.0, and £5 is not > £10 — the boundary case passes both legs.
    assert reconcile_against_bill(stmt(100.0), 105.0)["flagged"] is False
    assert reconcile_against_bill(stmt(100.0), 105.01)["flagged"] is True


def test_the_control_cannot_fire_on_a_corrupt_statement_only_on_a_revenue_gap():
    # DELIBERATELY CORRUPT INPUT. The statement claims 1,000 kWh settled at
    # £100/MWh — £100 of energy — but bills the company £3. The company billed
    # its customer £3.05. SURPRISE: the reconciliation reports a 1.7% imbalance
    # and does NOT flag. `reconcile_against_bill` only ever compares billed
    # revenue against the cost line; volume_kwh and ssp_gbp_per_mwh are carried
    # on the statement and never read. The one input that makes the statement
    # provably wrong is invisible to the control that exists to catch it.
    corrupt = stmt(cost=3.0, volume_kwh=1000.0, ssp=100.0)
    r = reconcile_against_bill(corrupt, billed_revenue_gbp=3.05)
    assert r["flagged"] is False
    assert r["imbalance_gbp"] == 0.05
    assert r["imbalance_pct"] == 1.7


def test_hedge_pnl_is_recorded_on_the_statement_and_never_reconciled():
    # SURPRISE: hedge_pnl_gbp is a documented field of a settlement statement
    # ("hedge gain/loss recorded against this period") but no function in the
    # module reads it. A period whose entire economics are a £5,000 hedge loss
    # reconciles identically to one with no hedge at all.
    no_hedge = reconcile_against_bill(stmt(100.0, hedge=0.0), 105.0)
    big_loss = reconcile_against_bill(stmt(100.0, hedge=-5000.0), 105.0)
    assert no_hedge == big_loss


def test_the_ten_pound_absolute_floor_overrides_any_caller_supplied_threshold():
    # SURPRISE: `threshold_pct` is a parameter, but `flagged` is an OR against a
    # module-level £10 constant the caller cannot reach. On a £1,000,000
    # settlement an £11 discrepancy — 0.0011% — is flagged no matter what
    # threshold is passed. At portfolio scale this control flags everything.
    big = stmt(1_000_000.0)
    r = reconcile_against_bill(big, billed_revenue_gbp=1_000_011.0, threshold_pct=50.0)
    assert r["imbalance_pct"] == 0.0
    assert r["flagged"] is True
    assert IMBALANCE_FLAG_THRESHOLD_GBP == 10.0


def test_a_generous_threshold_still_cannot_unflag_a_small_absolute_gap():
    r = reconcile_against_bill(stmt(100.0), billed_revenue_gbp=200.0, threshold_pct=1000.0)
    assert r["imbalance_pct"] == 100.0  # well under the 1000% threshold
    assert r["flagged"] is True         # ...but £100 > £10, so flagged anyway


def test_a_zero_cost_statement_reports_zero_pct_not_infinity():
    # The <£0.01 guard means pct is reported as 0.0 rather than dividing by zero.
    # SURPRISE: 0.0% reads as "perfectly reconciled" in the output dict; only the
    # separate £10 leg distinguishes it. A £9 bill against a £0 settlement cost
    # is therefore recorded as a 0.0% imbalance and not flagged.
    r = reconcile_against_bill(stmt(0.0), billed_revenue_gbp=9.0)
    assert (r["imbalance_gbp"], r["imbalance_pct"], r["flagged"]) == (9.0, 0.0, False)


def test_pct_uses_absolute_values_so_a_sign_flip_is_invisible_in_the_pct():
    # A £-100 settlement (we are owed money) against £105 billed.
    r = reconcile_against_bill(stmt(-100.0), billed_revenue_gbp=105.0)
    assert r["imbalance_gbp"] == 205.0
    assert r["imbalance_pct"] == 205.0


@pytest.mark.parametrize("cost,revenue,imbalance", [(100.0, 105.0, 5.0), (100.0, 95.0, -5.0)])
def test_imbalance_sign_convention_positive_is_profitable(cost, revenue, imbalance):
    assert reconcile_against_bill(stmt(cost), revenue)["imbalance_gbp"] == imbalance


def test_rounding_is_two_dp_on_money_and_one_dp_on_pct():
    r = reconcile_against_bill(stmt(3.0), billed_revenue_gbp=3.456)
    assert r["billed_revenue_gbp"] == 3.46
    assert r["imbalance_gbp"] == 0.46
    assert r["imbalance_pct"] == 15.2


# ---------------------------------------------------------------------------
# reconcile_period_batch
# ---------------------------------------------------------------------------


def test_batch_reconciles_each_statement_against_its_customers_revenue():
    batch = reconcile_period_batch(
        [stmt(100.0, "C1"), stmt(200.0, "C2", period=P2)],
        {"C1": 105.0, "C2": 210.0},
    )
    assert batch["checked"] == 2
    assert batch["total_imbalance_gbp"] == 15.0
    # Both legs are strictly-greater-than, so C2's exactly-£10 / exactly-5.0%
    # gap clears both and nothing is flagged.
    assert batch["flagged_count"] == 0
    assert [r["imbalance_gbp"] for r in batch["results"]] == [5.0, 10.0]


def test_a_customer_missing_from_billed_revenues_is_treated_as_zero_revenue():
    # DELIBERATELY CORRUPT INPUT: C2's billing record is absent from the batch.
    # SURPRISE: `.get(cid, 0.0)` makes a MISSING billing record indistinguishable
    # from a genuine zero-revenue customer. The statement is silently reconciled
    # against £0 and reported as a £200 adverse imbalance — a data-integrity
    # failure is laundered into a trading loss with no separate signal.
    batch = reconcile_period_batch([stmt(200.0, "C2")], {})
    assert batch["results"][0]["billed_revenue_gbp"] == 0.0
    assert batch["results"][0]["imbalance_gbp"] == -200.0
    assert batch["flagged_count"] == 1


def test_extra_customers_in_billed_revenues_are_silently_ignored():
    # The other direction: revenue billed for a customer with NO settlement
    # statement never appears in the batch at all. `checked` counts statements,
    # so a whole customer going missing from settlement is not detectable here.
    batch = reconcile_period_batch([stmt(100.0, "C1")], {"C1": 105.0, "GHOST": 9_999.0})
    assert batch["checked"] == 1
    assert [r["customer_id"] for r in batch["results"]] == ["C1"]


def test_batch_totals_are_the_sum_of_already_rounded_rows():
    # total_imbalance accumulates the ROUNDED per-row figures, so the batch total
    # is not the same as reconciling the un-rounded sum. Frozen as-is.
    batch = reconcile_period_batch(
        [stmt(1.0, "C1"), stmt(1.0, "C2"), stmt(1.0, "C3")],
        {"C1": 1.005, "C2": 1.005, "C3": 1.005},
    )
    assert [r["imbalance_gbp"] for r in batch["results"]] == [0.0, 0.0, 0.0]
    assert batch["total_imbalance_gbp"] == 0.0


def test_empty_batch_is_a_clean_zero():
    assert reconcile_period_batch([], {}) == {
        "results": [], "total_imbalance_gbp": 0.0, "flagged_count": 0, "checked": 0,
    }


# ---------------------------------------------------------------------------
# imbalance_summary
# ---------------------------------------------------------------------------


def test_summary_partitions_rows_by_sign_and_drops_exact_zeros():
    # SURPRISE: favourable_count + unfavourable_count does not equal `checked`.
    # An exactly-zero imbalance — the perfectly reconciled case — is counted in
    # neither bucket, so a summary reading "0 favourable, 0 unfavourable, 3
    # checked" is what a flawless period looks like as well as an empty one.
    batch = reconcile_period_batch(
        [stmt(100.0, "C1"), stmt(100.0, "C2"), stmt(100.0, "C3")],
        {"C1": 100.0, "C2": 100.0, "C3": 100.0},
    )
    s = imbalance_summary(batch)
    assert s == {
        "total_imbalance_gbp": 0.0,
        "favourable_count": 0,
        "unfavourable_count": 0,
        "flagged_count": 0,
        "checked": 3,
        "net_position": "favourable",
    }


def test_net_position_calls_a_dead_flat_zero_favourable():
    # `>= 0` — a net position of exactly nothing is reported as "favourable".
    assert imbalance_summary({"total_imbalance_gbp": 0.0})["net_position"] == "favourable"
    assert imbalance_summary({"total_imbalance_gbp": -0.01})["net_position"] == "unfavourable"


def test_summary_of_an_empty_dict_reports_a_favourable_position():
    # SURPRISE (fail-open shape): summarising a batch result that is entirely
    # missing — no results key, no totals — returns a well-formed, cheerful
    # report rather than raising. A dropped batch reads as a clean period.
    assert imbalance_summary({}) == {
        "total_imbalance_gbp": 0.0,
        "favourable_count": 0,
        "unfavourable_count": 0,
        "flagged_count": 0,
        "checked": 0,
        "net_position": "favourable",
    }


def test_summary_offsets_a_large_loss_against_a_large_gain():
    # Netting is the whole design, but recorded because the summary reports one
    # "net_position" for a period containing a £500 win and a £500 loss.
    batch = reconcile_period_batch(
        [stmt(100.0, "C1"), stmt(100.0, "C2")],
        {"C1": 600.0, "C2": -400.0},
    )
    s = imbalance_summary(batch)
    assert (s["favourable_count"], s["unfavourable_count"]) == (1, 1)
    assert s["total_imbalance_gbp"] == 0.0
    assert s["net_position"] == "favourable"
    assert s["flagged_count"] == 2


def test_module_thresholds_are_the_documented_constants():
    assert IMBALANCE_FLAG_THRESHOLD_GBP == 10.0
    assert IMBALANCE_REPORT_THRESHOLD_PCT == 5.0
