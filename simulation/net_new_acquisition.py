"""NET-NEW ACQUISITION — the book grows because the company won it, or it does not grow.

Atom `PB3_book_growth_as_earned_outcome`. Source ruling:
`docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`
clause 3, verbatim:

    "Growth is gradual and earned. From that start, the book grows through the acquisition
     physics already built — won and lost against the market, not incremented. Churn,
     acquisition cost, and the competitor field are the mechanisms; **a growth curve that
     cannot be lost is not a growth curve.**"

WHAT WAS ALREADY THERE, AND WHY IT IS NOT THIS. Two acquisition paths ship today and neither
can grow a book:

  1. `run_phase2b`'s market replacement fires ONLY inside the churn branch. Every fresh-market
     win is named `f"{billing_account}_{suffix}"` — a successor to an account that just left.
     Wins are therefore identically bounded by losses: the book can be replaced, never grown.
  2. `simulation.population_draw.iter_acquisition_events` yields ACQUISITIONS. The activated
     Profile B trickle (λ=1.0/yr, `docs/design/curriculum/population_draw_activation.json`)
     appends its draw straight onto the supply book. Its own record is headed EARNED, NEVER
     GRANTED and argues the point against the N=200 coverage pool — a fair distinction, and
     not the one clause 3 is making. There is no win/lose step anywhere between that draw and
     the book, so every drawn event becomes a customer with certainty. At the fixed seed it
     realises as two customers over five years, and the company could not have failed to get
     either of them. That is a growth curve that cannot be lost.

THE CHANGE IS ONE STEP, AND IT IS THE STEP THE RULING NAMES. This module yields **prospects** —
homes in the market this year — and nothing else. It does not decide how many are quoted, it
does not decide who wins, and it books no money. A prospect becomes a customer only by
surviving `simulation.acquisition_funnel.run_acquisition_funnel`: the same five stages, the
same per-stage leakage, the same credit bureau and the same statutory cooling-off window that
every replacement win already goes through. Nothing new was invented to make growth happen;
what was missing was a reason for a quote to exist when nobody had churned.

WHY THE COUNT IS NOT A CONSTANT HERE, which is the design decision worth arguing. The obvious
shape is a second λ — "the world offers N prospects a year" — and it is wrong twice. It puts
the growth rate in the world, where the company cannot earn or lose it; and it makes the
number a curriculum value, which is the director's, so the atom would stall exactly where
PB1/PB2 stalled for thirteen days. Instead the world says only WHO is in the market, and the
company decides how many of them it can afford to quote
(`saas.growth_mandate.growth_quote_budget`, injected by `run_phase2b` — never imported
here; see the wall note on `plan_growth_campaign`). The binding constraint there is the Ofgem
minimum capital requirement per account, which this repo already models at £130
(`saas/capital/solvency.py::MCR_FLOOR_GBP_PER_CUSTOMER`, `company/finance/treasury.py::
MCR_PER_ACCOUNT`). So the supplier grows exactly as fast as its balance sheet can capitalise
the accounts it wins — which is the real constraint on a real small supplier, and it is a
company decision made from company-visible numbers.

THE PROSPECT POOL IS A CEILING, NOT A TARGET (R12). `PROSPECTS_PER_YEAR` below bounds how many
homes are in the market for this supplier at all. It is deliberately far above anything the
company can currently afford to quote, so that in every year of the shipped run the BINDING
constraint is the supplier's capital and never this number. If it ever becomes binding the
run says so out loud rather than silently capping growth — see `quote_capacity`.

THE WALL. This module is world-side. It imports `simulation.population_draw` and nothing from
`company/` or `saas/`. A prospect crosses to the company only as a saas-shaped observable
(`SyntheticCustomer.to_customer_dict()`, which omits the hidden `cohort` and `premise` by
construction) and only for prospects the company PAID to quote. The company never sees the
pool it did not quote, never sees who it could have quoted, and cannot count the market. That
is the correct epistemic position: a real supplier knows its own quote log and its own win
rate, and has no register of everyone it failed to reach.

WHAT THIS DELIBERATELY DOES NOT DO. It does not touch the replacement path, the Profile B
trickle, or the static roster — all three keep working exactly as before, and with the growth
mandate off (the default) this module is never called and the run is byte-identical. It also
does not model a competitor's counter-offer: `B4_competitor_field` is PB3's named couple and
is a separate atom. Today the loss side is the funnel's own leakage, which is real but is not
yet a rival supplier taking the customer.
"""
from __future__ import annotations

