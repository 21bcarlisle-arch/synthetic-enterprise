"""EBSS reaches both of the world's amount paths, from one door.

Defect this catches: the GBP 400 sat in `company/regulatory/energy_bill_support.py`, read by tests
and the dashboard only, so every world electricity bill from October 2022 to March 2023 asked the
household for GBP 66-67 a month more than it owed (crisis bad-debt finding, 2026-10-23 section;
`docs/market_research/energy_bills_support_scheme_delivery.md`).
"""

from __future__ import annotations

import ast
import inspect

import simulation.arrears_engine as ae
import simulation.run_phase2b as rp
from company.interfaces.bill_assembly import owed_after_scheme_credit
from company.regulatory.energy_bill_support import EBSS_INSTALMENT_GBP, ebss_credit_gbp


def _bill(cid, period_end, amount, commodity="electricity", segment="resi"):
    subtotal = amount / 1.05
    return {
        "customer_id": cid, "period_start": period_end[:8] + "01", "period_end": period_end,
        "total_consumption_kwh": 300.0, "commodity_amount_gbp": subtotal * 0.8,
        "non_commodity_amount_gbp": subtotal * 0.15, "standing_charge_gbp": subtotal * 0.05,
        "vat_gbp": amount - subtotal, "total_amount_gbp": amount,
        "average_unit_rate_gbp_per_mwh": 300.0, "clarity_score": 0.75,
        "bill_shock_pct": None, "segment": segment, "commodity": commodity,
    }


def test_the_credit_is_paid_and_withheld_where_the_scheme_says():
    # Both sides of the partition are reachable: a credit that is always zero, or never zero,
    # fails here before any branch is asked what it does.
    paid = ebss_credit_gbp("resi", "electricity", "2022-12")
    assert paid == 67.0
    assert ebss_credit_gbp("resi", "gas", "2022-12") == 0.0
    assert ebss_credit_gbp("SME", "electricity", "2022-12") == 0.0
    assert ebss_credit_gbp("resi", "electricity", "2022-09") == 0.0
    assert ebss_credit_gbp("resi", "electricity", "2023-04") == 0.0
    assert sum(EBSS_INSTALMENT_GBP.values()) == 400.0
    assert [EBSS_INSTALMENT_GBP[m] for m in sorted(EBSS_INSTALMENT_GBP)] == [66, 66, 67, 67, 67, 67]


def test_the_arrears_engine_asks_the_household_for_the_bill_net_of_the_credit():
    bills = [
        _bill("C1", "2022-11-30", 150.0),
        _bill("C1", "2022-11-30", 90.0, commodity="gas"),
        _bill("C1", "2022-09-30", 150.0),
        _bill("C2", "2023-01-31", 40.0),
    ]
    rows = {(r["customer_id"], r["period_end"], r["commodity"]): r
            for r in ae._resolve_bills(bills, {}, 42)}
    assert rows[("C1", "2022-11-30", "electricity")]["amount_gbp"] == 84.0
    assert rows[("C1", "2022-11-30", "gas")]["amount_gbp"] == 90.0
    assert rows[("C1", "2022-09-30", "electricity")]["amount_gbp"] == 150.0
    # A month the credit more than covers leaves the account in credit: nothing can fail.
    assert rows[("C2", "2023-01-31", "electricity")]["outcome"] == "credit"


def test_the_held_month_the_budget_weighs_asks_the_same_door():
    """The triad's held amount and the bill's amount net the same pounds because both call
    `owed_after_scheme_credit`. A second, hand-rolled netting in `run_phase2b` would drift."""
    src = inspect.getsource(rp)
    tree = ast.parse(src)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "attr", None) == "record_period"]
    assert calls, "run_phase2b no longer records the held month through record_period"
    for call in calls:
        amount = next(k.value for k in call.keywords if k.arg == "amount_gbp")
        named = {getattr(n, "id", None) for n in ast.walk(amount)}
        assert "owed_after_scheme_credit" in named, ast.unparse(amount)
    assert owed_after_scheme_credit(150.0, "resi", "electricity", "2022-11") == 84.0
