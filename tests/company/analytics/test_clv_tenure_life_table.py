"""EP1's tenure horizon on the book's exit LIFE TABLE by tenure year.

The constant all-cause hazard averaged a young book's quiet first-year months into its
first-renewal spike, and over-valued the 2017 beliefs that are 51 of the 69 graded rows
(SEAT_FINDING_EP1_ALL_CAUSE_EXIT_HAZARD_IS_RIGHT_BY_DEFINITION..., 2026-10-01). H2 now reads
a hazard per tenure year, starting at the year each account enters next.

What each control guards:

1. The valuation reduces to the closed form when every year has one hazard -- so the life
   table changed the hazard and nothing else.
2. The counting: the anniversary month closes its year (both departure shapes land in year
   1), and a year the book has not watched end to end is not in the table.
3. The tail pools from the last year anyone left in, so a quiet final year cannot claim an
   infinite tenure.
4. Every H2 outcome on the life-table path is reachable, in one control.
5. The account's own position moves its value -- the per-account variation the constant
   hazard could not carry.
6. The production caller passes the table AND each account's position.
"""

from __future__ import annotations

import pytest

from company.analytics.clv_three_horizon import (
    DISCOUNT_RATE,
    AccountObservables,
    BookExitRecord,
    Exclusion,
    Horizon,
    RenewalPoint,
    TenureYearHazard,
    TimeModel,
    estimate_account,
    expected_remaining_tenure_years,
    survival_discounted_value_by_year_gbp,
    survival_discounted_value_gbp,
)
from company.analytics.customer_value_view import (
    build_customer_value_view,
    observed_book_exits,
    observed_tenure_positions,
)
from saas.enterprise_value import ceased_billing_accounts
from tests.company.analytics.test_clv_book_renewal_hazard import _customers, _records


def _table(through: str = "2024-12-31") -> tuple[TenureYearHazard, ...]:
    records = _records(through)
    return observed_book_exits(
        records, ceased_billing_accounts(records), _customers()
    ).tenure_years


def _obs(position: int | None, margin: float | None = 120.0) -> AccountObservables:
    return AccountObservables(
        account_id="A", segment="resi", channel="unobserved", acquisition_year=2019,
        contract_term_years=1.0, renewal_history=(RenewalPoint("2020-03", 0.05),),
        annual_margin_gbp=margin, still_supplied=True, next_tenure_year=position,
    )


def _year(k: int, hazard: float, exits: int = 1) -> TenureYearHazard:
    return TenureYearHazard(tenure_year=k, at_risk=10, exits=exits, hazard=hazard)


# 1. ---------------------------------------------------------------------------


@pytest.mark.parametrize("hazard", [0.016, 0.137, 0.154, 0.3, 0.95])
@pytest.mark.parametrize("rate", [0.0, DISCOUNT_RATE, 0.25])
def test_a_constant_table_reproduces_the_closed_form(hazard, rate):
    # 1/h is fractional for most of these, so the fractional final year is checked too.
    closed = survival_discounted_value_gbp(100.0, hazard, rate, 1.0 / hazard)
    for years in (1, 2, 5):
        assert survival_discounted_value_by_year_gbp(
            100.0, [hazard] * years, rate
        ) == pytest.approx(closed, rel=1e-12)
    assert expected_remaining_tenure_years([hazard] * 3) == pytest.approx(1.0 / hazard)


def test_a_front_loaded_hazard_is_worth_less_than_its_tail_alone():
    """The finding's case: a renewal spike ahead of a quieter tail must cost value."""
    tail = survival_discounted_value_by_year_gbp(100.0, [0.10], DISCOUNT_RATE)
    spiked = survival_discounted_value_by_year_gbp(100.0, [0.40, 0.10], DISCOUNT_RATE)
    assert spiked < tail


def test_a_zero_final_hazard_is_refused_not_valued():
    with pytest.raises(ValueError):
        survival_discounted_value_by_year_gbp(100.0, [0.2, 0.0], DISCOUNT_RATE)


# 2. ---------------------------------------------------------------------------


def test_the_anniversary_month_closes_its_year():
    """L0 last settles the month BEFORE its anniversary, L1 the anniversary month: both
    are first-renewal departures and both land in year 1. M left mid-way through year 2."""
    table = _table()
    assert [(y.tenure_year, y.exits) for y in table[:2]] == [(1, 2), (2, 1)]
    # Month 11: five at risk, one leaves; month 12: four at risk, one leaves.
    assert table[0].hazard == pytest.approx(1 - (4 / 5) * (3 / 4))


def test_a_year_the_book_has_not_watched_end_to_end_is_not_in_the_table():
    # S, the longest account, is settled to tenure month 69: years 1-5 are complete and
    # year 6 (months 61-72) is not.
    assert [y.tenure_year for y in _table()] == [1, 2, 3, 4, 5]
    # At 2020-12 S is at month 21: year 2 is censored before its anniversary.
    assert [y.tenure_year for y in _table("2020-12-31")] == [1]