import datetime as dt
from typing import Iterator, Mapping, Optional

from simulation.population_draw import (
    DEFAULT_BAND_WEIGHTS,
    DEFAULT_COMMODITY_WEIGHTS,
    DEFAULT_SEGMENT_WEIGHTS,
    SyntheticCustomer,
    _draw_one,
    _substream,
    draw_region_for_customer,
    _load_cohort_curriculum,
)

#: Named substream. Isolated from `W2_2_population_draw` so that adding, removing or
#: re-sizing the prospect pool cannot perturb the Profile B trickle's own draw — the
#: activated curriculum's two customers must stay SYN-2021-001 and SYN-2025-001 whatever
#: happens here (C-S2 RNG substream discipline; proven by
#: `test_the_prospect_stream_does_not_perturb_the_profile_B_trickle`).
STREAM_NAME = "PB3_net_new_prospects"

#: How many homes are in the market for THIS supplier in a given year. A CEILING on the
#: world's side, never a growth target (R12) — see the module docstring. Sized so the
#: company's capital is the binding constraint in every year of the shipped run: at the
#: 2016 opening treasury the affordable quote count is in the tens, so 400 leaves the
#: market non-binding by an order of magnitude and `quote_capacity` reports it if that
#: ever stops being true.
PROSPECTS_PER_YEAR = 400

#: ELECTRICITY ONLY, and this is a limitation rather than a modelling choice. The shipped
#: replacement path says the same thing in its own words -- `saas.customers.
#: make_acquired_customer`'s docstring reads *"Electricity only (no gas leg in Phase 8a)"* --
#: and the reason is structural: a gas account's record carries `aq_kwh` and the drawn
#: saas-shaped dict does not, so `run_phase2b.TOTAL_GAS_AQ` raises `KeyError` on the first
#: won gas prospect. That is exactly the follow-on `simulation/live_population.py` flagged at
#: the population draw's own activation -- *"SYN-* dicts and the static CUSTOMERS dicts do
#: not share an identical key set ... downstream entrypoints must be hardened to tolerate the
#: SYN shape BEFORE the flag is flipped on"*. Found by running it, not by reading it.
#:
#: WHY NOT HARDEN IT HERE. Deriving an `aq_kwh` for a won gas account means inventing an
#: annual quantity for a home whose gas consumption nothing has yet modelled, and an invented
#: quantity feeding straight into the run's total gas position is worse than a book that
#: grows on one fuel. The dual-fuel half of net-new growth is real remaining work and it
#: belongs to whoever hardens the SYN shape, not to a default in this file.
ELECTRICITY_ONLY: dict[str, float] = {"electricity": 1.0}

#: DOMESTIC ONLY, for a reason that comes from the price rather than from convenience. The
#: whole growth plan is denominated in Ofgem's Minimum Capital Requirement, and that figure is
#: *"£130 per dual-fuel-equivalent DOMESTIC customer"* (26 July 2023 decision,
#: `docs/market_research/ofgem_licence_readiness.md` §2). An SME account is not priced by it,
#: is not won through the same channel, and carries an acquisition cost this repo already
#: models at 2.7x the domestic one -- so a campaign that quoted SMEs would be spending a
#: domestic capital budget on non-domestic accounts.
#:
#: There is a mechanical reason too and it is the one that surfaced first: `_draw_dwelling`
#: draws a dwelling only for domestic prospects, so a won SME reaches
#: `dwelling_records.build_properties` with no dwelling and no authored roster entry and
#: raises `DwellingNotDrawn`. That guard is correct -- the alternative is the supplier's own
#: modal-band approximation standing in as the world's ground truth (B12) -- and the right
#: answer is not to weaken it but to acquire the segment the plan actually prices.
DOMESTIC_ONLY: dict[str, float] = {"resi": 1.0}

#: Prospect ids are their own namespace. NOT `SYN-` (the trickle's, and those are customers
#: on the supply book) and not `C\\d+_\\d` (the replacement path's successor form). A prospect
#: that is never won must never be confusable with an account, in a log or in a register.
PROSPECT_ID_PREFIX = "PROS"


