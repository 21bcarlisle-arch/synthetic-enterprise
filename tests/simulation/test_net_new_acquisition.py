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
    capital_headroom_gbp,
    cost_per_acquisition_gbp,
    growth_quote_budget,
)
from simulation import net_new_acquisition as nna

HORIZON = dt.date(2026, 1, 1)
SEED = 20260824

# `plan_growth_campaign` takes the per-segment quote cost as DATA (KNIFE B6 -- the SIM is told
# the cost and cannot consult company accounting). This used to be `COST_PER_ACQUISITION`
# imported wholesale; that table was deleted on 2026-08-28 as unsourced, so the fixture builds
# the same shape from the sourced model instead. Residential is non-zero here on purpose: these
# tests assert that a campaign COSTS money, and the broker-acquired segments now cost 0.0
# per quote (their cost is a billing-time trail), which would make several of them vacuous.
_COST_PER_QUOTE = {
    "resi": cost_per_acquisition_gbp("resi"),
    "SME": cost_per_acquisition_gbp("SME"),
}


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
        cost_per_quote_gbp=_COST_PER_QUOTE,
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
    assert any("SETTLEMENT-SAMPLED" in n for n in out["notes"])
    # THE RATE IS THE STATEMENT, and it replaced `binding == "settlement_engine"` on
    # 2026-08-29. The ceiling no longer stops a year -- it takes a uniform sample of the whole
    # campaign -- so `binding` reports what limited the COMPANY and the machine's share is a
    # number on every row. Asserting the old label here would pin this test to a mechanism the
    # module no longer has, and asserting nothing would let a silent cap through.
    assert out["settlement_sample_rate"] < 1.0
    assert all(r["settlement_sample_rate"] < 1.0 for r in out["by_year"])
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


def test_the_refused_wins_are_COUNTED_and_not_just_the_first_one_named():
    """THE RULING OF 2026-08-28, first clause: the split is on the row a reader sees.

    A campaign that reports BOOKED wins alone cannot be read. 45 wins on 2,089 quotes is a
    supplier losing in the market if the 2.2% is commercial, and is this machine refusing to
    settle accounts the supplier won if it is not -- and until this split existed those two
    were the same number. `cy_exhausted_at` named the FIRST refused prospect and never how
    many followed it, so the campaign that exposed this reported a note and no quantity.
    """
    out = _campaign(quote_budget_fn=_budget(200), customer_year_budget=10.0)
    row = out["by_year"][0]

    assert row["wins_refused_by_settlement_budget"] > 0, (
        "vacuous: this fixture must actually refuse wins"
    )
    # THE IDENTITY, on every row and on the campaign. What the funnel won is what got booked
    # plus what this machine would not settle -- there is no third destination, and a win that
    # went missing between them would fail here rather than reading as a commercial loss.
    for r in out["by_year"]:
        assert r["funnel_wins"] == r["wins"] + r["wins_refused_by_settlement_budget"]
    assert out["funnel_wins"] == len(out["winners"]) + out["wins_refused_by_settlement_budget"]

    # The funnel's own verdict, independently: the split must agree with the spend ledger,
    # which is the only other place a win is recorded.
    assert out["funnel_wins"] == len([r for r in out["spend"] if r["won"]])
    total_refused = out["wins_refused_by_settlement_budget"]
    assert any(
        f"settled {len(out['winners'])} of them" in n for n in out["notes"]
    ), "the settlement note must carry the COUNT, not only the first prospect's id"
    assert total_refused == out["funnel_wins"] - len(out["winners"])


