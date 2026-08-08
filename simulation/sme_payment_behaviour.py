"""W2_sme_segment_case_normalisation -- the SME/microbusiness payment-outcome
model.

WHY THIS MODULE HAD TO EXIST BEFORE THE CASE BUG COULD BE FIXED
---------------------------------------------------------------
`simulation/arrears_engine.payment_outcome()` branches on
`_IC_SEGMENTS = ("ic", "I&C")` INSIDE its bacs/chaps arm. SME was never in
that tuple, so once an SME bill reached the corporate rail the function fell
through to a bare `return ("success", 0)` -- an SME could never be late, never
fail, never dispute. The case-sensitivity bug was MASKING that: because "SME"
never matched `== "sme"`, C5/C6 were routed to the residential model, which at
least models failure. Normalising the case alone would have moved them onto
the corporate rail and DELETED their bad debt outright (measured on the real
population: 3 failed payments and 3 arrears cases).

So the fix is: an anchored SME outcome model, then the case normalisation.
Not the other way round, and not one without the other.

ANCHORS (R13 baseline -- decided BLIND to company P&L, CITED not invented)
--------------------------------------------------------------------------
1. TIER SHARES -- Ofgem, "Businesses' experiences of the energy market 2025",
   published May 2026 (fieldwork 26 Aug - 1 Oct 2025; telephone survey of
   1,002 GB businesses, IFF Research; question D6: "Which ONE of the following
   statements BEST describes how well your business has been keeping up with
   [gas/electricity] bills over the past 12 months?"). Figure 4.4, all
   businesses:
       keeping up without any difficulties ............ 70%
       keeping up, but a struggle from time to time ... 19%
       keeping up, but a constant struggle ............  6%
       falling behind with some bills .................  1%
       real financial problems, in debt to supplier ...  1%
       real financial problems, behind with many bills . <1%
   Banner totals: keeping up 70%, struggling to some degree 25%, in
   debt/falling behind 2%. The ~3% residual is don't-know/refused.

   SIZE: the same report states sole traders and microbusinesses struggle MORE
   than average -- 26% vs the 25% all-business average (medium 16%, large
   12%). Ofgem does NOT publish the 19/6 sub-split by business size, so the
   all-business RATIO between "from time to time" and "constant struggle"
   (19:6) is applied to the microbusiness TOTAL of 26%. That is an anchored
   ratio applied to a size-specific total -- the same honesty convention
   `simulation/payment_behaviour_source.py` already documents for its non-DD
   sub-split, not a fabricated figure.

2. AGGREGATE LATE RATE -- Department for Business & Trade, "Late payments
   research: understanding variations in payment performance and practices
   across business sectors and sizes", published 19 September 2024 (300
   telephone interviews, 3-31 January 2024). Businesses AS PAYERS of their
   own supplier invoices: mean 7% of supplier invoices are not paid within the
   agreed timeframe; 81% of businesses report under 10% late. An energy bill
   IS a supplier invoice to the business, so this is the right direction of
   measurement -- what a business does when a supplier bills it.

   `SME_TARGET_LATE_RATE = 0.07` is that published mean, and the per-tier
   probabilities below are SOLVED so the population-weighted late rate equals
   it (see `_solve_late_scale`). The aggregate is therefore derived from the
   anchor rather than pinned by hand.

WHAT IS ESTIMATED, AND SAID SO (R10/ANCHORED-NOISE honesty)
------------------------------------------------------------
- `_LATE_RELATIVE_BY_TIER` -- the SHAPE of lateness across tiers. Neither
  source publishes "how many bills does a struggling business pay late", only
  how many businesses struggle (Ofgem) and what share of invoices are late in
  aggregate (DBT). The relative weights below are a labelled ESTIMATE. What is
  NOT estimated, and what the tests actually assert, is (a) the ORDERING --
  lateness is monotone non-decreasing in hardship, which is the only claim
  either source supports -- and (b) the population AGGREGATE, which is pinned
  to the DBT anchor. Tests assert the anchored properties, never the estimated
  intermediates.
- `SME_BEHIND_FAILURE_RATE` -- the share of an already-behind business's bills
  that actually fail. Informed by Ofgem's own sub-split ("falling behind with
  SOME bills" 1% vs "behind with MANY bills" <1%, i.e. "some" dominates), but
  the number itself is an ESTIMATE.

THE FAILURE MODEL IS READ OFF THE QUESTION WORDING, NOT INVENTED
-----------------------------------------------------------------
D6's first three options all say "KEEPING UP with bills" -- with no
difficulty, with an occasional struggle, with a constant struggle. A business
that is keeping up is, by the question's own words, paying. So the three
keeping-up tiers produce LATENESS and never a failure; only the BEHIND tier
(the 2% who are falling behind / in debt to the supplier) produces failed
payments. That is a reading of the source, which is why SME bad debt survives
this change instead of being deleted by it.

PER-CUSTOMER, NOT PER-BILL (why the tier is drawn from the customer id)
-----------------------------------------------------------------------
D6 classifies a BUSINESS over 12 months, not an invoice. Drawing a fresh tier
per bill would reproduce the right aggregate while destroying the thing that
makes it real: a chronically-struggling SME. It would also make
`payment_behaviour_source.classify_payment_pattern()` unable to ever return
CHRONIC. So the tier is drawn ONCE per customer from that customer's own named
sha256-seeded substream (C-S2 substream discipline -- never the global
`random`, never a substream shared with another subsystem), and is stable for
that customer across every bill. Where no customer id is available the tier
falls back to a draw from the caller's rng, which reproduces the population
mixture but not the persistence; that is documented at the call site rather
than hidden.

CURRICULUM vs BASELINE (R13, Law A)
------------------------------------
Every constant here is BASELINE -- real-world fidelity, decided blind to
company P&L. There is no scenario switch and this module must never be tuned
because company results look wrong. Note in particular that the SME failure
LEVEL falls out of Ofgem's 2%; it was not chosen to produce any particular
bad-debt number.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
-----------------------------------------------------
Pure WORLD/sim code. Imports no `company.*` or `saas.*`.
"""
from __future__ import annotations

