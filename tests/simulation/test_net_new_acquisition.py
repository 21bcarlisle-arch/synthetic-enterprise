"""PB3 — the book grows because the company won it, and can fail to.

WHAT IS ACTUALLY UNDER TEST, because it is a property and not a number. The director's
2026-08-11 ruling turns on one sentence: *"a growth curve that cannot be lost is not a growth
curve."* Both acquisition paths that shipped before this atom fail it, in different ways —
the replacement path can only ever break even against churn, and the Profile B trickle appends
its draw to the book with certainty. So the assertions that matter here are the ones that
prove growth is CONTINGENT: an always-lose funnel must produce a real bill and no customers,
and the mutation node must show that dropping the contingency is what makes the test pass
vacuously.

R15 THROUGHOUT: every control below has a paired mutation that injects the exact defect it
guards. A test that only ever ran an always-win funnel would pass on a module that ignored
the funnel entirely, which is the whole failure this atom exists to end.
"""
from __future__ import annotations

import datetime as dt

import pytest

from saas.growth_mandate import (
    COST_PER_ACQUISITION,
    capital_headroom_gbp,
    growth_quote_budget,
)
from simulation import net_new_acquisition as nna

HORIZON = dt.date(2026, 1, 1)
SEED = 20260824


class _Result:
    """The subset of AcquisitionFunnelResult `plan_growth_campaign` actually reads."""

    def __init__(self, won: bool, cost: float, stage: str):
        self.won = won
        self.total_cost_gbp = cost
        self.stage_reached = stage


def _always(won: bool, cost: float = 150.0):
    def _fn(segment, seed, term_start, credit_bureau, total_amount_gbp):
        return _Result(won, cost if won else cost * 0.4, "cooling_off" if won else "application")
    return _fn


def _budget(quotes: int):
    """A pinned company plan, so these tests measure the CAMPAIGN and not the budget rule.

    Takes the company's running quote book (2026-08-24) and deliberately IGNORES it: these tests
    pin the plan precisely so the campaign is what varies. `test_the_campaign_feeds_the_company_
    its_own_quote_book` below is the one that asserts the counts arrive, and it is separate for
    that reason -- a pinned budget that also consumed them could not tell the two apart.
    """
    def _fn(net_assets_gbp, accounts_held, quotes_issued_to_date=0, wins_to_date=0):
        return {"quotes": quotes, "budget_gbp": quotes * 150.0,
                "wins_capital_allows": quotes // 5, "binding": "capital",
                "headroom_gbp": net_assets_gbp}
    return _fn


def _campaign(**kw):
    base = dict(
        years=[2018],
        base_seed=SEED,
        opening_net_assets_gbp=2_000_000.0,
        accounts_held_at_start=14,
        horizon_end=HORIZON,
        credit_bureau=None,
        cost_per_quote_gbp=COST_PER_ACQUISITION,
        run_funnel=_always(True),
        quote_budget_fn=_budget(20),
    )
    base.update(kw)
    return nna.plan_growth_campaign(**base)


# ---------------------------------------------------------------------------
# The property the ruling is about
# ---------------------------------------------------------------------------

def test_a_campaign_whose_every_quote_FAILS_wins_nothing_and_still_costs_money():
    """THE ASSERTION THAT CARRIES THE ATOM. Growth has to be losable.

    A supplier that quotes twenty homes and converts none of them has spent real money and
    grown by nothing. If `winners` were ever non-empty here, the funnel's verdict is not
    being read and the book is being granted under a new name.
    """
    out = _campaign(run_funnel=_always(False))
    assert out["winners"] == []
    assert len(out["spend"]) == 20, "every quote issued must be billed, won or lost"
    assert all(not row["won"] for row in out["spend"])
    assert sum(r["amount_gbp"] for r in out["spend"]) > 0, (
        "a lost quote is not a free quote -- the funnel spends up to the stage it failed at"
    )
    assert out["by_year"][0]["wins"] == 0
    assert out["by_year"][0]["spend_gbp"] > 0


def test_MUTATION_a_campaign_that_ignores_the_funnel_verdict_wins_every_prospect():
    """R15 null control for the test above: same inputs, contingency removed.

    Drives an always-WIN funnel through the identical path. If this does not produce twenty
    winners, the previous test's empty `winners` proves nothing about the funnel being read
    -- it could be an empty prospect pool, a zero budget, or a broken loop.
    """
    out = _campaign(run_funnel=_always(True))
    assert len(out["winners"]) == 20
    assert all(row["won"] for row in out["spend"])


def test_the_win_rate_lands_between_the_two_extremes_on_the_real_funnel():
    """The shipped funnel, not a stub: some quotes convert and most do not.

    Anchored as a BAND rather than a number. The realised rate is a compound of five stage
    probabilities and a credit bureau, and pinning it exactly would make this test a mirror
    of the constants it is supposed to be independent of (R15 TAUTOLOGY). What matters is
    that it is neither 0 nor 1 -- i.e. that the funnel is a real filter here and not a
    formality.
    """
    from simulation.acquisition_funnel import run_acquisition_funnel
    from tools.credit_adapters import get_credit_bureau_adapter

    out = _campaign(
        run_funnel=run_acquisition_funnel,
        credit_bureau=get_credit_bureau_adapter(),
        quote_budget_fn=_budget(200),
    )
    wins = len(out["winners"])
    assert 0 < wins < 200, f"the real funnel neither wins nothing nor wins everything: {wins}"


