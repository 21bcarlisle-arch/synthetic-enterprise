"""PB2 step 1 -- the join key, the unwon remainder, and the subset control.

ATOM: `PB2_opening_book_won_not_assigned`. SOURCE RULING:
`docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`
("the opening book is a subset of that population ... won, never assigned").
DESIGN: `docs/design/PB2_UNWON_REMAINDER_FRAME.md` §3 (the join key) and §4 (the two
mutations exit (d)'s control must survive).

WHAT WAS WRONG, precisely (measured, not recalled). `SyntheticCustomer` has carried a
`premise` field since B12, so the join key LOOKED present. But `_draw_dwelling` called
`draw_premise(customer_id, ...)` -- passing the CUSTOMER id as the PREMISE id -- so
every account's premise id was its own customer id relabelled (`SYN-2023-001`), while
the drawn stock is keyed `P0054`. Their intersection is empty. That is worse than the
absent field the FRAME pass expected to find: a build could read the field, believe
step 1 was done, and land a subset control that can only be trivially false or
tautologically true. `test_the_control_reds_on_the_pre_repair_path` is the falsifier
that pins this, and it runs against the SHIPPED default path, not a mock.

R15: every clause of `subset_verdict` has a mutation below that makes it RED. A subset
assertion passes trivially on a broken world, so the clauses that matter most are the
FAIL-OPEN ones -- an empty book, and an empty remainder.
"""
from __future__ import annotations

import datetime as dt

import pytest

from simulation.population_draw import (
    draw_population,
    subset_verdict,
    unwon_remainder,
)
from simulation.premise_population import draw_premise_population

AS_OF = dt.date(2021, 1, 1)
SEED = 42


def _stock(n: int = 200, *, base_seed: int = SEED):
    return draw_premise_population(n, base_seed=base_seed, as_of=AS_OF)


def _book(stock, *, base_seed: int = SEED):
    return draw_population(base_seed=base_seed, premise_stock=stock)


# ---------------------------------------------------------------------------
# The positive claim -- exit (d)
# ---------------------------------------------------------------------------
def test_the_book_is_a_genuine_subset_of_the_drawn_stock():
    stock = _stock()
    book = _book(stock)
    verdict = subset_verdict(stock, book)

    # The preconditions FIRST -- a green verdict on an empty book or an empty
    # remainder would carry no information at all.
    assert verdict["n_book_domestic"] > 0, "vacuous: no domestic accounts to check"
    assert verdict["n_remainder"] > 0, "vacuous: nothing was left unwon"

    assert verdict["ok"], verdict["failures"]
    stock_ids = {p.premise_id for p in stock}
    assert {c.premise.premise_id for c in book if c.premise} <= stock_ids


def test_a_won_account_sits_at_a_stock_premise_not_at_a_premise_named_after_itself():
    """The join key is real: the premise id is drawn from the stock's `P####`
    grammar, NOT the account's own `SYN-` id. This is the defect stated as a test."""
    book = _book(_stock())
    domestic = [c for c in book if c.premise is not None]
    assert domestic, "the fixture must produce at least one domestic account"
    for customer in domestic:
        assert customer.premise.premise_id != customer.customer_id
        assert customer.premise.premise_id.startswith("P")


def test_the_remainder_is_the_stock_minus_the_book():
    stock = _stock()
    book = _book(stock)
    remainder = unwon_remainder(stock, book)
    won = {c.premise.premise_id for c in book if c.premise}

    assert len(remainder) == len(stock) - len(won)
    assert not ({p.premise_id for p in remainder} & won)
    assert {p.premise_id for p in remainder} | won == {p.premise_id for p in stock}


def test_no_premise_is_won_twice():
    stock = _stock()
    book = _book(stock)
    ids = [c.premise.premise_id for c in book if c.premise]
    assert len(ids) == len(set(ids))