def test_a_budget_the_OPENING_BOOK_has_already_spent_books_nothing_and_says_so():
    """THE FAR EDGE OF THE SAMPLE, which is a real operating state and not a hypothetical.

    82 founders already commit 778 of the 1,200 (`docs/design/FOUNDER_BOOK.yaml`), so one more
    curriculum act deepening the opening book takes the campaign's headroom to zero. The sample
    rate is then 0.0 and the honest outcome is an EMPTY campaign book with a note saying the
    machine refused all of it -- never a silent empty list, which is indistinguishable on a chart
    from a supplier that won nothing. It must also not divide by zero on the way there.
    """
    out = _campaign(quote_budget_fn=_budget(20), customer_year_budget=1.0,
                    customer_years_already_committed=1.0)

    assert out["funnel_wins"] > 0, "vacuous: the funnel must have won something to refuse"
    assert out["winners"] == []
    assert out["settlement_sample_rate"] == 0.0
    assert out["wins_refused_by_settlement_budget"] == out["funnel_wins"]
    assert any("SETTLEMENT-SAMPLED" in n for n in out["notes"]), (
        "an empty book the machine caused must SAY it caused it"
    )


def test_a_campaign_that_won_NOTHING_does_not_divide_by_zero_sampling_it():
    """The other degenerate end: no candidates at all. There is nothing to sample, the rate is
    1.0 because nothing was refused, and no note claims a machine limit that never bit."""
    out = _campaign(run_funnel=_always(False), quote_budget_fn=_budget(20))

    assert out["winners"] == []
    assert out["funnel_wins"] == 0
    assert out["settlement_sample_rate"] == 1.0
    assert out["customer_years_all_wins_would_cost"] == 0.0
    assert not any("SETTLEMENT-SAMPLED" in n for n in out["notes"])


def test_the_sample_is_PROPORTIONAL_in_every_year_and_not_merely_non_empty():
    """THE PROPERTY THAT MAKES THIS A SAMPLE RATHER THAN A SMALLER CLIFF.

    Booking something in every year is not enough -- first-come with a per-year sub-budget does
    that too, and loads the book into whichever years are cheapest. What the fix claims is that
    each year's booked wins are proportional to that year's FUNNEL wins, so `booked / rate`
    estimates what the company won without bias anywhere and the curve's shape stays commercial.

    A win's settlement cost falls with its date, so a rule that is not proportional shows it
    here: the ten-year fixture spans a 10x spread in cost per win.
    """
    out = _campaign(years=list(range(2016, 2026)), quote_budget_fn=_budget(40),
                    customer_year_budget=200.0)
    rate = out["settlement_sample_rate"]

    assert 0.0 < rate < 1.0, "vacuous: the ceiling must actually bite in this fixture"
    booked = [r for r in out["by_year"] if r["funnel_wins"]]
    assert len(booked) == 10, "every year must have funnel wins for this to test proportionality"
    for r in booked:
        realised = r["wins"] / r["funnel_wins"]
        assert abs(realised - rate) <= 0.5 * rate + (1.0 / r["funnel_wins"]), (
            f"{r['year']}: booked {r['wins']} of {r['funnel_wins']} funnel wins "
            f"({realised:.3f}) against a campaign rate of {rate:.3f} -- the sample is not "
            "proportional, so this year is over- or under-represented in the book"
        )
    assert out["customer_years_committed"] <= 200.0


def test_MUTATION_a_campaign_the_machine_never_refuses_reports_a_split_of_ZERO():
    """The null control for the test above, and without it that identity is not attributable.

    `funnel_wins == wins + refused` is satisfied by a `refused` hard-wired to 0 whenever the
    cap does not bite -- and if it were hard-wired to 0 ALWAYS, the test above would still
    pass everywhere except its own fixture. So the property is two-sided: the counter must be
    zero exactly when nothing is refused, and the run must be identical to the pre-split one.
    """
    out = _campaign(quote_budget_fn=_budget(20))
    assert out["wins_refused_by_settlement_budget"] == 0
    assert all(r["wins_refused_by_settlement_budget"] == 0 for r in out["by_year"])
    assert out["funnel_wins"] == len(out["winners"]) > 0, "vacuous: nothing was won"
    assert not any("SETTLEMENT-SAMPLED" in n for n in out["notes"])
    # THE NULL RESULT THAT SHOWS THE SAMPLING IS AIMED AT THE ARTEFACT. A ceiling the campaign
    # never reaches must leave a run byte-identical to one with no ceiling at all: rate exactly
    # 1.0, nothing refused, no note. If the sample fired here it would be shrinking a book that
    # fits.
    assert out["settlement_sample_rate"] == 1.0
    assert all(r["settlement_sample_rate"] == 1.0 for r in out["by_year"])