# ---------------------------------------------------------------------------
# A prospect is not a customer
# ---------------------------------------------------------------------------

def test_prospect_ids_cannot_be_confused_with_accounts():
    pool = list(nna.iter_prospects(2019, base_seed=SEED, n=5))
    assert len(pool) == 5
    for p in pool:
        assert p.customer_id.startswith("PROS-2019-")
        assert not p.customer_id.startswith("SYN-")
        assert dt.date.fromisoformat(p.acquisition_date).year == 2019


def test_prospects_are_drawn_in_date_order_and_are_deterministic():
    a = list(nna.iter_prospects(2019, base_seed=SEED, n=30))
    b = list(nna.iter_prospects(2019, base_seed=SEED, n=30))
    assert [x.acquisition_date for x in a] == sorted(x.acquisition_date for x in a)
    assert [x.customer_id for x in a] == [x.customer_id for x in b]
    assert [x.eac_kwh for x in a] == [x.eac_kwh for x in b]


def test_a_year_is_independent_of_every_other_year():
    """WHY THIS MATTERS: it is what makes a win attributable to the company's decision.

    If 2019's prospects depended on how much was spent in 2018, changing the budget would
    silently change WHO was in the market, and no growth figure could be read as a
    commercial result rather than a draw artefact.
    """
    first = [p.customer_id for p in nna.iter_prospects(2019, base_seed=SEED, n=10)]
    again = [p.customer_id for p in nna.iter_prospects(2019, base_seed=SEED, n=10)]
    other = [p.customer_id for p in nna.iter_prospects(2020, base_seed=SEED, n=10)]
    assert first == again
    assert first != other


def test_the_prospect_stream_does_not_perturb_the_profile_B_trickle():
    """C-S2 substream isolation, against the LIVE activated curriculum.

    `docs/design/curriculum/population_draw_activation.json` records that at base seed
    20260724 the director-signed Profile B trickle realises as exactly SYN-2021-001 and
    SYN-2025-001. That is a published curriculum fact. Drawing prospects from this module
    must not move it, whatever pool size is used.
    """
    from simulation.population_draw import draw_population

    before = [c.customer_id for c in draw_population(20260724)]
    list(nna.iter_prospects(2021, base_seed=20260724, n=400))
    list(nna.iter_prospects(2025, base_seed=20260724, n=400))
    after = [c.customer_id for c in draw_population(20260724)]
    assert before == after == ["SYN-2021-001", "SYN-2025-001"]


def test_an_empty_pool_is_refused_rather_than_returning_nothing():
    with pytest.raises(ValueError):
        list(nna.iter_prospects(2019, base_seed=SEED, n=0))


# ---------------------------------------------------------------------------
# Capital is what bounds the campaign
# ---------------------------------------------------------------------------

def test_the_mandate_is_the_off_switch_and_costs_nothing():
    plan = growth_quote_budget("flat", 2_000_000.0, 14)
    assert plan["quotes"] == 0
    assert plan["budget_gbp"] == 0.0
    assert plan["wins_capital_allows"] == 0
    assert plan["binding"] == "mandate"
    assert plan["headroom_gbp"] == 0.0
    # A company that is not going to market has no conversion to plan on and must not
    # imply one: the off switch reports its basis as the mandate, not as a belief it holds.
    assert plan["planning_on"] == "mandate"
    assert plan["realised_win_rate"] is None


def test_a_supplier_in_MCR_breach_has_no_growth_budget_at_all():
    """Not a small budget -- none. A breached balance sheet must not read as an instruction."""
    assert capital_headroom_gbp(500.0, 14) == 0.0
    plan = growth_quote_budget("grow", 500.0, 14)
    assert plan["quotes"] == 0
    assert plan["binding"] == "capital"


def test_MUTATION_headroom_ignoring_the_existing_book_would_fund_a_breach():
    """R15: the defect this clamp guards is counting gross net assets as spendable.

    A supplier holding £2,000 against 14 accounts owes £1,820 of MCR and has £180 free. Read
    gross, it would look like £2,000 -- eleven times the truth, and every pound of the
    difference is capital another customer's account is already standing on.
    """
    honest = capital_headroom_gbp(2_000.0, 14)
    gross = 2_000.0
    assert honest == pytest.approx(180.0)
    assert gross > honest * 10