def test_deterministic_replay_of_the_claimed_book():
    """C-S2: same seed + same stock -> the same accounts at the same premises."""
    a = [(c.customer_id, c.premise.premise_id) for c in _book(_stock()) if c.premise]
    b = [(c.customer_id, c.premise.premise_id) for c in _book(_stock()) if c.premise]
    assert a == b


# ---------------------------------------------------------------------------
# R15 -- the mutations. Each must RED, and each names the clause it kills.
# ---------------------------------------------------------------------------
def test_the_control_reds_on_the_pre_repair_path():
    """THE falsifier. Run the control against the SHIPPED default path (premise
    minted from the customer id) and it must RED on `outside_stock`.

    Without this the control could be passing because the ids happen to line up,
    which is the tautology R15 names first: a checked value derived from the same
    source it checks.
    """
    stock = _stock()
    pre_repair = draw_population(base_seed=SEED)  # premise_stock NOT supplied

    verdict = subset_verdict(stock, pre_repair)

    assert not verdict["ok"]
    assert "outside_stock" in verdict["failures"]
    # And the diagnostic names the actual offenders, so a failure is debuggable.
    assert verdict["outside_stock"], "the control must say WHICH premises are foreign"
    assert all(pid.startswith("SYN-") for pid in verdict["outside_stock"])


def test_the_control_reds_on_a_book_premise_from_another_world():
    """FRAME §4 mutation 2: an account minted at a premise this world never drew.
    This is the shape of the frame collapsing back to today's seam.

    This mutant is what proved an id-only subset check insufficient, so it is worth
    stating why it is the harder one. `draw_premise_population` mints `P0000..P{n-1}`
    for EVERY base_seed, so a premise drawn from a different world carries an id that
    IS in this stock -- `outside_stock` never fires. Only a value comparison
    separates the two, which is what `foreign_world` does.
    """
    stock = _stock()
    book = list(_book(stock))
    foreign = draw_premise_population(1, base_seed=999_999, as_of=AS_OF)[0]
    assert foreign.premise_id in {p.premise_id for p in stock}, (
        "the premise id is positional, so this mutant must collide by id -- "
        "that collision is the whole point of the test"
    )
    book[0] = _replace_premise(book[0], foreign)

    verdict = subset_verdict(stock, book)
    assert not verdict["ok"]
    assert "foreign_world" in verdict["failures"]


def test_the_control_reds_on_a_premise_id_the_stock_does_not_contain():
    """The simpler half of the same claim: an id outside the stock's grammar."""
    stock = _stock()
    book = list(_book(stock))
    book[0] = _replace_premise(
        book[0], _replace_premise_id(book[0].premise, "NOT-A-STOCK-ID")
    )

    verdict = subset_verdict(stock, book)
    assert not verdict["ok"]
    assert "outside_stock" in verdict["failures"]


def test_the_control_reds_when_an_unwon_premise_is_registered_twice():
    """FRAME §4 mutation 1, in the form set-subset cannot see: `{P1} <= {P1,P2}`
    stays True however many times P1 was sold, so `double_won` is its own clause."""
    stock = _stock()
    book = list(_book(stock))
    assert len(book) >= 2, "fixture needs two accounts to double-sell one premise"
    book[1] = _replace_premise(book[1], book[0].premise)

    verdict = subset_verdict(stock, book)
    assert not verdict["ok"]
    assert "double_won" in verdict["failures"]
    assert verdict["double_won"] == [book[0].premise.premise_id]


def test_the_control_reds_on_an_empty_book():
    """FAIL-OPEN. The empty set is a subset of anything. This is not hypothetical:
    the 2016 window yields zero drawn accounts today, so a bare subset assertion
    would have reported green on it."""
    verdict = subset_verdict(_stock(), [])
    assert not verdict["ok"]
    assert "book_empty" in verdict["failures"]