def iter_prospects(
    year: int,
    *,
    base_seed: int,
    n: int = PROSPECTS_PER_YEAR,
    segment_weights: Optional[Mapping[str, float]] = None,
    commodity_weights: Optional[Mapping[str, float]] = None,
    band_weights: Optional[Mapping[str, float]] = None,
    draw_region: bool = True,
) -> Iterator[SyntheticCustomer]:
    """Yield this year's prospects in date order. A prospect is NOT a customer.

    Deterministic in `(base_seed, year)` and independent per year: re-running 2019 yields
    the same prospects whatever happened in 2018, so a change to the company's spending
    cannot silently change WHO was in the market. That independence is the property that
    makes a win attributable to the company's decision rather than to the draw.

    `acquisition_date` on the yielded record is the date the prospect is IN THE MARKET —
    the day a quote could be issued. It becomes an acquisition date only if the funnel is
    survived, and `run_phase2b` stamps the won account with the funnel's own term start.
    """
    if n <= 0:
        raise ValueError(f"a prospect pool needs at least one home, got {n}")
    from simulation.premise_population import raked_joint

    # Fit the published stock joint ONCE per year-stream, not per prospect: 168 cells of
    # iterative proportional fitting, identical for every home. Same reason
    # `iter_acquisition_events` does it.
    premise_joint = raked_joint()
    region_curriculum = _load_cohort_curriculum() if draw_region else None

    rng = _substream(base_seed, salt=f"{STREAM_NAME}:{year}")
    days_in_year = (dt.date(year, 12, 31) - dt.date(year, 1, 1)).days
    offsets = sorted(rng.randint(0, days_in_year) for _ in range(n))
    for i, offset in enumerate(offsets, start=1):
        in_market = dt.date(year, 1, 1) + dt.timedelta(days=offset)
        pid = f"{PROSPECT_ID_PREFIX}-{year}-{i:04d}"
        region = (
            draw_region_for_customer(pid, base_seed, region_curriculum)
            if draw_region
            else "UNKNOWN_SYNTHETIC"
        )
        yield _draw_one(
            rng,
            customer_id=pid,
            acquisition_date=in_market,
            segment_weights=segment_weights or DEFAULT_SEGMENT_WEIGHTS,
            commodity_weights=commodity_weights or DEFAULT_COMMODITY_WEIGHTS,
            band_weights=band_weights or DEFAULT_BAND_WEIGHTS,
            region=region,
            base_seed=base_seed,
            assign_cohorts=False,
            premise_joint=premise_joint,
        )


def quote_capacity(affordable_quotes: int, pool_size: int = PROSPECTS_PER_YEAR) -> tuple[int, str | None]:
    """How many quotes actually get issued, and a WARNING if the world is the reason.

    Returns `(quotes, market_binding_reason_or_None)`. The second element exists because a
    growth number that is silently capped by a constant in this file would read, on the
    published site, exactly like a supplier that chose not to grow. The two are different
    facts and the run must be able to tell them apart — CLAUDE.md's no-silent-caps rule
    applied to the one number a reader is most likely to draw a conclusion from.
    """
    if affordable_quotes <= pool_size:
        return max(0, affordable_quotes), None
    return pool_size, (
        f"MARKET-BOUND: the company could afford {affordable_quotes} quotes and only "
        f"{pool_size} homes were in the market. Growth this year is limited by "
        f"net_new_acquisition.PROSPECTS_PER_YEAR, NOT by the supplier's capital — raise "
        f"the pool before reading this year's book as a commercial result."
    )


# ═══════════════════════════════════════════════════════════════════════════
# THE CAMPAIGN — turning a budget into a book, one survived funnel at a time
# ═══════════════════════════════════════════════════════════════════════════