def test_more_capital_buys_more_quotes_UNTIL_THE_RATE_CAP_TAKES_OVER():
    """Both limbs, because the handover between them IS the finding.

    Capital is monotonic while it binds. Past the point where the rate cap is tighter, more
    capital buys nothing more -- which is the state the published company is actually in:
    £2.47m of net assets against fourteen accounts, `wins_capital_allows` in the hundreds,
    and a book that grows at the rate our settlement engine can carry.
    """
    poor = growth_quote_budget("grow", 6_000.0, 40)
    rich = growth_quote_budget("grow", 2_000_000.0, 40)
    assert poor["binding"] == "capital"
    assert rich["binding"] == "growth_rate"
    assert poor["quotes"] < rich["quotes"], "capital binds below the rate cap"

    richer = growth_quote_budget("grow", 20_000_000.0, 40)
    assert richer["quotes"] == rich["quotes"], (
        "past the rate cap more capital must buy NOTHING -- if it does, the cap is not "
        "applied and the book will outrun what this machine can settle"
    )
    assert richer["wins_capital_allows"] > richer["wins_rate_allows"], (
        "the two numbers must stay separately reported: their gap is the over-capitalisation "
        "finding and collapsing them into one hides it"
    )


def test_the_campaign_spends_down_its_own_capital_across_years():
    """Growth is self-limiting: what is spent winning customers is not there next year."""
    out = _campaign(years=[2018, 2019, 2020], quote_budget_fn=_budget(10))
    rows = out["by_year"]
    assert [r["year"] for r in rows] == [2018, 2019, 2020]
    assert all(r["spend_gbp"] > 0 for r in rows)
    assert rows[-1]["accounts_after"] > rows[0]["accounts_after"]


# ---------------------------------------------------------------------------
# The engineering cap must never be silent
# ---------------------------------------------------------------------------

def test_a_settlement_bound_year_SAYS_SO_instead_of_publishing_a_smaller_book():
    """CLAUDE.md's no-silent-caps rule, on the number a reader most readily misreads.

    A growth curve flattened by this machine's RAM looks exactly like a supplier that ran out
    of money. They are different facts and the run has to be able to tell them apart.
    """
    out = _campaign(quote_budget_fn=_budget(200), customer_year_budget=10.0)
    assert out["notes"], "a settlement-bound campaign must leave a note"
    assert any("SETTLEMENT-BOUND" in n for n in out["notes"])
    assert out["by_year"][0]["binding"] == "settlement_engine"
    assert out["customer_years_committed"] <= 10.0


def test_a_win_refused_by_the_engineering_cap_is_STILL_BILLED():
    """The quote was paid for whether or not we can settle the account it won.

    Suppressing the spend would understate acquisition cost -- the one figure a reader uses
    to judge whether the growth was worth having.
    """
    out = _campaign(quote_budget_fn=_budget(200), customer_year_budget=10.0)
    won_rows = [r for r in out["spend"] if r["won"]]
    assert len(won_rows) > len(out["winners"]), (
        "this fixture must actually refuse some wins, or it proves nothing"
    )
    assert all(r["amount_gbp"] > 0 for r in won_rows)


def test_a_market_bound_year_says_so_too():
    quotes, note = nna.quote_capacity(5_000, pool_size=400)
    assert quotes == 400
    assert note is not None and "MARKET-BOUND" in note


def test_MUTATION_an_uncapped_year_returns_no_warning():
    """Null control: the warning must key on the cap biting, not fire unconditionally."""
    quotes, note = nna.quote_capacity(12, pool_size=400)
    assert (quotes, note) == (12, None)


def test_the_campaign_feeds_the_company_its_own_quote_book():
    """2026-08-24: the campaign must hand the company what it booked, so year N+1 is planned on
    evidence rather than on the founding assumption forever.

    R15 -- the assertion is that the counts ARRIVE and are CUMULATIVE and LAGGED. Year one must
    see an empty book (it has issued nothing yet), and each later year must see exactly the
    totals of the years before it, never including its own. A version that passed the current
    year's numbers would look identical on a one-year campaign, so this runs three.
    """
    seen = []

    def _recording_budget(net_assets_gbp, accounts_held, quotes_issued_to_date=0, wins_to_date=0):
        seen.append((quotes_issued_to_date, wins_to_date))
        return {"quotes": 10, "budget_gbp": 10 * 150.0,
                "wins_capital_allows": 2, "binding": "capital",
                "headroom_gbp": net_assets_gbp}

    out = _campaign(years=[2018, 2019, 2020], quote_budget_fn=_recording_budget)

    assert len(seen) == 3
    assert seen[0] == (0, 0), "year one has no book to learn from"

    by_year = out["by_year"]
    # Each year is handed the running totals of the years STRICTLY before it.
    for i in range(1, 3):
        expected_quotes = sum(y["quotes_issued"] for y in by_year[:i])
        expected_wins = sum(y["wins"] for y in by_year[:i])
        assert seen[i] == (expected_quotes, expected_wins), f"year index {i} saw the wrong book"

    # Non-vacuity: the campaign must actually have issued quotes, or the equality above is
    # 0 == 0 three times and asserts nothing.
    assert seen[-1][0] > 0, "vacuous: the campaign issued no quotes at all"


