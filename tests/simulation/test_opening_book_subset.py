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


# ═══════════════════════════════════════════════════════════════════════════
# PB2 STEP 3 -- THE INVERSION, JUDGED ON THE SHIPPED PATH
#
# Everything above judges the MECHANISM: hand `subset_verdict` a stock and a book
# and it fires on all five clauses. Step 1's own record was explicit that this is
# not the same as the property holding (`PB2_JOIN_KEY_BUILD.md` §4(d)): *"met as a
# mechanism, not yet as a property of the running company ... nothing in the shipped
# run path calls it yet"*. A control with no caller is this repo's characteristic
# failure, not an absent one.
#
# The tests below judge `simulation.live_population` -- the seam an actual run
# assembles its book through -- and the load-bearing falsifier is
# `test_the_shipped_control_reds_without_the_stock`, which runs the same predicate
# against the path as it shipped BEFORE this step and requires it to RED.
# ═══════════════════════════════════════════════════════════════════════════
import simulation.live_population as lp  # noqa: E402
from simulation.net_new_acquisition import (  # noqa: E402
    DOMESTIC_ONLY,
    PROSPECTS_PER_YEAR,
    iter_prospects,
    year_premise_stock,
)

RUN_SEED = lp._DEFAULT_BASE_SEED


@pytest.fixture
def _live(monkeypatch, tmp_path):
    """The shipped run's state: the draw activated and the campaign running.

    Stated rather than inherited. Both flags are committed curriculum today, so an
    unset environment already means ON -- but a test that depends on a curriculum
    file is a test that changes meaning when the director changes his mind, and the
    subject here is the MECHANISM, not the curriculum.

    THE RECORD PATH IS REDIRECTED, and this fixture learned that the hard way rather
    than by foresight. `_record_subset_verdict` fires whenever a campaign resolves for
    the first time in a process, and the falsifiers below deliberately resolve WRONG
    worlds -- so the first run of this file overwrote the repo's published
    `book_subset_verdict.json` with a red verdict from a mutant, listing all 66
    winners as `outside_stock`. A published figure produced by a test's mutation is
    worse than no figure: it is a real red about a world that does not exist.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    monkeypatch.setenv("SE_GROW_BOOK", "1")
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    lp._CAMPAIGN_MEMO.clear()
    yield
    lp._CAMPAIGN_MEMO.clear()


def _shipped_book(seed=RUN_SEED):
    """The run's whole drawn domestic book as `SyntheticCustomer`s: trickle + winners."""
    served = lp.served_segments()
    book = [sc for sc in lp._drawn_trickle(seed) if lp._serves(sc.to_customer_dict(), served)]
    book += [p for p, _won in lp._campaign(lp._pre_growth_book(seed), seed)["winners"]]
    return book


# ---------------------------------------------------------------------------
# The positive claim, on the path a run actually takes
# ---------------------------------------------------------------------------
def test_the_shipped_book_is_a_genuine_subset_of_the_worlds_stock(_live):
    verdict = lp.book_subset_verdict()

    # Preconditions FIRST. A green verdict on an empty book, or on a world where
    # everything was won, carries no information -- those are the two fail-open
    # shapes, and they are the ones that would have passed every day of this atom's
    # life before the inversion.
    assert verdict["n_book_domestic"] > 0, "vacuous: the run won nothing"
    assert verdict["n_remainder"] > 0, "vacuous: the world had nothing left unwon"
    assert verdict["ok"] is True, verdict["failures"]
    assert verdict["n_stock"] == PROSPECTS_PER_YEAR * len(lp.CAMPAIGN_YEARS) + (
        lp.TRICKLE_STOCK_RESERVE * len(lp.CAMPAIGN_YEARS)
    )


def test_both_halves_of_the_drawn_book_are_in_the_stock_not_only_the_campaign(_live):
    """The exclusion that would have made this green for free.

    The campaign is 66 of the 68 drawn accounts, so a verdict scoped to WINNERS
    alone would read green while the Profile-B trickle still sat at premises named
    after itself. `feedback_an_exclusion_that_makes_your_own_verdict_green` is
    exactly that shape. Both halves are asserted to be in the stock by VALUE.
    """
    stock = set(lp.world_premise_stock(RUN_SEED))
    trickle = [sc for sc in lp._drawn_trickle(RUN_SEED) if sc.premise is not None]
    winners = [p for p, _w in lp._campaign(lp._pre_growth_book(RUN_SEED), RUN_SEED)["winners"]]

    assert trickle, "vacuous: the trickle drew nobody"
    assert winners, "vacuous: the campaign won nobody"
    for sc in trickle + winners:
        assert sc.premise in stock, f"{sc.customer_id} is at a premise the world never drew"
        assert sc.premise.premise_id != sc.customer_id, (
            f"{sc.customer_id} sits at a premise named after itself -- the false join key"
        )


