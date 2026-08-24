"""LIVE POPULATION SEAM — the single accessor a run uses to obtain its book.

This is the reversible half of the generator draw-wiring (PLANNER-MINTED
`generator_draw_wiring`, PRODUCT-FIRST item 2, section D). It exists so that
the eventual director-authorised activation is a one-flag flip against a
tested seam, not a fresh build.

Default behaviour is BYTE-IDENTICAL to today: return the static hand-authored
`CUSTOMERS` literal from `saas/customers.py`. When the default-OFF activation
flag `SE_DRAW_POPULATION=1` is set, the seam ADDITIVELY appends the synthetic
segment-coupled acquisition cohort drawn by `simulation.population_draw`
(rendered saas-shaped via `SyntheticCustomer.to_customer_dict()`), filling the
FRAME-found "book stops acquiring after 2020" gap with SYN-* 2021-2025
acquisitions. Additive-not-replacive: every existing `customer_id` survives.

WALL / R13 ACTIVATION — AUTHORISED 2026-08-13 (director console):
  Flipping this flag on changes WHICH WORLD the company faces every run — a
  CURRICULUM act reserved to the director (W2_2's own ruling; the 2026-07-24
  waiver preserved "curriculum values remain director-reserved"). It was held
  from 2026-07-24 until the director's console word on 2026-08-13: *"activate
  the population draw (SE_DRAW_POPULATION) and wire the entrypoints. The book
  stays earned, never granted."* The mechanism still ships DEFAULT-OFF and the
  flag is still the only switch; what changed is that the switch is now
  authorised to be thrown, and the published run throws it (see
  `docs/design/curriculum/POPULATION_DRAW_ACTIVATION.md`).

EARNED, NEVER GRANTED (the director's own term, and the binding constraint):
  Activation appends the λ=1.0 "Profile B trickle" the director signed in W2_2 —
  a Poisson(1.0)/yr draw over 2021-2025, which at the fixed base seed realises
  as TWO customers (SYN-2021-001, SYN-2025-001). It does NOT append the N=200
  COVERAGE POOL; that is a separate concept for coverage reporting and it is not
  a book. A run that hands the company 200 customers it never won would be a
  grant, and this seam must never become one.

EPISTEMIC WALL (never crosses `company/interfaces/sim_interface.py`):
  The drawn `SyntheticCustomer`'s HIDDEN GROUND-TRUTH `cohort` is NEVER exposed
  here — `to_customer_dict()` omits it by construction, so the book this seam
  returns carries only saas-shaped OBSERVABLES, exactly like the static literal.
  The company discovers segment structure through the wall
  (`company/analytics/cohort_discovery.py`), never reads the drawn cohort.
  `draw_population` is imported LOCALLY (inside the activated branch) so a
  caller that never activates never pulls the SIM-truth generator onto its
  import graph.

KNOWN ACTIVATION-TIME FOLLOW-ON (honest, not silent): SYN-* dicts and the
static `CUSTOMERS` dicts do not share an identical key set (SYN carries
`payment_method`/`consumption_band`/`data_regime`/`acquisition_type`; the
static literal carries `home_type`/`bedrooms`/`epc_rating`/`contract_type`).
Downstream entrypoints must be hardened to tolerate the SYN shape BEFORE the
flag is flipped on — that hardening is part of the held activation, not this
seam. The seam's contract is only "produce the additive book"; it does not
claim the whole pipeline is SYN-ready.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from company.interfaces.supply_book import register_drawn_points, registered_supply_points

# The supply book, bound once at import: the seam hands back the LIVE roster
# objects (see company/interfaces/supply_book.py, IDENTITY), so a runtime append
# to the acquired book is visible here exactly as it was before KNIFE pass 2.
CUSTOMERS = registered_supply_points()

#: The hand-authored roster as it stood at import, frozen. `CUSTOMERS` above is a LIVE view of
#: the supply book by design (KNIFE pass 2 IDENTITY: a runtime append to the acquired book
#: must be visible through it), which makes it the wrong thing to compute an OPENING position
#: from -- it grows as the run registers wins. This is the same records, snapshotted once.
_STATIC_ROSTER = tuple(CUSTOMERS)

# Director-authorised activation (R13 curriculum). The env var is the OVERRIDE;
# the committed curriculum file is the durable state of record.
_ACTIVATION_ENV = "SE_DRAW_POPULATION"
_ACTIVATION_CURRICULUM = (
    Path(__file__).resolve().parent.parent
    / "docs" / "design" / "curriculum" / "population_draw_activation.json"
)

# Fixed base seed so the drawn cohort is deterministic + replayable (C-S2).
# This is a MECHANISM default (determinism), NOT a curriculum knob — the
# curriculum decision is on/off (director-reserved); the seed only fixes which
# deterministic draw the "on" state yields.
_DEFAULT_BASE_SEED = 20260724


def _curriculum_activated() -> bool:
    """Read the committed activation curriculum. FAIL-CLOSED to OFF.

    The activation state is a versioned artefact in the repo, not an export on one
    machine: behaviour-determining state must be reconstructible from the repo
    alone (OPERATIONAL_LAYER_DESIGN, IaC core). Read LIVE on every call, the same
    idiom `population_draw` uses for the segmentation curriculum, so a director
    change is one versioned edit and never a code change.

    Missing, unreadable, or malformed file -> False. Fail-closed is the correct
    direction HERE and only here: OFF is the byte-identical default, so a broken
    curriculum file degrades to today's world rather than silently activating a
    different one. (Note this is the opposite of the model-tier classifier, which
    fails closed toward the EXPENSIVE option -- in both cases "closed" means
    toward the outcome whose failure mode is cheapest, not toward a fixed value.)
    """
    try:
        with open(_ACTIVATION_CURRICULUM, encoding="utf-8") as fh:
            doc = json.load(fh)
        return doc["activated"]["value"] is True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def draw_population_enabled() -> bool:
    """True iff the population draw is activated.

    Precedence: an EXPLICIT `SE_DRAW_POPULATION` env value wins ("1" on, "0" off)
    so a test can pin either state without editing a committed curriculum file;
    otherwise the committed curriculum decides. Unset env + curriculum activated
    == ON, which is what makes the published run see the drawn book without any
    out-of-tree state.
    """
    env = os.environ.get(_ACTIVATION_ENV, "")
    if env == "1":
        return True
    if env == "0":
        return False
    return _curriculum_activated()


def live_population(base_seed: Optional[int] = None) -> List[dict]:
    """Return the run's customer book as a list of saas-shaped dicts.

    DEFAULT (flag off): the static ``CUSTOMERS`` literal, unchanged — a fresh
    list byte-identical in content to importing ``CUSTOMERS`` directly.

    ACTIVATED (``SE_DRAW_POPULATION=1``, director-reserved): ``CUSTOMERS``
    followed by the additive synthetic acquisition cohort (saas-shaped,
    ground-truth ``cohort`` excluded). Additive-not-replacive.
    """
    if not draw_population_enabled():
        return list(CUSTOMERS)
    # Local import: keep the SIM-truth generator off the import graph of any
    # caller that never activates (wall hygiene).
    from simulation.population_draw import draw_population

    seed = _DEFAULT_BASE_SEED if base_seed is None else base_seed
    # draw_region=True (ACTIVATION §1): the activated book carries REAL regions
    # from the ratified curriculum marginal, not the UNKNOWN_SYNTHETIC placeholder
    # — region is a PUBLIC observable the company sees at enrolment (curriculum
    # note), so it belongs in the saas-shaped dict. The hidden `cohort` stays
    # excluded by `to_customer_dict()` (wall). Still behind the default-OFF flag:
    # this only prepares the tested seam; flipping the flag remains the held,
    # director-reserved release rung.
    #
    # assign_cohorts=True (CA1, DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED §1,
    # curriculum act committed e685eb76d, tag proceed; go/no-go on record in
    # docs/design/CA4_COHORT_ACTIVATION_SEQUENCING_VERDICT.md): each drawn
    # household carries its SIM-truth cohort (tenure-tilted accommodation/cars/
    # nssec joint + region-pinned heating + curriculum-drawn green_stance/
    # price_sensitivity/channel_pref at RATIFIED values — no tuning, R13). This
    # rides on the HIDDEN `SyntheticCustomer.cohort`; `to_customer_dict()` still
    # omits it, so the saas-shaped OBSERVABLE stream stays byte-identical to the
    # no-cohort case (§2 elicitation wall — the company discovers, never reads,
    # cohort structure). `assign_cohort()` draws from its OWN named substream so
    # this cannot perturb the acquisition draw (C-S2). The wall is RE-PROVEN to
    # fire post-activation in test_wall_drawn_book_never_exposes_ground_truth_
    # cohort, which now asserts cohorts ARE assigned yet NEVER surface.
    drawn = [
        sc.to_customer_dict()
        for sc in draw_population(seed, draw_region=True, assign_cohorts=True)
    ]
    # ACTIVATION (2026-08-13): register the drawn points on the supply book before
    # handing them back. Iterating a book you cannot then RESOLVE BY ID is what
    # broke the home-move path -- `run_phase2b` looks a winning account back up
    # with `registered_point()`, got `None` for a drawn customer, and passed that
    # `None` into `register_acquired_point()`. Registering closes that gap at the
    # single point where the drawn cohort enters the system, so every entrypoint
    # gets it, not just the ones that remembered to.
    #
    # Idempotent by `customer_id`: entrypoints bind the book at import time in
    # whatever order Python resolves them, so this runs more than once per process
    # and must not double the book.
    register_drawn_points(drawn)
    book = list(CUSTOMERS) + drawn

    won = _won_customer_dicts(_campaign(_pre_growth_book(seed), seed))
    if won:
        register_drawn_points(won)
        book = book + won
    return book


# ---------------------------------------------------------------------------
# PB3 — NET-NEW ACQUISITION, the earned half of the book
# ---------------------------------------------------------------------------
# WHY IT ENTERS HERE. This seam is already the single place a run's book is
# assembled, and the drawn trickle already arrives through it, registered on the
# supply book so `registered_point()` can resolve an id later. A won account has
# exactly the same requirement. Putting the campaign anywhere else in
# `run_phase2b` would mean an account appearing after renewal schedules had been
# built, which is the same defect the successor path was designed around.
#
# WHAT IT IS NOT. The trickle above APPENDS its draw: every drawn event becomes a
# customer with certainty, which is a growth curve that cannot be lost. These
# accounts each survived `run_acquisition_funnel` — five stages, per-stage
# leakage, a real credit check and the statutory cooling-off window — and the
# quotes that did NOT survive were paid for anyway. The two lists are kept apart
# for that reason and never merged.

_GROWTH_MANDATE_CURRICULUM = (
    Path(__file__).resolve().parent.parent
    / "docs" / "design" / "curriculum" / "book_growth_activation.json"
)


def growth_mandate_active() -> bool:
    """True iff the net-new acquisition campaign runs. Same shape as the draw flag.

    DEFAULT OFF and fail-closed on every error path: an unreadable or malformed
    curriculum file means the book does not grow, because the alternative — a
    published book that changed size because a JSON file failed to parse — is the
    worst outcome available here.
    """
    env = os.environ.get("SE_GROW_BOOK", "")
    if env == "1":
        return True
    if env == "0":
        return False
    try:
        with open(_GROWTH_MANDATE_CURRICULUM) as fh:
            return json.load(fh)["activated"]["value"] is True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def _opening_net_assets_gbp(book: List[dict]) -> float:
    """The company's opening capital, computed from the PRE-GROWTH book.

    `run_phase2b.STARTING_TREASURY_GBP` scales treasury with the book's own
    consumption (£3,250 per 15,000 kWh of EAC), so reading it after the campaign
    has run would let the accounts the campaign won pay for themselves — a
    supplier bootstrapping capital out of customers it has not yet acquired.
    Recomputed here from the roster as it stands BEFORE any win, which is what an
    opening balance sheet means.

    THE HALF-HOURLY ACCOUNTS ARE THE WHOLE NUMBER, and getting this wrong the first
    time is worth recording. A smart-metered or I&C account carries `eac_kwh: None`
    because its consumption is read from real half-hourly data rather than an
    estimate, so summing `eac_kwh` and skipping the Nones silently drops the four
    GWh-scale I&C accounts and values the opening balance sheet at about £20k
    instead of £2.4m — two orders of magnitude, all of it in the accounts that
    matter most. The campaign then read as CAPITAL-bound from its second year and
    stopped issuing quotes entirely by 2022, which looked like a plausible
    commercial story and was an arithmetic error. `run_phase2b.EFFECTIVE_EAC_KWH`
    derives those accounts through `estimate_annual_kwh(load_hh_consumption(cid))`
    and this uses the same call, so the two cannot drift.

    Duplicating the £3,250/15,000 kWh constant rather than importing it is
    deliberate and narrow: `run_phase2b` imports THIS module at module scope, so
    importing back would be a cycle. The two are pinned together by
    `test_opening_capital_matches_the_runs_own_treasury_scaling`.
    """
    from simulation.hh_consumption import estimate_annual_kwh, load_hh_consumption

    total_eac = 0.0
    for c in book:
        if c.get("commodity") != "electricity":
            continue
        eac = c.get("eac_kwh")
        if eac is None:
            eac = estimate_annual_kwh(load_hh_consumption(c["customer_id"]))
        total_eac += eac
    return 3250.0 * (total_eac / 15_000.0)


#: Memo, keyed on seed. Every other draw in this module RE-DRAWS rather than caching, and
#: says so, because a population draw is cheap and a cache is a place for staleness to live.
#: The campaign is different in kind: it is 265 resolutions of a five-stage funnel plus a
#: credit check, and `live_population()`, `live_premises()` and `live_drawn_households()`
#: each need the same answer within one process. It is deterministic in `(seed, book size)`,
#: so the memo cannot return a different campaign from a re-run — only a faster one.
_CAMPAIGN_MEMO: dict = {}


def _campaign(book: List[dict], seed: int) -> dict:
    """The resolved campaign for this seed: winners, spend, per-year rows, notes."""
    if not growth_mandate_active():
        return {"winners": [], "spend": [], "by_year": [], "notes": [],
                "customer_years_committed": 0.0, "customer_year_budget": 0.0}
    # KEYED ON THE SEED ALONE, and the first draft's `(seed, len(book))` is why this comment
    # exists. `CUSTOMERS` is a LIVE view of the supply book (`registered_supply_points()`), so
    # its length changes the moment the trickle registers -- two callers reaching this from
    # either side of that registration got two different keys, resolved two different
    # campaigns, and `live_premises()` ended up holding dwellings for winners that were not
    # in the book. Every caller now resolves against the same `_pre_growth_book(seed)`, so
    # the book is not a key at all.
    if seed not in _CAMPAIGN_MEMO:
        _CAMPAIGN_MEMO[seed] = _resolve_campaign(book, seed)
    return _CAMPAIGN_MEMO[seed]


def _pre_growth_book(seed: int) -> List[dict]:
    """The roster the campaign runs AGAINST: static plus the trickle, and nothing it won.

    One function so that every caller resolves the identical campaign. It also states the
    obvious thing that would otherwise be implicit: the opening balance sheet and the opening
    account count a growth plan is built on are the ones BEFORE it grows.
    """
    if not draw_population_enabled():
        return list(_STATIC_ROSTER)
    from simulation.population_draw import draw_population

    return list(_STATIC_ROSTER) + [
        sc.to_customer_dict()
        for sc in draw_population(seed, draw_region=True, assign_cohorts=True)
    ]


def _resolve_campaign(book: List[dict], seed: int) -> dict:
    """Run the campaign. Callers want `_campaign`; this is the uncached body."""
    import datetime as _dt

    # THROUGH THE SEAM, never straight at `saas.growth_mandate`. The first draft imported
    # the budget rule directly and `test_no_new_sim_reads_company` refused it as a new
    # SIM->company crossing -- correctly, because `company/interfaces/growth_desk.py` is
    # exactly the sanctioned route and already carries `decide_acquisition` for the
    # replacement path. Two scalars go out, a decision comes back; the MCR, the capital
    # share, the growth-rate cap and the per-segment cost table all stay on the company side.
    from company.interfaces.growth_desk import plan_growth_campaign_year, quote_cost_gbp
    from simulation.acquisition_funnel import run_acquisition_funnel
    from simulation.net_new_acquisition import plan_growth_campaign
    from tools.credit_adapters import get_credit_bureau_adapter

    horizon = _dt.date(2026, 1, 1)
    existing_cy = sum(
        max(0.0, (horizon - _dt.date.fromisoformat(c["acquisition_date"])).days / 365.25)
        for c in book
    )
    outcome = plan_growth_campaign(
        years=range(2016, 2026),
        base_seed=seed,
        opening_net_assets_gbp=_opening_net_assets_gbp(book),
        accounts_held_at_start=len(book),
        horizon_end=horizon,
        credit_bureau=get_credit_bureau_adapter(),
        cost_per_quote_gbp={
            seg: quote_cost_gbp(segment=seg) for seg in ("resi", "SME")
        },
        run_funnel=run_acquisition_funnel,
        quote_budget_fn=lambda net_assets_gbp, accounts_held: vars(
            plan_growth_campaign_year(
                net_assets_gbp=net_assets_gbp, accounts_held=accounts_held
            )
        ),
        customer_years_already_committed=existing_cy,
    )
    LAST_CAMPAIGN.clear()
    LAST_CAMPAIGN.update({k: v for k, v in outcome.items() if k != "winners"})
    return outcome


def _won_customer_dicts(outcome: dict) -> List[dict]:
    """Winners as saas-shaped OBSERVABLES, stamped with the date they were actually won.

    `acquisition_date` moves from "the day this home was in the market" to "the day the
    contract started", because that is what the field means to every downstream consumer and
    a prospect that was quoted in March and won in April did not acquire in March.
    """
    return [
        {**prospect.to_customer_dict(),
         "acquisition_date": won_on.isoformat(),
         "acquisition_type": "net_new_won"}
        for prospect, won_on in outcome["winners"]
    ]


#: The campaign's own record of the run just assembled — per-year quotes, wins, spend and
#: the BINDING reason. Published rather than discarded because the growth curve is
#: meaningless without it: a flat year is a supplier that lost, a supplier that could not
#: afford to try, or this machine refusing to settle the wins, and those are three different
#: facts that look identical on a chart.
LAST_CAMPAIGN: dict = {}


# ---------------------------------------------------------------------------
# THE WORLD'S DWELLING FOR A DRAWN HOME (B12) — SIM TRUTH, NOT A SEAM OUTPUT
# ---------------------------------------------------------------------------
# `live_population()` above returns OBSERVABLES: it is what the company is handed.
# The three accessors below return the world's GROUND TRUTH about the drawn homes —
# property type, build era, EPC band, bedrooms, heating — and they are therefore NOT
# part of that seam. They exist for WORLD consumers only (`simulation.run_phase2b`'s
# property records and household register), and no `company/**` or `saas/**` module
# may call them; `test_the_worlds_dwelling_never_crosses_the_wall` enumerates the
# importers and fails if one appears.
#
# Why the world needs them at all: before B12 the world had no dwelling of its own
# for a drawn home, so `saas.property_model` filled the record from the SUPPLIER's
# modal-band approximation and the company's confidence-0.10 guess scored 100% on
# the drawn cohort — the half of the book that grows.
def live_premises(base_seed: Optional[int] = None) -> dict:
    """{customer_id: DrawnPremise} for the drawn DOMESTIC cohort; {} when off.

    Deterministic in the seed, so this is the SAME cohort `live_population()` returns
    — it re-draws rather than caching, exactly as `live_population()` does.
    """
    if not draw_population_enabled():
        return {}
    from simulation.population_draw import draw_population

    seed = _DEFAULT_BASE_SEED if base_seed is None else base_seed
    premises = {
        sc.customer_id: sc.premise
        for sc in draw_population(seed, draw_region=True, assign_cohorts=True)
        if sc.premise is not None
    }
    # A WON HOME IS STILL A HOME (B12). `dwelling_records.build_properties` raises
    # `DwellingNotDrawn` for any supplied customer the world drew no dwelling for, and it is
    # right to: the alternative is `saas.property_model` approximating the world's ground
    # truth from the supplier's own modal band, which is the exact defect B12 exists to stop.
    # A net-new win carries the dwelling drawn with it as a prospect, so it belongs in this
    # register on the same terms as the trickle -- found by running the full sim, which
    # stopped on `PROS-2016-0003`.
    for prospect, _won_on in _campaign(_pre_growth_book(seed), seed)["winners"]:
        if prospect.premise is not None:
            premises[prospect.customer_id] = prospect.premise
    return premises


def live_dwellings(base_seed: Optional[int] = None) -> dict:
    """{customer_id: dwelling record} for the drawn cohort, in the property record's
    plain-dict vocabulary — what `saas.property_model.build_properties()` takes."""
    from simulation.premise_population import dwelling_record

    return {
        cid: dwelling_record(premise)
        for cid, premise in live_premises(base_seed).items()
    }


def live_drawn_households(base_seed: Optional[int] = None) -> dict:
    """{customer_id: Household} for the drawn cohort — what
    `simulation.household.build_household_register()` takes."""
    return {cid: premise.household for cid, premise in live_premises(base_seed).items()}
