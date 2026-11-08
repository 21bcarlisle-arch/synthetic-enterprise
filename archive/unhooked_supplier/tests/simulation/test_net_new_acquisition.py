# ARCHIVED LEGS of tests/simulation/test_net_new_acquisition.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/simulation/test_net_new_acquisition.py.
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
import pathlib
import re

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
    def _fn(net_assets_gbp, accounts_held, quotes_issued_to_date=0, wins_to_date=0, as_of=None):
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









# ---------------------------------------------------------------------------
# A prospect is not a customer
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
# Capital is what bounds the campaign
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
# The engineering cap must never be silent
# ---------------------------------------------------------------------------



































# ---------------------------------------------------------------------------
# PB3 exit (a): the market is REAL, and it is the same market churn sees
# ---------------------------------------------------------------------------















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
# RE-MEASURED 2026-08-30, and the cause is a world change rather than a campaign change: the
# in-play market is `min(pool, pool * market_switching_multiplier(year))`, and that multiplier is
# now a ratio of the PUBLISHED switching record instead of a ratio of the savings curve. The
# record thins 2017 (0.870, was 1.630), 2022 (0.267, was 0.444) and 2023 (0.776, was 0.881), so
# nine fewer quotes were affordable. Nobody re-priced anything: 2737 -> 2728 quotes,
# £60,838.81 -> £60,622.86, at the unchanged £20.63 unit price with 2728 * 20.63 + rounding.
# RE-MEASURED 2026-10-03, a world change again: the campaign's prospects now come to market in each
# year's published months (DESNZ Table 2.7.1, `population_draw._seasonal_day_offsets`, as the
# founders and the trickle already did). Only 2025 moves, 176 -> 157: the campaign stops at
# REPORT_END (7 June), and the seasonal days are drawn from their own stream, so how many of 2025's
# prospects fall before the cutoff is a fresh draw (binomial sd ~10 on 400). Every other year is
# byte-identical: 2728 -> 2709, £60,622.86 -> £60,210.25, at the same £20.63.
# RE-MEASURED 2026-10-03, a world change: the commons moved onto DESNZ QEP 2.7.1 and the multiplier
# the in-play pool is clipped by moved with it (2017 0.870 -> 2.015, 2022 0.267 -> 0.339, 2023
# 0.776 -> 0.701). 2709 -> 2707 quotes, at the same £20.63.
# RE-MEASURED 2026-10-08, a curriculum change (director: acquisition selects on each prospect's own
# responsiveness, `docs/design/curriculum/acquisition_selects_on_own_responsiveness.json`). The
# quotes go to the engagement-weighted first prospects, so different homes win, the company's own
# realised win rate differs and with it the quote budget from 2017: 2707 -> 2694 quotes,
# £60,170.37 -> £59,859.52. With that file's `activated` false it is 2707 / £60,170.37 exactly.
# RE-MEASURED 2026-10-09 at the 400-founder book (director's founder ruling, 2026-10-08): the
# quote budget is sized off the book the campaign plans against, so a five-times-larger opening
# book quotes more -- 2694 -> 3345 quotes, £59,859.52 -> £74,356.09, all still inside the window.
# RE-MEASURED 2026-10-12, a factual correction: capital held per account 130 -> 115 (Ofgem's decided
# Capital Target; £130 was the consultation). More headroom lifts the one capital-bound year (2025)
# off its ceiling: 3345 -> 3373 quotes, £74,356.09 -> £74,990.15, all still inside the window.
# RE-MEASURED 2026-10-20 at 400 founder HOUSEHOLDS (689 supply points; director's ruling 20 Oct
# 17:40): 3373 -> 3250 quotes, £74,990.15 -> £72,262.76, all still inside the window. FEWER quotes
# from a larger book, the opposite of the 10-09 move; which leg of the quote budget binds is not
# yet attributed.
CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG = 3250
CAMPAIGN_SPEND_AT_SHIPPED_CONFIG = 72262.76

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
CAMPAIGN_QUOTES_INSIDE_WINDOW = 3250
CAMPAIGN_SPEND_INSIDE_WINDOW = 72262.76
















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