def test_each_year_records_the_basis_it_was_planned_on():
    """The gap is reported per year, so the growth curve can be read as a belief being corrected."""
    out = _campaign(years=[2018, 2019], quote_budget_fn=_budget(10))
    for row in out["by_year"]:
        assert "planning_on" in row and "believed_win_rate" in row
        assert "realised_win_rate_used" in row


# ---------------------------------------------------------------------------
# PB3 exit (a): the market is REAL, and it is the same market churn sees
# ---------------------------------------------------------------------------

def test_the_in_play_market_follows_the_real_switching_series():
    """Until PB3 the pool was PROSPECTS_PER_YEAR flat, so the market was equally open every
    year from 2016 to 2025. It was not. These are the DESNZ-calibrated years the LOSS side has
    used since it was built: 2016 peak competition, 2022 the crisis when switching stopped."""
    peak, peak_mult = nna.homes_in_market(2016)
    normal, normal_mult = nna.homes_in_market(2024)
    crisis, crisis_mult = nna.homes_in_market(2022)

    assert peak >= normal > crisis, (peak, normal, crisis)
    assert normal > 2 * crisis, "the series must bite, not merely tilt"
    assert normal_mult == pytest.approx(1.0, abs=0.05), "2024 is the normalisation year"
    assert peak_mult > 2.0 and crisis_mult < 0.5, "the real series, not a flattened stand-in"


def test_the_market_can_only_be_THINNED_never_widened_past_the_stock_partition():
    """THE CAP, and it is coherence rather than caution.

    Prospects come from `iter_prospects(year, n=prospects_per_year)` out of a stock partition
    PB2 splits with the Profile-B trickle. A 2.17x year asking for 869 homes out of a 400-home
    partition does not get 869 prospects -- it gets 400, plus a quotes_issued that claims
    quotes the run never issued and never billed. Measured before the cap went in: 2016
    reported 600 quotes and 400 wins on an always-win funnel.

    The cost is a NAMED simplification: above 1.0 the multiplier is inert, so a peak year
    understates how open the market was.
    """
    assert nna.homes_in_market(2016)[0] == nna.PROSPECTS_PER_YEAR
    assert nna.homes_in_market(2024, multiplier=5.0)[0] == nna.PROSPECTS_PER_YEAR
    assert nna.homes_in_market(2024, multiplier=0.25)[0] == nna.PROSPECTS_PER_YEAR // 4


def test_every_quote_the_run_REPORTS_is_a_quote_it_actually_BILLED():
    """The defect the cap exists to prevent, asserted end-to-end rather than at the helper.

    `quotes_issued` is what the published growth curve is read from, and `spend` is one row per
    quote actually put through the funnel. If the pool can promise more homes than the stock
    partition holds, the first number silently exceeds the second.
    """
    for year in (2016, 2022, 2024):
        out = _campaign(years=[year], quote_budget_fn=_budget(600),
                        customer_year_budget=100_000.0)
        row = out["by_year"][0]
        assert row["quotes_issued"] == len(out["spend"]), (
            f"{year}: reported {row['quotes_issued']} quotes, billed {len(out['spend'])}"
        )
        assert row["wins"] == len(out["winners"])


def test_MUTATION_a_flat_multiplier_gives_back_the_pre_PB3_flat_market():
    """R15 null control for the test above. Pin the multiplier and the variation vanishes --
    so the spread really does come from the switching series and not from the year arithmetic,
    the rounding, or the prospect draw."""
    pools = {nna.homes_in_market(y, multiplier=1.0)[0] for y in (2016, 2022, 2024)}
    assert pools == {nna.PROSPECTS_PER_YEAR}


def test_a_thin_market_wins_fewer_customers_from_the_same_balance_sheet():
    """THE ADD PATH. Identical capital, identical funnel, identical plan -- only the year
    differs. A supplier cannot win customers who are not in the market to be won.

    THE SETTLEMENT BUDGET IS LIFTED HERE, and finding out why is most of what this test is
    worth. Left at its default this comparison INVERTS: 2016 wins 60 and 2022 wins 157, because
    a customer won in 2016 accrues ten customer-years against the horizon and one won in 2022
    accrues four, so a fixed settlement budget buys fewer of the earlier ones. That is a real
    mechanism and not a bug -- but it is an ENGINEERING ceiling, and reading it as a market
    effect would credit the switching series with a result the horizon arithmetic produced.
    The two are separated rather than blended: the budget is raised until it cannot bind, and
    what remains is the market alone.
    """
    kw = dict(quote_budget_fn=_budget(600), customer_year_budget=100_000.0)
    rich = _campaign(years=[2016], **kw)
    thin = _campaign(years=[2022], **kw)

    assert len(rich["winners"]) > len(thin["winners"])
    assert rich["by_year"][0]["quotes_issued"] > thin["by_year"][0]["quotes_issued"]
    assert rich["by_year"][0]["homes_in_market"] > thin["by_year"][0]["homes_in_market"]
    # Non-vacuity: the thin year must still be a real campaign, not an empty one -- otherwise
    # this passes on a mechanism that simply switched acquisition off.
    assert thin["by_year"][0]["quotes_issued"] > 0
    assert len(thin["winners"]) > 0
    # And neither year may be settlement-bound, or the budget is still what is being measured.
    assert not any("SETTLEMENT-BOUND" in n for n in rich["notes"] + thin["notes"])


