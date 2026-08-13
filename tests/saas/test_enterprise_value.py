import pytest

from saas.clv_model import build_clv
from saas.enterprise_value import (
    adjust_churn_risk_for_home_move,
    build_enterprise_value,
    effective_churn_probability,
)
from saas.home_move_win_rate import build_home_move_win_rates

CUSTOMERS = [
    {"customer_id": "C1", "segment": "resi", "epc_rating": "D"},
    {"customer_id": "C2", "segment": "resi", "epc_rating": "D"},
    {"customer_id": "C3", "segment": "resi", "epc_rating": "D"},
]

CHURN_RISK = {
    "C1": [
        {"renewal_period": "2017-01", "bill_shock_count": 1, "churn_probability": 0.08},
        {"renewal_period": "2018-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2019-01", "bill_shock_count": 2, "churn_probability": 0.11},
    ],
    "C2": [
        {"renewal_period": "2017-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2018-01", "bill_shock_count": 0, "churn_probability": 0.05},
    ],
    "C3": [],
}

COST_TO_SERVE = {
    "by_customer": {
        "C1": {"cost_to_serve_gbp": 100.0, "margin_gbp": 500.0, "net_margin_gbp": 400.0},
        "C1g": {"cost_to_serve_gbp": 50.0, "margin_gbp": 200.0, "net_margin_gbp": 150.0},
        "C2": {"cost_to_serve_gbp": 80.0, "margin_gbp": 300.0, "net_margin_gbp": 220.0},
    }
}


def test_effective_churn_probability_is_product_of_churn_and_loss():
    assert effective_churn_probability(0.1, 0.6) == pytest.approx(0.1 * 0.4)


def test_effective_churn_probability_zero_when_win_probability_is_one():
    assert effective_churn_probability(0.5, 1.0) == 0.0


def test_effective_churn_probability_equals_churn_when_win_probability_is_zero():
    assert effective_churn_probability(0.5, 0.0) == 0.5


def test_adjust_churn_risk_reduces_churn_probability():
    win_rates = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, price_differential_pct=0.0)
    adjusted = adjust_churn_risk_for_home_move(CHURN_RISK, win_rates)

    for account_id in ("C1", "C2"):
        for raw, adj in zip(CHURN_RISK[account_id], adjusted[account_id]):
            assert adj["churn_probability"] < raw["churn_probability"]
            assert adj["renewal_period"] == raw["renewal_period"]
            assert adj["bill_shock_count"] == raw["bill_shock_count"]


def test_adjust_churn_risk_preserves_accounts_with_no_renewals():
    win_rates = build_home_move_win_rates(CHURN_RISK, CUSTOMERS, 0.0)
    adjusted = adjust_churn_risk_for_home_move(CHURN_RISK, win_rates)
    assert adjusted["C3"] == []


def test_build_enterprise_value_excludes_accounts_with_no_renewals():
    result = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, ceased_accounts=set(), n_draws=50)
    assert set(result["by_customer"].keys()) == {"C1", "C2"}
    assert result["portfolio"]["account_count"] == 2


def test_build_enterprise_value_portfolio_total_matches_sum_of_accounts():
    result = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, ceased_accounts=set(), n_draws=50)
    total = sum(entry["clv_gbp"] for entry in result["by_customer"].values())
    assert result["portfolio"]["enterprise_value_gbp"] == pytest.approx(total)


def test_home_move_win_back_increases_clv_versus_raw_churn():
    # Lower effective churn (thanks to win-back potential) -> longer expected
    # lifetime -> higher CLV than clv_model's raw-churn projection.
    raw_clv = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    result = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, ceased_accounts=set(), n_draws=50)

    for account_id in ("C1", "C2"):
        assert result["by_customer"][account_id]["clv_gbp"] >= raw_clv[account_id]["clv_gbp"]


def test_higher_price_differential_reduces_enterprise_value():
    # A price disadvantage lowers win_probability, raising effective churn,
    # which should not increase enterprise value relative to price parity.
    at_parity = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, ceased_accounts=set(), n_draws=50)
    overpriced = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.1, ceased_accounts=set(), n_draws=50)

    assert overpriced["portfolio"]["enterprise_value_gbp"] <= at_parity["portfolio"]["enterprise_value_gbp"]


def test_build_enterprise_value_empty_churn_risk_returns_empty():
    result = build_enterprise_value({"C1": []}, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, ceased_accounts=set(), n_draws=50)
    assert result["by_customer"] == {}
    assert result["portfolio"] == {"enterprise_value_gbp": 0.0, "account_count": 0}


