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

WALL / R13 ACTIVATION — DIRECTOR-RESERVED (held, escalated):
  Flipping this flag on changes WHICH WORLD the company faces every run — a
  CURRICULUM act reserved to the director (W2_2's own ruling "the agent may
  STAGE the integration but must not flip it on"; the 2026-07-24 waiver
  preserved "curriculum values remain director-reserved"). This module
  therefore ships the mechanism DEFAULT-OFF and does NOT wire itself into any
  run entrypoint — both wiring the ~19 `run_phase*` entrypoints to consume this
  seam AND flipping the flag are the escalated irreducible core, held for the
  director. Building the seam is the reversible part of the ESCALATION_IS_NTFY
  decompose (build the reversible half; escalate + hold the core).

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

import os
from typing import List, Optional

from saas.customers import CUSTOMERS

# Director-reserved activation flag (R13 curriculum). Default OFF.
_ACTIVATION_ENV = "SE_DRAW_POPULATION"

# Fixed base seed so the drawn cohort is deterministic + replayable (C-S2).
# This is a MECHANISM default (determinism), NOT a curriculum knob — the
# curriculum decision is on/off (director-reserved); the seed only fixes which
# deterministic draw the "on" state yields.
_DEFAULT_BASE_SEED = 20260724


def draw_population_enabled() -> bool:
    """True iff the director-reserved activation flag is set. Default OFF."""
    return os.environ.get(_ACTIVATION_ENV, "") == "1"


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
    drawn = [sc.to_customer_dict() for sc in draw_population(seed, draw_region=True)]
    return list(CUSTOMERS) + drawn