def test_the_company_plans_on_its_FUNNELS_wins_not_on_what_the_machine_would_settle():
    """THE RULING OF 2026-08-28, second clause, and it is a WALL test.

    `SETTLEMENT_CUSTOMER_YEAR_BUDGET` is THIS MACHINE's ceiling -- the module's own note says
    so -- and it does not exist in the modelled world. Feeding the wins it truncated back into
    `quote_budget_fn` put it inside the company's own commercial belief: at the 80-founder book
    the company's realised win rate read 1.7% instead of 17.9%, so it bought 2,826 quotes to
    book 45 accounts. That is not a supplier being allowed to be wrong about its market; it is
    the harness reaching into its books.

    The fixture is the shape that makes the two answers differ: a budget so small that almost
    every win is refused. A campaign passing BOOKED wins hands the planner ~0; the ruled one
    hands it what the funnel actually converted.
    """
    seen = []

    def _recording_budget(net_assets_gbp, accounts_held, quotes_issued_to_date=0, wins_to_date=0):
        seen.append(wins_to_date)
        return {"quotes": 40, "budget_gbp": 40 * 150.0, "wins_capital_allows": 8,
                "binding": "capital", "headroom_gbp": net_assets_gbp}

    out = _campaign(years=[2018, 2019], quote_budget_fn=_recording_budget,
                    customer_year_budget=10.0)

    first_year = out["by_year"][0]
    assert first_year["wins_refused_by_settlement_budget"] > 0, (
        "vacuous: with nothing refused, booked wins and funnel wins are the same number and "
        "this fixture cannot see the defect it is written for"
    )
    # What year two is handed is year one's FUNNEL verdict...
    assert seen[1] == first_year["funnel_wins"]
    # ...and it is strictly more than the book got, which is what makes the two readings
    # distinguishable rather than merely differently named.
    assert seen[1] > first_year["wins"]


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
    #
    # `funnel_wins`, NOT `wins` (2026-08-28 ruling). The two are equal in this fixture because
    # nothing is refused here, so this line alone cannot tell them apart -- that is what
    # `test_the_company_plans_on_its_FUNNELS_wins_not_on_what_the_machine_would_settle` below
    # is for, and it is separate for exactly the reason `_budget`'s docstring gives.
    for i in range(1, 3):
        expected_quotes = sum(y["quotes_issued"] for y in by_year[:i])
        expected_wins = sum(y["funnel_wins"] for y in by_year[:i])
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


# ---------------------------------------------------------------------------
# EXIT (c) — THE QUOTES ARE PAID FOR IN THE ACCOUNTS, NOT IN A JSON FILE
# ---------------------------------------------------------------------------
# Criterion (c) asks that no step change in book size be unmodelled, and names three
# things a modelled acquisition does: pass a funnel, COST A PENNY, and be able to fail.
# The campaign's winners passed a funnel from the day it was built and (b1) made them
# able to fail on price. They did not cost a penny. `run_phase2b`'s two
# `acquisition_spend_events.append` sites both sit inside the churn branch of the
# replacement path, so the only acquisition spend that ever reached the P&L was the cost
# of replacing customers who left; the campaign's own 1,295 quotes and £157,155 were
# summed into `book_growth_campaign.json`, which is a report and not a ledger.
#
# THE MEASUREMENT THAT MADE THIS A BUILD rather than a hunch, taken on unmodified HEAD at
# the shipped configuration: campaign spend £157,155 over 1,295 quotes; published ledger
# `acquisition_spend_gbp` £5,587.50 over 43 rows. 96.4% of what this supplier spent
# winning customers was missing from its own accounts, and the activation record for this
# very campaign had told the director "Growth costs money."