#: THE ENGINEERING CEILING, and it is a completely different kind of number from everything
#: else in this module. `saas.growth_mandate.growth_quote_budget` says what the SUPPLIER can
#: afford; this says what THIS MACHINE can settle inside a publish cycle. They are nowhere near
#: each other.
#:
#: SET FROM WALL CLOCK, MEASURED, 2026-08-24 — not from the scale probe any more, and the
#: correction matters. The first value (279) came from AO12's probe dying at 8,145,405
#: HALF-HOURLY settlement records, i.e. 465 customer-years OF HALF-HOURLY METERING. Applying
#: that to a residential book charges profile-class households at the half-hourly rate and
#: over-states their cost. What actually constrains a run is wall clock against the publish
#: cadence, and that was measured directly:
#:
#:     33 accounts (resi + I&C + SME)   3,226,200 settlement periods   8.5 min
#:     49 accounts (residential only)   3,217,400 settlement periods   8.4 min
#:
#: Linear in accounts x half-hours, with no redundancy in it — a cache on the hottest function
#: returned ONE hit in 13,784 calls and changed the elapsed time not at all
#: (docs/design/SETTLEMENT_CEILING_2026-08-24.md). So 600 customer-years is about 7 million
#: periods, roughly 18 minutes, which keeps a full cycle inside half an hour and leaves the
#: publisher its gate. 200 accounts would be ~34 min and would push the cycle past it.
#:
#: A DIAL, and the one most likely to be wrong (R12). Nothing optimises toward it, and the
#: campaign REPORTS when this is what bound the book rather than the balance sheet — because a
#: growth curve flattened by our wall clock reads, on the published site, exactly like a
#: supplier that ran out of money, and those are not the same fact. The director's instruction
#: was to surface exactly this: "a growth curve that's an artefact of our engine is an
#: inconsistency, not a result."
SETTLEMENT_CUSTOMER_YEAR_BUDGET = 600.0


def _customer_years(win_date: dt.date, horizon_end: dt.date) -> float:
    """Settlement cost of one won account, in customer-years, from its win to the horizon."""
    return max(0.0, (horizon_end - win_date).days / 365.25)


