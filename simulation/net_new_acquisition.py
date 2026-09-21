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
import functools
from typing import Iterator, Mapping, Optional, Sequence

from simulation.population_draw import (
    DEFAULT_BAND_WEIGHTS,
    DEFAULT_COMMODITY_WEIGHTS,
    DEFAULT_SEGMENT_WEIGHTS,
    SyntheticCustomer,
    _draw_one,
    _load_cohort_curriculum,
    _substream,
    draw_region_for_customer,
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
#:
#: THAT CONDITION IS NOW FALSE, 2026-08-29, AND THE SENTENCE ABOVE IS KEPT SO THE FAILURE IS
#: READABLE RATHER THAN TIDIED AWAY. On the same day `accounts` moved onto FUNNEL wins — the
#: second leg of the 2026-08-28 wall fix, see `SETTLEMENT_CUSTOMER_YEAR_BUDGET` — the
#: company's account count stopped being frozen by our settlement ceiling and its quote budget
#: grew with it. It can now afford 861 quotes in 2024 against this pool of 400. Three of the
#: ten shipped years (2020, 2024, 2025) are capped here, so the market is binding rather than
#: non-binding, and by roughly a factor of two rather than an order of magnitude the other way.
#:
#: WHAT WORKED, and it is worth naming on a day spent repairing controls that did not: this
#: constant stated the condition under which it would stop being right, and `quote_capacity`
#: reported the moment it did. Nothing had to be noticed.
#:
#: WHY IT IS NOT SIMPLY RAISED, and the first draft of this note gave the weaker of the two
#: reasons. The weak one: "raise it until the market stops binding" picks a number to preserve
#: a design property rather than from evidence. True, and not the binding objection.
#:
#: THE BINDING ONE IS R13, AND IT MAKES THIS THE DIRECTOR'S. This constant is how many homes
#: are in the market — a property of the WORLD, and raising it makes the world easier to grow
#: in. That is a difficulty change, and R13 is explicit that difficulty changes are named,
#: versioned, director-authored artefacts. **And the trigger here is a COMPANY OUTCOME** — the
#: pool started binding because the supplier got richer and could afford more quotes — which is
#: precisely the case R13 names: "never adjusted by the agent in response to company outcomes".
#: An agent that widens the market whenever its company outgrows it is marking its own homework
#: on both sides of the wall. So this stays where it is until he moves it.
#:
#: WHAT HE WOULD NEED, priced, because a reserved decision is owed a menu rather than a flag.
#: The mechanism is one constant: `live_population._year_stock` draws
#: `PROSPECTS_PER_YEAR + TRICKLE_STOCK_RESERVE` and hands the campaign the head, so raising
#: this grows the draw and does NOT take homes off the trickle — the two streams are additive,
#: not zero-sum, and the cost is linear in `draw_premise` calls per year.
#: The EVIDENCE for a level already exists in this repo and is sourced, so this is not a
#: research problem: `docs/market_research/churn_price_elasticity.md` §1 carries the real GB
#: domestic switching VOLUMES year by year, from DESNZ Quarterly Energy Prices Table 2.1 /
#: Energy UK / Ofgem SotM — 4.82m switches in 2016, 6.39m at the 2020 peak, 0.8–1.2m in the
#: 2022 crisis. 400 against ~5m is a 1-in-12,500 sample of the real market, and the honest
#: form of this constant is that ratio stated out loud rather than a bare 400.
#:
#: Until he moves it the three capped years are SURFACED, not silently absorbed: `binding`
#: reports `prospect_ceiling` (distinct from `market`, which is the real switching rate binding
#: a year and must NEVER be raised), the published page labels it "Our prospect pool" with a
#: warning, and `prospect_ceiling_statement` names the years.
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

#: Stock premise ids are NAMESPACED BY YEAR, and the namespace is load-bearing rather than
#: cosmetic. `premise_population.draw_premise_population` mints `P0000..P{n-1}` for every
#: `base_seed` and every `as_of`, so a bare `P0007` names a SLOT and not a dwelling — PB2's
#: `foreign_world` clause exists because two unrelated worlds share that id set entirely. The
#: year-scoped id makes the union below a genuine stock instead of ten overlapping ones, so
#: "the homes this supplier could have won, 2016-2025" is a set that can actually be counted.
STOCK_ID_PREFIX = "PSTK"


#: WHERE THE WORLD'S HOMES COME FROM. `True` draws each home as a whole ROW of the NEED-fitted
#: joint raked onto this world's published marginals (`premise_population.fitted_stock_joint`);
#: `False` is the pre-2026-09-10 path — three attributes from a 144-cell joint, then heating,
#: bedrooms and insulation drawn independently or by lookup, and `has_solar=False` for every home
#: in the country.
#:
#: A CONSTANT AND A PARAMETER, not a hardcoded call, because a population draw is the DIRECTOR'S
#: instrument under R13 and a change to it has to be visible and reversible in one line rather
#: than archaeology. The change itself is BASELINE and its justification is fidelity alone:
#: measured co-occurrence over an independent product, and a floor area the physics needs and the
#: old record did not have. Its effect on company P&L was pre-registered as unknown in sign before
#: it was written and may not be tuned against
#: (`docs/staging/records/SEAT_PREREGISTRATION_WHAT_WIRING_THE_GENERATOR_INTO_THE_WORLDS_STOCK_MOVES_2026-09-10.md`).
STOCK_FROM_FITTED_JOINT = True


def year_premise_stock(
    year: int, *, base_seed: int, n: int = PROSPECTS_PER_YEAR,
    from_fitted_joint: bool | None = None,
) -> tuple:
    """The addressable housing stock in `year` — the homes the campaign quotes INTO.

    PB2's inversion (`PB2_UNWON_REMAINDER_FRAME.md` §1): the SIM draws the STOCK and the
    company's funnel decides which of it becomes a book. What is returned here is world
    truth with no company-side name — a supplier holds no register of the households it
    never approached — so it must never cross `company/interfaces/sim_interface.py`.

    **Drawn PER YEAR, at that year's `as_of`, and that is a fidelity requirement rather
    than an implementation convenience.** `draw_premise` reads `as_of` twice: the meter
    cadence is drawn against `smart_read_share(as_of.year)` and the EPC lodgement is drawn
    uniformly over the ten years before it. One stock drawn once at 2016 would therefore
    model a country in which no meter ever got smarter and no certificate was ever
    re-lodged across the whole decade the run covers — strictly less faithful than the
    per-acquisition draw this replaces, which is the one direction R13 forbids. A year's
    stock is "the homes in the market in that year", which is exactly the object
    `iter_prospects` was already modelling one prospect at a time.

    HONEST SIMPLIFICATION, dated 2026-08-24: a home in the market in 2016 and again in
    2019 appears as two members of the union, because nothing here carries a dwelling's
    identity across years. That is the same simplification `iter_prospects` already made
    (its per-year pools are independent draws) and it is visible in the remainder as a
    slight over-count of distinct homes. Fixing it needs a persistent dwelling register,
    which is a larger object than this atom.

    Deterministic in `(base_seed, year, n)` and independent of everything the company
    does — the property that makes a win attributable to the campaign rather than the draw.
    """
    if n <= 0:
        raise ValueError(f"a premise stock needs at least one home, got {n}")
    from simulation.premise_population import (
        draw_premise,
        draw_premise_from_joint,
        fitted_stock_joint,
        raked_joint,
    )

    use_fitted = STOCK_FROM_FITTED_JOINT if from_fitted_joint is None else from_fitted_joint
    as_of = dt.date(year, 1, 1)
    # The joint is fitted ONCE per year-stream for the same reason the raked one is: it is
    # identical for every home and the fit is not free.
    if use_fitted:
        fitted = fitted_stock_joint()
        draw, kwarg = draw_premise_from_joint, "fitted"
    else:
        fitted = raked_joint()
        draw, kwarg = draw_premise, "joint"
    return tuple(
        draw(
            f"{STOCK_ID_PREFIX}-{year}-{i:04d}",
            base_seed=base_seed,
            as_of=as_of,
            **{kwarg: fitted},
        )
        for i in range(1, n + 1)
    )


def _claim_slot(premise, _customer_id: str):
    """The claim `_draw_one` calls: this prospect's slot, already decided.

    `_draw_one`'s hook takes the customer id because the flat claim in
    `population_draw` needs it for its exhaustion message. A positional claim has
    already resolved the slot before the hook is built, so the id is unused here —
    named with a leading underscore rather than dropped, because a hook whose
    signature quietly diverges from its one interface is how the next caller breaks.
    """
    return premise


def iter_prospects(
    year: int,
    *,
    base_seed: int,
    n: int = PROSPECTS_PER_YEAR,
    segment_weights: Optional[Mapping[str, float]] = None,
    commodity_weights: Optional[Mapping[str, float]] = None,
    band_weights: Optional[Mapping[str, float]] = None,
    draw_region: bool = True,
    premise_stock: Optional[Sequence] = None,
) -> Iterator[SyntheticCustomer]:
    """Yield this year's prospects in date order. A prospect is NOT a customer.

    Deterministic in `(base_seed, year)` and independent per year: re-running 2019 yields
    the same prospects whatever happened in 2018, so a change to the company's spending
    cannot silently change WHO was in the market. That independence is the property that
    makes a win attributable to the company's decision rather than to the draw.

    `acquisition_date` on the yielded record is the date the prospect is IN THE MARKET —
    the day a quote could be issued. It becomes an acquisition date only if the funnel is
    survived, and `run_phase2b` stamps the won account with the funnel's own term start.

    `premise_stock` (default None — PB2 step 3, the inversion). Supplied, prospect `i` is a
    home AT `premise_stock[i - 1]`: it is drawn OUT OF the world's stock rather than having
    a dwelling minted for it. Default None keeps the per-prospect mint and therefore a
    byte-identical stream, so the parameter is additive.

    **POSITIONAL, deliberately, and not shuffled.** Stock members are exchangeable — each
    is an independent draw from the same raked joint, keyed on its own premise id — so
    slot `i` is already a uniform sample and a shuffle would buy nothing. It would cost
    something real: `PB2_JOIN_KEY_BUILD.md` §5 recorded that the trickle's claim shuffle is
    seeded on the stock SIZE, so growing the stock re-rolls which premises were won. A
    positional claim into a per-year slice has no such term. Prospect `PROS-2019-0007` sits
    at `PSTK-2019-0007` however large the pool gets and whatever the company spent, which
    is the membership stability that §5 said step 3 was expected to deliver.

    Exhaustion RAISES rather than truncating. A pool silently shortened to fit its stock
    has its size set by the wrong thing and would still pass every subset control.
    """
    if n <= 0:
        raise ValueError(f"a prospect pool needs at least one home, got {n}")
    if premise_stock is not None and len(premise_stock) < n:
        raise ValueError(
            f"premise stock exhausted for {year}: a pool of {n} homes wants {n} stock "
            f"members and was given {len(premise_stock)}. A market cannot be larger than "
            f"the world it is drawn from -- raise the stock, never truncate the pool."
        )
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
        # C-S2: the claim reads a pre-drawn sequence and never touches `rng`, so switching
        # the stock on cannot perturb the prospect draw itself. Segment, commodity, band,
        # EAC, payment method and the in-market date are all byte-identical with and
        # without a stock; the funnel is seeded on the prospect's own id, so THE SAME
        # PROSPECTS WIN either way. What changes is the house each of them lives in.
        claim = None
        if premise_stock is not None:
            claim = functools.partial(_claim_slot, premise_stock[i - 1])
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
            claim_premise=claim,
        )