def test_a_thin_market_and_our_own_ceiling_carry_OPPOSITE_instructions():
    """No-silent-caps, split in two. Both cap the year; one is our artefact and should be
    raised, the other is a real crisis and raising anything would falsify it. The pre-PB3
    message said 'raise the pool' unconditionally, which on a market-thin year is exactly
    backwards."""
    _, thin_note = nna.quote_capacity(10_000, 178, engineering_ceiling=400)
    _, ceiling_note = nna.quote_capacity(10_000, 400, engineering_ceiling=400)

    assert "MARKET-THIN" in thin_note and "would falsify it" in thin_note
    assert "raise the pool" not in thin_note
    assert "MARKET-BOUND" in ceiling_note and "raise" in ceiling_note

    # And an uncapped year says nothing at all.
    assert nna.quote_capacity(10, 400, engineering_ceiling=400)[1] is None


def test_both_legs_read_the_SAME_switching_constant():
    """THE ANTI-GOAL-SEEK GUARD (director, 2026-08-17), registered in this atom's
    simplifications file BEFORE the build and asserted here so it cannot be quietly lost.

    Acquisition and churn must resolve the same function. If they ever read separate
    constants, book size becomes tunable in one direction and R12 goal-seeking on it stops
    being structurally unavailable and becomes merely forbidden -- which this project has
    repeatedly found is not the same thing.
    """
    import inspect

    from simulation import customer_events, market_switching_propensity

    assert customer_events.market_switching_multiplier is (
        market_switching_propensity.market_switching_multiplier
    ), "the LOSS leg no longer reads the shared constant"

    src = inspect.getsource(nna.homes_in_market)
    assert "market_switching_propensity" in src, "the ADD leg no longer reads it either"


# ---------------------------------------------------------------------------
# EXIT (b1) — the arrival stream held FIXED, and our own market position alone
# moves the book in BOTH directions
#
# This is the leg the 2026-08-18 re-amendment added and the 2026-08-20 DISCOVER pass
# measured absent: "the company's price is the only lever on book size, and it works in
# one direction." Losses have read `price_differential_pct` since Phase NS
# (`customer_events` -> `home_move_win_rate`); until 2026-08-25 nothing on the win side
# did, so a company with the best offer in the market acquired at the same 24% as one
# with the worst.
#
# EVERYTHING EXCEPT THE PRICE IS PINNED in the three tests below -- same seed, same year,
# same prospect draw, same premise stock, same credit bureau, same quote budget, same
# settlement budget. `price_differential_pct` is the only input that moves, which is what
# "our own market position ALONE" requires and what makes the difference attributable.
# ---------------------------------------------------------------------------

def _priced(d: float, *, year: int = 2018, quotes: int = 300):
    """The identical campaign at one price position. Nothing here varies but `d`."""
    import functools

    from simulation.acquisition_funnel import run_acquisition_funnel
    from tools.credit_adapters import get_credit_bureau_adapter

    return _campaign(
        years=[year],
        run_funnel=functools.partial(run_acquisition_funnel, price_differential_pct=d),
        credit_bureau=get_credit_bureau_adapter(),
        quote_budget_fn=_budget(quotes),
        customer_year_budget=100_000.0,
    )


def test_b1_our_own_price_position_moves_the_book_in_BOTH_directions():
    """The exit criterion, stated as the ruling states it: won AND lost against the market.

    Cheaper than the market average wins MORE of the same prospects; dearer wins FEWER. One
    company decision, one mechanism, both directions -- which is what separates this from a
    curve that merely goes up and down for unrelated reasons (the R15 fail-open the
    2026-08-18 re-amendment closed).
    """
    cheap = len(_priced(-0.05)["winners"])
    parity = len(_priced(0.0)["winners"])
    dear = len(_priced(+0.05)["winners"])

    assert cheap > parity, f"pricing below the market won nothing extra: {cheap} vs {parity}"
    assert dear < parity, f"pricing above the market cost nothing: {dear} vs {parity}"
    # Non-vacuity on both ends: neither extreme may be the trivial all-or-nothing campaign,
    # or this passes on a mechanism that simply switched acquisition off or on.
    assert 0 < dear, "the dear campaign won nothing at all -- that is a switch, not elasticity"
    assert cheap < 300, "the cheap campaign won every quote -- the funnel stopped filtering"


