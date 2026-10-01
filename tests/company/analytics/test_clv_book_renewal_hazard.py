"""EP1's tenure horizon on the book's OWN observed exits, and the renewal diagnostic beside it.

EP1 pass 20 measured that the whole of the CLV gap's excess over 1 was the LEVEL of the
lifetime term: H2 read a 0.05 hazard off `saas.churn_model` for every account. 81977a312
moved it to the book's per-renewal departure frequency (`observed_book_renewals`); the
measurement after it found the world decides a renewal at one anniversary in five and 40
of 89 cessations fall away from any anniversary. A TENURE ends at any exit, so H2 now
values on the book's all-cause annual exit probability (`observed_book_exits`), and the
renewal record is published beside it as a diagnostic only.

What each control guards:

1. The renewal counting rule's five cases (stay, leave in the anniversary month, leave the
   month before it, undecided, off-anniversary cessation). Each is a fixture account whose
   expected contribution is stated beside it.
2. The blindfold: a truncated window counts only what had been decided by then.
3. The exit count: exposure per account, and an off-anniversary leaver IS an exit.
4. The partition: every H2 outcome on the book path can be REACHED (counted, no exposure,
   no exits), and a book nobody has left is blank, not a picked prior.
5. The production caller actually takes the exit path -- a seam that grew the argument
   and a caller that never passed it would leave every other test here green.
"""

from __future__ import annotations

import pytest

from company.analytics.clv_three_horizon import (
    DISCOUNT_RATE,
    FIRST_RENEWAL_DEPARTURE_PRIOR,
    AccountObservables,
    BookExitRecord,
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
    observed_book_exits,
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
# 3. The exit count.
# ---------------------------------------------------------------------------

#: Settled months per fixture account over the full window: S 2019-03..2024-12, L1
#: 2020-06..2021-06, L0 2020-04..2021-03, M 2020-01..2021-07, U 2024-01..2024-12.
_EXPOSURE_MONTHS = {"S": 70, "L1": 13, "L0": 12, "M": 19, "U": 12}


def _exits(through: str = "2024-12-31") -> BookExitRecord:
    records = _records(through)
    return observed_book_exits(records, ceased_billing_accounts(records))


def test_exposure_is_each_accounts_settled_span_and_every_leaver_is_an_exit():
    got = _exits()
    assert got.account_years == pytest.approx(sum(_EXPOSURE_MONTHS.values()) / 12.0)
    # L1 and L0 left at an anniversary; M left MID-TERM. The renewal record counts
    # two departures, the exit record three -- M is the case this record exists for.
    assert got.exits == 3
    assert _count().departures == 2


def test_the_exit_record_counts_only_what_was_observed_by_the_cutoff():
    early = _exits("2020-12-31")
    assert early.account_years == pytest.approx((22 + 7 + 9 + 12) / 12.0)
    assert early.exits == 0


def test_the_hazard_is_the_annual_probability_not_the_rate():
    record = BookExitRecord(account_years=20.0, exits=3)
    assert record.rate == pytest.approx(0.15)
    assert record.hazard == pytest.approx(1.0 - 2.718281828459045 ** -0.15)
    assert record.hazard < record.rate


# ---------------------------------------------------------------------------
# 4. The H2 partition on the book path.
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


_COUNTED = BookExitRecord(account_years=20.0, exits=3)


def test_every_h2_outcome_on_the_book_path_is_reachable():
    outcomes = {
        "counted": estimate_account(_obs(), book_exits=_COUNTED),
        "no_exposure": estimate_account(_obs(), book_exits=BookExitRecord(0.0, 0)),
        "no_exits": estimate_account(_obs(), book_exits=BookExitRecord(4.0, 0)),
    }
    h2 = {k: v.tenure_expected for k, v in outcomes.items()}
    assert all(v.time_model is TimeModel.BOOK_OBSERVED_EXIT_HAZARD for v in h2.values())
    assert h2["counted"].value_gbp is not None
    assert h2["no_exposure"].value_gbp is None
    assert h2["no_exposure"].population.reasons == {Exclusion.NO_BOOK_EXPOSURE.value: 1}
    assert h2["no_exits"].value_gbp is None
    assert h2["no_exits"].population.reasons == {Exclusion.NO_BOOK_EXITS.value: 1}


def test_the_first_renewal_prior_is_unestablished_and_says_so():
    """Keyed to the property: while no prior is established, the renewal diagnostic of a
    book with no decided renewal publishes no hazard."""
    assert BookRenewalRecord(0, 0).hazard == FIRST_RENEWAL_DEPARTURE_PRIOR


def test_h2_is_priced_at_the_books_exit_hazard_and_not_the_accounts_belief():
    low = estimate_account(_obs(belief=0.05), book_exits=_COUNTED).tenure_expected
    high = estimate_account(_obs(belief=0.60), book_exits=_COUNTED).tenure_expected
    h = _COUNTED.hazard
    assert low.value_gbp == high.value_gbp == pytest.approx(
        survival_discounted_value_gbp(120.0, h, DISCOUNT_RATE, 1.0 / h)
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
    h2 = estimate_account(no_history, book_exits=_COUNTED).tenure_expected
    assert h2.value_gbp is not None
    blank = estimate_account(_obs(margin=None), book_exits=_COUNTED)
    assert blank.tenure_expected.population.reasons == {
        Exclusion.NO_MARGIN_OBSERVED.value: 1
    }


def test_the_published_book_carries_the_n_behind_the_hazard():
    payload = estimate_book(
        [_obs()], book_exits=_COUNTED, book_renewals=BookRenewalRecord(8, 2)
    ).as_published_dict()
    assert payload["book_exits"] == {
        "account_years": 20.0, "exits": 3, "rate": 0.15, "hazard": _COUNTED.hazard,
    }
    assert payload["book_renewals"] == {"decisions": 8, "departures": 2, "hazard": 0.25}
    bare = estimate_book([_obs()]).as_published_dict()
    assert bare["book_exits"] is None and bare["book_renewals"] is None


def test_the_renewal_record_is_published_and_never_valued_on():
    """Passing a renewal record whose hazard differs from the exit hazard moves nothing:
    H2 reads the exit record alone."""
    with_renewals = estimate_book(
        [_obs()], book_exits=_COUNTED, book_renewals=BookRenewalRecord(10, 9)
    )
    without = estimate_book([_obs()], book_exits=_COUNTED)
    assert (
        with_renewals.accounts[0].tenure_expected.value_gbp
        == without.accounts[0].tenure_expected.value_gbp
    )


def test_departures_cannot_exceed_decisions():
    with pytest.raises(ValueError):
        BookRenewalRecord(1, 2)
    with pytest.raises(ValueError):
        BookExitRecord(-1.0, 0)


# ---------------------------------------------------------------------------
# 5. The production caller takes the exit path.
# ---------------------------------------------------------------------------


def test_the_production_view_values_h2_on_the_books_own_exits():
    view = build_customer_value_view(_records(), _customers(), 0.0)
    book = view.three_horizon_clv
    assert book.book_exits == _exits()
    assert book.book_renewals == _count()
    models = {a.horizon(Horizon.TENURE_EXPECTED).time_model for a in book.accounts}
    assert models == {TimeModel.BOOK_OBSERVED_EXIT_HAZARD}