# RE-MEASURED 2026-08-26 (1,295 -> 1,115 quotes, £157,155 -> £135,285), on this test's own
# instruction: "the shipped campaign has been re-sized -- re-measure before trusting the
# figures in this file's header". Two director-ordered changes moved the prospect mix, and
# neither is a regression:
#   * 4e884cdbf  the I&C suspension (director, 2026-08-24) -- the campaign stopped quoting
#                the business segments it is no longer allowed to serve.
#   * fb8a8fda5  the funnel won electricity and never gas -- fixing that changed which
#                prospects the campaign draws, and how far into 2025 its schedule runs.
# This file went red at fb8a8fda5 and stayed red across three further commits, because the
# gate selects tests by filename stem and no commit since touched a stem that reaches here.
#   * 2026-08-28  the acquisition costs were sourced (COST_PER_ACQUISITION's invented
#                £150/£400 deleted for saas/opex_ledger.py's PCS commission), AND the
#                campaign stopped quoting prospects dated after the reported period.
#                TWO THINGS CHANGED AT ONCE, so the split is stated rather than asserted --
#                and it is recoverable here because the pre-change file already carried both
#                legs. £135,285 was the whole campaign at the invented prices; £129,285 was
#                the same campaign with the 49 post-period quotes removed and the prices
#                still invented (the old CAMPAIGN_SPEND_INSIDE_WINDOW, directly below); and
#                £23,709 is that same 1,066-quote population at the sourced prices. So:
#                    the quote cutoff  -£6,000    (4.4% of the fall)
#                    sourcing the cost -£105,576  (78.0%)
#                The population is identical across the second step, which is what makes it a
#                price effect and not a mix effect.
#
# RE-MEASURED 2026-08-28 (1,066 -> 2,089 quotes, £23,709 -> £46,408), and this one is NOT the
# usual "re-measure before trusting the header". These four constants went red on a DIRECTOR'S
# CURRICULUM ACT -- the 80-founder book (`docs/design/FOUNDER_BOOK.yaml`, "take the 80
# founders") -- and they are being re-baselined only because the run behind them has been
# understood first. R12: the number is attributed, not fitted. Two things moved it and the
# split is MEASURED rather than stated, one variable at a time, at the same seed:
#
#     1,066  founders 13, the pre-decision run (reachable today: set `founder_accounts: 13`)
#     2,826  founders 80, before the wall fix -- the settlement ceiling inside the planner
#     2,089  founders 80, on the funnel's own record  <- SHIPPED
#
#   the founder book   +1,023  (a deeper opening book is more opening capital, so more quotes
#                               the company can afford: an ordinary commercial consequence)
#   the wall fix         -737  (£16,404 the company spent because THIS MACHINE's settlement
#                               budget had been fed back into its own realised win rate --
#                               see net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET)
#
# The 13-founder run is BYTE-IDENTICAL across the wall fix (1,066 quotes, 200 funnel wins, 200
# booked, 0 refused), which is what says the fix is aimed at the artefact and not at the answer.
#
# RE-MEASURED 2026-08-29 (2,089 -> 2,737 quotes, £46,408 -> £60,839), and again the split is
# measured one variable at a time rather than stated. Two changes landed, in this order:
#
#     2,089  the record above                                              <- was SHIPPED
#     2,737  `accounts` counts FUNNEL wins, not booked ones (the second leg of the 2026-08-28
#            wall fix, left behind when the first leg landed)              <- SHIPPED
#     2,737  the settlement ceiling samples instead of stopping -- IDENTICAL, because the
#            sampling pass runs after every quote is issued and paid for
#
#   the accounts leg   +648 quotes, +£14,431  (`accounts_held` sizes the Ofgem capital headroom
#                               and the 33% growth-rate cap. Incrementing it only on a SETTLED
#                               win froze the company's account count from 2018 at this
#                               machine's ceiling, so it planned eight years against a balance
#                               sheet our wall clock had written. In the modelled world it won
#                               those accounts and holds capital against them.)
#   the sampling leg   0                      (the ceiling decides which wins reach the BOOK; it
#                               has never decided which prospects were quoted, and this null is
#                               what says so)
#
# PREDICTED BEFORE EITHER RAN, in `docs/design/SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md` §3:
# "booked wins stay at exactly 45 and every published book figure is unchanged" across the
# accounts leg. They did, and 2016 and 2017 came back byte-identical -- the budget is exhausted
# inside 2017 under either rule, so the two only diverge from 2018.
CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG = 2737
CAMPAIGN_SPEND_AT_SHIPPED_CONFIG = 60838.81