def plan_growth_campaign(
    years,
    *,
    base_seed: int,
    opening_net_assets_gbp: float,
    accounts_held_at_start: int,
    horizon_end: dt.date,
    credit_bureau,
    cost_per_quote_gbp: Mapping[str, float],
    run_funnel,
    quote_budget_fn,
    customer_year_budget: float | None = None,
    customer_years_already_committed: float = 0.0,
    prospects_per_year: int = PROSPECTS_PER_YEAR,
    commodity_weights: Optional[Mapping[str, float]] = None,
    segment_weights: Optional[Mapping[str, float]] = None,
) -> dict:
    """Resolve a multi-year acquisition campaign into won accounts and booked spend.

    EX ANTE PLAN, EX POST BOOK. Each year the company sets a quote budget from the capital
    it actually holds (`saas.growth_mandate.growth_quote_budget`, passed in as the caller's
    own decision so this module never imports company accounting). Those quotes are then
    issued to that year's prospects and resolved ONE AT A TIME through `run_funnel` -- the
    same five-stage funnel, the same credit bureau and the same statutory cooling-off window
    every replacement win already goes through. A year in which every quote fails is a legal
    outcome and produces no growth, which is the property the ruling asked for.

    WHY THE FUNNEL RUNS HERE AND NOT DURING SETTLEMENT. `run_phase2b` builds every renewal
    schedule before its term loop begins, so an account that appears mid-loop has no
    schedule. Resolving the campaign first means winners can be added to the book BEFORE
    schedules are built, which is the same shape the successor path already uses
    (pre-generate, then activate only what was actually won). It costs nothing epistemically:
    the funnel's outcome is seeded on the prospect's own id and date, so no information from
    later in the run reaches this decision, and the company's budget uses only the balance
    sheet it holds at the time.

    `run_funnel(segment, seed, term_start, credit_bureau, total_amount_gbp)` is injected
    rather than imported so a test can drive an always-win and an always-lose bureau without
    reaching into the funnel's internals.

    THE WALL, and this is the one place this module could have breached it. An earlier draft
    called `saas.growth_mandate.growth_quote_budget` directly from here -- a SIM module
    reaching into the supplier's own management accounts to find out what it can afford. That
    is precisely the crossing `run_acquisition_funnel` removed from itself in KNIFE pass 3
    (design `B6_cpa_is_company_accounting`), and for the same reason: what a supplier can
    afford to spend is company accounting, and the world has no view of it and no business
    deciding it. So `quote_budget_fn(net_assets_gbp, accounts_held) -> plan` ARRIVES as an
    injected callable, exactly like `run_funnel` and `cost_per_quote_gbp`. `run_phase2b` is
    the orchestrator and is the layer permitted to hold both sides; nothing under
    `simulation/` imports `saas.*` to make this work.

    Returns a dict with `winners` (SyntheticCustomer, win_date) pairs, `spend` (one row per
    quote, won or lost), `by_year` rows carrying the binding reason, and `notes` -- any year
    where the ENGINEERING budget rather than the company's capital was what stopped it.
    """
    # READ AT CALL TIME, not bound as a default argument. `customer_year_budget: float =
    # SETTLEMENT_CUSTOMER_YEAR_BUDGET` evaluates the module constant when the FUNCTION IS
    # DEFINED, so `monkeypatch.setattr(module, "SETTLEMENT_CUSTOMER_YEAR_BUDGET", x)` -- and
    # every measurement run that tried it -- silently did nothing. Found by running a
    # deliberate 3,000-customer-year sweep and watching it stop at 279 anyway. A constant that
    # cannot be moved is a constant nobody can measure the sensitivity of, which is most of
    # what a dial is for.
    if customer_year_budget is None:
        customer_year_budget = SETTLEMENT_CUSTOMER_YEAR_BUDGET

    winners: list[tuple[SyntheticCustomer, dt.date]] = []
    spend: list[dict] = []
    by_year: list[dict] = []
    notes: list[str] = []

    net_assets = float(opening_net_assets_gbp)
    accounts = int(accounts_held_at_start)
    committed_cy = float(customer_years_already_committed)

    for year in years:
        plan = quote_budget_fn(net_assets_gbp=net_assets, accounts_held=accounts)
        quotes, market_note = quote_capacity(plan["quotes"], prospects_per_year)
        if market_note:
            notes.append(f"{year}: {market_note}")

        binding = plan["binding"]
        won_this_year = 0
        spent_this_year = 0.0
        cy_exhausted_at = None

        if quotes:
            pool = iter_prospects(
                year, base_seed=base_seed, n=prospects_per_year,
                commodity_weights=commodity_weights or ELECTRICITY_ONLY,
                segment_weights=segment_weights or DOMESTIC_ONLY,
            )
            for i, prospect in enumerate(pool):
                if i >= quotes:
                    break
                segment = prospect.segment
                cost = cost_per_quote_gbp.get(segment, cost_per_quote_gbp["resi"])
                in_market = dt.date.fromisoformat(prospect.acquisition_date)
                result = run_funnel(
                    segment,
                    f"prospect_{prospect.customer_id}",
                    in_market,
                    credit_bureau,
                    total_amount_gbp=cost,
                )
                spent_this_year += result.total_cost_gbp
                spend.append({
                    "prospect_id": prospect.customer_id,
                    "event_date": prospect.acquisition_date,
                    "segment": segment,
                    "won": result.won,
                    "amount_gbp": result.total_cost_gbp,
                    "stage_reached": result.stage_reached,
                })
                if not result.won:
                    continue
                # THE ENGINEERING CAP BITES ON THE WIN, not on the quote. A quote the
                # company paid for is spent money whatever we can settle, and suppressing
                # it would silently understate acquisition cost -- the one number a reader
                # would use to judge whether growth was worth it. What we cannot afford is
                # SETTLING the account, so the win is recorded as spend and refused a place
                # on the book, loudly.
                cost_cy = _customer_years(in_market, horizon_end)
                if committed_cy + cost_cy > customer_year_budget:
                    if cy_exhausted_at is None:
                        cy_exhausted_at = prospect.customer_id
                        binding = "settlement_engine"
                    continue
                committed_cy += cost_cy
                winners.append((prospect, in_market))
                accounts += 1
                won_this_year += 1

        net_assets -= spent_this_year
        by_year.append({
            "year": year,
            "quotes_issued": quotes,
            "quotes_affordable": plan["quotes"],
            "wins": won_this_year,
            "spend_gbp": round(spent_this_year, 2),
            "accounts_after": accounts,
            "capital_headroom_gbp": plan["headroom_gbp"],
            "binding": binding,
            "customer_years_committed": round(committed_cy, 1),
        })
        if cy_exhausted_at is not None:
            notes.append(
                f"{year}: SETTLEMENT-BOUND at {cy_exhausted_at}. The company won accounts "
                f"this run refused to settle -- {customer_year_budget} customer-years is "
                f"THIS MACHINE's budget (60% of the 465 measured in AO12's scale probe), "
                f"not a commercial limit. The book below is smaller than the supplier's "
                f"balance sheet supports."
            )

    return {
        "winners": winners,
        "spend": spend,
        "by_year": by_year,
        "notes": notes,
        "customer_years_committed": round(committed_cy, 1),
        "customer_year_budget": customer_year_budget,
    }
