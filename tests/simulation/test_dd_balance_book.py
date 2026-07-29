"""Closed-loop tests for DD2 (atom DD_seasonal_cashflow_physics) --
simulation/dd_balance_book.py: the per-customer level-DD seasonal
credit/debit balance and the portfolio held-credit LIABILITY it aggregates to.
"""
from __future__ import annotations

from simulation.dd_balance_book import (
    build_dd_balance_book,
    BalancePoint,
    _SAMPLE_TRAJECTORY_CUSTOMERS,
)


def _bill(cid, period_end, amount, segment="resi", commodity="electricity"):
    return {
        "customer_id": cid,
        "period_end": period_end,
        "total_amount_gbp": amount,
        "segment": segment,
        "commodity": commodity,
    }


def _monthly_bills(cid, monthly_amounts, segment="resi", start_year=2016):
    """12*N monthly bills for one customer. `monthly_amounts` is a flat list,
    one per consecutive month."""
    out = []
    y, m = start_year, 1
    for amt in monthly_amounts:
        # last day of month is unimportant to the logic; use day 28 for safety
        out.append(_bill(cid, f"{y:04d}-{m:02d}-28", amt, segment=segment))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def _pick_ids(n, want_dd=True):
    """Real resi customer ids whose payment_method resolves to direct_debit
    (or standard_credit / non-DD when want_dd=False) -- for resi the method is
    ARCHETYPE-driven off the id, not the segment, so the fixture must select
    ids by their actual resolved method (mirrors dd_collection_book's own gate)."""
    from simulation.arrears_engine import payment_method

    ids = []
    i = 0
    while len(ids) < n and i < 5000:
        cid = f"C{i}"
        is_dd = payment_method("resi", 90.0, cid, "electricity") == "direct_debit"
        if is_dd == want_dd:
            ids.append(cid)
        i += 1
    assert len(ids) == n, "could not find enough ids of the requested method"
    return ids


# The DD balance book keys everything by customer_id, so a single fixed DD id
# is enough for the single-customer physics tests below.
_DD_ID = _pick_ids(1, want_dd=True)[0]


# ---- seasonal physics ------------------------------------------------------

def test_summer_credit_builds_winter_draws_down():
    """A perfectly seasonal customer whose annual spend equals its level DD
    ends a full year near zero, but PEAKS in credit mid-year (summer build)."""
    # Level DD in year 0 = first bill. Make month 1 (Jan) the standing DD and
    # give a summer trough of consumption so credit accrues, winter spike so it
    # draws back. Sum over the year == 12 * first bill so it returns ~level.
    jan = 100.0
    # 100,100 (Jan/Feb) then a summer dip to 40 for 6 months then winter 160.
    amounts = [jan, jan, 40, 40, 40, 40, 40, 40, 160, 160, 160, 160]
    bills = _monthly_bills(_DD_ID, amounts)
    book = build_dd_balance_book(bills)
    pts = book.trajectories[_DD_ID]
    balances = [p.balance_gbp for p in pts]
    # Credit builds during the summer dip (collect 100, consume 40 -> +60/mo).
    assert max(balances) > 0, "seasonal credit should build during summer"
    # ... and is drawn back down by the winter spike (consume 160 > collect 100).
    assert balances[-1] < max(balances), "winter should draw the credit down"


def test_balance_is_cumulative_collected_minus_consumed():
    amounts = [80.0, 50.0, 50.0]  # standing DD (year0) = 80 (first bill)
    bills = _monthly_bills(_DD_ID, amounts)
    book = build_dd_balance_book(bills)
    pts = book.trajectories[_DD_ID]
    # month1: 80-80=0 ; month2: +80-50=+30 ; month3: +80-50=+30 -> 60
    assert pts[0].balance_gbp == 0.0
    assert pts[1].balance_gbp == 30.0
    assert pts[2].balance_gbp == 60.0


def test_held_credit_is_positive_balance_only():
    """A customer in DEBIT (consumes more than collected) contributes to the
    portfolio balance but NOT to the held-credit liability (which is money OWED
    BACK -- positive balances only)."""
    # Standing DD (year0) = 50 (first bill), then consume 200/mo -> deep debit.
    amounts = [50.0, 200.0, 200.0]
    bills = _monthly_bills(_DD_ID, amounts)
    book = build_dd_balance_book(bills)
    s = book.summary()
    assert s["portfolio_final_balance_gbp"] < 0, "customer should be in debit"
    assert s["portfolio_final_held_credit_gbp"] == 0.0, (
        "a customer in debit holds no credit owed back"
    )


