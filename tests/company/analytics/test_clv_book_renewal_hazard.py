"""EP1's tenure horizon on the book's OWN observed renewal departures.

EP1 pass 20 measured that the whole of the CLV gap's excess over 1 was the LEVEL of the
lifetime term: H2 read a 0.05 hazard off `saas.churn_model` for every account while the
book realised 0.36 at renewal. H2 now reads the book's pooled per-renewal departure
frequency, counted by `observed_book_renewals` from the supplier's own settled records.

What each control guards:

1. The counting rule's five cases (stay, leave in the anniversary month, leave the month
   before it, undecided, off-anniversary cessation). Each is a fixture account whose
   expected contribution is stated beside it.
2. The blindfold: a truncated window counts only what had been decided by then.
3. The partition: every H2 outcome on the book path can be REACHED (counted, no
   decisions, no departures), and the no-decisions branch is blank, not a picked prior.
4. The production caller actually takes the book path -- a seam that grew the argument
   and a caller that never passed it would leave every other test here green.
"""

from __future__ import annotations

import pytest

from company.analytics.clv_three_horizon import (
    DISCOUNT_RATE,
    FIRST_RENEWAL_DEPARTURE_PRIOR,
    AccountObservables,
    BookRenewalRecord,
    Exclusion,
    Horizon,
    RenewalPoint,
    TimeModel,
    estimate_account,
    estimate_book,
    survival_discounted_value_gbp,
)
from company.analytics.customer_value_view import (
    build_customer_value_view,
    observed_book_renewals,
)
from saas.enterprise_value import ceased_billing_accounts

_MONTH_END = {
    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
}

#: account -> (acquisition_date, first settled month, last settled month,
#:             expected (decisions, departures) over the full window)
_BOOK = {
    # Anniversaries 2020-03 .. 2024-03, all before its last month: five stays.
    "S": ("2019-03-10", "2019-03", "2024-12", (5, 0)),
    # Anniversary 2021-06-15; last settled 2021-06, then ceased: one departure.
    "L1": ("2020-06-15", "2020-06", "2021-06", (1, 1)),
    # Term from the 1st ends the day before the anniversary month; last settled is
    # the month BEFORE it: still one departure, not a silent nothing.
    "L0": ("2020-04-01", "2020-04", "2021-03", (1, 1)),
    # Renewed 2021-01, then left mid-term in 2021-07: one stay and no renewal departure.
    "M": ("2020-01-15", "2020-01", "2021-07", (1, 0)),
    # Anniversary 2024-12-30 falls in its last settled month and it is still supplied:
    # undecided, counted nowhere.
    "U": ("2023-12-31", "2024-01", "2024-12", (0, 0)),
}


def _months(first: str, last: str):
    y, m = (int(x) for x in first.split("-"))
    while f"{y:04d}-{m:02d}" <= last:
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def _customers() -> list[dict]:
    return [
        {
            "customer_id": cid,
            "segment": "resi",
            "acquisition_date": acq,
            "contract_type": "fixed_1yr",
        }
        for cid, (acq, *_rest) in _BOOK.items()
    ]


def _records(through: str = "2024-12-31") -> list[dict]:
    out = []
    for cid, (_acq, first, last, _exp) in _BOOK.items():
        for y, m in _months(first, last):
            d = f"{y:04d}-{m:02d}-{_MONTH_END[m]:02d}"
            if d > through:
                continue
            revenue = 100.0 + (60.0 if y >= 2021 and cid == "S" else 0.0)
            out.append({
                "customer_id": cid,
                "settlement_date": d,
                "settlement_period": 1,
                "commodity": "electricity",
                "revenue_gbp": revenue,
                "wholesale_cost_gbp": revenue * 0.6,
                "margin_gbp": revenue * 0.4,
                "net_margin_gbp": revenue * 0.1,
                "consumption_kwh": 300.0,
            })
    return out


def _count(through: str = "2024-12-31") -> BookRenewalRecord:
    records = _records(through)
    return observed_book_renewals(records, _customers(), ceased_billing_accounts(records))


# ---------------------------------------------------------------------------
# 1. The counting rule.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("account", sorted(_BOOK))
def test_each_case_contributes_what_the_rule_says(account):
    acq, first, last, expected = _BOOK[account]
    records = [r for r in _records() if r["customer_id"] == account]
    # The edge must be the BOOK's edge, or a leaver reads as still supplied.
    ceased = ceased_billing_accounts(_records()) & {account}
    got = observed_book_renewals(records, _customers(), ceased)
    assert (got.decisions, got.departures) == expected, account


def test_the_whole_book_sums_its_cases():
    want_d = sum(e[0] for *_x, e in _BOOK.values())
    want_l = sum(e[1] for *_x, e in _BOOK.values())
    got = _count()
    assert (got.decisions, got.departures) == (want_d, want_l) == (8, 2)
    assert got.hazard == pytest.approx(0.25)


def test_a_customer_missing_from_the_roster_is_not_invented():
    records = _records()
    record = observed_book_renewals(
        records, [c for c in _customers() if c["customer_id"] != "S"],
        ceased_billing_accounts(records),
    )
    assert record.decisions == 3