def test_effective_churn_probability_monotone_in_churn_rate():
    # Higher raw churn -> higher effective churn (for fixed win probability)
    low = effective_churn_probability(0.05, 0.5)
    high = effective_churn_probability(0.10, 0.5)
    assert high > low


def test_build_enterprise_value_by_customer_has_clv_key():
    result = build_enterprise_value(CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, ceased_accounts=set(), n_draws=50)
    for entry in result["by_customer"].values():
        assert "clv_gbp" in entry


def test_effective_churn_probability_bounded_by_raw_churn():
    raw = 0.15
    result = effective_churn_probability(raw, 0.5)
    assert 0.0 <= result <= raw


# ---------------------------------------------------------------------------
# THE VALUED POPULATION IS THE SUPPLIED BOOK
#
# WORKER_FINDING_THE_BOOK_VALUE_COUNTS_CUSTOMERS_WHO_HAVE_ALREADY_LEFT (BLOCKING,
# lane B_commercial, 2026-08-13): five of thirteen billing accounts churned during
# the published run and every one still carried a forward-looking CLV in the final
# artefact and in every year-end snapshot after it left -- 51.8% of the residential
# book's published CLV total. `build_enterprise_value`'s roster was "has renewal
# history", never "is still supplied".
# ---------------------------------------------------------------------------

from datetime import date, timedelta  # noqa: E402

from saas.enterprise_value import (  # noqa: E402
    SUPPLY_CONTINUITY_DAYS,
    ceased_billing_accounts,
)


def _daily_records(customer_id: str, start: str, end: str) -> list[dict]:
    """Settlement records for a supplied meter point: one per day it is on
    supply, matching `simulation/settlement.py`'s emission (48 periods a day
    for every day between acquisition and contract end)."""
    day, last = date.fromisoformat(start), date.fromisoformat(end)
    out = []
    while day <= last:
        out.append({"customer_id": customer_id, "settlement_date": day.isoformat()})
        day += timedelta(days=1)
    return out


# C1 stops settling at the end of 2021; C2 settles to the edge of the window.
BOOK_RECORDS = (
    _daily_records("C1", "2021-11-01", "2021-12-30")
    + _daily_records("C1g", "2021-11-01", "2021-12-30")
    + _daily_records("C2", "2021-11-01", "2025-12-31")
    + _daily_records("C2g", "2021-11-01", "2025-12-31")
)


def test_ceased_accounts_are_read_off_the_suppliers_own_settled_records():
    """The account that went quiet is ceased; the one still settling is not."""
    ceased = ceased_billing_accounts(BOOK_RECORDS)
    assert ceased == {"C1"}


def test_a_dual_fuel_account_is_ceased_only_when_both_legs_go_quiet():
    """Losing the electricity leg is not losing the household -- the gas leg is
    still on supply and still worth something, so the account stays valued."""
    half_gone = (
        _daily_records("C1", "2021-11-01", "2021-12-30")      # elec leg stops
        + _daily_records("C1g", "2021-11-01", "2025-12-31")   # gas leg continues
        + _daily_records("C2", "2021-11-01", "2025-12-31")
    )
    assert ceased_billing_accounts(half_gone) == set()


def test_an_account_that_only_just_left_is_not_yet_declared_ceased():
    """The supplier cannot tell a cessation from a late read inside the
    continuity window, and this control pins that it does not pretend to.
    C1's last record is 2021-12-30; as at 2021-12-31 it is still on the book."""
    assert ceased_billing_accounts(BOOK_RECORDS, as_of="2021-12-31") == set()
    beyond = (date(2021, 12, 30) + timedelta(days=SUPPLY_CONTINUITY_DAYS + 1)).isoformat()
    assert ceased_billing_accounts(BOOK_RECORDS, as_of=beyond) == {"C1"}


def test_no_records_declares_no_cessations():
    """Absent data must not manufacture a cessation -- an empty book is not a
    book of departed customers."""
    assert ceased_billing_accounts([]) == set()


def test_a_ceased_account_is_dropped_from_the_valued_book():
    """The finding's headline: an account that has gone carries no forward value."""
    result = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts={"C1"}, n_draws=50,
    )
    assert "C1" not in result["by_customer"]
    assert result["portfolio"]["account_count"] == 1
    assert result["excluded_ceased_accounts"] == ["C1"]