def test_the_two_streams_never_claim_the_same_home(_live):
    """The reserve partition. The campaign takes the head of each year's stock and the
    trickle the tail, so a home cannot be sold twice. `subset_verdict`'s `double_won`
    clause is the general control; this pins the specific arrangement that satisfies it,
    because the two slices are computed in different functions and could drift apart.
    """
    for year in lp.CAMPAIGN_YEARS:
        whole = lp._year_stock(year, RUN_SEED)
        campaign = whole[:PROSPECTS_PER_YEAR]
        trickle = lp._trickle_stock(year, RUN_SEED)
        assert set(campaign).isdisjoint(set(trickle))
        assert len(campaign) + len(trickle) == len(whole), "a slot belongs to neither"


# ---------------------------------------------------------------------------
# R15 -- the falsifiers. Each runs the SHIPPED predicate on a world it must refuse.
# ---------------------------------------------------------------------------
def test_the_shipped_control_reds_without_the_stock(_live):
    """THE LOAD-BEARING FALSIFIER. Judge the book the seam produced BEFORE step 3 --
    both halves minting a dwelling per account -- against the same world stock, with
    the same predicate. It must RED on `outside_stock`.

    Run against the real generators rather than a mock: `premise_stock_fn=None` and
    `premise_stock_fn=None` on the campaign IS the shipped pre-step-3 path, reachable
    by dropping one argument at each of two call sites. If this ever goes green the
    control has stopped testing subset and started testing that two sets exist.
    """
    from simulation.population_draw import draw_population as _draw

    pre_step3_trickle = _draw(RUN_SEED, draw_region=True, assign_cohorts=True)
    verdict = subset_verdict(lp.world_premise_stock(RUN_SEED), pre_step3_trickle)

    assert verdict["ok"] is False
    assert "outside_stock" in verdict["failures"]
    # And name the shape rather than only the clause: the "premise" was the account.
    assert any(sc.premise.premise_id == sc.customer_id for sc in pre_step3_trickle)


