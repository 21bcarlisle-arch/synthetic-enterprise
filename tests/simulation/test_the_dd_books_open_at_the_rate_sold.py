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
from simulation.experienced_bill_shock import sold_unit_rate

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