#: The subset the ACCOUNTS can carry: quotes dated inside [REPORT_START, REPORT_END].
#:
#: EQUAL TO THE WHOLE CAMPAIGN SINCE 2026-08-28, and that is the point of the quote cutoff
#: rather than a coincidence: the campaign no longer plans quotes dated after the last day
#: the accounts cover, so there is nothing left for the window filter to drop. The POPULATION
#: is unchanged from before that commit -- the same 1066 prospects were always the in-window
#: ones -- so what moved is the price of each quote and not who was quoted.
#:
#: The filter is still real and still tested: `test_c_MUTATION_the_window_filter_can_actually_
#: EXCLUDE` hands it a mid-decade `report_end` and requires it to drop the rest.
CAMPAIGN_QUOTES_INSIDE_WINDOW = 2737
CAMPAIGN_SPEND_INSIDE_WINDOW = 60838.81


def test_c_every_quote_the_campaign_paid_for_is_BOOKED_as_acquisition_spend():
    """THE EXIT TEST for (c)'s cost clause. Nothing the campaign bought goes unbooked.

    Judged quote-by-quote rather than on the total, because a total can be right while
    the population behind it is wrong -- one £157,155 row would satisfy a sum check and
    would not be a ledger. The subject is `campaign_quotes_paid_for()` itself, so this
    cannot pass by the two lists agreeing on a number neither of them got from the
    campaign.
    """
    from simulation.live_population import campaign_quotes_paid_for
    from simulation.run_phase2b import (
        REPORT_END,
        REPORT_START,
        campaign_acquisition_spend_events,
    )

    quotes = campaign_quotes_paid_for()
    events = campaign_acquisition_spend_events()

    assert len(quotes) == CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG, (
        "the shipped campaign has been re-sized -- re-measure before trusting the "
        f"figures in this file's header ({len(quotes)} quotes)"
    )
    assert round(sum(q["amount_gbp"] for q in quotes), 2) == CAMPAIGN_SPEND_AT_SHIPPED_CONFIG

    # THE SUBJECT IS THE REPORTED PERIOD, not the campaign's whole schedule (2026-08-26).
    # `campaign_acquisition_spend_events` books what the accounts cover; the clause is that
    # nothing inside that period escapes it.
    inside = [q for q in quotes if REPORT_START <= q["event_date"] <= REPORT_END]
    assert len(inside) == CAMPAIGN_QUOTES_INSIDE_WINDOW, (
        f"the reported period now carries {len(inside)} quotes -- re-measure the header"
    )
    assert len(events) == len(inside), (
        f"{len(inside) - len(events)} quote(s) the company paid for inside the reported "
        "period were never booked"
    )
    quotes = inside
    # The ledger's sign convention: spend is a NEGATIVE amount (`saas.ledger.
    # make_acquisition_spend_event`), and `company.finance.pnl` negates it back into an
    # operating cost. A positive row here would ADD £157,155 of margin instead.
    assert round(-sum(e["amount_gbp"] for e in events), 2) == CAMPAIGN_SPEND_INSIDE_WINDOW

    by_account = {e["billing_account"]: e for e in events}
    for quote in quotes:
        booked = by_account.get(quote["prospect_id"])
        assert booked is not None, f"{quote['prospect_id']} was quoted and never booked"
        assert booked["event_type"] == "acquisition_spend_event"
        assert booked["timestamp"] == quote["event_date"]
        assert booked["amount_gbp"] == -quote["amount_gbp"]
        assert booked["segment"] == quote["segment"]
        # THE LOST QUOTES ARE THE POINT. A ledger that booked only the winners would
        # report a cost per acquisition of one quote per account and make growth look
        # free at the margin -- the exact shape that stops acquisition cost being
        # something this company can get wrong.
        assert booked["acquisition_won"] == quote["won"]

    lost = [e for e in events if not e["acquisition_won"]]
    assert lost, "vacuous: no losing quote was booked, so nothing here proves losses cost"


