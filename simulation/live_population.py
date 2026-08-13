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
    return list(CUSTOMERS) + drawn
