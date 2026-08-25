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
from simulation.segment_vocabulary import (
    CANONICAL_SEGMENTS,
    UnknownSegmentError,
    normalise_segment,
)

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

    THE TWO FLAGS ARE INDEPENDENT, and until 2026-08-25 they were not (PB3 exit
    (b2)). The drawn trickle is an ARRIVAL: a home the curriculum hands this
    supplier, which it could not have failed to get. The campaign is a CONTEST:
    prospects quoted at the company's own expense, most of which it loses. They
    are different objects and they answer to different flags —
    ``SE_DRAW_POPULATION`` and ``SE_GROW_BOOK`` — but the campaign used to sit
    INSIDE the trickle's branch, so emptying the arrival stream emptied growth
    with it. Measured at HEAD before this change: draw off, mandate on, ten years
    of campaign, book 18 -> 18, nought won, and the mandate reported itself
    ACTIVE the whole time. That is exit (b2) red — "with the arrival stream
    EMPTIED, the book must still be able to grow" — and it was red for a
    structural reason rather than a commercial one, which is the worst kind:
    every published growth figure was contingent on a flag that has nothing to do
    with whether this company can win a customer.
    """
    # SEGMENT SUSPENSION (2026-08-24, director: "stop the company serving business accounts
    # for now"). Applied HERE, at the one place a run's book is assembled, rather than as a
    # branch inside each consumer -- there are dozens of consumers and a filter per consumer
    # is a filter that is missing from one of them. Applied FIRST, before the drawn trickle
    # and before the campaign, so nothing downstream ever sees a suspended account and the
    # opening capital those two are sized from is the served book's, not the whole roster's.
    served = served_segments()
    static = [c for c in CUSTOMERS if _serves(c, served)]
    seed = _DEFAULT_BASE_SEED if base_seed is None else base_seed
    book = static

    if draw_population_enabled():
        drawn = [sc.to_customer_dict() for sc in _drawn_trickle(seed)]
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
        drawn = [c for c in drawn if _serves(c, served)]
        register_drawn_points(drawn)
        book = static + drawn

    # OUTSIDE the branch above, which is the whole of the (b2) change. `_campaign`
    # short-circuits to an empty outcome when `growth_mandate_active()` is false and
    # touches neither memo nor record on that path, so with both flags off this call
    # is a dict literal and the returned book is byte-identical to the pre-change
    # `return static`. `_pre_growth_book` was already flag-aware in both directions --
    # it has returned the static roster alone under a disabled draw since it was
    # written -- so the campaign already knew how to plan against a book with no
    # arrivals in it. Nothing was missing but the reachability.
    won = _won_customer_dicts(_campaign(_pre_growth_book(seed), seed))
    if won:
        register_drawn_points(won)
        book = book + won
    return book


# ---------------------------------------------------------------------------
# PB2 — THE WORLD'S STOCK, AND THE BOOK AS A SUBSET OF IT
# ---------------------------------------------------------------------------
# THE INVERSION (`PB2_UNWON_REMAINDER_FRAME.md` §1). Before this, both halves of the
# drawn book MINTED a dwelling per account: `_draw_dwelling` is keyed on the customer
# id, so a "premise" was the account's own name in another grammar. There was no set
# the book came out of, so there was no remainder, so "won, never assigned" had
# nothing that could falsify it — the world contained exactly the homes the company
# had already acquired and not one more.
#
# Now the SIM draws the STOCK — the homes addressable in each year — and both halves
# claim out of it. The campaign quotes into it and loses most of what it quotes; the
# Profile-B trickle takes its slot from a reserved tail. What neither ever claimed is
# the UNWON REMAINDER, and it is the object every one of PB2's remaining exits needs.
#
# WHERE THE REMAINDER MUST NOT GO. It is world truth with no company-side name: a
# supplier holds no register of the households it never approached (FRAME §2, bottom
# row). Nothing below crosses `company/interfaces/sim_interface.py`, and the runtime
# wall guard in `tests/simulation/test_live_population_seam.py` is what proves it.

#: Reserved tail of each year's stock. The campaign claims slots `[0, PROSPECTS_PER_YEAR)`
#: and the Profile-B trickle claims from `[PROSPECTS_PER_YEAR, +RESERVE)`, so the two
#: streams can never claim the same home however either is re-sized. 40 against a
#: Poisson(1.0) year is not a guess dressed as a margin — exhaustion RAISES rather than
#: truncating, so the cost of it being too small is a loud stop, and the cost of it being
#: generous is 40 premise draws a year at the 0.04 ms each measured below.
TRICKLE_STOCK_RESERVE = 40

#: The years the campaign runs over. Named once because the stock, the campaign and the
#: verdict must all mean the same decade; a second literal is how they stop meaning it.
CAMPAIGN_YEARS = range(2016, 2026)

#: Where the subset verdict lands for readers in later processes — the same reason
#: `book_growth_campaign.json` exists. WORLD TRUTH, and deliberately COUNTS ONLY: the
#: remainder's membership is the thing the wall forbids leaking, and a file naming 3,934
#: specific unwon homes is a register of exactly what a supplier does not have.
_SUBSET_VERDICT_RECORD = (
    Path(__file__).resolve().parent.parent
    / "docs" / "observability" / "book_subset_verdict.json"
)


#: Memo, keyed on `(year, seed)`. The same justification the campaign memo below states,
#: and the same narrow scope: a year's stock is 440 premise draws, it is resolved by the
#: campaign, by the trickle and by `world_premise_stock` within one process, and it is a
#: pure function of its key — so the memo can return the same stock faster, never a
#: different one. Measured: it takes a repeated `live_population()` from 80 ms to 10 ms.
_YEAR_STOCK_MEMO: dict = {}


def _year_stock(year: int, seed: int):
    """The addressable housing stock in `year`, campaign slots then trickle reserve."""
    from simulation.net_new_acquisition import PROSPECTS_PER_YEAR, year_premise_stock

    key = (year, seed)
    if key not in _YEAR_STOCK_MEMO:
        _YEAR_STOCK_MEMO[key] = year_premise_stock(
            year, base_seed=seed, n=PROSPECTS_PER_YEAR + TRICKLE_STOCK_RESERVE
        )
    return _YEAR_STOCK_MEMO[key]


def _trickle_stock(year: int, seed: int):
    """The trickle's reserved tail of `year`'s stock.

    A SLICE of the same object the campaign draws from, never a second stock. Two
    stocks would be two worlds, and the subset control would then be judging the book
    against whichever one the caller happened to hand it — the wrong-subject shape at
    one remove, and the exact reason `subset_verdict` matches by value.
    """
    from simulation.net_new_acquisition import PROSPECTS_PER_YEAR

    return _year_stock(year, seed)[PROSPECTS_PER_YEAR:]


def world_premise_stock(seed: int) -> tuple:
    """Every home addressable across the campaign's decade. SIM TRUTH — never a seam
    output, and no `company/**` or `saas/**` module may call it.

    Re-drawn rather than cached, the convention this module already keeps for the
    trickle and the premise register: measured 2026-08-24 at **0.16 s / 1.8 MB RSS for
    4,400 premises** (~417 bytes each), which is the first measurement of the premise
    draw's per-unit cost anywhere in the repo — `PB1_POPULATION_TARGET_AND_ITS_PRICE.md`
    §(b) and this atom's own FRAME §5 both record that no such number existed, and both
    correctly refused to infer one from the 860 bytes AO12 measured for a *customer*.
    """
    stock: list = []
    for year in CAMPAIGN_YEARS:
        stock.extend(_year_stock(year, seed))
    return tuple(stock)


def _drawn_trickle(seed: int):
    """The Profile-B trickle as `SyntheticCustomer`s, each at a claimed stock premise.

    ONE accessor for what were three identical `draw_population(...)` call sites
    (`live_population`, `_pre_growth_book`, `live_premises`). They had to agree on
    every argument or the run would hold dwellings for accounts that were not in its
    own book — the same class of drift the campaign memo's own comment records paying
    for once. Now they cannot disagree, because there is nothing left to disagree about.

    draw_region=True (ACTIVATION §1): the activated book carries REAL regions from the
    ratified curriculum marginal, not the UNKNOWN_SYNTHETIC placeholder — region is a
    PUBLIC observable the company sees at enrolment, so it belongs in the saas-shaped
    dict. The hidden `cohort` stays excluded by `to_customer_dict()` (wall).

    assign_cohorts=True (CA1, DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED §1, curriculum
    act committed e685eb76d; go/no-go in `docs/design/CA4_COHORT_ACTIVATION_SEQUENCING_
    VERDICT.md`): each drawn household carries its SIM-truth cohort at RATIFIED values
    (no tuning, R13). It rides on the HIDDEN `SyntheticCustomer.cohort`, which
    `to_customer_dict()` omits, so the OBSERVABLE stream is byte-identical to the
    no-cohort case (§2 elicitation wall — the company discovers, never reads, cohort
    structure). `assign_cohort()` draws from its OWN named substream so it cannot
    perturb the acquisition draw (C-S2), and the wall is re-proven to fire
    post-activation in `test_wall_drawn_book_never_exposes_ground_truth_cohort`.

    premise_stock_fn (PB2 step 3): the trickle's home is now a slot in the world's
    stock rather than a dwelling minted under the account's own name. Isolated the same
    way — the claim reads a pre-drawn sequence and never touches the acquisition `rng`,
    so segment, commodity, band, EAC, payment method and date are byte-identical to the
    mint (`test_the_stock_claim_does_not_perturb_the_trickle`).
    """
    from simulation.population_draw import draw_population

    return draw_population(
        seed,
        draw_region=True,
        assign_cohorts=True,
        premise_stock_fn=lambda year: _trickle_stock(year, seed),
    )


def book_subset_verdict(seed: Optional[int] = None) -> dict:
    """PB2 exit (d), judged on the SHIPPED path: is this run's book a genuine subset?

    The subject is the WHOLE drawn domestic book — the trickle AND the campaign's
    winners — because an exclusion is what would make this verdict green for free. The
    13 hand-authored founders are excluded STRUCTURALLY rather than by a filter: they
    predate the stock, carry no premise, and are not `SyntheticCustomer`s at all, so
    they are not candidates for membership in the first place. `n_founders` is reported
    anyway, because an exclusion nobody can count is an exclusion nobody can check.

    Returns `subset_verdict`'s own dict (the SAME predicate the tests judge — never a
    re-derivation of it) plus the run's context. Returns a verdict with
    `ok=False, failures=['draw_inactive']` when the population draw is off: there is no
    drawn book to be a subset of anything, and reporting that as green is the fail-open
    shape this control exists to refuse.
    """
    from simulation.population_draw import subset_verdict

    if not draw_population_enabled():
        return {"ok": False, "failures": ["draw_inactive"], "n_stock": 0,
                "n_book_domestic": 0, "n_remainder": 0}
    seed = _DEFAULT_BASE_SEED if seed is None else seed
    served = served_segments()
    book = [sc for sc in _drawn_trickle(seed) if _serves(sc.to_customer_dict(), served)]
    book += [p for p, _won_on in _campaign(_pre_growth_book(seed), seed)["winners"]]
    verdict = dict(subset_verdict(world_premise_stock(seed), book))
    verdict["n_founders"] = len([c for c in _STATIC_ROSTER if _serves(c, served)])
    return verdict


def _record_subset_verdict(seed: int) -> None:
    """Persist the verdict for readers in a later process. Never raises.

    NOT a gate, and deliberately not one. A run that assembles a book must not be
    stopped by its own measurement of that book: the verdict is evidence, and the
    control that FAILS on a bad verdict is a test
    (`tests/simulation/test_opening_book_subset.py`), which is where a control belongs
    — one that can be run against a deliberately broken world and observed to red.
    """
    try:
        _SUBSET_VERDICT_RECORD.parent.mkdir(parents=True, exist_ok=True)
        _SUBSET_VERDICT_RECORD.write_text(
            json.dumps(
                {
                    "generated_by": "simulation.live_population._record_subset_verdict",
                    "base_seed": seed,
                    **book_subset_verdict(seed),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


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

_SERVED_SEGMENTS_CURRICULUM = (
    Path(__file__).resolve().parent.parent
    / "docs" / "design" / "curriculum" / "served_segments.json"
)

#: What the company serves when the curriculum file cannot be read: EVERY segment, i.e. the
#: pre-2026-08-24 book unchanged. Fail-OPEN here and not closed, which is the opposite
#: direction to most guards in this repo and is deliberate: an unreadable curriculum file must
#: not silently DELETE accounts from a published book. Losing customers because a JSON file
#: failed to parse is a far worse published figure than serving a segment the director meant
#: to suspend, and the suspension is visible on the site the moment anyone looks.
#:
#: IMPORTED, NOT RE-DECLARED. The first version wrote the tuple out here and
#: `tools/segment_case_guard.py` refused the commit, by name: "every copy drifts, and a bare
#: `in` against a copy is case-SENSITIVE, so a lower-case spelling silently is not a member".
#: It was right twice over — the copy was redundant, and `_serves` below was doing exactly the
#: bare `in` it warns about, so an account carrying `"RESI"` or `"i&c"` would have been
#: silently suspended. `normalise_segment` fixes that as well as the duplication.


def served_segments() -> tuple[str, ...]:
    """The segments this supplier currently serves. Curriculum, the director's (R13).

    `SE_SERVED_SEGMENTS` overrides as a comma-separated list, for a measurement run without
    editing a committed file — same convention as the two sibling activations.
    """
    env = os.environ.get("SE_SERVED_SEGMENTS", "").strip()
    if env:
        return tuple(s.strip() for s in env.split(",") if s.strip())
    try:
        with open(_SERVED_SEGMENTS_CURRICULUM) as fh:
            value = json.load(fh)["served"]["value"]
        if isinstance(value, list) and value and all(isinstance(v, str) for v in value):
            return tuple(value)
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return CANONICAL_SEGMENTS


def _serves(customer: dict, served: tuple[str, ...]) -> bool:
    """Is this account one the company currently takes?

    Both sides are normalised through `simulation.segment_vocabulary`, so a roster spelling of
    `"I&C"`, `"IC"` or `"i and c"` all resolve to the same member and a curriculum file written
    in any of them means what its author meant. (The first version of this line also claimed
    `"industrial"`; it is not one of the vocabulary's aliases, and naming a spelling that in
    fact falls through to the fail-open branch is how a suspension quietly stops suspending.)

    A missing or unrecognisable `segment` is SERVED, not suspended -- the same fail-open
    direction as the default above, and for the same reason: an account with a field this
    filter cannot read must not vanish from a published book.

    THAT LAST PARAGRAPH DESCRIBED BEHAVIOUR THIS FUNCTION DID NOT HAVE (found 2026-08-24 while
    writing its control, fixed before landing). `normalise_segment` RAISES `UnknownSegmentError`
    on a present-but-unrecognised spelling -- it defaults only for a genuinely ABSENT one -- so
    the uncaught call did the exact opposite of the documented direction: a single typo in the
    director's curriculum file, or one roster row carrying a segment the vocabulary has not
    learned yet, took down every run that assembles a book rather than serving everything. A
    fail-open guard that fails HARD is the worst of both, and it is invisible until the day the
    typo happens. The raise is now caught on both sides, which is what the docstring always
    claimed and what `served_segments()`'s own default deliberately chose.
    """
    account = _canonical(customer.get("segment"))
    if account is None:
        return True
    allowed = {c for c in (_canonical(s) for s in served) if c is not None}
    if not allowed:
        # Every entry in the curriculum list was unreadable. Serving NOBODY is the one
        # outcome worse than serving everybody: it empties the published book on a typo.
        return True
    return account in allowed


def _canonical(segment) -> Optional[str]:
    """The canonical spelling of `segment`, or None if this filter cannot read it.

    Absent and unrecognised are collapsed deliberately: `_serves` treats both the same way
    (serve it), and the distinction `normalise_segment` draws between them -- defaulting for
    one, raising for the other -- is the right call for a BILLING path and the wrong one for a
    filter whose failure mode is deleting accounts from a published book.
    """
    if segment is None:
        return None
    try:
        return normalise_segment(segment, default=None)
    except UnknownSegmentError:
        return None


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
        # AFTER the memo is populated, never inside `_resolve_campaign`: the verdict
        # re-enters `_campaign` to read the winners, and computing it before the memo
        # is set would recurse forever. Recorded here rather than at the seam because
        # this is the one place a campaign is resolved exactly once per seed.
        _record_subset_verdict(seed)
    return _CAMPAIGN_MEMO[seed]


def _pre_growth_book(seed: int) -> List[dict]:
    """The roster the campaign runs AGAINST: static plus the trickle, and nothing it won.

    One function so that every caller resolves the identical campaign. It also states the
    obvious thing that would otherwise be implicit: the opening balance sheet and the opening
    account count a growth plan is built on are the ones BEFORE it grows.
    """
    served = served_segments()
    static = [c for c in _STATIC_ROSTER if _serves(c, served)]
    if not draw_population_enabled():
        return static
    return static + [
        sc.to_customer_dict()
        for sc in _drawn_trickle(seed)
        if _serves(sc.to_customer_dict(), served)
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
    import functools

    from company.interfaces.growth_desk import plan_growth_campaign_year, quote_cost_gbp
    from simulation.acquisition_funnel import run_acquisition_funnel
    from simulation.customer_events import PRICE_DIFFERENTIAL_PCT
    from simulation.net_new_acquisition import plan_growth_campaign
    from tools.credit_adapters import get_credit_bureau_adapter

    horizon = _dt.date(2026, 1, 1)
    from simulation.net_new_acquisition import PROSPECTS_PER_YEAR
    existing_cy = sum(
        max(0.0, (horizon - _dt.date.fromisoformat(c["acquisition_date"])).days / 365.25)
        for c in book
    )
    outcome = plan_growth_campaign(
        years=CAMPAIGN_YEARS,
        base_seed=seed,
        # PB2 step 3, the inversion: the campaign quotes INTO the world's stock instead
        # of minting a dwelling for each prospect it invents. The slice is the campaign's
        # half of each year's stock; `_trickle_stock` takes the tail, so the two streams
        # cannot claim the same home. This is what gives the run a remainder — the homes
        # nobody won — and therefore what makes "won, never assigned" falsifiable rather
        # than definitionally true.
        premise_stock_fn=lambda year: _year_stock(year, seed)[:PROSPECTS_PER_YEAR],
        # THE SAME OPENING CAPITAL THE RUN ITSELF USES, and getting this wrong once is why
        # the comment is here. The campaign planned from `_opening_net_assets_gbp(book)` --
        # the EAC-scaled formula -- while `run_phase2b` had already moved to the founding
        # capital figure, so the plan was sized from £12,134 and the company it was planning
        # for held £250,000. It read as a supplier that ran out of money in 2019; it was two
        # halves of one balance sheet disagreeing.
        opening_net_assets_gbp=founding_capital_gbp(
            fallback=_opening_net_assets_gbp(book)
        ),
        accounts_held_at_start=len(book),
        horizon_end=horizon,
        credit_bureau=get_credit_bureau_adapter(),
        cost_per_quote_gbp={
            seg: quote_cost_gbp(segment=seg) for seg in ("resi", "SME")
        },
        # THE SAME MARKET POSITION THE LOSS LEG IS ALREADY PRICED AT (PB3 (b1), 2026-08-25).
        # `PRICE_DIFFERENTIAL_PCT` is the run's own parameter for where this supplier's price
        # sits against the market average, and `simulation.customer_events` has been handing
        # it to the retention side since Phase NS. Binding it here rather than adding a
        # parameter to `plan_growth_campaign` keeps the campaign a pure resolver -- the
        # caller decides what the company's offer is, and the campaign only resolves it --
        # and it makes the shared input visible at the one place both legs are configured.
        # At the shipped 0.0 the multiplier is exactly 1.0 and the book is unchanged.
        run_funnel=functools.partial(
            run_acquisition_funnel, price_differential_pct=PRICE_DIFFERENTIAL_PCT
        ),
        quote_budget_fn=lambda net_assets_gbp, accounts_held, quotes_issued_to_date=0, wins_to_date=0: vars(
            plan_growth_campaign_year(
                net_assets_gbp=net_assets_gbp, accounts_held=accounts_held,
                quotes_issued_to_date=quotes_issued_to_date, wins_to_date=wins_to_date,
            )
        ),
        customer_years_already_committed=existing_cy,
    )
    LAST_CAMPAIGN.clear()
    LAST_CAMPAIGN.update({k: v for k, v in outcome.items() if k != "winners"})

    # PERSISTED, because the site has to be able to say WHICH constraint stopped the book.
    # `LAST_CAMPAIGN` lives in the run's process and dies with it, so a generator running in a
    # later process — which is every site generator — could only see the final book size and
    # not the reason it is that size. A curve flattened by our wall clock and a supplier that
    # ran out of money look identical on a chart, and the director asked for the difference
    # surfaced rather than left to be inferred (2026-08-24: "a growth curve that's an artefact
    # of our engine is an inconsistency, not a result").
    #
    # Write failures are swallowed on purpose: this is a REPORT of the run, not an input to it,
    # and a full disk must not stop a book being assembled.
    try:
        record = {
            "generated_by": "simulation.live_population._resolve_campaign",
            "by_year": outcome["by_year"],
            "notes": outcome["notes"],
            "customer_years_committed": outcome["customer_years_committed"],
            "customer_year_budget": outcome["customer_year_budget"],
            "wins": len(outcome["winners"]),
            "quotes": len(outcome["spend"]),
            "spend_gbp": round(sum(r["amount_gbp"] for r in outcome["spend"]), 2),
        }
        _CAMPAIGN_RECORD.parent.mkdir(parents=True, exist_ok=True)
        _CAMPAIGN_RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
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


def campaign_quotes_paid_for(base_seed: Optional[int] = None) -> List[dict]:
    """Every quote the growth campaign PAID FOR this run — won and lost alike.

    PB3 exit (c), the "costs a penny" clause, 2026-08-25. Until now this list existed and
    nothing spent it. `_resolve_campaign` summed it into `book_growth_campaign.json` as a
    reported total and `LAST_CAMPAIGN` held it in the run's own process, and neither is an
    account: `run_phase2b`'s `acquisition_spend_events` — the list that actually reaches
    `company.finance.accounting_close.close_the_books` and therefore the P&L — was appended
    to at exactly two sites, both inside the CHURN branch of the replacement path. Measured
    at HEAD on the shipped configuration: the campaign issued **1,295 quotes and spent
    £157,155**, the published ledger reported **£5,587.50** of acquisition spend, and the
    annual report carried **43** acquisition_spend_events. 96.4% of what this supplier spent
    winning customers was absent from its own accounts.

    That is not a reporting gap, it is the atom's own mechanism missing. The ruling names
    three — "churn, acquisition cost, and the competitor field" — and a growth curve whose
    cost is booked to a JSON file cannot be lost on price, because losing costs nothing.
    The activation record for this very campaign told the director *"Growth costs money. 245
    quotes were paid for and 231 lost"*; in the accounts they were not.

    ROWS, NOT EVENTS. This returns the campaign's own rows and stops there. `run_phase2b`
    books them through `company.interfaces.growth_desk.book_acquisition_spend`, the same door
    the replacement path uses, because what an attempt COST is company accounting and the
    world has no view of it — the wall `run_acquisition_funnel` states in its own docstring.
    A `make_acquisition_spend_event` call in this module would be the world writing the
    supplier's ledger.

    Deterministic in the seed and memoised with the campaign, so this costs nothing beyond
    the resolution `live_population()` has already paid for.
    """
    seed = _DEFAULT_BASE_SEED if base_seed is None else base_seed
    return list(_campaign(_pre_growth_book(seed), seed)["spend"])


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
    seed = _DEFAULT_BASE_SEED if base_seed is None else base_seed
    premises = {
        sc.customer_id: sc.premise
        for sc in _drawn_trickle(seed)
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
    `simulation.household.build_household_register()` takes.

    RELABELLED to the customer id, and this line is PB2 step 3 paying a debt it
    created rather than a convenience. `premise_population.draw_premise` builds its
    household with `customer_id=premise_id`, which was harmless while the two were
    the same string — that sameness WAS the false join key. Now that an account sits
    at `PSTK-2021-0401`, handing that household on unlabelled makes
    `make_household`'s "one home, one id" guard raise on every drawn account in the
    book: a control that was correct, and whose correctness rested entirely on the
    defect next door.

    The guard is kept, not weakened. What changes is that the label now says what
    the field is named after — the customer this household belongs to — and the
    binding is made HERE, at the one seam that holds both the account and the
    premise it was won at. The cross-path property the guard cannot see from inside
    `make_household` (that `live_premises` and `live_population` agree on which
    accounts exist at all, the drift the campaign memo already paid for once) is
    asserted directly in `test_live_population_seam.py` instead of inferred from an
    id collision.
    """
    import dataclasses

    return {
        cid: dataclasses.replace(premise.household, customer_id=cid)
        for cid, premise in live_premises(base_seed).items()
    }