def test_the_verdict_reds_when_the_draw_is_inactive(monkeypatch):
    """FAIL-OPEN, the shape R15 names second. With the draw off there is no drawn book
    at all, and a control that reports green on "nothing to check" is worse than none --
    it would have read green on every run this atom ever made before activation."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "0")
    verdict = lp.book_subset_verdict()
    assert verdict["ok"] is False
    assert verdict["failures"] == ["draw_inactive"]


def test_a_pool_larger_than_its_stock_raises_rather_than_truncating():
    """R15 fail-closed, the prospect side. A market silently shortened to fit its stock
    has its size set by the wrong thing, and every prospect that survived would still
    pass the subset control -- the truncation is invisible in the verdict."""
    short = year_premise_stock(2019, base_seed=RUN_SEED, n=10)
    with pytest.raises(ValueError, match="premise stock exhausted"):
        list(iter_prospects(2019, base_seed=RUN_SEED, n=400, premise_stock=short))


def test_the_reserve_raises_when_a_year_out_draws_more_than_it(monkeypatch):
    """The trickle's own fail-closed edge. `TRICKLE_STOCK_RESERVE` is headroom over a
    Poisson(1.0) year, and the reason a generous reserve is safe is that being wrong
    STOPS rather than truncates. Driven at a lambda that exhausts it deliberately."""
    from simulation.population_draw import draw_population as _draw

    with pytest.raises(ValueError, match="premise stock exhausted"):
        _draw(
            RUN_SEED,
            start_year=2021,
            end_year=2021,
            acquisitions_per_year_lambda=200.0,
            premise_stock_fn=lambda y: year_premise_stock(y, base_seed=RUN_SEED, n=3),
        )


def test_supplying_both_claim_shapes_raises():
    """One mechanism, two shapes. Honouring both would claim each premise twice, and
    the resulting book would still be a subset -- the failure would be silent."""
    from simulation.population_draw import draw_population as _draw

    with pytest.raises(ValueError, match="two shapes of one claim"):
        _draw(
            RUN_SEED,
            premise_stock=_stock(),
            premise_stock_fn=lambda y: year_premise_stock(y, base_seed=RUN_SEED, n=5),
        )


# ---------------------------------------------------------------------------
# The properties step 3 was expected to deliver
# ---------------------------------------------------------------------------
def test_membership_is_stable_when_the_stock_grows():
    """`PB2_JOIN_KEY_BUILD.md` §5 recorded this as OWED, and named step 3 as the place
    it would be paid: the flat claim's shuffle is seeded on the stock SIZE, so growing
    the world re-rolls which homes were won. A positional claim into a year's stock has
    no such term. Asserted against the pre-existing shuffle as the CONTRAST, so this
    cannot quietly stop testing what it says it tests."""
    def claimed(stock_n):
        return [
            c.premise.premise_id
            for c in iter_prospects(
                2019, base_seed=RUN_SEED, n=20, segment_weights=DOMESTIC_ONLY,
                premise_stock=year_premise_stock(2019, base_seed=RUN_SEED, n=stock_n),
            )
            if c.premise is not None
        ]

    small, grown = claimed(100), claimed(4000)
    assert small and small == grown

    # THE CONTRAST that makes the assertion above mean something: the flat, shuffled
    # claim this replaces does NOT have the property, so a reader can see the two are
    # different mechanisms rather than take the docstring's word for it.
    from simulation.population_draw import draw_population as _draw

    flat_small = [c.premise.premise_id for c in _draw(
        SEED, start_year=2021, end_year=2025, acquisitions_per_year_lambda=3.0,
        premise_stock=draw_premise_population(60, base_seed=SEED, as_of=AS_OF),
    ) if c.premise]
    flat_grown = [c.premise.premise_id for c in _draw(
        SEED, start_year=2021, end_year=2025, acquisitions_per_year_lambda=3.0,
        premise_stock=draw_premise_population(400, base_seed=SEED, as_of=AS_OF),
    ) if c.premise]
    assert flat_small and flat_small != flat_grown


def test_a_years_stock_is_drawn_at_that_years_as_of():
    """The fidelity reason the stock is per-year rather than one decade-wide draw.

    `draw_premise` reads `as_of` for the meter cadence (`smart_read_share(as_of.year)`)
    and the EPC lodgement window. A single stock at 2016 would model a country in which
    no meter ever got smarter across the run's whole decade -- strictly LESS faithful
    than the per-acquisition mint step 3 replaces, and the one direction R13 forbids.
    """
    from simulation.premise_population import DAILY_CADENCE_DAYS

    def smart_share(year):
        stock = year_premise_stock(year, base_seed=RUN_SEED, n=300)
        return sum(p.meter_cadence_days == DAILY_CADENCE_DAYS for p in stock) / len(stock)

    early, late = smart_share(2016), smart_share(2025)
    assert late > early, (
        f"the stock is time-blind: 2016 smart share {early:.3f}, 2025 {late:.3f}"
    )
    # And every member of a year's stock carries a lodgement inside THAT year's window,
    # not the decade's -- the second thing `as_of` decides.
    for p in year_premise_stock(2016, base_seed=RUN_SEED, n=50):
        if p.epc_lodged is not None:
            assert dt.date(2006, 1, 1) <= p.epc_lodged < dt.date(2016, 1, 1)


def test_the_stock_claim_does_not_perturb_the_prospect_stream():
    """C-S2. The claim reads a pre-drawn sequence and never touches the prospect `rng`,
    so segment, commodity, band, EAC, payment method and the in-market date must be
    byte-identical with and without a stock. This is what bounds the change's blast
    radius to one field: every figure measured before it was measured on this world."""
    def attrs(pool):
        return [
            (c.customer_id, c.acquisition_date, c.segment, c.commodity,
             c.payment_method, c.consumption_band, c.eac_kwh, c.region)
            for c in pool
        ]

    # DOMESTIC_ONLY, the weights the shipped campaign uses. Not cosmetic: a claim is
    # made only for a domestic point, so a mixed pool would leave the comparison below
    # dereferencing a None premise on the SME rows -- and would be comparing a
    # different thing from what the run does.
    plain = list(iter_prospects(2019, base_seed=RUN_SEED, n=50,
                                segment_weights=DOMESTIC_ONLY))
    claimed = list(iter_prospects(
        2019, base_seed=RUN_SEED, n=50, segment_weights=DOMESTIC_ONLY,
        premise_stock=year_premise_stock(2019, base_seed=RUN_SEED, n=50),
    ))
    assert attrs(plain) == attrs(claimed)
    assert [c.premise.premise_id for c in plain] != [c.premise.premise_id for c in claimed]


def test_the_same_prospects_win_with_and_without_the_stock(_live):
    """The blast radius, stated as a claim and checked rather than asserted in prose.

    The funnel is seeded on the prospect's own id and date, and neither moves, so the
    inversion changes WHICH HOUSE each winner lives in and nothing else. If this ever
    fails, the campaign's outcome has become a function of the stock and every published
    growth figure moved for a reason nobody declared.
    """
    won_with = [p.customer_id for p, _w in lp._campaign(lp._pre_growth_book(RUN_SEED), RUN_SEED)["winners"]]
    lp._CAMPAIGN_MEMO.clear()

    import simulation.net_new_acquisition as nna
    real = nna.iter_prospects
    try:
        # The pre-step-3 call: identical but for the stock argument being dropped.
        nna.iter_prospects = lambda *a, **kw: real(
            *a, **{k: v for k, v in kw.items() if k != "premise_stock"}
        )
        won_without = [
            p.customer_id
            for p, _w in lp._campaign(lp._pre_growth_book(RUN_SEED), RUN_SEED)["winners"]
        ]
    finally:
        nna.iter_prospects = real
    assert won_with and won_with == won_without


def test_the_recorded_verdict_is_the_predicate_the_tests_judge(_live, tmp_path, monkeypatch):
    """R15 independence. The published record must be the SAME function this file
    judges, never a re-derivation beside it -- a second copy of the arithmetic is how a
    published green and a red control end up living in the same repo."""
    import json

    record = tmp_path / "book_subset_verdict.json"
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", record)
    lp._record_subset_verdict(RUN_SEED)

    written = json.loads(record.read_text())
    live = lp.book_subset_verdict(RUN_SEED)
    for key, value in live.items():
        assert written[key] == value, key
    assert written["base_seed"] == RUN_SEED
