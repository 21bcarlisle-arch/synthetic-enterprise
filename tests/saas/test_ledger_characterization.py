"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: saas/ledger.py — the transaction log the whole company's P&L, cash
position and board reporting are derived from. Every billing, settlement,
capital, payment, bad-debt, VAT, acquisition, fixed-cost and memo event in the
simulation is minted here, and `derive_pnl`/`derive_cash_position` are what the
annual report prints.

All inputs are fixed literals. No RNG is drawn: transaction ids are uuid5
digests, and a few are frozen verbatim so a change to the id scheme (which would
silently re-key every event in the ledger) cannot pass unnoticed.

RECORDED GAP: `build_ledger` reaches `log_decision_event`, which stamps
`datetime.now(utc)` and appends to a module-global governance log. That path is
exercised below but its timestamp is not — there is no clock injection point.
"""
from __future__ import annotations

import pytest

from saas.ledger import (
    build_ledger,
    build_payment_behaviour_map,
    derive_cash_position,
    derive_pnl,
    ledger_summary,
    make_acquisition_spend_event,
    make_back_billing_write_off_event,
    make_bad_debt_event,
    make_billing_event,
    make_capital_charge_event,
    make_cost_to_serve_event,
    make_fixed_cost_event,
    make_non_commodity_cost_event,
    make_payment_received_event,
    make_retention_cost_event,
    make_revenue_restatement_event,
    make_settlement_event,
    make_vat_remittance_event,
    unbilled_revenue_accrual,
)


def bill(customer_id="C1", period_start="2024-01-01", period_end="2024-01-31",
         total=1_000.0, kwh=2_000.0, **extra):
    b = {
        "customer_id": customer_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_amount_gbp": total,
        "total_consumption_kwh": kwh,
    }
    b.update(extra)
    return b


def record(customer_id="C1", settlement_date="2024-01-01", period=1,
           wholesale=400.0, kwh=2_000.0, rate=200.0, **extra):
    r = {
        "customer_id": customer_id,
        "settlement_date": settlement_date,
        "settlement_period": period,
        "wholesale_cost_gbp": wholesale,
        "consumption_kwh": kwh,
        "unit_rate_gbp_per_mwh": rate,
    }
    r.update(extra)
    return r


class StubPaymentBehaviour:
    """Duck-typed stand-in for the payment_behaviour module."""

    DEFAULT_CREDIT_RISK = "medium"
    CREDIT_RISK_BY_CUSTOMER = {"C1": "high", "C2": "low"}

    RATES = {"high": 0.10, "medium": 0.03, "low": 0.0}

    def bad_debt_provision_gbp(self, credit_risk, total_amount_gbp):
        return round(total_amount_gbp * self.RATES[credit_risk], 2)

    def expected_payment_date(self, period_end, credit_risk):
        return {"high": "2024-03-01", "medium": "2024-02-20", "low": "2024-02-10"}[credit_risk]


# ---------------------------------------------------------------------------
# Event constructors — sign conventions and deterministic ids
# ---------------------------------------------------------------------------


def test_the_sign_convention_is_positive_in_negative_out():
    assert make_billing_event("C1", "electricity", "2024-01-01", 100.0, 500.0)["amount_gbp"] == 100.0
    assert make_settlement_event(record(wholesale=40.0))["amount_gbp"] == -40.0
    assert make_capital_charge_event(record(capital_cost_gbp=5.0))["amount_gbp"] == -5.0
    assert make_fixed_cost_event("2024-01", 50.0)["amount_gbp"] == -50.0
    assert make_cost_to_serve_event("2024-01", 12.0)["amount_gbp"] == -12.0
    assert make_acquisition_spend_event("A1", "2024-01-01", 30.0, True, "resi")["amount_gbp"] == -30.0
    assert make_retention_cost_event("A1", "2024-01-01", 8.0, 0.2)["amount_gbp"] == -8.0
    assert make_vat_remittance_event(bill(vat_gbp=50.0))["amount_gbp"] == -50.0
    assert make_non_commodity_cost_event(bill(non_commodity_amount_gbp=200.0))["amount_gbp"] == -200.0


def test_transaction_ids_are_frozen_uuid5_digests():
    # A change to the _tid scheme would silently re-key every event in every
    # ledger and break idempotent replay (C-S2). Frozen verbatim.
    assert make_billing_event("C1", "electricity", "2024-01-01", 100.0, 1000.0)[
        "transaction_id"] == "9b9e94cc-aaa7-56d0-ba09-4b27c8fdf08a"
    assert make_fixed_cost_event("2024-01", 50.0)[
        "transaction_id"] == "8098a5f5-4985-5db9-9348-eb5aff1a4ff9"
    assert make_settlement_event(record())[
        "transaction_id"] == "d39a0d21-50da-57a4-bbcd-bf9d2b84ffa6"


def test_the_billing_id_ignores_the_amount_so_two_different_bills_collide():
    # SURPRISE: a billing event's id is keyed on (customer, commodity,
    # period_start) only. A £1,000 bill and a £9,999 rebill for the same customer
    # and period share a transaction_id, and `build_ledger` appends both — the
    # ledger carries two different amounts under one identity, so a downstream
    # consumer deduplicating on transaction_id would drop real money.
    a = make_billing_event("C1", "electricity", "2024-01-01", 1_000.0, 2_000.0)
    b = make_billing_event("C1", "electricity", "2024-01-01", 9_999.0, 2_000.0)
    assert a["transaction_id"] == b["transaction_id"]
    assert a["amount_gbp"] != b["amount_gbp"]


def test_the_fixed_cost_id_is_keyed_on_the_month_alone():
    # Two fixed-cost events for the same month — a correction, say — collide too.
    assert make_fixed_cost_event("2024-01", 50.0)["transaction_id"] == \
           make_fixed_cost_event("2024-01", 5_000.0)["transaction_id"]


def test_settlement_and_capital_ids_are_namespaced_apart():
    r = record(capital_cost_gbp=5.0)
    assert make_settlement_event(r)["transaction_id"] != make_capital_charge_event(r)["transaction_id"]


def test_a_settlement_event_carries_volume_and_rate_that_are_never_reconciled():
    # 2,000 kWh at £200/MWh is £400 of energy, and the event says £40. SURPRISE:
    # nothing in this module — or in derive_pnl — checks amount against
    # volume x rate, so an internally impossible settlement record flows through
    # to the P&L unchallenged.
    e = make_settlement_event(record(wholesale=40.0, kwh=2_000.0, rate=200.0))
    assert e["amount_gbp"] == -40.0
    assert e["volume_kwh"] * e["unit_rate_gbp_per_mwh"] / 1000.0 == 400.0


def test_the_bad_debt_event_is_dated_thirty_days_after_the_payment_date():
    e = make_bad_debt_event(bill(), 100.0, "2024-02-15")
    assert e["timestamp"] == "2024-03-16"
    assert e["amount_gbp"] == -100.0


def test_a_payment_received_event_is_billed_minus_provision():
    e = make_payment_received_event(bill(total=1_000.0), 150.0, "2024-02-15")
    assert e["amount_gbp"] == 850.0
    assert e["timestamp"] == "2024-02-15"


def test_the_memo_events_carry_zero_money_by_design():
    # Deliberate per their docstrings (a second cash event would double-count),
    # recorded because it means these lines are invisible to cash and to margin.
    wo = make_back_billing_write_off_event(bill(catchup_written_off_gbp=250.0))
    rs = make_revenue_restatement_event(bill(catchup_raw_delta_gbp=800.0,
                                             catchup_adjustment_gbp=300.0,
                                             catchup_direction="under",
                                             catchup_periods_covered=3))
    assert wo["amount_gbp"] == 0.0 and wo["write_off_amount_gbp"] == 250.0
    assert rs["amount_gbp"] == 0.0 and rs["restated_gbp"] == 800.0
    assert rs["chargeable_gbp"] == 300.0 and rs["periods_covered"] == 3


def test_memo_events_default_their_money_fields_to_zero_when_the_bill_lacks_them():
    # DELIBERATELY CORRUPT INPUT: a bill with no catchup fields at all still
    # produces a well-formed write-off event reporting £0.00 written off.
    assert make_back_billing_write_off_event(bill())["write_off_amount_gbp"] == 0.0
    assert make_revenue_restatement_event(bill())["restated_gbp"] == 0.0


# ---------------------------------------------------------------------------
# build_ledger
# ---------------------------------------------------------------------------


def test_a_minimal_ledger_is_one_settlement_and_one_billing_event():
    events = build_ledger([record()], [bill()])
    # Same timestamp, so the tiebreak is settlement_period (a billing event has
    # none, so `.get(..., 0)` sorts it first) then event_type alphabetically.
    assert [e["event_type"] for e in events] == ["billing_event", "settlement_event"]
    assert events[0]["timestamp"] == "2024-01-01"


def test_a_zero_capital_cost_produces_no_capital_event_at_all():
    # `if cap:` — a genuinely zero capital charge is indistinguishable from a
    # record that never had the field.
    assert len(build_ledger([record(capital_cost_gbp=0.0)], [])) == 1
    assert len(build_ledger([record(capital_cost_gbp=5.0)], [])) == 2


def test_events_sort_by_timestamp_then_settlement_period_then_type():
    events = build_ledger(
        [record(settlement_date="2024-01-02", period=2),
         record(settlement_date="2024-01-02", period=1)],
        [bill(period_start="2024-01-01")],
    )
    assert [(e["event_type"], e.get("settlement_period")) for e in events] == [
        ("billing_event", None), ("settlement_event", 1), ("settlement_event", 2),
    ]


def test_a_customers_commodity_is_inferred_from_their_first_settlement_record_only():
    # SURPRISE: a dual-fuel customer's bills are ALL labelled with whichever
    # commodity appeared first in the settlement records. The gas bill below is
    # stamped "electricity"; there is no per-bill commodity and no warning.
    events = build_ledger(
        [record(commodity="electricity"), record(period=2, commodity="gas")],
        [bill(), bill(period_start="2024-02-01")],
    )
    billing = [e for e in events if e["event_type"] == "billing_event"]
    assert {e["commodity"] for e in billing} == {"electricity"}


def test_a_customer_with_bills_but_no_settlement_records_defaults_to_electricity():
    events = build_ledger([], [bill(customer_id="GHOST")])
    assert events[0]["commodity"] == "electricity"


def test_vat_and_non_commodity_offsets_only_appear_when_the_bill_carries_them():
    # SURPRISE (fail-open shape): `if b.get("vat_gbp")` — a bill whose VAT is
    # missing, None or 0.0 produces no remittance event, and `derive_pnl` then
    # reports the VAT-INCLUSIVE total as ex-VAT revenue (see the P&L test below).
    # Nothing distinguishes "zero-rated" from "the field was dropped upstream".
    with_vat = build_ledger([], [bill(vat_gbp=50.0, non_commodity_amount_gbp=200.0)])
    without = build_ledger([], [bill()])
    assert {e["event_type"] for e in with_vat} == {
        "billing_event", "vat_remittance_event", "non_commodity_cost_event",
    }
    assert {e["event_type"] for e in without} == {"billing_event"}


def test_the_write_off_memo_needs_a_strictly_positive_amount_but_the_restatement_does_not():
    # Asymmetric guards on two sibling memo events: `> 0` vs truthiness.
    assert len(build_ledger([], [bill(catchup_written_off_gbp=0.0)])) == 1
    assert len(build_ledger([], [bill(catchup_written_off_gbp=0.01)])) == 2
    assert len(build_ledger([], [bill(catchup_applied=True)])) == 2
    assert len(build_ledger([], [bill(catchup_applied=False)])) == 1


def test_extra_events_are_merged_and_sorted_but_never_validated():
    # DELIBERATELY CORRUPT INPUT: `extra_events` is spliced in verbatim. A
    # caller-supplied dict with an invented event_type and a nine-figure amount
    # is accepted, sorted into the ledger, and flows into derive_cash_position.
    junk = {"transaction_id": "x", "event_type": "not_a_real_event",
            "timestamp": "2024-01-01", "amount_gbp": 999_999_999.0}
    events = build_ledger([], [bill()], extra_events=[junk])
    assert junk in events
    assert derive_cash_position(0.0, events) == 1_000_000_999.0


def test_the_payment_lifecycle_adds_a_payment_and_a_bad_debt_event():
    events = build_ledger([record()], [bill(total=1_000.0)], StubPaymentBehaviour())
    by_type = {e["event_type"]: e for e in events}
    assert by_type["payment_received_event"]["amount_gbp"] == 900.0   # high risk: 10%
    assert by_type["bad_debt_event"]["amount_gbp"] == -100.0


def test_a_zero_provision_customer_gets_a_payment_event_and_no_bad_debt_event():
    events = build_ledger([], [bill(customer_id="C2")], StubPaymentBehaviour())
    assert [e["event_type"] for e in events] == ["billing_event", "payment_received_event"]


def test_an_unknown_customer_falls_back_to_the_default_credit_risk():
    events = build_ledger([], [bill(customer_id="NEW")], StubPaymentBehaviour())
    payment = next(e for e in events if e["event_type"] == "payment_received_event")
    assert payment["amount_gbp"] == 970.0   # medium risk: 3%


def test_building_a_ledger_mutates_a_module_global_governance_log():
    # SURPRISE: `build_ledger` is documented as deriving a transaction log from
    # existing outputs, and the P&L functions below it are labelled "pure
    # function — no simulation state". But whenever a provision is raised it
    # calls `log_decision_event`, which appends to a process-wide decision log
    # and stamps `datetime.now(utc)`. Deriving the same ledger twice is NOT a
    # no-op on process state, and the events it writes are not reproducible.
    from company.governance.decision_rights import get_decision_log

    log = get_decision_log()
    before = len(log.all_records())
    build_ledger([], [bill()], StubPaymentBehaviour())
    after_once = len(log.all_records())
    build_ledger([], [bill()], StubPaymentBehaviour())
    after_twice = len(log.all_records())
    assert after_once > before
    assert after_twice > after_once   # replaying the same input logs again


# ---------------------------------------------------------------------------
# derive_pnl
# ---------------------------------------------------------------------------


def test_a_pre_phase_9a_ledger_reports_the_five_base_lines_only():
    events = build_ledger([record(wholesale=400.0, capital_cost_gbp=20.0)], [bill(total=1_000.0)])
    assert derive_pnl(events) == {
        "revenue_gbp": 1_000.0,
        "wholesale_cost_gbp": 400.0,
        "gross_margin_gbp": 600.0,
        "capital_cost_gbp": 20.0,
        "net_margin_gbp": 580.0,
    }


def test_vat_is_stripped_from_revenue_when_a_remittance_event_exists():
    events = build_ledger([record(wholesale=400.0)],
                          [bill(total=1_050.0, vat_gbp=50.0, non_commodity_amount_gbp=200.0)])
    pnl = derive_pnl(events)
    assert pnl["total_billed_gbp"] == 1_050.0
    assert pnl["vat_remittance_gbp"] == 50.0
    assert pnl["revenue_gbp"] == 1_000.0
    assert pnl["non_commodity_cost_gbp"] == 200.0
    assert pnl["gross_margin_gbp"] == 400.0


def test_a_bill_missing_its_vat_field_reports_vat_inclusive_revenue_as_revenue():
    # The consequence of the fail-open guard above: the same £1,050 gross bill
    # reports £1,050 of "ex-VAT supplier revenue" when the VAT field is absent —
    # £50 of HMRC's money booked as the company's own, with no line to show it.
    events = build_ledger([], [bill(total=1_050.0)])
    assert derive_pnl(events)["revenue_gbp"] == 1_050.0
    assert "vat_remittance_gbp" not in derive_pnl(events)


def test_cash_net_margin_never_subtracts_the_vat_the_company_must_remit():
    # SURPRISE: `revenue_gbp` is struck net of VAT, but `cash_net_margin_gbp` is
    # `cash_collected - wholesale - capital - non_commodity` — the VAT
    # remittance is missing from the subtraction even though the event exists and
    # the cash was collected VAT-inclusive. Cash margin is overstated by the full
    # VAT liability: £600 reported against a £550 accrual margin here.
    events = build_ledger(
        [record(wholesale=400.0)],
        [bill(total=1_050.0, vat_gbp=50.0)],
        StubPaymentBehaviour(),
    )
    pnl = derive_pnl(events)
    assert pnl["revenue_gbp"] == 1_000.0
    assert pnl["gross_margin_gbp"] == 600.0
    assert pnl["cash_collected_gbp"] == 945.0     # 1050 less the 10% provision
    assert pnl["bad_debt_gbp"] == 105.0
    assert pnl["cash_net_margin_gbp"] == 545.0    # 945 - 400, VAT never deducted


def test_operating_net_margin_appears_only_when_an_operating_event_exists():
    base = build_ledger([record(wholesale=400.0)], [bill(total=1_000.0)])
    assert "operating_net_margin_gbp" not in derive_pnl(base)
    with_ops = base + [make_fixed_cost_event("2024-01", 100.0),
                       make_cost_to_serve_event("2024-01", 25.0),
                       make_acquisition_spend_event("A1", "2024-01-01", 75.0, True, "resi")]
    pnl = derive_pnl(with_ops)
    assert pnl["fixed_cost_gbp"] == 100.0
    assert pnl["cost_to_serve_gbp"] == 25.0
    assert pnl["acquisition_spend_gbp"] == 75.0
    assert pnl["operating_net_margin_gbp"] == 400.0


def test_retention_cost_events_are_minted_but_never_reach_the_pnl():
    # SURPRISE: `make_retention_cost_event` exists and carries real negative cash,
    # but `derive_pnl` has no branch for `retention_cost_event`. Retention spend
    # therefore reduces the CASH POSITION (which sums everything) while appearing
    # in no margin line at all — the two views disagree by the whole spend.
    events = [make_billing_event("C1", "electricity", "2024-01-01", 1_000.0, 100.0),
              make_retention_cost_event("A1", "2024-01-05", 250.0, 0.2)]
    pnl = derive_pnl(events)
    assert pnl["net_margin_gbp"] == 1_000.0
    assert "retention_cost_gbp" not in pnl
    assert derive_cash_position(0.0, events) == 750.0


def test_an_empty_ledger_produces_a_clean_zeroed_pnl():
    # SURPRISE (fail-open shape): no events at all reports a perfectly balanced
    # £0 P&L rather than an absence. A dropped ledger and a dormant company are
    # the same report.
    assert derive_pnl([]) == {
        "revenue_gbp": 0.0, "wholesale_cost_gbp": 0.0, "gross_margin_gbp": 0.0,
        "capital_cost_gbp": 0.0, "net_margin_gbp": 0.0,
    }


def test_a_write_off_memo_event_missing_its_amount_field_raises():
    # DELIBERATELY CORRUPT INPUT: `derive_pnl` subscripts
    # e["write_off_amount_gbp"] directly rather than using .get, so a malformed
    # memo event takes down the entire P&L derivation, not just its own line.
    events = [{"transaction_id": "x", "event_type": "back_billing_write_off_event",
               "timestamp": "2024-01-31", "amount_gbp": 0.0}]
    with pytest.raises(KeyError):
        derive_pnl(events)


def test_the_memo_totals_are_reported_when_present():
    events = build_ledger([], [bill(catchup_written_off_gbp=250.0, catchup_applied=True,
                                    catchup_raw_delta_gbp=800.0)])
    pnl = derive_pnl(events)
    assert pnl["back_billing_write_off_gbp"] == 250.0
    assert pnl["revenue_restated_gbp"] == 800.0
    assert pnl["revenue_restatement_count"] == 1


# ---------------------------------------------------------------------------
# derive_cash_position
# ---------------------------------------------------------------------------


def test_cash_position_is_the_signed_sum_of_every_event():
    events = build_ledger([record(wholesale=400.0, capital_cost_gbp=20.0)], [bill(total=1_000.0)])
    assert derive_cash_position(5_000.0, events) == 5_580.0


def test_cash_position_counts_billed_revenue_twice_once_billed_once_collected():
    # SURPRISE, and the largest finding in this module: `derive_cash_position`
    # sums EVERY event's amount_gbp. `billing_event` is +£1,000 (an invoice
    # RAISED, not cash) and `payment_received_event` is +£900 (the cash actually
    # collected against that same invoice). Both are positive and both are
    # summed, so the moment payment-lifecycle events are switched on, the
    # reported cash position is roughly DOUBLE the money that moved: £1,800 here
    # for a customer who paid £900 against a £1,000 bill and defaulted on £100.
    events = build_ledger([], [bill(total=1_000.0)], StubPaymentBehaviour())
    assert sorted(e["event_type"] for e in events) == [
        "bad_debt_event", "billing_event", "payment_received_event",
    ]
    assert derive_cash_position(0.0, events) == 1_800.0   # 1000 + 900 - 100
    # Without the payment lifecycle the same bill yields the honest £1,000.
    assert derive_cash_position(0.0, build_ledger([], [bill(total=1_000.0)])) == 1_000.0


def test_cash_position_of_an_empty_ledger_is_the_opening_balance():
    assert derive_cash_position(1_234.56, []) == 1_234.56


# ---------------------------------------------------------------------------
# unbilled_revenue_accrual
# ---------------------------------------------------------------------------


def test_an_unresolved_estimated_bill_is_carried_as_unbilled_revenue():
    bills = [bill(billing_basis="estimated", total=500.0),
             bill(period_start="2024-02-01", period_end="2024-02-29",
                  billing_basis="actual", total=600.0)]
    assert unbilled_revenue_accrual(bills) == {
        "unbilled_revenue_gbp": 500.0,
        "outstanding_bill_count": 1,
        "by_customer": {"C1": 500.0},
    }


def test_a_later_catchup_covering_the_period_clears_the_accrual():
    bills = [
        bill(billing_basis="estimated", total=500.0),
        bill(period_start="2024-03-01", period_end="2024-03-31", catchup_applied=True,
             catchup_period_start="2024-01-01", catchup_period_end="2024-02-29"),
    ]
    assert unbilled_revenue_accrual(bills)["unbilled_revenue_gbp"] == 0.0


def test_a_catchup_with_a_missing_start_range_clears_every_earlier_estimate():
    # DELIBERATELY CORRUPT INPUT: `catchup_applied` set but `catchup_period_start`
    # absent. SURPRISE (fail-open): the missing bound defaults to "", and
    # `"" <= period_end <= end` is TRUE for every estimated bill up to the end
    # date. One malformed catch-up silently writes off the entire unbilled
    # revenue asset for that customer — the accrual goes to zero with no error.
    bills = [
        bill(billing_basis="estimated", total=500.0),
        bill(period_start="2023-06-01", period_end="2023-06-30",
             billing_basis="estimated", total=400.0),
        bill(period_start="2024-03-01", period_end="2024-03-31", catchup_applied=True,
             catchup_period_end="2024-02-29"),
    ]
    assert unbilled_revenue_accrual(bills) == {
        "unbilled_revenue_gbp": 0.0, "outstanding_bill_count": 0, "by_customer": {},
    }


def test_a_catchup_with_a_missing_end_range_clears_nothing():
    # The mirror case fails CLOSED — "" as the upper bound matches nothing. The
    # two missing-bound cases behave in opposite directions.
    bills = [
        bill(billing_basis="estimated", total=500.0),
        bill(period_start="2024-03-01", period_end="2024-03-31", catchup_applied=True,
             catchup_period_start="2024-01-01"),
    ]
    assert unbilled_revenue_accrual(bills)["unbilled_revenue_gbp"] == 500.0


def test_a_catchup_resolves_estimates_it_precedes_in_time():
    # SURPRISE: the range test is on dates alone with no ordering constraint, so
    # a catch-up recorded on an EARLIER bill still resolves a LATER estimate
    # whose period falls inside its range. "no LATER bill has a catchup covering
    # it" is what the docstring promises; the code checks any bill at all.
    bills = [
        bill(period_start="2023-01-01", period_end="2023-01-31", catchup_applied=True,
             catchup_period_start="2020-01-01", catchup_period_end="2030-01-01"),
        bill(billing_basis="estimated", total=500.0),
    ]
    assert unbilled_revenue_accrual(bills)["unbilled_revenue_gbp"] == 0.0


def test_a_zero_value_estimate_is_counted_but_never_attributed_to_its_customer():
    # SURPRISE: `outstanding_count` increments per unresolved bill, but the
    # `if customer_total:` guard drops any customer whose total is exactly zero.
    # The returned dict is internally inconsistent — one outstanding bill, no
    # customer owning it.
    result = unbilled_revenue_accrual([bill(billing_basis="estimated", total=0.0)])
    assert result == {
        "unbilled_revenue_gbp": 0.0, "outstanding_bill_count": 1, "by_customer": {},
    }


def test_offsetting_estimates_cancel_a_customer_out_of_the_breakdown():
    # A +£500 and a -£500 estimate net to zero, so the customer vanishes from
    # by_customer while still contributing 2 to the outstanding count.
    result = unbilled_revenue_accrual([
        bill(billing_basis="estimated", total=500.0),
        bill(period_start="2024-02-01", period_end="2024-02-29",
             billing_basis="estimated", total=-500.0),
    ])
    assert result["outstanding_bill_count"] == 2
    assert result["by_customer"] == {}


def test_a_bill_with_no_billing_basis_is_treated_as_confirmed():
    # SURPRISE (fail-open): only `billing_basis == "estimated"` counts as
    # provisional. A bill missing the field entirely — or carrying "Estimated" —
    # is silently treated as confirmed against an actual read and never accrued.
    assert unbilled_revenue_accrual([bill(total=500.0)])["unbilled_revenue_gbp"] == 0.0
    assert unbilled_revenue_accrual(
        [bill(total=500.0, billing_basis="Estimated")])["unbilled_revenue_gbp"] == 0.0


def test_an_empty_bill_list_reports_no_unbilled_revenue():
    assert unbilled_revenue_accrual([]) == {
        "unbilled_revenue_gbp": 0.0, "outstanding_bill_count": 0, "by_customer": {},
    }


# ---------------------------------------------------------------------------
# ledger_summary and build_payment_behaviour_map
# ---------------------------------------------------------------------------


def test_ledger_summary_counts_events_by_type_and_embeds_the_pnl():
    events = build_ledger([record(wholesale=400.0, capital_cost_gbp=20.0)], [bill(total=1_000.0)])
    summary = ledger_summary(events)
    assert summary["event_count"] == 3
    assert summary["by_type"] == {
        "settlement_event": 1, "capital_charge_event": 1, "billing_event": 1,
    }
    assert summary["pnl"]["net_margin_gbp"] == 580.0


def test_ledger_summary_of_an_empty_ledger():
    assert ledger_summary([]) == {"event_count": 0, "by_type": {}, "pnl": derive_pnl([])}


def test_build_payment_behaviour_map_is_a_verbatim_copy_of_the_risk_dict():
    assert build_payment_behaviour_map(StubPaymentBehaviour()) == {"C1": "high", "C2": "low"}
