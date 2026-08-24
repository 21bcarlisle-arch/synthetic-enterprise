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