def homes_in_market(year: int, prospects_per_year: int = PROSPECTS_PER_YEAR,
                    multiplier: float | None = None) -> tuple[int, float]:
    """How many homes are actually in play in `year`, and the multiplier that set it.

    PB3's ADD path (2026-08-24). Until now the in-play pool was `PROSPECTS_PER_YEAR`, a flat
    engineering constant, so the market was equally open every year from 2016 to 2025. It was
    not: `market_switching_propensity` already carries the real, DESNZ-calibrated answer, and
    the LOSS side has been using it since it was built. 2016 is peak competition at ~2.2x the
    2024 normal; 2022 is the crisis at ~0.4x, when switching very nearly stopped.

    THE SAME CONSTANT ON BOTH LEGS, which is the point and is the director's anti-goal-seek
    guard (2026-08-17, registered in this atom's simplifications file BEFORE the build). Churn
    reads this multiplier in `customer_events`; acquisition now reads it here. A parameter
    change that opens the market to win more customers opens it equally for the ones already
    on the book, so R12 goal-seeking on book size is structurally unavailable rather than
    merely forbidden. That guarantee is a property of the SHARING, and anything that later
    splits the legs owes a replacement -- see this atom's simplification entry, which says so.

    IT CAN ONLY THIN, NEVER WIDEN, and this cap is load-bearing rather than defensive. The
    prospects are drawn `iter_prospects(year, n=prospects_per_year)` out of a stock partition
    PB2 splits with the Profile-B trickle -- the campaign takes the head, the trickle the tail.
    Letting a 2.17x year ask for 869 homes out of a 400-home partition does not produce 869
    prospects; it produces 400 and a `quotes_issued` of 869 that claims quotes the run never
    issued and never billed. Measured before the cap: 2016 reported 600 quotes and 400 wins on
    an always-win funnel, which is the same defect one step downstream.

    SO THE SIMPLIFICATION IS NAMED, not silent (registered in this atom's simplifications
    file): above 1.0 the multiplier is inert, and in a peak-competition year this model
    UNDERSTATES how open the market was. Closing it means widening the stock partition itself,
    which is PB2's boundary with the trickle and not a number to change from here.

    `multiplier` is injectable for tests only; the default is the real year-keyed series.
    """
    if multiplier is None:
        from simulation.market_switching_propensity import market_switching_multiplier
        multiplier = market_switching_multiplier(year)
    in_play = min(prospects_per_year, int(round(prospects_per_year * multiplier)))
    return max(0, in_play), float(multiplier)