#: Where the campaign's own record of a run lands, for generators in later processes.
_CAMPAIGN_RECORD = (
    Path(__file__).resolve().parent.parent
    / "docs" / "observability" / "book_growth_campaign.json"
)

_FOUNDING_CAPITAL_CURRICULUM = (
    Path(__file__).resolve().parent.parent
    / "docs" / "design" / "curriculum" / "founding_capital.json"
)


def founding_capital_gbp(*, fallback: float) -> float:
    """The company's opening capital. Curriculum, the director's (R13).

    LIVES HERE rather than in `run_phase2b` because this module is already the place a run's
    opening position is decided -- it assembles the book the old formula was computed FROM --
    and because `run_phase2b` imports this at module scope, so the reverse would be a cycle.

    `fallback` is the caller's own pre-existing expression, evaluated by the caller and passed
    in. That shape is deliberate: an unreadable or `null` curriculum file returns the number
    the run would have had anyway, so this can never zero a balance sheet by failing. A
    company with no capital is not a conservative default; it is a company that cannot trade.
    """
    env = os.environ.get("SE_FOUNDING_CAPITAL_GBP", "").strip()
    if env:
        try:
            return float(env)
        except ValueError:
            return fallback
    try:
        with open(_FOUNDING_CAPITAL_CURRICULUM) as fh:
            value = json.load(fh)["founding_capital_gbp"]["value"]
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return fallback