def test_b1_the_prospect_STREAM_is_identical_across_the_three_price_positions():
    """The null control the criterion names: the ARRIVAL STREAM must be HELD FIXED.

    Without this, `test_b1_...BOTH_directions` above is satisfiable by a price that quietly
    reshuffles or re-sizes the draw -- a bigger book from more prospects, not from a better
    offer. The homes quoted into, the number of quotes issued and the year's in-play market
    are asserted byte-identical at all three positions, so the ONLY thing that differs
    between them is which prospects said yes.
    """
    rows = {d: _priced(d)["by_year"][0] for d in (-0.05, 0.0, +0.05)}

    assert len({r["homes_in_market"] for r in rows.values()}) == 1, (
        "our price changed the SIZE of the market -- that is the world's fact, not ours"
    )
    assert len({r["quotes_issued"] for r in rows.values()}) == 1, (
        "our price changed how many quotes we issued -- the arrival stream is not held fixed"
    )
    quoted = {
        d: tuple(row["prospect_id"] for row in _priced(d)["spend"])
        for d in (-0.05, 0.0, +0.05)
    }
    assert quoted[-0.05] == quoted[0.0] == quoted[+0.05], (
        "a different set of homes was quoted at a different price -- the win difference is "
        "not attributable to the offer"
    )


def test_b1_the_win_side_reads_the_SAME_elasticity_the_loss_side_does():
    """Both legs, one curve. `_savings_to_rate` is the DESNZ-calibrated piecewise function
    the churn leg has used since Phase NS; the win side must resolve that same object rather
    than a private copy of it, or book size becomes tunable on one leg alone.
    """
    import inspect

    from simulation import acquisition_funnel, market_switching_propensity as msp

    assert "_savings_to_rate" in inspect.getsource(msp.offer_position_multiplier), (
        "the win side stopped reading the shared elasticity"
    )
    assert "offer_position_multiplier" in inspect.getsource(
        acquisition_funnel._quote_to_application_rate
    ), "the funnel stopped reading the price position at all"

    # And the guarantee that makes goal-seeking structurally unavailable rather than merely
    # forbidden: every gain on one leg is exactly the reciprocal of the cost on the other.
    for d in (0.01, 0.05, 0.10, 0.25):
        assert msp.offer_position_multiplier(d) * msp.offer_position_multiplier(-d) == pytest.approx(
            1.0
        ), f"the two directions stopped being each other's price at d={d}"


def test_b1_parity_is_EXACTLY_unchanged_so_the_shipped_run_moved_not_one_roll():
    """The wiring is provably inert at the run's shipped position (`PRICE_DIFFERENTIAL_PCT
    = 0.0`). A mechanism that shifted the book merely by existing could not be read as a
    response to a price the company chose."""
    from simulation.acquisition_funnel import QUOTE_TO_APPLICATION, _quote_to_application_rate
    from simulation.market_switching_propensity import offer_position_multiplier

    assert offer_position_multiplier(0.0) == 1.0
    for segment in ("resi", "SME"):
        assert _quote_to_application_rate(segment) == QUOTE_TO_APPLICATION[segment]
        assert _quote_to_application_rate(segment, 0.0) == QUOTE_TO_APPLICATION[segment]


def test_MUTATION_b1_a_price_blind_funnel_makes_both_directions_vanish():
    """R15 for `test_b1_our_own_price_position_moves_the_book_in_BOTH_directions`.

    The mutation IS the pre-2026-08-25 build: a quote-to-application rate that is a function
    of segment alone. Applied to the imported module object through monkeypatch, never to a
    file. If the book still moved with the price under this mutation, the movement would be
    coming from somewhere other than the mechanism this atom built.
    """
    from simulation import acquisition_funnel

    original = acquisition_funnel._quote_to_application_rate
    try:
        acquisition_funnel._quote_to_application_rate = (
            lambda segment, price_differential_pct=0.0: acquisition_funnel.
            QUOTE_TO_APPLICATION.get(segment, acquisition_funnel.QUOTE_TO_APPLICATION["resi"])
        )
        cheap = len(_priced(-0.05)["winners"])
        parity = len(_priced(0.0)["winners"])
        dear = len(_priced(+0.05)["winners"])
    finally:
        acquisition_funnel._quote_to_application_rate = original

    assert cheap == parity == dear, (
        "the price-blind funnel STILL moved the book -- the win difference in the live test "
        f"is not attributable to the price position ({cheap}/{parity}/{dear})"
    )


def test_MUTATION_b1_the_market_crisis_floor_on_the_dearer_side_flattens_it():
    """R15 for the negative branch, and it guards a defect this build actually had.

    The first draft read `_savings_to_rate` straight on both sides. Its negative branch
    returns the flat crisis floor, which encodes 2022's "nowhere cheaper to go" -- a fact
    about THE MARKET having no cheaper alternative, false by construction for one supplier
    priced above the average. Under that reading every dearer position collapsed onto a
    single value: 1% above the market cost exactly what 20% above cost, i.e. a supplier
    could raise prices without limit at no cost to its win rate.

    The mutation restores the straight read. The live assertion below it is the one that
    fails under the mutation, which is what makes it a control rather than a comment.
    """
    from simulation import market_switching_propensity as msp

    dear = [msp.offer_position_multiplier(d) for d in (0.01, 0.05, 0.10, 0.20)]
    assert dear == sorted(dear, reverse=True) and len(set(dear)) == 4, (
        "the dearer side is not strictly monotone -- a price rise is free somewhere"
    )

    mutated = [
        msp._savings_to_rate(-d * msp.CALIBRATION_ANNUAL_BILL_GBP) / msp._PARITY_RATE
        for d in (0.01, 0.05, 0.10, 0.20)
    ]
    assert len(set(mutated)) == 1, (
        "the mutation no longer reproduces the flat-crisis-floor defect, so this control is "
        "asserting against a mechanism that has moved"
    )