import hashlib
import random

from simulation.segment_vocabulary import SME, normalise_segment

#: Hardship tiers, ordered least to most hardship. The names mirror Ofgem
#: D6's own answer options.
TIER_NONE = "NO_DIFFICULTY"
TIER_OCCASIONAL = "OCCASIONAL_STRUGGLE"
TIER_CONSTANT = "CONSTANT_STRUGGLE"
TIER_BEHIND = "FALLING_BEHIND"

#: Ordered least -> most hardship. Several invariants below depend on this
#: ordering being the real one, so it is declared once here.
TIERS_BY_HARDSHIP = (TIER_NONE, TIER_OCCASIONAL, TIER_CONSTANT, TIER_BEHIND)

# --- Anchor 1: Ofgem D6 (2025), as PUBLISHED. Raw percentages, so the
# derivation below is auditable against the report rather than being a set of
# pre-chewed decimals nobody can check. -----------------------------------
OFGEM_D6_ALL_BUSINESS_PCT = {
    TIER_NONE: 70.0,        # "keeping up with bills without any difficulties"
    TIER_OCCASIONAL: 19.0,  # "keeping up, but a struggle from time to time"
    TIER_CONSTANT: 6.0,     # "keeping up, but it is a constant struggle"
    TIER_BEHIND: 2.0,       # banner total: falling behind / in debt to supplier
}

#: Ofgem 2025: sole traders and microbusinesses struggling = 26% (vs the 25%
#: all-business average). This is the size-specific figure the SME segment
#: should use.
OFGEM_MICROBUSINESS_STRUGGLING_PCT = 26.0

#: Ofgem does not publish "in debt / falling behind" by business size, so the
#: all-business figure is carried across unchanged rather than guessed.
OFGEM_BEHIND_PCT = OFGEM_D6_ALL_BUSINESS_PCT[TIER_BEHIND]


