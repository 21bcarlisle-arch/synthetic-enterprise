"""Controls on `tools/dd_book_legs.py`, the split of the DD book's balance into named legs.

The subject is an attribution. An attribution whose legs do not sum to the thing attributed
still prints a plausible table, so the sum is checked first and each leg is pinned to a hand
computation second.
"""
from __future__ import annotations

from datetime import date

import pytest

import tools.dd_book_legs as legs_mod
from simulation.arrears_engine import payment_method
from tools.dd_book_legs import account_legs, decompose

# One account, opening debit £10. Window 0 bills £12.50 a month (£150), so the review sets
# round(12.5 + 0.5) = £13. Window 1 averages £15 a month but opens on three £21 bills.
# By hand at the third window-1 bill: opening (10 - 12.5) * 12 = -30, rounding (13 - 12.5) * 3
# = +1.5, review lag (12.5 - 15) * 3 = -7.5, seasonal phase 15 * 3 - 63 = -18. Total -54, which
# is also 10 * 12 - 150 + 13 * 3 - 63.
WINDOW_0 = [12.5] * 12
WINDOW_1 = [21.0] * 3 + [13.0] * 9


def _seq():
    out = []
    for i, amt in enumerate(WINDOW_0 + WINDOW_1):
        y, m = divmod(i, 12)
        end = date(2016 + y, m + 1, 28)
        out.append((end, end.replace(day=1), amt, amt))
    return out


def test_each_leg_matches_the_hand_computation():
    """DEFECT: a leg is computed against the wrong level, so the money moves between legs.

    The sum check alone cannot see this. Rounding booked as review lag, for example, still sums.
    """
    got = account_legs(_seq(), 10.0, "2017-03")
    assert got["balance_gbp"] == pytest.approx(-54.0)
    assert got["legs"]["opening_sizing"] == pytest.approx(-30.0)
    assert got["legs"]["rounding"] == pytest.approx(1.5)
    assert got["legs"]["review_lag"] == pytest.approx(-7.5)
    assert got["legs"]["seasonal_phase"] == pytest.approx(-18.0)
    assert got["legs"]["estimate_vs_actual"] == pytest.approx(0.0)
    assert got["window"] == 1 and got["window_start_month"] == 1 and got["winter_start"]


def test_a_billed_estimate_above_the_true_charge_is_its_own_leg():
    """DEFECT: estimation is folded into the level or the phase, so the estimate-v-actual leg
    always reads zero."""
    seq = _seq()
    end, start, _, true = seq[13]
    seq[13] = (end, start, true + 4.0, true)
    got = account_legs(seq, 10.0, "2017-03")
    assert got["legs"]["estimate_vs_actual"] == pytest.approx(-4.0)
    assert sum(got["legs"].values()) == pytest.approx(got["balance_gbp"])


def _bills(cid: str) -> list[dict]:
    return [{"customer_id": cid, "period_start": start.isoformat(), "period_end": end.isoformat(),
             "total_amount_gbp": amt, "segment": "resi", "commodity": "electricity"}
            for end, start, amt, _ in _seq()]


def _a_direct_debit_id() -> str:
    for i in range(1, 500):
        cid = f"C{i}"
        if payment_method("resi", 10.0, cid, "electricity") == "direct_debit":
            return cid
    raise AssertionError("no direct-debit id in C1..C499")


def test_the_legs_sum_to_the_books_own_balance_and_a_dropped_leg_is_refused(monkeypatch):
    """DEFECT: the legs describe a different book from `build_dd_balance_book`, or a leg is lost.

    The refusal is only worth having if it can fire, so the happy path must first admit the
    account (n_accounts == 1) before a dropped leg is shown to be refused.
    """
    cid = _a_direct_debit_id()
    out = decompose(_bills(cid), {cid: 10.0}, "2017-03")
    assert out["groups"]["all"]["n_accounts"] == 1
    assert out["groups"]["all"]["balance_gbp"] == pytest.approx(-54.0)
    assert out["book_portfolio_balance_gbp"] == pytest.approx(-54.0)

    real = legs_mod.account_legs

    def drops_rounding(*a, **k):
        got = real(*a, **k)
        if got:
            got["legs"]["rounding"] = 0.0
        return got

    monkeypatch.setattr(legs_mod, "account_legs", drops_rounding)
    with pytest.raises(ValueError, match="legs"):
        decompose(_bills(cid), {cid: 10.0}, "2017-03")