def test_c_NULL_CONTROL_with_the_growth_mandate_OFF_no_campaign_spend_is_booked(
    monkeypatch, tmp_path
):
    """The null control, and without it the test above is not attributable.

    `campaign_acquisition_spend_events` books whatever `campaign_quotes_paid_for` hands
    it. If that accessor returned the REPLACEMENT path's spend, or a constant, or
    anything at all under a switched-off campaign, the £157,155 above would be a number
    the build produced rather than the campaign's. With the mandate off the company runs
    no campaign, so it must book nothing -- and the shipped default path must be exactly
    as expensive as it was before this build.
    """
    from simulation import live_population as lp
    from simulation.run_phase2b import campaign_acquisition_spend_events

    monkeypatch.setenv("SE_GROW_BOOK", "0")
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    monkeypatch.setattr(lp, "_CAMPAIGN_RECORD", tmp_path / "campaign.json")
    lp._CAMPAIGN_MEMO.clear()
    try:
        assert campaign_acquisition_spend_events() == []
    finally:
        lp._CAMPAIGN_MEMO.clear()


def test_c_the_window_filter_excludes_nothing_at_the_shipped_configuration():
    """The claim `campaign_acquisition_spend_events` makes about its own filter.

    A period filter that silently dropped part of the decade would understate the very
    cost this build exists to book, and it would look identical to a smaller campaign.

    RE-AIMED 2026-08-26. As written this asserted that EVERY quote is inside the window --
    which was true only while the campaign's schedule and the report's period happened to
    end together, and stopped being true at fb8a8fda5 when fixing the electricity-only
    funnel changed how far into 2025 the schedule runs. It reds at a coincidence, not at
    the defect.

    The defect it exists to catch is a drop INSIDE the decade: a quote dated in a period
    the accounts cover, paid for, and missing from them. A quote dated 2025-07-20 in a run
    that reports to 2025-06-07 is a different thing entirely -- in the reported world it
    has not happened yet, and booking it would put cost in a period the ledger does not
    report. So the claim is now stated as what it means: the excluded set is exactly the
    post-period tail, and the window's interior is whole.
    """
    from simulation.live_population import campaign_quotes_paid_for
    from simulation.run_phase2b import REPORT_END, REPORT_START, campaign_acquisition_spend_events

    outside = [
        q for q in campaign_quotes_paid_for()
        if not REPORT_START <= q["event_date"] <= REPORT_END
    ]
    # Nothing is dropped from BEFORE or WITHIN the reported period -- the only exclusions
    # are dated after its last day. A quote dated 2019 going missing would fail here, which
    # is the case the original assertion was written for.
    early = [q["prospect_id"] for q in outside if q["event_date"] < REPORT_START]
    assert not early, f"quotes predate the reported period and are dropped: {early}"
    assert all(q["event_date"] > REPORT_END for q in outside)

    # NON-VACUITY: the tail must be a tail. If it ever grew to a material share of the
    # campaign, "outside the period" would have become the excuse the original assertion
    # was guarding against, and this reds rather than absorbing it.
    assert len(outside) < 0.10 * CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG, (
        f"{len(outside)} of {CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG} quotes fall outside the "
        "reported period -- that is no longer a schedule tail, it is unbooked spend"
    )
    assert len(campaign_acquisition_spend_events()) == CAMPAIGN_QUOTES_INSIDE_WINDOW