def test_the_exclusion_is_not_vacuous_the_same_account_is_valued_when_supplied():
    """Anti-vacuity in the direction that matters: the test above must be
    removing something. With nobody ceased, C1 is valued and carries real money,
    so `by_customer` shrinking is the exclusion working and not C1 having been
    absent all along."""
    valued = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts=set(), n_draws=50,
    )
    assert "C1" in valued["by_customer"]
    assert valued["by_customer"]["C1"]["clv_gbp"] > 0
    assert valued["excluded_ceased_accounts"] == []


def test_mutation_a_valued_account_marked_ceased_removes_its_value_from_the_total():
    """R15, the mutation the finding named: mark one valued account as ceased and
    the book must lose its value.

    EXACT ADDITIVITY, restored 2026-08-13. The book-value finding originally
    asked for "the total must fall by EXACTLY that account's CLV" and this test
    could not assert it: the sibling BLOCKING finding
    (WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES)
    meant the per-account lifetime came out of a posterior-predictive draw, so
    removing C1 also moved C2's projection. Rather than tune this control green
    against a defect it is not about, the coupling was pinned by a tripwire test
    (`test_removing_one_account_still_moves_another_accounts_projection`) that
    would go red the day the estimator was fixed. It did. The estimator is now
    per-account and deterministic (`clv_model.fit_theta_posterior_per_account`),
    a retained account's projection no longer depends on who else is in the
    valued draw, the tripwire has been deleted as it instructed, and the
    exact-equality assertion the finding asked for is written below."""
    full = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts=set(), n_draws=50,
    )
    mutated = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts={"C1"}, n_draws=50,
    )
    assert mutated["portfolio"]["enterprise_value_gbp"] < full["portfolio"]["enterprise_value_gbp"]
    # The total is exactly the accounts that remain -- no residue of the departed.
    assert mutated["portfolio"]["enterprise_value_gbp"] == pytest.approx(
        sum(e["clv_gbp"] for e in mutated["by_customer"].values())
    )
    assert full["by_customer"]["C1"]["clv_gbp"] not in [
        e["clv_gbp"] for e in mutated["by_customer"].values()
    ]
    # The exact-additivity assertion the book-value finding asked for: the book
    # loses C1's value and NOTHING ELSE.
    assert mutated["portfolio"]["enterprise_value_gbp"] == pytest.approx(
        full["portfolio"]["enterprise_value_gbp"] - full["by_customer"]["C1"]["clv_gbp"]
    ), "excluding one account moved the value of the accounts that remain"


def test_a_retained_accounts_projection_does_not_depend_on_who_else_is_valued():
    """The property that made exact additivity possible, asserted on the per-account
    entry rather than only on the total -- a total can net two offsetting errors.
    Successor to the deleted cross-contamination tripwire.

    Assert the premise first: if the exclusion itself has broken, C1 is still in
    the draw and C2 being unchanged is trivially true rather than the estimator
    being independent."""
    full = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts=set(), n_draws=50,
    )
    mutated = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts={"C1"}, n_draws=50,
    )
    assert "C1" not in mutated["by_customer"], (
        "the ceased-account exclusion is not being applied -- fix that first; "
        "this test's subject is estimator independence, not the exclusion"
    )
    assert full["by_customer"]["C2"] == mutated["by_customer"]["C2"], (
        "C2's whole valuation entry moved because a DIFFERENT account left the "
        "valued book -- the per-account estimator is reading something global again"
    )


def test_build_enterprise_value_refuses_to_default_the_valued_population():
    """The fail-open proof. `ceased_accounts` has no default on purpose: a default
    of `set()` would have silently restored the published defect at every call site
    that never thought about the roster."""
    with pytest.raises(TypeError):
        build_enterprise_value(
            CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0, n_draws=50
        )


def test_a_departed_customers_history_still_informs_the_churn_prior():
    """Dropping their VALUE must not drop their EVIDENCE. A supplier learns most
    from the customers who left; the Beta prior is fitted over every account's
    renewal history whether or not that account is still supplied."""
    full = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts=set(), n_draws=50,
    )
    mutated = build_enterprise_value(
        CHURN_RISK, COST_TO_SERVE, CUSTOMERS, price_differential_pct=0.0,
        ceased_accounts={"C1"}, n_draws=50,
    )
    assert mutated["by_customer"]["C2"]["alpha"] == pytest.approx(full["by_customer"]["C2"]["alpha"])
    assert mutated["by_customer"]["C2"]["beta"] == pytest.approx(full["by_customer"]["C2"]["beta"])