@pytest.fixture(scope="module")
def shared_fabric_traces():
    """The two runs below settle the same book over the same window and neither touches the
    physics, so the second reuses the first's traces -- `fdp.sharing_traces`. The mutation leg's
    patched `campaign_acquisition_spend_events` feeds spend, not households or weather."""
    from simulation import fabric_demand_path as fdp

    with fdp.sharing_traces():
        yield


def test_c_the_booked_spend_REACHES_THE_RUN_and_therefore_the_P_AND_L(
    shipped_supply_book, shared_fabric_traces
):
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
    # TO THE PENNY, not exact: the statement sums unrounded floats, and at the 400-founder book the
    # summation order gave 4500.2699999999995 against 4500.27 (2026-10-09).
    assert round(statement["acquisition_spend_gbp"], 2) == spent, (
        "the campaign's spend events reached the run and not the income statement"
    )
    assert round(statement["total_operating_costs_gbp"], 2) >= spent




# ── THE CEILING IS A CONSEQUENCE OF THE MEASURED CURVE, AND CAN STOP BEING ONE ─────────────────
#
# WHAT THESE GUARD, stated as a property so they do not rot into a pin on today's answer.
# `SETTLEMENT_CUSTOMER_YEAR_BUDGET` moved off its historical 1,200 on 2026-09-22 and became a
# consequence of `settlement_ceiling_slope_20260921.json` priced against the LIVE guest. The claim
# that can go false is not "the constant is 1,263" -- it is "the constant does not outrun the
# memory the box can actually find for it". So the assertion is an INEQUALITY in one direction
# only. A future invocation lowering the value, or a curve re-measured more honestly in the safe
# direction, must not red these; raising the value past the evidence, or shrinking the guest under
# it, must.

#: NO ANCHOR LITERAL LIVES HERE ANY MORE, and its deletion is the point. Until 2026-09-22 this
#: file carried `CGROUP_PEAK_MB_AT_THE_ANCHOR = 5734.4` and `CGROUP_PEAK_ANCHOR_CUSTOMER_YEARS =
#: 1200.0` -- the cgroup correction, hand-copied into the control because
#: `load_whole_run_rss_curve` did not apply it and still returned the probe's single-child
#: `ru_maxrss`. That made the test right about the world and the loader wrong about it, with the
#: site publishing the loader's number: a control agreeing with a corrected copy of a quantity
#: whose one home was uncorrected. The loader now anchors on the cgroup, so the anchor is READ
#: OFF THE CURVE below and the two cannot drift apart by hand.


def _memory_ceiling_customer_years(*, total_mb=None, anchor_peak_mb=None):
    """The memory ceiling in customer-years, from the landed curve and a guest size.

    Imported inside the function on purpose: `premise_population` is a heavy sim module and this
    file's other 60-odd tests have no business paying for it at collection time.
    """
    from simulation.premise_population import load_whole_run_rss_curve

    curve = load_whole_run_rss_curve()
    share = curve.get("share_of_guest_the_run_may_hold")
    assert share, (
        "the landed curve records no share of the guest a run may hold, so no memory ceiling "
        "can be priced from it -- and inventing one here is the defect this control exists over"
    )
    if total_mb is None:
        from background.resource_headroom import sample

        total_mb = sample()["total_mb"]
        assert total_mb, "/proc/meminfo gave no MemTotal, so the share is a share of nothing"
    slope = float(curve["mb_per_customer_year"])
    assert slope > 0, f"a non-positive slope ({slope} MB/cy) would make the book unbounded"
    budget_mb = float(total_mb) * float(share)
    # THE ANCHOR IS THE CURVE'S, BOTH COORDINATES. Taking the y from the curve and the x from a
    # literal here is how the two came to disagree by 3.0 customer-years in the first place --
    # the probe committed 1,197.0 at a budget of 1,200 and only the committed figure is a
    # measurement. `anchor_peak_mb` overrides the y so the journal leg below can re-price the
    # same line on today's peak; there is no override for the x because there is no second
    # instrument for it.
    anchor = float(curve["anchor_peak_rss_mb"]) if anchor_peak_mb is None else float(anchor_peak_mb)
    assert float(curve["production_parent_rss_mb"]) > 0, (
        "the curve reports no production parent, so its anchor is the probe's single child "
        "again and this control is back to comparing the constant against a bound the run "
        "cannot hold -- the defect repaired on 2026-09-22"
    )
    return float(curve["anchor_customer_years"]) + (budget_mb - anchor) / slope