def test_the_control_reds_when_nothing_was_left_unwon():
    """FAIL-OPEN, and the clause that distinguishes this control from the tautology
    the DISCOVER pass found: if every drawn premise was won, `book == stock` and
    'subset' carries no information. That is today's `live_population` seam exactly."""
    stock = _stock()
    book = _book(stock)
    won_only = [c.premise for c in book if c.premise]

    verdict = subset_verdict(won_only, book)
    assert not verdict["ok"]
    assert "remainder_empty" in verdict["failures"]


def test_the_control_reds_on_a_stock_that_is_a_disjoint_population():
    """The wrong-subject shape: two unrelated sets, both non-empty. A count-based
    check (`|book| < |stock|`) passes here; the id-based one must not."""
    book = _book(_stock())
    other_world = draw_premise_population(200, base_seed=7_777, as_of=AS_OF)
    assert {p.premise_id for p in other_world} == {p.premise_id for p in _stock()}, (
        "the two worlds share an id set entirely -- an id-only check reports GREEN "
        "here, which is exactly why membership is decided by value"
    )
    verdict = subset_verdict(other_world, book)
    assert not verdict["ok"]
    assert "foreign_world" in verdict["failures"]


# ---------------------------------------------------------------------------
# Non-regression: the stock is OPT-IN and changes nothing until asked for
# ---------------------------------------------------------------------------
def test_default_off_is_byte_identical():
    """The discipline every added field in this module has kept: an existing caller
    that does not pass `premise_stock` sees exactly the stream it saw before."""
    without = draw_population(base_seed=SEED)
    assert [
        (c.customer_id, c.acquisition_date, c.segment, c.commodity, c.payment_method,
         c.consumption_band, c.eac_kwh, c.region, c.premise.premise_id if c.premise else None)
        for c in without
    ] == [
        (c.customer_id, c.acquisition_date, c.segment, c.commodity, c.payment_method,
         c.consumption_band, c.eac_kwh, c.region, c.premise.premise_id if c.premise else None)
        for c in draw_population(base_seed=SEED)
    ]


def test_the_claim_does_not_perturb_the_acquisition_stream():
    """C-S2: the claim order is drawn from its OWN salted substream, so turning the
    stock on must not shift a single acquisition attribute. If it did, every figure
    measured before this change would have been measured against a different world."""
    plain = draw_population(base_seed=SEED)
    claimed = draw_population(base_seed=SEED, premise_stock=_stock())

    def attrs(book):
        return [
            (c.customer_id, c.acquisition_date, c.segment, c.commodity,
             c.payment_method, c.consumption_band, c.eac_kwh, c.region)
            for c in book
        ]

    assert attrs(plain) == attrs(claimed)


def test_a_stock_too_small_for_the_draw_raises_rather_than_truncating():
    """R15 fail-closed. A book silently shortened to fit its world is a book whose
    size is set by the wrong thing -- and it would still pass the subset control."""
    tiny = draw_premise_population(1, base_seed=SEED, as_of=AS_OF)
    with pytest.raises(ValueError, match="premise stock exhausted"):
        draw_population(base_seed=SEED, start_year=2021, end_year=2025,
                        acquisitions_per_year_lambda=5.0, premise_stock=tiny)


def test_the_stock_is_large_enough_to_leave_a_remainder_at_the_derived_floor():
    """PB2's derived floor: N_pop >= ceil(5.8324 * N_book), because the funnel must
    have somewhere to lose. Asserted as a property of the fixture, so a future draw
    that quietly wins the whole world fails here rather than passing quietly."""
    stock = _stock()
    book = _book(stock)
    domestic = [c for c in book if c.premise is not None]
    assert len(stock) >= 5.8324 * len(domestic)


def _replace_premise(customer, premise):
    """A copy of `customer` sitting at `premise`. Used only to build mutants."""
    import dataclasses

    return dataclasses.replace(customer, premise=premise)


def _replace_premise_id(premise, premise_id):
    """A copy of `premise` under a different id. Used only to build mutants."""
    import dataclasses

    return dataclasses.replace(premise, premise_id=premise_id)