def quote_capacity(affordable_quotes: int, pool_size: int = PROSPECTS_PER_YEAR,
                   *, engineering_ceiling: int | None = None) -> tuple[int, str | None]:
    """How many quotes actually get issued, and a WARNING if the world is the reason.

    Returns `(quotes, market_binding_reason_or_None)`. The second element exists because a
    growth number that is silently capped by a constant in this file would read, on the
    published site, exactly like a supplier that chose not to grow. The two are different
    facts and the run must be able to tell them apart — CLAUDE.md's no-silent-caps rule
    applied to the one number a reader is most likely to draw a conclusion from.

    `engineering_ceiling` SPLITS that warning in two, because since PB3 wired the real
    switching series into the pool there are two different reasons a year can be capped and
    they carry opposite instructions. Hitting OUR constant is an artefact and the reader
    should raise it. Being capped because 2022 was a crisis in which almost nobody switched
    supplier is a genuine commercial result and raising anything would be falsifying it. The
    old message said "raise the pool" unconditionally; on a market-bound year that is now
    exactly the wrong advice, so the two are worded apart.
    """
    ceiling = pool_size if engineering_ceiling is None else engineering_ceiling
    if affordable_quotes <= pool_size:
        return max(0, affordable_quotes), None
    if pool_size < ceiling:
        return pool_size, (
            f"MARKET-THIN: the company could afford {affordable_quotes} quotes and only "
            f"{pool_size} homes were in the market, against an engineering ceiling of "
            f"{ceiling}. The binding constraint is the REAL switching rate for this year, "
            f"not a constant in this file — this year's book IS a commercial result, and "
            f"raising the pool would falsify it."
        )
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
#:
#: RAISED 600 -> 1200, 2026-08-24, ON A MEASUREMENT RATHER THAN A HOPE. The daily settlement
#: fold (simulation/settlement_daily.py) changed both constraints this number was set from, so
#: the full 2016-2025 horizon was re-measured with the fold live:
#:
#:     at  600:  elapsed 433.8s (7.2 min)   peak RSS 2,011 MB    454.4 customer-years
#:     at 1200:  elapsed 746.8s (12.4 min)  peak RSS 3,117 MB    796.1 customer-years
#:
#: Both rows are MEASURED, not the second extrapolated from the first — and the extrapolation
#: would have been wrong in the pessimistic direction: cost per customer-year FELL from 4.43 MB
#: to 3.91 as the book grew, so the straight line through the first row (~19 min, ~5.3 GB) is
#: not what the raise actually costs. 12.4 minutes leaves seventeen for the publisher's gate
#: inside the half-hour cycle, which is the SAME design point the 600 was chosen for and in
#: fact better than the ~18 minutes the old budget cost pre-fold for a third of the book. The
#: memory figure is 4.5x better than the 14.2 GB the box was surviving (badly: ten OOM kills)
#: before the fold. So this spends part of what the fold bought and deliberately not all of it:
#: the headroom is a budget, not a solved problem, and 1,200 leaves the larger half unspent.
#:
#: WHY IT MOVES AT ALL, which is the director's instruction of 2026-08-24: "200 residential
#: earned through the funnel, now the fold has bought the room." A book growing from ~13 to 200
#: over the ten-year window is roughly 1,060 customer-years, which 600 cannot hold and 1,200
#: can. This is an ENGINEERING ceiling — what this machine can settle in a cycle — and not an
#: R13 curriculum value: it does not decide how hard the world is, only how much of the world
#: this box can afford to settle.
#:
#: THE RULING OF 2026-08-28, on "does the campaign keep paying for quotes after the budget can
#: no longer convert them -- company defect, or fidelity?" (BLOCKING finding
#: WORKER_FINDING_THE_FOUNDER_BOOK_EXPOSES_A_CAMPAIGN_THAT_KEEPS_QUOTING_AFTER_THE_BUDGET_STOPS).
#: **NEITHER. The question was malformed and the run could not answer it as posed.** Measured
#: at the director's 80-founder book against the 13-founder one, one variable at a time:
#:
#:                          founders 13    founders 80
#:     quotes paid for            1,066          2,089
#:     wins the FUNNEL gave         200            380
#:     wins BOOKED                  200             45
#:     wins refused by THIS BUDGET    0            335
#:     funnel conversion           18.8%          18.2%
#:
#: The company's commercial behaviour is unchanged: it converts at the same rate on a book six
#: times deeper. 335 of the 380 wins (88%) were not lost in the market -- they were won and then
#: refused a place on the book by the line below, which is an engineering ceiling and does not
#: exist in the modelled world. There was never a supplier marketing past its capacity to rule
#: on. Dividing quotes by BOOKED wins mixes a commercial class with a harness one and reports
#: the machine's limit as the company's judgement.
#:
#: WHAT WAS A DEFECT is a WALL breach, not a commercial one, and it is fixed at
#: `wins_to_date` below: this ceiling was being fed back into the company's own planner, which
#: drove its `realised_win_rate` to 1.7% and its quote budget to 2,000, so it bought 2,826
#: quotes (£62,812) to book 45 accounts. On the funnel's own record it buys 2,089 (£46,408) --
#: so £16,404 of the campaign's spend was this constant reaching into the company's books. At
#: 13 founders the fix changes NOTHING (1,066/200/200, byte-identical), because nothing is
#: refused there; that null result is what shows it is aimed at the artefact and not the answer.
#: RE-MEASURED 2026-08-29 AND DELIBERATELY NOT MOVED — `docs/design/SETTLEMENT_CEILING_REMEASURED_
#: _2026-08-29.md`, artefact `docs/observability/settlement_ceiling_probe.json`, instrument
#: `tools/settlement_ceiling_probe.py`. Three things came back and none of them is a new value.
#:
#: 1. THE COST ABOVE IS 36% LOW AND 35% LIGHT. At this same 1,200, measured on the live path's
#:    own compute this week: 1,018.7s and 4,193 MB, against the 746.8s and 3,117 MB recorded
#:    above. Nothing regressed. The August figure was taken while this ceiling was SLACK — the
#:    campaign committed 796.1 of its 1,200 — and the founder book made it TAUT, so the same
#:    constant now buys 1,199.9 customer-years and costs what 1,200 always would have. A cost
#:    note taken at a budget the run never reached is a note about a different run.
#:
#: 2. THE TIME ARGUMENT ABOVE IS CIRCULAR AND SHOULD NOT BE REPEATED. "12.4 minutes leaves
#:    seventeen for the publisher's gate inside the half-hour cycle" reasons against
#:    `suite_duration_watch.PUBLISH_CADENCE_SECONDS`, which is 1,500s and not 1,800s, and which
#:    that module's own comment defines as "a measurement of how often runs actually arrive".
#:    Run duration sets marker inter-arrival, so raising this ceiling raises the cadence that is
#:    supposed to bound it — and lengthening the run also widens the interval `absolute_band()`
#:    checks the gate's speed against, so it buys silence from that alarm too. MEMORY against
#:    the guest is the only bound here that is evidence; a time bound has to be a publish
#:    interval somebody CHOSE and named.
#:
#:    WHAT THAT LEAVES, TAKEN TO ITS CONCLUSION 2026-08-29 (director: "it needs a non-circular
#:    basis, not a bigger number"). Both legs were then looked at, and NEITHER of them sets
#:    1,200:
#:
#:      MEMORY — measured, non-circular, and SLACK BY 4.5x. The clean 1,200 point peaks at
#:        4,193 MB against a guest holding 24,032 MB with 19,009 MB available
#:        (`background.resource_headroom.sample()`, 2026-08-29T06:16Z — read it, never quote
#:        it). This bound is real evidence precisely because it cannot be gamed by the run:
#:        a slower run does not make the box bigger. It is also nowhere near binding, so it
#:        is not what this number came from.
#:      TIME — the binding leg, and it has NO VALID BASIS TODAY. It needs a publish interval
#:        somebody chose and named in a file a reader can disagree with. There is no such
#:        artefact, and inventing one to fill the slot is the exact move this file's own rules
#:        forbid. The non-circular candidate, when it is taken up, is an EXTERNAL anchor —
#:        how often the inputs this site reports actually change — because that is a fact
#:        about Elexon and NESO rather than about how long our own run takes.
#:
#:    SO 1,200 STANDS ON NO CURRENT EVIDENCE, and this comment says so rather than dressing it.
#:    It is a historical number that survived because nothing forced the question.
#:    [2026-09-22: true when written, and it stopped being the value on that date. The question
#:    was forced, MEMORY turned out to be the binding leg and not TIME, and the reasoning below
#:    this line supersedes the two legs above it. Read to the end before quoting any of it.]
#:
#:    WHAT MAKES THAT SURVIVABLE IS THE ALLOCATION FIX OF THE SAME DAY, and this is the reason
#:    the ceiling was not moved instead. Until 2026-08-29 this constant decided WHICH YEARS
#:    EXISTED: spent first-come on a cohort whose settlement tails cost 9.83 customer-years
#:    each, it was exhausted inside 2017 and booked zero in all eight later years, so its exact
#:    value was decisive and every downstream comparison inherited the cliff. It now sets a
#:    uniform SAMPLE RATE over the campaign's own wins, so every year is represented in
#:    proportion to what it won and getting this number wrong costs the book's precision rather
#:    than its coverage. A constant with no basis is a defect either way — but it is a defect
#:    that can now wait for a real answer instead of forcing an invented one.
#:    `docs/design/SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md`.
#:
#: 3. THE SECOND POINT WAS CONTAMINATED AND THE PROBE NOW SAYS SO — and that run has since been
#:    taken (`settlement_ceiling_slope_20260921.json`, landed c4bee75e3). "I cannot yet say" was
#:    the result for three weeks and is no longer; what replaced it is §"WHERE 1,263 COMES FROM"
#:    below. The contamination did not go away, it was routed around: points 2 and 3 contribute
#:    their `customer_year_budget_seen` and `peak_rss_mb`, which are the probe's own, and never
#:    their `customer_years_committed`, which another writer's `book_growth_campaign.json` is in.
#:
#: ── WHAT THIS IS A BUDGET OF, 2026-08-29 ────────────────────────────────────────────────────
#:
#: The director's ask was for one sentence a reader can check, and this is it:
#:
#:   SETTLEMENT_CUSTOMER_YEAR_BUDGET is how many customer-years of settlement this box folds
#:   inside one publish cycle — bounded above by the guest's memory, and by the run's wall
#:   clock against a publish interval WE CHOOSE.
#:
#: Every clause is checkable. The unit is customer-years (`_customer_years` below). The memory
#: bound is `background.resource_headroom.sample()["total_mb"]` against the probe's measured
#: peak RSS. The time bound is the run's wall clock against an interval — and the last three
#: words are the whole repair, because the interval used to be measured.
#:
#: THE CIRCULARITY IS BROKEN, AND THIS IS WHAT BROKE IT. The old bound was
#: `suite_duration_watch.PUBLISH_CADENCE_SECONDS`, which its own comment defines as "a
#: measurement of how often runs actually arrive". Run duration sets marker inter-arrival, so
#: raising this ceiling raised the bound it was checked against, in the flattering direction.
#: Breaking that needs a requirement fixed INDEPENDENTLY of the arrival rate. §7 of
#: `SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md` named the candidate — how often the inputs this
#: site reports actually change, a fact about Elexon and NESO rather than about our own run —
#: and it was then taken up rather than left as a plan:
#:
#:   `run_phase2b.REPORT_END` is 2025-06-07. `settlement_timetable.RF_MONTHS` is 14, verified
#:   against an Elexon-authored primary document. 2025-06-07 + 14 months = 2026-08-07, so the
#:   reported window reached Final Reconciliation three weeks ago and NO new settlement data
#:   can revise a figure inside it.
#:   (`docs/market_research/elexon_settlement_run_timetable_verified.md`, committed 703e4dbb7.)
#:
#: **The external data-freshness requirement is ZERO, and a requirement of zero is exactly what
#: a non-circular bound looks like: it does not move when this ceiling moves.** That is the
#: break, and it is a stronger answer than the one the direction anticipated.
#:
#: WHAT IT LEAVES, SAID RATHER THAN DRESSED. With the external requirement at zero, the publish
#: interval is not derivable from evidence AT ALL. It is a preference about how quickly our own
#: changes become visible — the director's to name, a decision and not a measurement. Locating
#: it correctly is the result; inventing an interval and calling it a basis is the move this
#: file's own rules forbid, and it would be harder to undo than the circular argument was,
#: because it would arrive with a justification attached.
#:
#: THE ASYMMETRY THAT FALLS OUT OF IT, and it is the uncomfortable half. Memory is now the only
#: leg with evidence behind it, and memory is SLACK BY 4.5x (4,193 MB peak against a 24,032 MB
#: guest). So on today's evidence nothing bounds this constant at 1,200 except an interval
#: preference nobody has stated. 1,200 remains a historical number, and this note still says so.
#:
#: ── THE INTERVAL HAS BEEN STATED SINCE 2026-09-04, AND THIS NOTE MISSED IT FOR 17 DAYS ──────
#:
#: CORRECTED 2026-09-21, beside the claim rather than over it. The paragraph above ends "an
#: interval preference nobody has stated", and that was true when written and went FALSE six
#: days later. The director named it, verbatim, in `background/publish_freshness.py`:
#:
#:   *"The site publishes numbers and runs once a week, thoroughly and robustly, not every half
#:   hour ... The reason is cost."* — director, 2026-09-04
#:   `publish_freshness.PUBLISH_CADENCE_SECONDS = 7 * 24 * 60 * 60` (604,800s), and that module
#:   declares itself "the SINGLE SOURCE OF TRUTH for that cadence".
#:
#: THE REASONING ABOVE WAS RIGHT AND IS WHY THIS IS A CONFIRMATION, NOT A RETRACTION. It located
#: the interval as the director's to name rather than inventing one; he then named it. What
#: failed is that nothing connected the two — the sentence sat here asserting the decision was
#: outstanding while the decision was in the tree, and every reader of this constant since has
#: been told the ceiling waits on something it does not.
#:
#: AND THE PROBE STILL PRICES THE CEILING ON THE CIRCULAR RULER. `settlement_ceiling_probe`'s
#: `publisher_context()` reads `cadence_seconds` out of `publish_gate_duration.jsonl`, which
#: `suite_duration_watch` stamps from ITS `PUBLISH_CADENCE_SECONDS` — 5,400s, and its own comment
#: still says "it is a measurement of how often runs actually arrive". That is the exact constant
#: the paragraphs above record as removed for circularity, reached by a second route nobody
#: re-asked. The two live cadences differ by 112x. The probe was built for this: `recommend()`
#: takes a CHOSEN `publish_interval_s` and flags `chosen: false` when it falls back — and nobody
#: had ever passed one, so every reading it has produced carries the circular bound.
#:
#: SO THE ARITHMETIC MOVES, BUT THE NUMBER DOES NOT MOVE HERE YET, and the distinction is the
#: whole point. A stated interval is not a ceiling; a cost curve turns it into one, and the curve
#: is being measured now (`docs/observability/settlement_ceiling_slope_20260921.json`, launched
#: 2026-09-21 against `--publish-interval 604800` on a producer-held box). Writing a new value
#: from the old slope would be the move this file's own rules forbid, with a better-dressed
#: justification than the last one. What can be said before it lands: at a weekly interval the
#: time leg stops being the binding one by orders of magnitude, so the leg that binds becomes
#: memory — and memory re-ruled to the records the book actually retains is ~38,275 customer-
#: years. If that survives the measurement, nothing bounds 1,200 and the constant's own history
#: is all that holds it there.
#:
#: ── THE CURVE LANDED, 2026-09-21T19:49Z, AND IT REFUTES THE PARAGRAPH ABOVE ─────────────────
#:
#: `docs/observability/settlement_ceiling_slope_20260921.json`, four full-window points at
#: `--publish-interval 604800` (the director's stated weekly cadence). **THE PREDICTION DIRECTLY
#: ABOVE — "memory re-ruled is ~38,275 customer-years; if that survives the measurement, nothing
#: bounds 1,200" — DID NOT SURVIVE.** It is kept unedited because a prediction revised after its
#: answer is not one.
#:
#:     budget     committed cy     wall (s)     peak RSS (MB)     clean
#:      1,200        1,197.0        1,499.6         5,507.4        yes
#:      2,000        1,995.2        2,666.5         8,504.7        no
#:      2,800        2,799.3        4,591.5        12,501.8        no
#:      3,400        3,135.5        5,296.0        13,920.9        yes
#:
#: Between the two CLEAN points: **1.958 s and 4.340 MB per marginal customer-year.** The middle
#: two are labelled unclean by the probe itself — another process wrote
#: `book_growth_campaign.json` mid-run, so their x-axis is not their own; their parent-side wall
#: clock and RSS are uncontaminated, and they are reported rather than dropped.
#:
#: 1. **MEMORY IS NOT SLACK BY 4.5x. IT IS SLACK BY 1.09x, AND IT IS WHAT BINDS.** The re-ruled
#:    38,275 came from `premise_population.settled_book_ceiling_customer_years`, which prices two
#:    stage costs from an old scale probe — `settlement_build` and `run_output_serialization` —
#:    at 0.224 MB per customer-year. Measured whole-run cost is **4.340 MB/cy, 19.4x higher**,
#:    because those two stages were never the run's footprint, only one of its data structures.
#:    The 2026-09-21 repair at `c58350e2e` was right to cut the record population from 17,520 to
#:    289.4 and fixed a 59.7x error in the PESSIMISTIC direction; it left one of similar size in
#:    the OPTIMISTIC one, which is the direction that licenses "memory is not what caps this
#:    book". On the probe's 25%-of-guest share memory supports **1,312.3 customer-years**.
#:
#: 2. **THE INTERVAL QUESTION IS ALL BUT MOOT, WHICH NOBODY EXPECTED.** Across the menu the probe
#:    was given — 90 minutes, 24 hours, one week, a factor of 112 — the supported ceiling moves
#:    only from 1,194.6 to 1,312.3, **9.9%**. Time binds at 90 minutes; memory binds at both
#:    longer intervals and caps it at 1,312.3 whatever he chooses. Four weeks of this note
#:    treating the director's interval as the thing standing between us and a bigger book was
#:    reasoning about the wrong leg.
#:
#: 3. **THE PARAGRAPH THAT STOOD HERE SAID "NOT MOVED, and deliberately", AND IT WAS WRONG ON ITS
#:    OWN TERMS. It is kept stated rather than quietly replaced, because the way it was wrong is
#:    the finding.** It read the admissible band as 1,194.6–1,312.3 and declined to spend the
#:    memory headroom. Both ends of that band price the peak RSS of ONE CHILD PROCESS — the
#:    probe's `ru_maxrss` of the `run_annual_report` it spawned. What has to fit this box is the
#:    CGROUP: `sim-runner.service` peaked at **5,734.4 MB** across 8 runs in 24h (systemd's own
#:    `MemoryPeak`, via `resource_headroom.weight_drift("sim_run")`, 2026-09-22) against the
#:    probe's 5,507.4 MB at the same budget. The 227.0 MB difference is the `sim_runner.py` parent
#:    the probe never spawned and the kernel always counts. So 1,312 was never admissible: it puts
#:    the cgroup 227 MB OVER the memory budget it was derived to respect. Declining to move TO an
#:    over-budget number is not caution, it is two errors that happened to point opposite ways.
#:
#: 4. **WHERE 1,250 COMES FROM.** One line, three inputs, all readable:
#:
#:      budget_mb = sample()["total_mb"] × 0.25                      = 6,008.0 MB
#:      ceiling   = 1,200 + (budget_mb − 5,734.4) / 4.3402 MB-per-cy = 1,263.0 customer-years
#:      shipped   = that, floored                                    = 1,250.0 customer-years
#:
#:    **THE FLOOR IS NOT A ROUNDING PREFERENCE, it is the only reason the control over this
#:    number is not sitting on its own boundary.** Shipping 1,263.0 leaves 0.8 MB of MemTotal
#:    between green and red, and MemTotal on this WSL2 guest is not a constant — it is a share of
#:    a Windows host and it moves between restarts, which is why this file's rules say read it and
#:    never quote it. A control that reds because the guest came back 1 MB smaller would name a
#:    file nobody touched and stop every lane. 1,250.0 buys 13.0 customer-years = 56.6 MB of run
#:    RSS = **226.5 MB of guest drift (0.94%)** before the control has anything to say. It is also
#:    the honest precision: the ceiling across the three admissible slope fits spans 1,263.0 (the
#:    landed secant), 1,273.0 (the 1,200→2,000 secant) and 1,287.7 (the quadratic's marginal at
#:    1,200), so a tenth of a customer-year was false precision on a ±2% quantity.
#:
#:    * **The slope is 4.3402 MB per customer-year** — the landed curve's own, and the STEEPEST of
#:      the three the artefact supports (a quadratic fitted to the budget axis gives 3.1217 at
#:      1,200 and the 1,200→2,000 secant 3.7466). Steepest means narrowest ceiling, which is the
#:      direction to take when three fits of one quantity disagree. The budget-axis fit is in the
#:      result doc; it is convex there too, so the wide secant overstates the local slope and
#:      therefore under-states this ceiling. Corroboration, not the basis.
#:    * **Point 4 (budget 3,400) is excluded and this is why:** it refused 0 of 500 funnel wins, so
#:      it is funnel-bound, not budget-bound, and it is not a point about this constant's ceiling
#:      at all. Its RSS is the RSS of the 3,135.5 customer-years the funnel could supply, not of
#:      the 3,400 it was offered — fitting RSS against the offer would flatten the slope.
#:    * **The share is 0.25 of the guest TOTAL, and it is a RECORDED CHOICE, not a measurement.**
#:      It is `--rss-share`'s default in `tools/settlement_ceiling_probe.py`, recorded beside the
#:      curve, and `premise_population.settled_book_ceiling_customer_years` refuses to invent a
#:      fresh one — so using the artefact's keeps the two agreeing instead of arguing. It is the
#:      conservative leg by a wide margin: the admission governor's own budget is
#:      `total_mb − RESERVE_FOR_UNDECLARED_MB` = 23,008.1 MB, **3.83x** larger. Establishing the
#:      share properly would raise this ceiling well past the funnel's supply, at which point §5
#:      binds instead and the question stops mattering. Filed, not fixed here.
#:
#: 5. **WHICH LEG BINDS AT 1,263: MEMORY, and the other two are not close.** Wall clock against
#:    `publish_freshness.PUBLISH_CADENCE_SECONDS` (604,800s, the director's, named 2026-09-04)
#:    allows 22,879 customer-years on the honest convex fit — 18x this ceiling. The funnel's whole
#:    demand is 3,135.5. Memory is the only leg in contact with the number.
#:    **At 1,250.0 the run claims 5,951.4 MB, which is 24.8% of the live guest** (the ceiling's
#:    own 1,263.0 is 6,008.0 MB and 25.0% by construction),
#:    and `resource_headroom.CLASS_WEIGHTS_MB["sim_run"]` at 13,824 MB covers it at 0.43x, so the
#:    declared weight does NOT drift at this value and is not re-declared in this commit. That
#:    13,824 is a stale high-water mark from the 2026-08-24 OOM-kill day, 2.41x what the unit
#:    actually peaks at now — over-declared, therefore fail-CLOSED, therefore not urgent. It is
#:    also why point 4's 13,920.9 MB does not oblige a re-declaration: that peak belongs to a
#:    budget of 3,400 this constant will never be set to.
#:
#: 4. **AND THE WORLD CANNOT SUPPLY THE BOOK THE THESIS NEEDS, CEILING OR NO CEILING.** At 3,400
#:    the campaign refused nothing — 500 funnel wins, 500 booked — so **3,135.6 customer-years is
#:    the campaign's entire demand** and a ceiling above it buys no accounts at all. The smallest
#:    leg of `what_would_settle_the_sign` needs 3,163.9. The world tops out ~28 customer-years
#:    short of it, and 1,312.3 is where this box stops long before that. "This world cannot reach
#:    it" is the complete answer, and it is now measured on both legs rather than asserted.
#:
#: WHAT IS STILL OWED, named so it is not read as closed. **Two live constants both declare
#: themselves the publish cadence and they differ by 112x** — `publish_freshness` at 604,800s
#: (the director's, 2026-09-04) and `suite_duration_watch` at 5,400s, which is what stamps
#: `publish_gate_duration.jsonl` and therefore what the probe falls back to. That is a repo
#: defect and not a director question. Filed:
#: `docs/staging/SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_..._2026-09-21.md`.
#:
#: WHAT IS BEING MEASURED, AND WHY IT IS A CURVE AND NOT A NUMBER. A chosen interval only
#: becomes a ceiling through a cost curve — seconds and MB per marginal customer-year — so the
#: curve is the deliverable and the number is its consequence. `tools/settlement_ceiling_probe.py`
#: takes it; the run this constant is a consequence OF is
#: `docs/observability/settlement_ceiling_slope_20260921.json` (landed c4bee75e3), deliberately
#: NOT `settlement_ceiling_probe.json`, whose 2,000 row is the contaminated one.
#:
#: THE PAGE SAYS ALL OF THIS NOW, which is where it belongs: `engine_bound_basis` in
#: `tools/generate_book_growth_data.py`, rendered at `site/capabilities/`. A reader meets the
#: fact that the height of the growth curve is our compute budget rather than the supplier's
#: commerce. What ceiling that basis supports IS now known and is the value below — the clause
#: here saying it was not is deleted, and the sentence elsewhere in this note calling the publish
#: interval unstated went with it: the director named 604,800s on 2026-09-04. The zero-requirement
#: claim has a control that can fail —
#: `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py::
#: test_the_published_no_freshness_requirement_claim_is_STILL_TRUE` reds if `REPORT_END` is ever
#: extended back inside the reconciliation window, which is the one change that makes the
#: published sentence false and which nothing else in the tree would notice.
#: ORIGIN: derived 2026-09-22 from the measured curve at
#: `docs/observability/settlement_ceiling_slope_20260921.json` (landed c4bee75e3) against the LIVE
#: guest — 0.25 × `resource_headroom.sample()["total_mb"]` = 6,008.0 MB — anchored on the CGROUP
#: peak systemd recorded for `sim-runner.service` (5,734.4 MB at the previous value of 1,200), not
#: on the probe's single-child 5,507.4 MB. That prices 1,263.0; shipped floored to 1,250.0 so the
#: control has 226.5 MB of guest drift in hand rather than 0.8. MEMORY is the binding leg; see
#: §3–§5 above for the
#: arithmetic and for what the paragraph that held this at 1,200 got wrong. The control that can
#: fail is `test_the_settlement_ceiling_does_not_outrun_the_measured_memory_curve`.
SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1250.0