# ---- population gate -------------------------------------------------------

def test_non_direct_debit_customers_excluded():
    dd_id = _pick_ids(1, want_dd=True)[0]
    nondd_id = _pick_ids(1, want_dd=False)[0]
    # A non-DD resi customer AND an SME (bacs) -- both must be excluded.
    dd_bills = _monthly_bills(dd_id, [90.0] * 12)
    nondd_resi = _monthly_bills(nondd_id, [90.0] * 12)
    sme_bills = _monthly_bills("SME1", [90.0] * 12, segment="sme")
    book = build_dd_balance_book(dd_bills + nondd_resi + sme_bills)
    assert dd_id in book.trajectories
    assert nondd_id not in book.trajectories, "non-DD resi customer must not carry a DD balance"
    assert "SME1" not in book.trajectories, "SME (bacs) customer must not carry a DD balance"


# ---- determinism / idempotency (C-S2) --------------------------------------

def test_deterministic_and_order_insensitive():
    amounts = [90.0, 40.0, 40.0, 160.0, 90.0, 90.0]
    bills = _monthly_bills(_DD_ID, amounts)
    a = build_dd_balance_book(bills).serialise()
    b = build_dd_balance_book(list(reversed(bills))).serialise()
    assert a == b, "book must be a pure function of the bill SET, order-insensitive"


def test_replay_reproduces_identical_book():
    bills = _monthly_bills(_DD_ID, [90.0] * 24)
    assert build_dd_balance_book(bills).serialise() == build_dd_balance_book(bills).serialise()


# ---- year-on-year DD reset consistency with DD4a ---------------------------

def test_standing_dd_resets_from_prior_year_actual():
    """Year 1's standing level DD is the DD4a recommendation off year 0's actual
    -- the same chain dd_review_runner walks (mutual consistency)."""
    from company.billing.dd_review import _recommended_monthly
    # Year 0: first bill 100, rest 100 -> actual 1200 -> recommended 100.
    # Year 1: all 200 -> the collected each month in year1 should be the year0
    # recommendation, i.e. _recommended_monthly(1200) == 100, NOT 200.
    y0 = [100.0] * 12
    y1 = [200.0] * 12
    bills = _monthly_bills(_DD_ID, y0 + y1)
    book = build_dd_balance_book(bills)
    pts = book.trajectories[_DD_ID]
    expected_y1_dd = _recommended_monthly(sum(y0))
    for p in pts[12:24]:
        assert p.collected_gbp == round(expected_y1_dd, 2)


# ---- serialise shape -------------------------------------------------------

def test_serialise_shape_and_sample_cap():
    ids = _pick_ids(_SAMPLE_TRAJECTORY_CUSTOMERS + 4, want_dd=True)
    bills = []
    for cid in ids:
        bills += _monthly_bills(cid, [90.0] * 12)
    out = build_dd_balance_book(bills).serialise()
    assert set(out) == {"summary", "monthly_held_credit_series", "sample_trajectories"}
    assert len(out["sample_trajectories"]) == _SAMPLE_TRAJECTORY_CUSTOMERS, (
        "sample trajectories must be capped for the business surface"
    )
    s = out["summary"]
    for k in (
        "peak_held_credit_gbp", "peak_month", "trough_held_credit_gbp",
        "portfolio_final_held_credit_gbp", "n_customers", "n_ever_in_credit",
    ):
        assert k in s


def test_empty_bills_safe():
    book = build_dd_balance_book([])
    s = book.summary()
    assert s["n_customers"] == 0
    assert s["peak_held_credit_gbp"] == 0.0
    assert s["peak_month"] is None
    assert book.serialise()["monthly_held_credit_series"] == []


# ---- R15-style: the held-credit tell cannot silently read zero -------------

def test_held_credit_liability_is_actually_measured_not_fail_open():
    """Mutation guard: a customer who is genuinely IN CREDIT must move the
    portfolio held-credit liability off zero. If build_dd_balance_book ever
    fails open (drops the population, forces held credit to 0), this reds."""
    # Standing DD (year0) = 100, then a long summer of low consumption -> large
    # sustained credit that cannot round to zero.
    amounts = [100.0] + [20.0] * 8
    bills = _monthly_bills(_DD_ID, amounts)
    s = build_dd_balance_book(bills).summary()
    assert s["peak_held_credit_gbp"] > 100.0, (
        "a sustained-credit customer must register real held credit"
    )
    assert s["n_ever_in_credit"] == 1