def _microbusiness_tier_shares() -> dict[str, float]:
    """Derive the SME tier shares from the published Ofgem figures.

    The two struggling tiers are rescaled so they sum to the MICROBUSINESS
    total (26%) while keeping the published 19:6 ratio between them; the
    behind tier keeps the all-business figure; whatever is left of 100% after
    the don't-know residual is removed becomes the no-difficulty tier. The
    result is renormalised to sum to exactly 1.0, because a probability
    distribution must -- Ofgem's own columns sum to ~97% (the rest is
    don't-know/refused, which is not an outcome a bill can have).
    """
    published_struggling = (
        OFGEM_D6_ALL_BUSINESS_PCT[TIER_OCCASIONAL]
        + OFGEM_D6_ALL_BUSINESS_PCT[TIER_CONSTANT]
    )
    scale = OFGEM_MICROBUSINESS_STRUGGLING_PCT / published_struggling
    raw = {
        TIER_NONE: (
            OFGEM_D6_ALL_BUSINESS_PCT[TIER_NONE]
            - (OFGEM_MICROBUSINESS_STRUGGLING_PCT - published_struggling)
        ),
        TIER_OCCASIONAL: OFGEM_D6_ALL_BUSINESS_PCT[TIER_OCCASIONAL] * scale,
        TIER_CONSTANT: OFGEM_D6_ALL_BUSINESS_PCT[TIER_CONSTANT] * scale,
        TIER_BEHIND: OFGEM_BEHIND_PCT,
    }
    total = sum(raw.values())
    return {tier: pct / total for tier, pct in raw.items()}


#: The SME hardship distribution, derived from the published figures above.
SME_TIER_SHARES = _microbusiness_tier_shares()

# --- Anchor 2: DBT late-payments research (2024) --------------------------
#: Mean share of supplier invoices a business pays after the agreed timeframe.
SME_TARGET_LATE_RATE = 0.07

#: ESTIMATE (see module docstring): the relative shape of lateness across
#: hardship tiers. Only the ORDERING is anchored; the scale is solved.
_LATE_RELATIVE_BY_TIER = {
    TIER_NONE: 1.0,
    TIER_OCCASIONAL: 10.0,
    TIER_CONSTANT: 20.0,
    TIER_BEHIND: 20.0,
}

#: ESTIMATE: of an already-behind business's bills, the share that actually
#: fail rather than merely arriving late.
SME_BEHIND_FAILURE_RATE = 0.35

#: Reused from `arrears_engine._CORP_BACS_DISPUTE_PROB` rather than
#: re-derived. DBT 2024 does record that 31% of businesses attribute late
#: payment to disputed invoices, which supports SMEs disputing at least as
#: much as large corporates -- but that is a share of BUSINESSES, not of
#: INVOICES, so it cannot be turned into a per-bill dispute probability
#: without inventing the conversion. Inheriting the already-calibrated
#: corporate figure is the honest move; raising it would be fabricated
#: precision.
SME_DISPUTE_PROB = 0.007

#: Days-late range for a late SME payment. Reused from
#: `arrears_engine._CORP_LATE_DAYS` -- an SME on BACS is on the same
#: commercial payment terms as any other business customer, and inventing a
#: second range would be the duplicate-calibration problem `arrears_engine`'s
#: docstring exists to prevent.
SME_LATE_DAYS = (14, 45)