_RUN_STARTED = re.compile(r"Starting run — git=(?P<sha>[0-9a-f]{7,40})")
_RUN_PROCESS_PEAK = re.compile(r"Run largest process peak — git=[0-9a-f]{7,40}, (?P<mb>[0-9.]+) MB")


def _peaks_by_the_code_they_ran(journal_text, unit):
    """`(closed, current)` from one journal read: `closed` is `[(peak_mb, shas)]`, one per
    `Run largest process peak` line sim_runner writes after each completed run, `shas` every run
    the unit lifetime had started by then; `current` is the shas started since the last line.

    THE PEAK IS THE RUN'S LARGEST PROCESS, NOT THE CGROUP'S (2026-10-12). Since 38f3a565f the
    trace build's forked workers fill whatever memory is free above the floor, so the unit's
    `memory peak` grew to 7.5-8 GB with the run unchanged: it measures the box. The curve prices
    the run's own process. The line is `ru_maxrss`, a maximum over the runner's lifetime, so it is
    attributed to every run the lifetime held and never to its last run; a systemd close starts a
    new lifetime."""
    from background.oom_watch import _CONSUMED

    closed, shas = [], []
    for line in (journal_text or "").splitlines():
        started = _RUN_STARTED.search(line)
        if started:
            shas.append(started.group("sha"))
            continue
        peak = _RUN_PROCESS_PEAK.search(line)
        if peak:
            closed.append((float(peak.group("mb")), tuple(shas)))
            continue
        consumed = _CONSUMED.search(line)
        if consumed and consumed.group("unit") == unit:
            shas = []
    return closed, tuple(shas)


def _peaks_on_the_curves_code(closed, current, live_mb, carries_the_curve):
    """The peaks that are evidence about the curve: a lifetime counts only when it ran at least
    one run and EVERY run it held carried the code the curve was measured on."""
    def eligible(shas):
        return bool(shas) and all(carries_the_curve(sha) for sha in shas)

    peaks = [peak for peak, shas in closed if eligible(shas)]
    if live_mb is not None and eligible(current):
        peaks.append(live_mb)
    return peaks








def _live_total_mb():
    from background.resource_headroom import sample

    total = sample()["total_mb"]
    assert total, "/proc/meminfo gave no MemTotal"
    return float(total)


# ---------------------------------------------------------------------------
# The quote asked BEFORE the win (`first_term_offer_fn`), 2026-10-02
# ---------------------------------------------------------------------------

def _offer_by_position(prospect, in_market):
    """Withholds one prospect in three, quotes the rest dear or cheap by id parity. Positional
    on the prospect id so the three states are fixed by the stream, not by the funnel."""
    n = int("".join(ch for ch in prospect.customer_id if ch.isdigit()) or 0)
    if n % 3 == 0:
        return {"quoted": False, "reason": f"test: withheld {prospect.customer_id}"}
    return {"quoted": True, "price_differential_pct": 0.5 if n % 2 else -0.5}


def _recording_funnel(seen: dict):
    """Wins a quote iff it arrives cheaper than the market; records the position it was read at."""
    def _fn(segment, seed, term_start, credit_bureau, total_amount_gbp,
            price_differential_pct=None):
        seen[seed] = price_differential_pct
        won = price_differential_pct is not None and price_differential_pct < 0
        return _Result(won, 150.0 if won else 60.0, "cooling_off" if won else "application")
    return _fn