def _customer_years(win_date: dt.date, horizon_end: dt.date) -> float:
    """Settlement cost of one won account, in customer-years, from its win to the horizon."""
    return max(0.0, (horizon_end - win_date).days / 365.25)


def settle_within_budget(
    candidates,
    *,
    committed_cy: float,
    customer_year_budget: float,
):
    """Which of the campaign's wins THIS MACHINE can afford to settle.

    LIFTED OUT OF `plan_growth_campaign` (2026-09-11) so that a selection rule can be measured
    against another one on ONE candidate list. It was inline, and inline it could only be compared
    by running the whole campaign twice -- which puts the seed stream in the comparison and makes
    the result unattributable.

    THE LIFT AND THE CHOOSER WERE WRITTEN ON OPPOSITE SIDES OF THE 09-11 ORIGIN FORK, and this is
    the body the merge that closed it produced. The lift moved the rule without changing it; the
    other side replaced the rule's core with `settlement_choice.choose_settled_sample` while it was
    still inline. Both are here: the chooser runs inside the lifted function, so the reason the
    lift exists (one candidate list, two rules, a measurable difference) is what makes the chooser
    checkable rather than something the merge had to pick between. The controls are
    `tests/simulation/test_the_settled_book_is_chosen_and_weighted_not_culled_by_count.py` --
    `test_all_three_selection_STATES_are_reachable_through_settle_within_budget_and_tellable_apart`
    is the one over the whole partition, and it drives THIS function on one candidate list with
    only the budget varying.

    **THE PREVIOUS SENTENCE HERE WAS FALSE and is kept corrected rather than quietly replaced.**
    It cited `test_both_selections_can_actually_happen_in_the_campaign` as the proof the fallback
    branch is reachable. That test never called this function: it asserted
    `callable(plan_growth_campaign)` and then called `choose_settled_sample` directly. Measured
    2026-09-15 by replacing each fallback path with a `raise`: the HEADROOM route fired 5 tests
    (all of them written about the note or the refused-win counts, none about the selection) and
    the UNPLACEABLE route fired NONE. So the branch this docstring claimed was held had no
    control, and `selection == "uniform_count"` was asserted nowhere in the tree.

    `uniform_count` IS the initialised value and therefore reports THREE different states -- the
    null case where nothing was selected at all, the unplaceable refusal, and the headroom
    refusal. `choice_refusal` is what separates the first from the other two, and the control above
    asserts the three stay tellable apart from this dict alone.

    Returns the selection and everything the caller's rows are filled from. `committed_cy` is
    passed IN rather than read, because the opening book has already charged the same budget.
    """
    campaign_cy = sum(cy for _y, _p, _d, cy in candidates)
    headroom_cy = max(0.0, customer_year_budget - committed_cy)
    # f >= 1 IS THE NULL CASE and it must stay byte-identical to a run with no ceiling at
    # all: nothing refused, no sample, no note. That is the result which shows this change is
    # aimed at the artefact rather than at the answer -- at 13 founders the campaign fits
    # inside the budget and this whole pass is a no-op.
    sample_rate = 1.0 if campaign_cy <= headroom_cy else headroom_cy / campaign_cy

    # ── WHICH WINS, AND WHAT EACH ONE STANDS FOR ──────────────────────────────────────────
    # THE COUNT RULE BELOW IS THE FALLBACK NOW, NOT THE DESIGN. `settlement_choice` picks the
    # sample for DIFFERENCE over the demand axes and solves for the mass each settled account
    # stands for; the systematic cull is what runs when it cannot, and every reason it cannot is
    # named on the note. Measured 2026-09-11, seed 42, two arms at one HEAD with one variable:
    # worst-axis KS against the full candidate population 0.12798 culled against 0.08241 chosen,
    # a factor of 1.553, with every year's weight reconstructing its funnel wins to 0.1%.
    #
    # WHY THE CULL IS KEPT AT ALL rather than deleted: it is the only thing that can settle a book
    # when a candidate has no home to place on the axes, and a run that refused to book anything in
    # that case would make the whole campaign depend on the premise stock being wired.
    #
    # `sample_rate < 1.0` GUARDS THE WHOLE THING, so a campaign that fits inside its budget takes
    # neither path and stays byte-identical to a run with no ceiling at all -- the null property
    # this pass has had since 2026-08-29, and a change aimed at the artefact must be invisible when
    # the artefact is absent.
    chosen = None
    selection = "uniform_count"
    choice_refusal = None
    if sample_rate < 1.0:
        from simulation.settlement_choice import (
            _fuel_of,
            choose_settled_sample,
            demand_vector,
        )
        vectors = [demand_vector(p, cy) for _y, p, _d, cy in candidates]
        unplaceable = sum(v is None for v in vectors)
        if unplaceable:
            choice_refusal = (
                f"{unplaceable} of {len(candidates)} wins carry no home the demand axes can be "
                f"evaluated on, so the sample could not be chosen for difference and was culled "
                f"by count instead"
            )
        else:
            chosen = choose_settled_sample(
                vectors,
                [cy for _y, _p, _d, cy in candidates],
                [_fuel_of(p) for _y, p, _d, _cy in candidates],
                headroom_cy=headroom_cy,
                candidate_years=[y for y, _p, _d, _cy in candidates],
            )
            if chosen is None:
                choice_refusal = (
                    "not even the smallest chosen set fits the customer-year headroom, so the "
                    "sample was culled by count instead"
                )
    if chosen is not None:
        selection = "chosen_weighted"

    winners: list = []
    booked_by_year: dict = {}
    refused_by_year: dict = {}
    booked_cy_by_year: dict = {}
    # THE MASS EACH SETTLED ACCOUNT STANDS FOR, parallel to `winners` and in COMMERCIAL WINS. Under
    # the cull every entry is `1 / sample_rate` and the vector says the same thing the scalar did;
    # under the chooser they differ by two orders of magnitude, which is the whole point. Carried
    # as a list rather than folded onto the prospect because a prospect is the WORLD's object and a
    # weight is a fact about OUR sample of it.
    settlement_weights: list[float] = []
    weight_by_year: dict = {}
    chosen_weight = dict(zip(chosen["positions"], chosen["weights"])) if chosen else {}
    for i, (year, prospect, in_market, cost_cy) in enumerate(candidates):
        # SYSTEMATIC, not random and not first-come. `int((i+1)*r) > int(i*r)` takes every
        # 1-in-1/r of the sequence, spread evenly through it, so each year's booked wins are
        # proportional to that year's funnel wins and `booked / sample_rate` estimates what
        # the company won without bias in ANY year. Deterministic, so a re-run books the same
        # accounts; no RNG stream to seed and none to drift.
        wanted = (i in chosen_weight) if chosen else (
            int((i + 1) * sample_rate) > int(i * sample_rate))
        # THE HARD GUARD, kept even though `sample_rate` was derived from the budget. The
        # selection is by count and the budget is in customer-years, so a sample whose members
        # happen to be dearer than the population's mean could cross the ceiling by one
        # account. Never exceeding it is what the ceiling IS, so the guard is the invariant
        # and the rate is the estimate.
        if wanted and committed_cy + cost_cy <= customer_year_budget:
            committed_cy += cost_cy
            winners.append((prospect, in_market))
            # THE CULL'S WEIGHT IS THE SCALAR IT ALWAYS IMPLIED. `1 / sample_rate` was never
            # absent from the old design -- it was on the page as the thing a reader was told to
            # divide by. Writing it per account here is what makes the two paths comparable and
            # what stops every consumer needing to know which one ran.
            w = chosen_weight[i] if chosen else (1.0 / sample_rate if sample_rate else 0.0)
            settlement_weights.append(w)
            weight_by_year[year] = weight_by_year.get(year, 0.0) + w
            booked_by_year[year] = booked_by_year.get(year, 0) + 1
            booked_cy_by_year[year] = booked_cy_by_year.get(year, 0.0) + cost_cy
        else:
            refused_by_year[year] = refused_by_year.get(year, 0) + 1

    return {
        "winners": winners,
        "booked_by_year": booked_by_year,
        "refused_by_year": refused_by_year,
        "booked_cy_by_year": booked_cy_by_year,
        "committed_cy": committed_cy,
        "sample_rate": sample_rate,
        # WHAT THE WHOLE CAMPAIGN WOULD HAVE COST TO SETTLE, returned rather than recomputed by
        # the caller: it is the denominator `sample_rate` came from, and two copies of a
        # denominator is how a rate and the figure it is published beside come to disagree.
        "campaign_cy": campaign_cy,
        # WHICH RULE ACTUALLY RAN, as a fact rather than as something the caller re-derives from
        # the weights. `chosen` is a BOOL here and not the chooser's own dict: the caller needs to
        # know only that the sample was chosen, and returning the dict would put the positions in
        # two places at once.
        "chosen": chosen is not None,
        "selection": selection,
        "choice_refusal": choice_refusal,
        "settlement_weights": settlement_weights,
        "weight_by_year": weight_by_year,
    }


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
    switching_multiplier_fn=None,
    customer_year_budget: float | None = None,
    customer_years_already_committed: float = 0.0,
    prospects_per_year: int = PROSPECTS_PER_YEAR,
    commodity_weights: Optional[Mapping[str, float]] = None,
    segment_weights: Optional[Mapping[str, float]] = None,
    premise_stock_fn=None,
    quote_cutoff: str | None = None,
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

    `premise_stock_fn(year) -> Sequence[DrawnPremise]` (default None) is injected on the same
    terms and is PB2's inversion: supplied, each year's prospects are homes claimed out of
    the world's addressable stock rather than dwellings minted per prospect, so the book this
    campaign wins is a measurable SUBSET of a population that also contains everyone it never
    won. `year_premise_stock` in this module is the shipped implementation; injecting it
    rather than calling it keeps the default byte-identical and lets a control hand in a
    deliberately wrong stock.

    THE WALL, and this is the one place this module could have breached it. An earlier draft
    called `saas.growth_mandate.growth_quote_budget` directly from here -- a SIM module
    reaching into the supplier's own management accounts to find out what it can afford. That
    is precisely the crossing `run_acquisition_funnel` removed from itself in KNIFE pass 3
    (design `B6_cpa_is_company_accounting`), and for the same reason: what a supplier can
    afford to spend is company accounting, and the world has no view of it and no business
    deciding it. So `quote_budget_fn(net_assets_gbp, accounts_held, quotes_issued_to_date,
    wins_to_date) -> plan` ARRIVES as an injected callable, exactly like `run_funnel` and
    `cost_per_quote_gbp`. `run_phase2b` is the orchestrator and is the layer permitted to hold
    both sides; nothing under `simulation/` imports `saas.*` to make this work.

    The last two arguments are the company's OWN quote book, carried forward by the year loop
    below (2026-08-24). They travel the same direction as the first two and for the same reason:
    a supplier knows how many quotes it issued and how many converted because it issued them, so
    this is its commercial record arriving back at its own planner, not the world disclosing an
    outcome. Year one sees an empty book and plans on its founding belief; every year after it
    plans on what its books have since said.

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

    # THIS CAMPAIGN IS PRICED FOR DOMESTIC ACCOUNTS AND REFUSES ANY OTHER AT ITS OWN EDGE,
    # rather than falling back three layers in. `segment_weights` is a DEFAULTED parameter, so
    # until 2026-09-15 nothing here said no: `segment_weights={"sme": 1.0}` ran the whole campaign.
    # Measured that day, seed 42, 20 prospects: 20 of 20 candidates carried no premise, so
    # `settlement_choice.demand_vector` refused every one of them and `settle_within_budget` took
    # its unplaceable route and wrote "N of M wins carry no home the demand axes can be evaluated
    # on". THAT SENTENCE NAMES THE SAMPLING INSTRUMENT AND THE DEFECT IS THE SEGMENT MIX -- it
    # sends the reader to the chooser for a campaign that was never priced for what it was told to
    # quote. The same measurement is why this is a refusal and not a widening: with the shipped
    # `DOMESTIC_ONLY` the same run gives 0 of 20 unplaceable, so the route is unreachable through
    # the shipped configuration and reachable only by overriding this parameter.
    #
    # WHY NO, and the reason is already on `DOMESTIC_ONLY` rather than newly invented here: the
    # growth plan is denominated in Ofgem's Minimum Capital Requirement, which is £130 per
    # dual-fuel-equivalent DOMESTIC customer, and an SME is not priced by it; and `_draw_dwelling`
    # draws a dwelling only for domestic prospects, so a won SME reaches
    # `dwelling_records.build_properties` with no dwelling and raises `DwellingNotDrawn`. THE RUN
    # DIES EITHER WAY. What this changes is where and with what message: here, naming the
    # campaign's own pricing, or much later inside the world's dwelling register, naming a missing
    # home -- a failure whose message blames the artefact for a decision made at this call.
    #
    # THE FALLBACK IN `settle_within_budget` IS NOT DELETED AND THIS IS NOT ITS REPLACEMENT. That
    # function is also called directly, its unplaceable route is a real state at ITS boundary, and
    # it is held there over the whole partition by
    # `test_all_three_selection_STATES_are_reachable_through_settle_within_budget_and_tellable_apart`.
    # What was wrong was narrower: the CAMPAIGN could manufacture that state and have it reported
    # as a sampling refusal. Held at two altitudes because there are two subjects, not one.
    if segment_weights is not None:
        non_domestic = sorted(
            s for s, w in segment_weights.items() if s not in DOMESTIC_ONLY and w > 0
        )
        if non_domestic:
            raise ValueError(
                f"this growth campaign is priced for DOMESTIC accounts and was asked to quote "
                f"{', '.join(non_domestic)}. The plan is denominated in Ofgem's Minimum Capital "
                f"Requirement (£130 per dual-fuel-equivalent domestic customer, 26 July 2023), "
                f"which does not price a non-domestic account, and the world draws a dwelling "
                f"only for domestic prospects -- so every such win carries no home, reaches the "
                f"settlement chooser unplaceable, and would raise DwellingNotDrawn downstream. "
                f"Refused at the campaign's edge rather than culled by count later, because the "
                f"cull's note names the sampling instrument and the defect is the segment mix. "
                f"To model non-domestic growth, price it first -- see DOMESTIC_ONLY."
            )

    winners: list[tuple[SyntheticCustomer, dt.date]] = []
    spend: list[dict] = []
    by_year: list[dict] = []
    notes: list[str] = []

    net_assets = float(opening_net_assets_gbp)
    accounts = int(accounts_held_at_start)
    committed_cy = float(customer_years_already_committed)
    # EVERY FUNNEL WIN, WITH WHAT IT WOULD COST TO SETTLE. The sampling pass after the year
    # loop turns this into the book. `(year, prospect, in_market_date, customer_years)`.
    candidates: list[tuple[int, SyntheticCustomer, dt.date, float]] = []

    # The company's own running quote book, carried year to year. This is what makes the
    # campaign a LEARNING one rather than a plan repeated: year one is issued on the founding
    # belief, and every year after it is issued on what the company's own books have since
    # said. The counts are the company's, so they cross back into its plan freely.
    quotes_issued_to_date = 0
    wins_to_date = 0

    for year in years:
        plan = quote_budget_fn(
            net_assets_gbp=net_assets, accounts_held=accounts,
            quotes_issued_to_date=quotes_issued_to_date, wins_to_date=wins_to_date,
        )
        # NOT `in_market`: that name is already taken in this function for a PROSPECT'S OWN
        # in-market DATE (`winners.append((prospect, in_market))`), and shadowing it put a date
        # into this row and would have put an int into every winner tuple.
        homes_in_play, switching_multiplier = homes_in_market(
            year, prospects_per_year, multiplier=switching_multiplier_fn(year)
            if switching_multiplier_fn else None)
        quotes, market_note = quote_capacity(
            plan["quotes"], homes_in_play, engineering_ceiling=prospects_per_year)
        if market_note:
            notes.append(f"{year}: {market_note}")

        # THE COMMERCIAL BINDING REASON, and after 2026-08-29 it stays commercial. It used to
        # be overwritten with "settlement_engine" in any year the ceiling ran out, which was
        # nine of the shipped ten -- and that reading was right while the ceiling STOPPED a
        # year dead. A uniform sample does not stop any year; it scales the whole book. So the
        # artefact is reported as `settlement_sample_rate` on every row, which is a number
        # rather than a label, and `binding` goes back to saying what limited the COMPANY.
        # WHAT ACTUALLY LIMITED THE YEAR, which is the TIGHTER of the company's own plan and
        # the pool it had to quote into -- and until 2026-08-29 this line only ever reported
        # the first. `quote_capacity` has split its warning in two since PB3 (MARKET-THIN: the
        # real switching rate bound it, a commercial result; MARKET-BOUND: OUR
        # `PROSPECTS_PER_YEAR` bound it, an artefact), and both went into `notes` while the row
        # a reader actually sees kept saying `growth_rate`. So the published page attributed
        # our own prospect ceiling to the supplier's growth mandate, which is the exact
        # misreading the director asked to be prevented on 2026-08-24.
        #
        # `market` was in `generate_book_growth_data.BINDING_MEANING` the whole time, fully
        # worded, for a value NOTHING IN THIS FILE EVER EMITTED -- a documented branch with no
        # producer. It has one now.
        #
        # WHY THIS ONLY BIT NOW: `PROSPECTS_PER_YEAR = 400` carries its own design condition --
        # "sized so the company's capital is the binding constraint in every year ... 400
        # leaves the market non-binding by an order of magnitude". Moving `accounts` onto
        # funnel wins the same day let the company afford 861 quotes in 2024, so that
        # condition is now FALSE in three of ten years. The constant stated the condition
        # under which it would stop being right, and `quote_capacity` reported it the moment
        # it did. That one worked.
        binding = plan["binding"]
        if market_note:
            binding = (
                "prospect_ceiling" if market_note.startswith("MARKET-BOUND") else "market"
            )
        # THE FUNNEL'S OWN VERDICT, kept apart from the book's: wins the market gave us,
        # before this machine decides how many of them it can settle. Split because the ratio
        # of quotes to BOOKED wins mixes two classes -- a supplier losing in the market, and
        # this machine running out of customer-years -- and only the first is commercial.
        # Reported unsplit, an unobservable harness limit reads as company behaviour.
        funnel_wins_this_year = 0
        spent_this_year = 0.0

        if quotes:
            # THE STOCK IS DRAWN WHOLE, not up to the quote count, and that is the
            # independence property rather than an inefficiency. `pool` is a generator and
            # the loop below breaks at `quotes`, so only the quoted prospects are ever
            # materialised -- but the STOCK slot each of them claims must not depend on how
            # many the company could afford, or "who was in the market" would quietly become
            # a function of the balance sheet. A positional claim into a whole year's stock
            # has no such term (see `iter_prospects`' own note).
            pool = iter_prospects(
                year, base_seed=base_seed, n=prospects_per_year,
                commodity_weights=commodity_weights or ELECTRICITY_ONLY,
                segment_weights=segment_weights or DOMESTIC_ONLY,
                premise_stock=(
                    premise_stock_fn(year) if premise_stock_fn is not None else None
                ),
            )
            for i, prospect in enumerate(pool):
                if i >= quotes:
                    break
                # THE COMPANY CANNOT QUOTE INTO A WEEK THE REPORTED WORLD HAS NOT REACHED
                # (2026-08-28). `horizon_end` is the settlement horizon (2026-01-01) and is
                # deliberately NOT this: it prices how long a won account settles for. This
                # is the Point-in-Time Blindfold on the QUOTE — a prospect whose in-market
                # date falls after the run's last reported day has not come to market yet,
                # so the supplier has not met them and cannot have paid to quote them.
                #
                # This was latent until the acquisition costs were sourced. At the invented
                # £112.50 a quote the campaign could only afford to reach 49 such prospects
                # (4.4% of it) and the tail read as a rounding edge; at the sourced £20.63 it
                # reached 143 (11.8%), and `test_c_the_window_filter_excludes_nothing_at_the_
                # shipped_configuration`'s non-vacuity bound fired exactly as written. The
                # bound was right and the behaviour was wrong: the fix is to stop planning
                # the quotes, not to widen the bound to admit more of them.
                #
                # `continue`, not `break`: the budget is a quote COUNT, and a prospect the
                # company never met should not consume one. The pool is date-ordered in
                # practice, so this is usually a tail — but a `break` would make the outcome
                # depend on that ordering holding, which nothing guarantees.
                if quote_cutoff is not None and prospect.acquisition_date > quote_cutoff:
                    continue
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
                funnel_wins_this_year += 1
                # THE SUPPLIER'S ACCOUNT COUNT, NOT THE BOOK'S, and this is the same wall fix
                # as `wins_to_date` below rather than a new one -- it was left behind when that
                # one landed on 2026-08-28, nine lines from here, because the leak has two legs
                # and only one of them was named. `accounts` is what `quote_budget_fn` sizes the
                # Ofgem capital headroom AND the 33% growth-rate cap from, so incrementing it
                # only on a SETTLED win puts this machine's ceiling inside the company's own
                # balance sheet: from 2018 the budget is spent, nothing more is booked, and the
                # supplier plans every remaining year against an account count frozen by our
                # wall clock. In the modelled world it won those accounts and holds capital
                # against them. The settlement refusal is invisible to it because it did not
                # happen there.
                accounts += 1
                # THE ENGINEERING CAP BITES ON THE WIN, not on the quote. A quote the
                # company paid for is spent money whatever we can settle, and suppressing
                # it would silently understate acquisition cost -- the one number a reader
                # would use to judge whether growth was worth it. What we cannot afford is
                # SETTLING the account, so the win is recorded as spend and refused a place
                # on the book, loudly.
                #
                # WHICH wins get that place is decided AFTER this loop, not here, and the
                # move out is the 2026-08-29 fix (design doc
                # `SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md`). Deciding it here means
                # deciding it first-come, and a win's settlement cost is its tail to the
                # horizon -- 9.83 customer-years for a 2016 win against 0.78 for a 2025 one.
                # First-come therefore spends the whole budget on the most expensive cohort
                # and books ZERO in every year after it runs out: eight of ten years of the
                # shipped campaign, and no budget avoids that shape because a bigger one only
                # moves the cliff. Collect the candidates, then sample them uniformly.
                candidates.append(
                    (year, prospect, in_market, _customer_years(in_market, horizon_end)))

        net_assets -= spent_this_year
        # Booked BEFORE the record below, so `planning_on` in each year's row is the basis this
        # year was planned on -- not one retro-fitted from a total that already includes it.
        quotes_issued_to_date += quotes
        # THE FUNNEL'S WINS, NOT THE BOOK'S, and this line is a WALL fix rather than a tuning
        # one (ruled 2026-08-28, see the module note at `SETTLEMENT_CUSTOMER_YEAR_BUDGET`).
        # The row's `wins` is truncated by THIS MACHINE's settlement budget, which is an
        # engineering ceiling and not a thing that exists in the modelled world. Feeding it
        # back to `quote_budget_fn` put that ceiling inside the company's own commercial
        # belief: at the 80-founder book it drove the company's `realised_win_rate` from
        # 17.8% to 1.7% and its quote budget from 135 to 2,000, so the company bought 2,826
        # quotes to book 45 accounts -- a supplier responding rationally to a number the
        # harness made up. What a supplier actually knows is what its own funnel converted:
        # it quoted, the prospect accepted. That is `funnel_wins_this_year`, and the
        # settlement refusal is invisible to it because in the modelled world it did not
        # happen. The refusal stays visible to the READER on every `by_year` row.
        wins_to_date += funnel_wins_this_year
        by_year.append({
            "year": year,
            "quotes_issued": quotes,
            "quotes_affordable": plan["quotes"],
            # FILLED BY THE SAMPLING PASS BELOW, which cannot run until the campaign's whole
            # candidate list exists. Written here as zero rather than left absent so the row's
            # key set does not depend on how far the run got.
            "wins": 0,
            # THE SPLIT, on the row a reader actually sees. `wins` is booked wins and always
            # was; these two say what it is made of. `funnel_wins` is what the market gave
            # the company, `wins_refused_by_settlement_budget` is what THIS MACHINE would
            # not settle, and the identity funnel_wins == wins + refused holds on every row.
            "funnel_wins": funnel_wins_this_year,
            "wins_refused_by_settlement_budget": 0,
            "believed_win_rate": plan.get("believed_win_rate"),
            "realised_win_rate_used": plan.get("realised_win_rate"),
            "planning_on": plan.get("planning_on", "belief"),
            # PB3: how open the market actually was this year, and the real switching
            # multiplier that decided it. Reported so a flat year can be read as the crisis it
            # was rather than as a supplier that chose not to grow.
            "homes_in_market": homes_in_play,
            "switching_multiplier": round(switching_multiplier, 3),
            "spend_gbp": round(spent_this_year, 2),
            # THE SUPPLIER'S, AND THIS MACHINE'S. `accounts_after` is what the company holds and
            # sizes its capital against; `book_after` is what we settled. Equal whenever the
            # ceiling is slack, and their difference is the whole of the engineering artefact.
            "accounts_after": accounts,
            "book_after": 0,
            "capital_headroom_gbp": plan["headroom_gbp"],
            "binding": binding,
            "customer_years_committed": 0.0,
        })

    # ── THE SAMPLING PASS ─────────────────────────────────────────────────────────────────
    # WHAT THE CEILING DECIDES IS THE BOOK'S SCALE, NOT WHICH YEARS EXIST. Everything above
    # is the campaign as the world resolved it and is untouched by this: the quotes, the
    # spend, the funnel's verdict on each prospect, and the company's own plan. This pass
    # only chooses which of the wins THIS MACHINE can afford to settle.
    #
    # IT IS NOT A WALL CROSSING and the two-pass shape is why the question comes up. Nothing
    # the company decided above can see this pass -- it has already decided everything -- so
    # no information travels backwards. A sampling frame that needs its own population is
    # ordinary; what would be a crossing is the company's PLAN depending on the sample, and
    # `accounts` and `wins_to_date` were both moved off the book precisely so it cannot.
    settled = settle_within_budget(
        candidates,
        committed_cy=committed_cy,
        customer_year_budget=customer_year_budget,
    )
    booked_by_year = settled["booked_by_year"]
    refused_by_year = settled["refused_by_year"]
    booked_cy_by_year = settled["booked_cy_by_year"]
    committed_cy = settled["committed_cy"]
    sample_rate = settled["sample_rate"]
    campaign_cy = settled["campaign_cy"]
    # WHICH RULE RAN AND WHAT EACH SETTLED ACCOUNT STANDS FOR. The notes and the per-year rows
    # below are the only readers; they are unpacked here rather than reached for through `settled`
    # so the prose that describes the selection sits beside the name it describes.
    chosen = settled["chosen"]
    selection = settled["selection"]
    choice_refusal = settled["choice_refusal"]
    settlement_weights = settled["settlement_weights"]
    weight_by_year = settled["weight_by_year"]
    winners.extend(settled["winners"])

    # THE ROWS ARE FILLED IN YEAR ORDER, so `book_after` and `customer_years_committed` still
    # read as running totals at the end of that year -- the same thing they meant when the
    # booking decision was taken inside the year loop. The candidate list is built in year
    # order and `by_year` is appended in year order, so no sort is needed and adding one would
    # hide it if that ever stopped being true.
    running_book = int(accounts_held_at_start)
    running_cy = float(customer_years_already_committed)
    for row in by_year:
        year = row["year"]
        row["wins"] = booked_by_year.get(year, 0)
        row["wins_refused_by_settlement_budget"] = refused_by_year.get(year, 0)
        running_book += row["wins"]
        running_cy += booked_cy_by_year.get(year, 0.0)
        row["book_after"] = running_book
        row["customer_years_committed"] = round(running_cy, 1)
        # THE RATE IS ON EVERY ROW because it is what refused this year's wins, and a reader
        # who sees `funnel_wins` and `wins` disagree is owed the reason on the same line.
        #
        # IT IS STILL TRUE UNDER THE CHOOSER AND IT NO LONGER MEANS WHAT IT MEANT. It is the share
        # of the company's wins that reached the book -- a COUNT ratio -- and that is exactly what
        # it was always defined as. What has stopped being true is the inference every consumer
        # drew from it: that dividing a settled figure by it recovers the commercial one. Under a
        # chosen sample the inflation is per account, so `settlement_weight` below is the number
        # that does that job and the rate is a diagnostic.
        row["settlement_sample_rate"] = round(sample_rate, 4)
        # WHAT THIS YEAR'S SETTLED ACCOUNTS STAND FOR, in the company's own wins. Under the cull it
        # is `wins / rate` and says nothing new; under the chooser it is the fitted estimate of
        # `funnel_wins`, and the two agreeing to 0.1% is a measured property of the fit and not an
        # identity. A reader comparing this with `funnel_wins` on the same row is reading the
        # sample's accuracy directly, which is the one check the scalar rate made impossible.
        row["settlement_weight"] = round(weight_by_year.get(year, 0.0), 1)
        row["settlement_selection"] = selection

    if sample_rate < 1.0:
        # `1 / sample_rate` IS NOT SAFE HERE and a rate of exactly zero is a real operating
        # state, not a hypothetical: the opening book is charged against the same budget, so a
        # curriculum act that deepens it far enough leaves the campaign no headroom at all. 82
        # founders already take 778 of the 1,200. Caught by
        # `test_a_budget_the_OPENING_BOOK_has_already_spent_books_nothing_and_says_so`, which was
        # written for the empty-book-must-say-so property and found this on its first run.
        # THE WHOLE SENTENCE IS CONDITIONAL, not just the division. At a rate of zero "every
        # year is represented in proportion to what it won" is false -- no year is represented
        # at all -- and a note that keeps its reassuring clause through the degenerate case is
        # the shape that publishes a claim nobody checked.
        # THE NOTE HAS TO SAY WHICH SAMPLE IT IS, and until 2026-09-11 it could only ever say one
        # thing. It asserted the book was UNIFORM -- "spread evenly", "divide by the rate" -- and
        # under the chooser every one of those clauses is false. A note whose reassuring sentence
        # survives a change to the mechanism it describes is the shape that publishes a claim
        # nobody checked, which is the same failure its own zero-rate branch was written to avoid.
        how = (
            "chosen for DIFFERENCE over the demand axes rather than culled by count, each "
            "carrying the mass of commercial wins it stands for"
            if chosen else
            f"one in every {1 / sample_rate:.1f}, spread evenly across the campaign so every "
            f"year is represented in proportion to what it won"
            if sample_rate else
            "which is NONE of them: the opening book had already committed the whole budget "
            "before the campaign won anything, so this book carries no campaign accounts at all"
        )
        if chosen:
            reading = (
                "The book below is a CHOSEN sample and is deliberately not proportional by "
                "count: every settled account carries its own `settlement_weight` in the "
                "company's own wins, and those weights -- not the rate -- are what read the "
                "company rather than the sample. Per year they sum to that year's `funnel_wins`, "
                "which is a fitted property on the row to be checked, not an identity."
            )
        elif sample_rate:
            reading = (
                "The book below is a uniform SAMPLE of the book this supplier's balance sheet "
                "supports -- divide by the rate to read the company, not the sample."
            )
        else:
            reading = "The book below is the opening book alone. It is not what this supplier won."
        notes.append(
            f"SETTLEMENT-SAMPLED at {sample_rate:.4f}: the company won "
            f"{len(candidates)} accounts and this machine settled {len(winners)} of them, "
            f"{how}. "
            f"{customer_year_budget} customer-years is THIS MACHINE's budget "
            f"(basis: `simulation/net_new_acquisition.py::SETTLEMENT_CUSTOMER_YEAR_BUDGET`, "
            f"artefact `docs/observability/settlement_ceiling_probe.json`), not a commercial "
            f"limit. " + reading
        )
    if choice_refusal:
        # THE REFUSAL NAMES ITS REASON, on the same channel the reader already watches. A sample
        # that silently fell back to counting would publish a page whose selection sentence is
        # wrong in the one direction nobody would check -- it would read as chosen.
        notes.append(f"SETTLEMENT SAMPLE NOT CHOSEN: {choice_refusal}.")

    return {
        "winners": winners,
        "spend": spend,
        "by_year": by_year,
        "notes": notes,
        "customer_years_committed": round(committed_cy, 1),
        "customer_year_budget": customer_year_budget,
        # HOW THE SAMPLE WAS TAKEN, as a value rather than something a consumer infers from the
        # rate. Every published sentence about this book that says "uniform" has to be able to
        # stop saying it, and a page that branches on a named selection cannot assert uniformity
        # about a chosen sample by omission.
        "settlement_selection": selection,
        # PARALLEL TO `winners`, in commercial wins. Sums to `funnel_wins` under either path.
        "settlement_weights": [round(w, 4) for w in settlement_weights],
        # WHAT THE CEILING COST, as one number. `1 - rate` is the share of the company's own
        # wins this machine could not settle, and it is the honest headline for the artefact.
        "settlement_sample_rate": round(sample_rate, 4),
        "customer_years_all_wins_would_cost": round(campaign_cy, 1),
        # CAMPAIGN TOTALS OF THE SPLIT. Derived from the rows rather than counted again, so
        # the two can never disagree; here because the question a reader asks of a campaign
        # ("did we lose these in the market, or did the machine refuse them?") is asked of
        # the whole run and not of one year.
        "funnel_wins": sum(r["funnel_wins"] for r in by_year),
        "wins_refused_by_settlement_budget": sum(
            r["wins_refused_by_settlement_budget"] for r in by_year),
    }