# ═══════════════════════════════════════════════════════════════════════════
# EXIT (b2) — the arrival stream EMPTIED, and the book must still be able to grow
#
# THE OTHER HALF OF THE NULL CONTROL, and the criterion is explicit about why one
# leg alone is not enough: "(b1) without (b2) is satisfiable by the curriculum".
# (b1) holds the arrival stream FIXED and moves the price — which proves the win is
# contested, but says nothing about whether the book would have grown anyway. (b2)
# takes the arrivals away entirely. Whatever is left is what this company won.
#
# WHAT "THE ARRIVAL STREAM" IS, named exactly as criterion (c) names it — the seven
# supply points this book gained in ten years without contesting one of them:
#   * FIVE from the static roster's hand-authored `acquisition_date` literals,
#     C_IC1 (2017-01-01), C_IC2 (2018-01-01), C_IC3 and C_IC3g (2019-01-01),
#     C_IC4 (2020-01-01) — one I&C site a year, each on New Year's Day;
#   * TWO from the curriculum's Profile-B trickle, SYN-2021-001 and SYN-2025-001.
# Emptying it means removing BOTH: the roster is trimmed to the accounts already on
# supply when the window opens, and `SE_DRAW_POPULATION` is off. Trimming only one
# would leave the other free to supply the growth and the test would pass on it.
#
# RED AT HEAD BEFORE THIS BUILD, `observed-with-evidence`, and for a structural
# reason rather than a commercial one. `live_population()` resolved the campaign
# INSIDE the `draw_population_enabled()` branch, so emptying the arrival stream also
# switched off the only mechanism by which the book could grow. Measured on the
# unmodified module at seed 20260724: draw off, `SE_GROW_BOOK=1`, `growth_mandate_
# active()` returning True the whole time, ten campaign years — book 18 -> 18, nought
# won. The mandate was live and unreachable. `test_MUTATION_b2_*` below restores that
# reachability and asserts the book goes flat again, which is what makes the pass
# above it evidence rather than a description.
# ---------------------------------------------------------------------------

#: The run's own seed, not this module's `SEED`. (b2) is asserted at the SEAM — the
#: one place a book is assembled from arrivals plus wins — so it must be asserted on
#: the world the run actually draws.
RUN_SEED = 20260724

#: The window opens on the roster as it stands at the start of 2016. Any account
#: dated after this is something the book GAINED, and (b2) asks where it came from.
WINDOW_OPEN = "2016-12-31"


def _no_arrivals(monkeypatch, tmp_path, *, mandate: bool):
    """The book with the arrival stream emptied. Returns (book, opening_roster).

    Both halves of the stream go. The trickle is switched off at its flag; the
    roster's staggered dates are removed by trimming every account that arrives
    after the window opens, which leaves a roster that is entirely on supply on day
    one and can therefore gain nothing by standing still.

    NEITHER RECORD IS THE REPO'S. Resolving a campaign writes the subset verdict and
    the campaign record, and a run with no arrivals in it is not the published run —
    letting it overwrite either file would put a fixture's figures where a reader
    would take them for the company's.
    """
    from saas.customers import _clear_drawn_customers
    from simulation import live_population as lp

    opening = [c for c in lp._STATIC_ROSTER if c["acquisition_date"] <= WINDOW_OPEN]
    monkeypatch.setenv("SE_DRAW_POPULATION", "0")
    monkeypatch.setenv("SE_GROW_BOOK", "1" if mandate else "0")
    monkeypatch.setattr(lp, "_STATIC_ROSTER", tuple(opening))
    monkeypatch.setattr(lp, "CUSTOMERS", list(opening))
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    monkeypatch.setattr(lp, "_CAMPAIGN_RECORD", tmp_path / "campaign.json")
    lp._CAMPAIGN_MEMO.clear()
    try:
        return lp.live_population(RUN_SEED), opening
    finally:
        lp._CAMPAIGN_MEMO.clear()
        _clear_drawn_customers()