# ---------------------------------------------------------------------------
# 2. The blindfold.
# ---------------------------------------------------------------------------


def test_a_truncated_window_counts_only_what_was_decided_by_then():
    assert (_count("2019-12-31").decisions, _count("2019-12-31").departures) == (0, 0)
    early = _count("2020-12-31")
    # S's 2020-03 anniversary is decided; M's 2021-01 one is not yet.
    assert (early.decisions, early.departures) == (1, 0)
    assert _count("2021-12-31").decisions > early.decisions


# ---------------------------------------------------------------------------
# 3. The H2 partition on the book path.
# ---------------------------------------------------------------------------


def _obs(account_id: str = "A", *, belief: float = 0.05, margin: float | None = 120.0):
    return AccountObservables(
        account_id=account_id,
        segment="resi",
        channel="unobserved",
        acquisition_year=2019,
        contract_term_years=1.0,
        renewal_history=(RenewalPoint("2020-03", belief),),
        annual_margin_gbp=margin,
        still_supplied=True,
    )


def test_every_h2_outcome_on_the_book_path_is_reachable():
    outcomes = {
        "counted": estimate_account(_obs(), book_renewals=BookRenewalRecord(8, 2)),
        "no_decisions": estimate_account(_obs(), book_renewals=BookRenewalRecord(0, 0)),
        "no_departures": estimate_account(_obs(), book_renewals=BookRenewalRecord(4, 0)),
    }
    h2 = {k: v.tenure_expected for k, v in outcomes.items()}
    assert all(v.time_model is TimeModel.BOOK_OBSERVED_RENEWAL_HAZARD for v in h2.values())
    assert h2["counted"].value_gbp is not None
    assert h2["no_decisions"].value_gbp is None
    assert h2["no_decisions"].population.reasons == {
        Exclusion.NO_BOOK_RENEWAL_DECISIONS.value: 1
    }
    assert h2["no_departures"].value_gbp is None
    assert h2["no_departures"].population.reasons == {
        Exclusion.NO_BOOK_RENEWAL_DEPARTURES.value: 1
    }


def test_the_first_renewal_prior_is_unestablished_and_says_so():
    """Keyed to the property: while no prior is established, a book with no decided
    renewal is blank. If a SOURCED prior is ever filed, this asserts it is used."""
    record = BookRenewalRecord(0, 0)
    assert record.hazard == FIRST_RENEWAL_DEPARTURE_PRIOR
    h2 = estimate_account(_obs(), book_renewals=record).tenure_expected
    assert (h2.value_gbp is None) == (FIRST_RENEWAL_DEPARTURE_PRIOR is None)


def test_h2_is_priced_at_the_books_frequency_and_not_the_accounts_belief():
    record = BookRenewalRecord(8, 2)
    low = estimate_account(_obs(belief=0.05), book_renewals=record).tenure_expected
    high = estimate_account(_obs(belief=0.60), book_renewals=record).tenure_expected
    assert low.value_gbp == high.value_gbp == pytest.approx(
        survival_discounted_value_gbp(120.0, 0.25, DISCOUNT_RATE, 4.0)
    )
    # The belief path, for contrast, does move -- so the equality above is the book
    # path's doing and not a horizon that ignores its hazard altogether.
    assert (
        estimate_account(_obs(belief=0.05)).tenure_expected.value_gbp
        != estimate_account(_obs(belief=0.60)).tenure_expected.value_gbp
    )


def test_h2_on_the_book_path_needs_a_margin_not_a_renewal_of_its_own():
    no_history = AccountObservables(
        account_id="N", segment="resi", channel="unobserved", acquisition_year=2024,
        contract_term_years=1.0, renewal_history=(), annual_margin_gbp=80.0,
        still_supplied=True,
    )
    h2 = estimate_account(no_history, book_renewals=BookRenewalRecord(8, 2)).tenure_expected
    assert h2.value_gbp is not None
    blank = estimate_account(_obs(margin=None), book_renewals=BookRenewalRecord(8, 2))
    assert blank.tenure_expected.population.reasons == {
        Exclusion.NO_MARGIN_OBSERVED.value: 1
    }


def test_the_published_book_carries_the_n_behind_the_hazard():
    payload = estimate_book([_obs()], book_renewals=BookRenewalRecord(8, 2)).as_published_dict()
    assert payload["book_renewals"] == {"decisions": 8, "departures": 2, "hazard": 0.25}
    assert estimate_book([_obs()]).as_published_dict()["book_renewals"] is None


def test_departures_cannot_exceed_decisions():
    with pytest.raises(ValueError):
        BookRenewalRecord(1, 2)


# ---------------------------------------------------------------------------
# 4. The production caller takes the book path.
# ---------------------------------------------------------------------------


def test_the_production_view_values_h2_on_the_books_own_renewals():
    view = build_customer_value_view(_records(), _customers(), 0.0)
    book = view.three_horizon_clv
    assert book.book_renewals == _count()
    models = {a.horizon(Horizon.TENURE_EXPECTED).time_model for a in book.accounts}
    assert models == {TimeModel.BOOK_OBSERVED_RENEWAL_HAZARD}