def test_the_campaign_quote_cutoff_is_the_reported_period_end():
    """`live_population.CAMPAIGN_QUOTE_CUTOFF` restates `run_phase2b.REPORT_END` because it
    cannot import it (run_phase2b imports live_population). A restated constant is free to
    drift, so this is the thing that stops it: move either and this reds."""
    from simulation.live_population import CAMPAIGN_QUOTE_CUTOFF
    from simulation.run_phase2b import REPORT_END

    assert CAMPAIGN_QUOTE_CUTOFF == REPORT_END


def test_the_campaign_never_quotes_a_prospect_the_reported_world_has_not_met():
    """The Point-in-Time Blindfold on the quote itself (2026-08-28).

    Not merely "the tail is small" — the tail must be EMPTY. A prospect dated after the last
    reported day has not come to market, so the supplier cannot have paid to quote them.
    """
    from simulation.live_population import campaign_quotes_paid_for
    from simulation.run_phase2b import REPORT_END

    late = [q["prospect_id"] for q in campaign_quotes_paid_for() if q["event_date"] > REPORT_END]
    assert not late, f"{len(late)} quotes are dated after the reported period ends"


def test_MUTATION_without_the_cutoff_the_campaign_DOES_quote_past_the_period():
    """R15 for the test above: with the cutoff removed the tail comes back, so the assertion
    is about the cutoff working and not about the campaign happening to end early."""
    from simulation.acquisition_funnel import run_acquisition_funnel
    from tools.credit_adapters import get_credit_bureau_adapter

    kw = dict(
        years=[2025], base_seed=SEED, opening_net_assets_gbp=2_000_000.0,
        accounts_held_at_start=14, horizon_end=HORIZON,
        credit_bureau=get_credit_bureau_adapter(), cost_per_quote_gbp=_COST_PER_QUOTE,
        run_funnel=run_acquisition_funnel, quote_budget_fn=_budget(400),
    )
    uncapped = nna.plan_growth_campaign(**kw)
    capped = nna.plan_growth_campaign(**kw, quote_cutoff="2025-06-07")

    late_uncapped = [r for r in uncapped["spend"] if r["event_date"] > "2025-06-07"]
    late_capped = [r for r in capped["spend"] if r["event_date"] > "2025-06-07"]

    assert late_uncapped, "without the cutoff there must BE a post-period tail to remove"
    assert not late_capped
    assert len(capped["spend"]) < len(uncapped["spend"])


def test_c_MUTATION_the_window_filter_can_actually_EXCLUDE():
    """R15 for the test above: a filter that never excludes anything is not a filter.

    The test above passes if the `if` were deleted entirely, so on its own it proves the
    filter harmless rather than present. Handed a `report_end` mid-decade, it must drop
    exactly the quotes dated after it -- which is also the truncated-window behaviour a
    short run depends on.
    """
    from simulation.live_population import campaign_quotes_paid_for
    from simulation.run_phase2b import campaign_acquisition_spend_events

    cutoff = "2019-12-31"
    booked = {e["billing_account"] for e in campaign_acquisition_spend_events(cutoff)}
    expected = {q["prospect_id"] for q in campaign_quotes_paid_for()
                if q["event_date"] <= cutoff}

    assert booked == expected
    assert 0 < len(booked) < CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG, (
        f"the filter excluded {CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG - len(booked)} quotes; "
        "a filter that excludes nothing on a truncated window is not filtering"
    )


