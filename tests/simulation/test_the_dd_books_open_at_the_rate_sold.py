"""The company's DD books open each account at the rate it was SOLD at, not at the cap.

`simulation/run_phase4c_on_phase2b._opening_dd_by_customer` is the production caller of
`opening_monthly_amount` for the DD balance book and the annual review. Until 2026-10-01 it
passed no contracted rate, so every pre-2019 account was unestimated (no cap existed) and every
post-2019 fixed account opened at the default-tariff cap. Each test names the defect it catches.
"""
from __future__ import annotations

import ast
import inspect

from simulation import run_phase4c_on_phase2b as run4c
from simulation.experienced_bill_shock import (
    opening_monthly_for_household,
    sold_standing_charge,
    sold_unit_rate,
)
from simulation.household import household_of

_PRE_CAP = {"customer_id": "C-PRE", "acquisition_date": "2016-03-01",
            "commodity": "electricity", "eac_kwh": 3100.0}
_POST_CAP = {"customer_id": "C-POST", "acquisition_date": "2021-03-01",
             "commodity": "electricity", "eac_kwh": 3100.0}


def _first_month(cid: str, period: str, rate: float) -> list[dict]:
    return [{"customer_id": cid, "settlement_date": f"{period}-{d:02d}",
             "unit_rate_gbp_per_mwh": rate, "consumption_kwh": 8.0} for d in range(1, 29)]


_RECORDS = _first_month("C-PRE", "2016-03", 110.0) + _first_month("C-POST", "2021-03", 120.0)


def test_both_arms_are_reachable_and_only_the_sold_rate_opens_a_pre_cap_account():
    """Defect: a pre-2019 account stays unestimated because the caller passes no rate. And the
    partition: without records the cap arm still refuses it and still opens the post-cap one."""
    cap_arm = run4c._opening_dd_by_customer([_PRE_CAP, _POST_CAP])
    sold_arm = run4c._opening_dd_by_customer([_PRE_CAP, _POST_CAP], _RECORDS)
    assert "C-PRE" not in cap_arm and "C-POST" in cap_arm
    assert "C-PRE" in sold_arm and "C-POST" in sold_arm


def test_the_opening_is_sized_at_the_rate_on_the_first_bill():
    """Defect: the sold rate is read but not used, or read from the wrong rows. Doubling the
    first-month rate must move the opening, and the rate used must be `sold_unit_rate`'s."""
    assert sold_unit_rate("C-POST", _RECORDS) == 120.0
    base = run4c._opening_dd_by_customer([_POST_CAP], _RECORDS)["C-POST"]
    doubled = run4c._opening_dd_by_customer(
        [_POST_CAP], _first_month("C-POST", "2021-03", 240.0))["C-POST"]
    assert doubled > base * 1.5


def test_an_account_with_no_settled_rate_falls_back_to_the_cap_not_to_zero():
    """Defect: an account absent from the book is opened at a rate of None→0 or dropped."""
    cap_only = run4c._opening_dd_by_customer([_POST_CAP])["C-POST"]
    other = _first_month("C-OTHER", "2021-03", 50.0)
    assert run4c._opening_dd_by_customer([_POST_CAP], other)["C-POST"] == cap_only
    assert "C-PRE" not in run4c._opening_dd_by_customer([_PRE_CAP], other)


def test_the_run_hands_its_settlement_book_to_the_dd_opening():
    """Defect: the rule exists and no production caller reaches it -- `main` calls
    `_opening_dd_by_customer` with the customers alone, so the books open at the cap again."""
    tree = ast.parse(inspect.getsource(run4c.main))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "_opening_dd_by_customer"]
    assert len(calls) == 1
    assert len(calls[0].args) == 2 and getattr(calls[0].args[1], "id", None) == "all_records"


def _with_standing_charge(rows: list[dict], gbp_per_day: float) -> list[dict]:
    return [{**r, "standing_charge_gbp": gbp_per_day} for r in rows]


def test_the_opening_is_sized_at_the_standing_charge_on_the_first_bill():
    """Defect: the books quote the door's 53p 2024 charge while the bill shock quotes the first
    bill's (22p gas in 2016), so the two disagree about what the household was told. The charge
    sold must move the opening, an account whose first month carries none must keep the fallback,
    and the books must quote exactly what the bill shock quotes for the same leg."""
    low = _with_standing_charge(_first_month("C-POST", "2021-03", 120.0), 0.20)
    high = _with_standing_charge(_first_month("C-POST", "2021-03", 120.0), 0.80)
    assert sold_standing_charge("C-POST", low) == 0.20
    at_low = run4c._opening_dd_by_customer([_POST_CAP], low)["C-POST"]
    at_high = run4c._opening_dd_by_customer([_POST_CAP], high)["C-POST"]
    no_charge = run4c._opening_dd_by_customer([_POST_CAP], _RECORDS)["C-POST"]
    assert at_low < no_charge < at_high
    leg = {**_POST_CAP, "customer_id": "C9"}
    rows = [{**r, "customer_id": "C9"} for r in low]
    assert run4c._opening_dd_by_customer([leg], rows)["C9"] == opening_monthly_for_household(
        household_of("C9"), [leg], rows)


def test_a_tou_account_is_sold_at_its_weighted_rate_not_its_off_peak_leg():
    """Defect: the daily row's `unit_rate_gbp_per_mwh` is the 00:00 rate, off-peak on a ToU
    account, so the books opened every ToU household about a fifth low. Read through the real
    fold, the sold rate is the month's consumption-weighted rate; a row the fold did not make
    still reads its own rate (the fallback the tests above exercise)."""
    from simulation.settlement_daily import fold_to_days

    periods = [{"customer_id": "C-TOU", "commodity": "electricity",
                "settlement_date": f"2024-06-{d:02d}", "settlement_period": p,
                "consumption_kwh": 1.0 if p == 1 else 3.0,
                "unit_rate_gbp_per_mwh": 110.0 if p == 1 else 210.0}
               for d in range(1, 29) for p in (1, 34)]
    days = fold_to_days(periods)
    assert all(r["unit_rate_gbp_per_mwh"] == 110.0 for r in days)
    assert abs(sold_unit_rate("C-TOU", days) - 185.0) < 1e-9