def test_without_the_roster_no_table_is_counted():
    records = _records()
    assert observed_book_exits(records, ceased_billing_accounts(records)).tenure_years is None


# 3. ---------------------------------------------------------------------------


def test_the_tail_pools_from_the_last_year_anyone_left_in():
    book = BookExitRecord(60.0, 3, (_year(1, 0.4), _year(2, 0.5), _year(3, 0.0, exits=0)))
    pooled = 1 - (0.5 * 1.0) ** 0.5
    assert book.forward_hazards(1) == pytest.approx((0.4, pooled))
    assert book.forward_hazards(2) == book.forward_hazards(9) == pytest.approx((pooled,))
    # A final year WITH an exit is its own tail.
    assert BookExitRecord(60.0, 3, (_year(1, 0.4), _year(2, 0.2))).forward_hazards(
        1
    ) == pytest.approx((0.4, 0.2))


# 4. ---------------------------------------------------------------------------


def test_every_h2_outcome_on_the_life_table_path_is_reachable():
    table = (_year(1, 0.3), _year(2, 0.2))
    outcomes = {
        "counted": estimate_account(_obs(1), book_exits=BookExitRecord(20.0, 3, table)),
        Exclusion.NO_MARGIN_OBSERVED: estimate_account(
            _obs(1, margin=None), book_exits=BookExitRecord(20.0, 3, table)),
        Exclusion.NO_BOOK_EXPOSURE: estimate_account(
            _obs(1), book_exits=BookExitRecord(0.0, 0, ())),
        Exclusion.NO_BOOK_EXITS: estimate_account(
            _obs(1), book_exits=BookExitRecord(20.0, 0, (_year(1, 0.0, exits=0),))),
        Exclusion.NO_COMPLETE_TENURE_YEAR: estimate_account(
            _obs(1), book_exits=BookExitRecord(5.0, 1, ())),
        Exclusion.NO_TENURE_POSITION: estimate_account(
            _obs(None), book_exits=BookExitRecord(20.0, 3, table)),
    }
    h2 = {k: v.tenure_expected for k, v in outcomes.items()}
    assert {v.time_model for v in h2.values()} == {
        TimeModel.BOOK_EXIT_LIFE_TABLE_BY_TENURE_YEAR
    }
    assert h2.pop("counted").value_gbp is not None
    for reason, value in h2.items():
        assert value.value_gbp is None and value.population.reasons == {reason.value: 1}
    # No table counted at all: the constant hazard, labelled as such.
    assert estimate_account(
        _obs(1), book_exits=BookExitRecord(20.0, 3)
    ).tenure_expected.time_model is TimeModel.BOOK_OBSERVED_EXIT_HAZARD


# 5. ---------------------------------------------------------------------------


def test_the_accounts_own_position_moves_its_value():
    book = BookExitRecord(20.0, 3, (_year(1, 0.4), _year(2, 0.1)))
    before = estimate_account(_obs(1), book_exits=book).tenure_expected.value_gbp
    after = estimate_account(_obs(2), book_exits=book).tenure_expected.value_gbp
    # Past its first anniversary an account no longer faces the spike.
    assert after > before
    assert after == pytest.approx(
        survival_discounted_value_by_year_gbp(120.0, [0.1], DISCOUNT_RATE)
    )


# 6. ---------------------------------------------------------------------------


def test_the_production_view_passes_the_table_and_each_accounts_position():
    records = _records()
    view = build_customer_value_view(records, _customers(), 0.0)
    book = view.three_horizon_clv
    assert book.book_exits.tenure_years == _table()
    # S last settles tenure month 69, so it enters month 70: year 6.
    assert observed_tenure_positions(records, _customers())["S"] == 6
    s = book.account("S").horizon(Horizon.TENURE_EXPECTED)
    assert s.time_model is TimeModel.BOOK_EXIT_LIFE_TABLE_BY_TENURE_YEAR
    margin = view.enterprise_value["by_customer"]["S"]["avg_annual_net_margin_gbp"]
    assert s.value_gbp == pytest.approx(
        survival_discounted_value_by_year_gbp(
            margin, book.book_exits.forward_hazards(6), DISCOUNT_RATE
        )
    )


def test_each_snapshot_publishes_the_position_it_read_the_table_from():
    """`clv_gap_selection.lifetime_level` reads the position off the snapshot; one the
    snapshot never wrote would leave every graded row unrecoverable."""
    from company.analytics.customer_value_view import build_three_horizon_clv_snapshots

    years = build_three_horizon_clv_snapshots(
        _records(), _customers(), 0.0, years=["2020", "2024"]
    )["years"]
    for year in ("2020", "2024"):
        cut = _records(year + "-12-31")
        want = observed_tenure_positions(cut, _customers())
        got = {a: row["next_tenure_year"] for a, row in years[year]["accounts"].items()}
        assert got == {a: want.get(a) for a in got}
    assert years["2024"]["accounts"]["S"]["next_tenure_year"] == 6
    assert years["2020"]["accounts"]["S"]["next_tenure_year"] == 2