@pytest.fixture
def shipped_supply_book():
    """The two run-based tests below need the supply book the SHIPPED run assembles.

    FOUND BY RUNNING THEM TOGETHER, not by reading. `_no_arrivals` above tears the drawn
    book down with `saas.customers._clear_drawn_customers()` on the way out — correctly,
    because a fixture's trimmed roster must not leak — but nothing puts the shipped drawn
    book BACK. Every test in this file that judges the campaign directly is indifferent to
    that; a test that runs `run_phase2b.main` is not, because the run resolves account ids
    against `DRAWN_CUSTOMERS` and gets `None` for a customer the book still contains.
    Combined with `tests/simulation/test_run_phase2b.py` in one session it surfaced as
    `AttributeError: 'NoneType' object has no attribute 'get'` in `hh_consumption`.

    So this re-registers by re-running the seam at the shipped configuration, and restores
    `ACQUIRED_CUSTOMERS` afterwards — the same idiom
    `tests/simulation/test_home_move_undeliverable_win.py::restore_acquired_book` already
    keeps for a run that appends wins to a module-level list.
    """
    import simulation.live_population as lp
    import simulation.run_phase2b as rp
    from saas.customers import _clear_drawn_customers

    acquired_before = list(rp.ACQUIRED_CUSTOMERS)
    _clear_drawn_customers()
    lp._CAMPAIGN_MEMO.clear()
    lp.live_population()
    try:
        yield
    finally:
        rp.ACQUIRED_CUSTOMERS[:] = acquired_before


def test_c_the_booked_spend_REACHES_THE_RUN_and_therefore_the_P_AND_L(shipped_supply_book):
    """The wiring, proven by running the thing rather than by reading it.

    A helper nothing calls books nothing, and that failure mode is invisible to every
    test above. This runs `run_phase2b.main` over a truncated window -- 5.6 s measured
    2026-08-25 -- and asserts the campaign's quotes are in the run's OWN
    `acquisition_spend_events`, which is the list `run_phase4c_on_phase2b` hands to
    `close_the_books`. Then it runs the P&L over exactly those events and asserts the
    money arrives as an operating cost, because a spend event the income statement
    ignored would be booked and still free.
    """
    from company.finance.pnl import company_income_statement
    from simulation.run_phase2b import main

    result = main(report_end="2016-06-30")
    events = result["acquisition_spend_events"]
    campaign_rows = [e for e in events if e["billing_account"].startswith("PROS-")]

    assert campaign_rows, "the run booked no campaign spend -- the helper is not wired in"
    spent = round(-sum(e["amount_gbp"] for e in campaign_rows), 2)
    assert spent > 0

    statement = company_income_statement(campaign_rows)
    assert statement["acquisition_spend_gbp"] == spent, (
        "the campaign's spend events reached the run and not the income statement"
    )
    assert statement["total_operating_costs_gbp"] >= spent


def test_MUTATION_c_the_PRE_BUILD_run_books_none_of_it(shipped_supply_book):
    """R15 for the wiring test: the mutation IS `run_phase2b` as it stood before today.

    Before this build the run seeded `acquisition_spend_events` with an empty list and
    filled it only from the replacement path. Restoring that -- by returning nothing from
    the helper the run seeds itself from -- must take the campaign's spend back out of the
    run entirely. If it did not, the spend asserted above is arriving from somewhere other
    than this build and the control is describing rather than proving.
    """
    import simulation.run_phase2b as rp

    real = rp.campaign_acquisition_spend_events
    rp.campaign_acquisition_spend_events = lambda report_end=rp.REPORT_END: []
    try:
        result = rp.main(report_end="2016-06-30")
    finally:
        rp.campaign_acquisition_spend_events = real

    campaign_rows = [e for e in result["acquisition_spend_events"]
                     if e["billing_account"].startswith("PROS-")]
    assert not campaign_rows, (
        "the pre-build run STILL books campaign spend -- the £157,155 measured above is "
        "not attributable to this change"
    )