def _solve_late_scale() -> float:
    """Scale the estimated per-tier shape so the population-weighted rate of
    bills NOT SETTLED ON TIME equals the DBT anchor exactly.

    The anchor's own wording is "supplier invoices [not] paid within the
    agreed timeframe", which a disputed or failed invoice also is -- so the
    quantity pinned to 7% is `late + failed + disputed`, not lateness alone.
    Disputes and failures are drawn FIRST in `sme_payment_outcome()`, so they
    pre-empt the lateness draw; this solve subtracts them from the budget and
    scales the remainder over the bills that actually reach that draw.

    Solved, never pinned: if a tier share, the failure rate, or a relative
    weight changes, the aggregate stays on the anchor instead of silently
    drifting off it.
    """
    dispute = SME_DISPUTE_PROB
    survives_dispute = 1.0 - dispute
    failed = survives_dispute * SME_TIER_SHARES[TIER_BEHIND] * SME_BEHIND_FAILURE_RATE

    budget = SME_TARGET_LATE_RATE - dispute - failed
    if budget <= 0:
        raise ValueError(
            "dispute + failure already exceed the anchored not-on-time rate; "
            "the shape cannot be solved"
        )

    weighted_shape = survives_dispute * sum(
        SME_TIER_SHARES[tier]
        * (1.0 - (SME_BEHIND_FAILURE_RATE if tier == TIER_BEHIND else 0.0))
        * _LATE_RELATIVE_BY_TIER[tier]
        for tier in TIERS_BY_HARDSHIP
    )
    if weighted_shape <= 0:
        raise ValueError("late-rate shape must be positive to solve a scale")
    return budget / weighted_shape


#: Per-bill probability that an SME pays LATE, by hardship tier. For the
#: BEHIND tier this is the probability of lateness among bills that did not
#: outright fail.
SME_LATE_PROB_BY_TIER = {
    tier: min(1.0, _LATE_RELATIVE_BY_TIER[tier] * _solve_late_scale())
    for tier in TIERS_BY_HARDSHIP
}


def _tier_substream(customer_id: str) -> random.Random:
    """This subsystem's OWN named, sha256-seeded substream for the hardship
    draw (C-S2). Keyed on the customer id alone, so a customer's tier is
    stable for their whole history and independent of how many bills any
    other customer has, of iteration order, and of every other subsystem's
    draws.
    """
    digest = hashlib.sha256(
        ("sme_payment_behaviour::hardship_tier::%s" % customer_id).encode("utf-8")
    ).hexdigest()
    return random.Random(int(digest[:16], 16))


def _draw_tier(rng: random.Random) -> str:
    """Draw one hardship tier from `SME_TIER_SHARES` using `rng`."""
    r = rng.random()
    cumulative = 0.0
    for tier in TIERS_BY_HARDSHIP:
        cumulative += SME_TIER_SHARES[tier]
        if r < cumulative:
            return tier
    return TIERS_BY_HARDSHIP[-1]


def hardship_tier(customer_id: str | None, rng: random.Random | None = None) -> str:
    """The SME's hardship tier (Ofgem D6 class).

    With a `customer_id`, the tier comes from that customer's own substream
    and is STABLE across their whole billing history -- the per-business
    persistence D6 actually measures. Without one, it is drawn from `rng`,
    which reproduces the population mixture but not the persistence.
    """
    if customer_id is not None:
        return _draw_tier(_tier_substream(customer_id))
    if rng is None:
        raise ValueError("hardship_tier needs either a customer_id or an rng")
    return _draw_tier(rng)


def sme_payment_outcome(rng: random.Random, customer_id: str | None = None):
    """Return `(outcome, days_late)` for one SME bill.

    Mirrors `simulation.arrears_engine.payment_outcome()`'s contract exactly:
    outcome is one of "success"/"failed"/"dispute", and a late-but-paid bill
    is a "success" with a non-zero `days_late`.

    Draw order is fixed (dispute, then failure, then lateness) so that adding
    a branch later cannot silently reshuffle an existing sequence.
    """
    tier = hardship_tier(customer_id, rng)

    if rng.random() < SME_DISPUTE_PROB:
        return ("dispute", 0)

    if tier == TIER_BEHIND and rng.random() < SME_BEHIND_FAILURE_RATE:
        return ("failed", 0)

    if rng.random() < SME_LATE_PROB_BY_TIER[tier]:
        return ("success", rng.randint(*SME_LATE_DAYS))

    return ("success", 0)


def is_sme(segment) -> bool:
    """True iff `segment` is the SME market segment, in ANY spelling.

    The one sanctioned SME test. Every caller routes through here rather than
    comparing a literal, which is what makes the case defect structurally
    unable to come back.
    """
    return normalise_segment(segment) == SME