def test_b2_the_arrival_stream_really_IS_empty(monkeypatch, tmp_path):
    """The null control, and it comes first because everything below rests on it.

    With the mandate off there is no campaign, so the fixture's book is the arrival
    stream and nothing else. If a single account still arrives after the window
    opens, the stream was not emptied and the growth measured in the next test could
    be that residue rather than a win. This is the assertion that stops (b2) being
    satisfied by an arrival the fixture forgot to remove.
    """
    book, opening = _no_arrivals(monkeypatch, tmp_path, mandate=False)

    assert [c["customer_id"] for c in book] == [c["customer_id"] for c in opening], (
        "with no mandate the book is not the opening roster -- something is still arriving"
    )
    late = [c["customer_id"] for c in book if c["acquisition_date"] > WINDOW_OPEN]
    assert not late, f"the arrival stream is not empty: {late}"
    # And the stream this is emptying is a real one: unemptied, those same five
    # staggered arrivals are there to be found. Without this the fixture could be
    # trimming a roster that never had a staggered date in it and the emptiness
    # above would be a property of the roster rather than of the trim.
    #
    # READ FROM `saas.customers`, not from `lp._STATIC_ROSTER`: monkeypatch does not
    # undo the trim until this test ENDS, so the module attribute is still the
    # trimmed tuple here and would report an empty stream whatever the roster held.
    from saas.customers import CUSTOMERS as _ROSTER

    staggered = [c["customer_id"] for c in _ROSTER
                 if c["acquisition_date"] > WINDOW_OPEN]
    assert set(staggered) == {"C_IC1", "C_IC2", "C_IC3", "C_IC3g", "C_IC4"}, staggered


def test_b2_with_the_arrival_stream_EMPTIED_the_book_still_GROWS(monkeypatch, tmp_path):
    """THE EXIT CRITERION. No arrivals, and the book is bigger at the end than at the start.

    Every account above the opening roster got there by surviving the five-stage
    funnel, the credit bureau and the statutory cooling-off window at the company's
    own expense — so the growth is the company's outcome, from the same contested
    mechanism (b1) proved can be lost, and not the curriculum handing it customers.
    """
    book, opening = _no_arrivals(monkeypatch, tmp_path, mandate=True)

    assert len(book) > len(opening), (
        f"the book did not grow with the arrivals removed: {len(opening)} -> {len(book)}"
    )
    gained = [c for c in book if c["customer_id"] not in {o["customer_id"] for o in opening}]
    assert gained, "vacuous: nothing was gained"
    granted = [c["customer_id"] for c in gained if c.get("acquisition_type") != "net_new_won"]
    assert not granted, f"the book grew by accounts nobody contested: {granted}"
    # Every gain is dated inside the campaign's decade, so none of them is an opening
    # account re-labelled or a record dated outside the window it was won in. NOT
    # `> WINDOW_OPEN`: `CAMPAIGN_YEARS` opens in 2016, so a first-year win is dated
    # inside the opening year and is still a win. What identifies a gain is that it is
    # not on the opening roster, which the id comparison above already establishes.
    assert all("2016-01-01" <= c["acquisition_date"] < "2026-01-01" for c in gained)


def test_MUTATION_b2_a_campaign_gated_behind_the_ARRIVAL_flag_goes_flat(monkeypatch, tmp_path):
    """R15 for the test above, and the mutation IS the pre-2026-08-25 module.

    Before this build `live_population()` returned early when the population draw was
    off, and the campaign sat below that return. The mutation restores exactly that
    reachability — the campaign resolves to nothing whenever the arrival stream is
    empty — without touching a file. If the book still grew under it, the growth in
    the live test would be arriving from somewhere other than the campaign, and the
    control would be describing rather than proving.
    """
    from simulation import live_population as lp

    real_campaign = lp._campaign

    def _gated(book, seed):
        if not lp.draw_population_enabled():
            return {"winners": [], "spend": [], "by_year": [], "notes": [],
                    "customer_years_committed": 0.0, "customer_year_budget": 0.0}
        return real_campaign(book, seed)

    monkeypatch.setattr(lp, "_campaign", _gated)
    book, opening = _no_arrivals(monkeypatch, tmp_path, mandate=True)

    assert len(book) == len(opening), (
        "the arrival-gated campaign STILL grew the book -- the growth asserted in "
        f"test_b2_... is not attributable to the decoupling ({len(opening)} -> {len(book)})"
    )


def test_b2_the_two_flags_are_INDEPENDENT_and_the_default_path_is_untouched(monkeypatch, tmp_path):
    """The decoupling must not have moved the shipped default, which is both flags off.

    With no draw and no mandate `live_population()` returns the served roster and
    nothing else, and — the part worth asserting rather than assuming — it resolves
    no campaign at all: the memo is still empty afterwards. A default path that
    quietly started resolving a 245-quote campaign to discard it would be inert in
    its output and not in its cost.
    """
    from simulation import live_population as lp

    monkeypatch.setenv("SE_DRAW_POPULATION", "0")
    monkeypatch.setenv("SE_GROW_BOOK", "0")
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    monkeypatch.setattr(lp, "_CAMPAIGN_RECORD", tmp_path / "campaign.json")
    lp._CAMPAIGN_MEMO.clear()
    try:
        book = lp.live_population(RUN_SEED)
        served = lp.served_segments()
        assert [c["customer_id"] for c in book] == [
            c["customer_id"] for c in lp.CUSTOMERS if lp._serves(c, served)
        ]
        assert not lp._CAMPAIGN_MEMO, "the default path resolved a campaign it then threw away"
        assert not (tmp_path / "campaign.json").exists()
    finally:
        lp._CAMPAIGN_MEMO.clear()
