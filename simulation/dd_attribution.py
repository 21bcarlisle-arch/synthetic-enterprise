"""W2_10_dd_attribution_confound -- hidden DD SELECTION-BIAS truth (world-side SIM).

WHAT THIS IS
------------
The hidden TRUE causal structure of a direct-debit (DD) channel-attribution
confound -- the FIRST entry of the named class "selection-bias traps the company
must discover it is falling into". Customers who are on DD differ SYSTEMATICALLY
from those who are not: they are more financially ORGANISED and (partly for that
same reason, not because of DD) carry a lower TRUE arrears risk. So a naive
analysis that attributes the DD cohort's better outcomes TO the DD channel
OVER-CREDITS DD -- most of the observed gap is SELECTION, not treatment.

This module holds the two quantities apart, as ground truth:

  * ``delta_true``  -- the GENUINE causal treatment effect of DD (the do-operator:
                       the same customer's arrears risk on DD vs not-on-DD). Small
                       and real: DD automates the payment, so a few "forgot to pay"
                       misses are genuinely removed. This is the ANSWER KEY.
  * ``delta_naive`` INGREDIENTS -- the per-customer OBSERVABLES a real supplier
                       holds (which channel a customer is on; whether they fell
                       into arrears). A naive channel-attribution analytics
                       aggregates ONLY these into ``delta_naive`` = (arrears rate
                       among non-DD) - (arrears rate among DD). It is much larger
                       than ``delta_true`` because the DD cohort is pre-selected
                       clean. The company-side twin (C12) computes ``delta_naive``
                       from these observables and the harness scores the GAP
                       = |delta_naive - delta_true| / |delta_naive| = the fraction
                       of the DD "business case" that is confound artefact.

This is the archetypal trap: the surface correlation is real (DD customers DO
have lower arrears), and the wrong causal reading of it is exactly the mistake a
real supplier's DD-discount business case makes. Ofgem itself has publicly noted
"a generalised shift ... to direct debit has reduced the numbers of customers who
fell into arrears" -- the precise surface correlation this atom warns against
reading as pure causation.

THE HIDDEN/OBSERVABLE SEAM (Architectural Law -- the company cannot see inside)
------------------------------------------------------------------------------
Everything about the CAUSAL MECHANISM is HIDDEN SIM ground truth. The company can
NEVER read a customer's ``organisation`` latent, ``dd_selection_prob``, income
decile, or -- crucially -- the COUNTERFACTUAL arrears probability under the channel
the customer is NOT on (``counterfactual_arrears_prob``). Those are the ANSWER
KEY. The company observes ONLY ``payment_channel`` and the realised ``had_arrears``
outcome -- exactly what a real supplier's billing system records. The whole
difficulty is that from those two observables alone the selection and the
treatment are NOT separable; that is why real suppliers fall into this trap.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
-----------------------------------------------------
WORLD/sim code. It MUST NOT import ``company.*`` or ``saas.*``. It reads the
sibling world module ``simulation.household_budget`` (W2_4) to COUPLE the DD
selection to hidden affordability (below) -- a sim->sim read, never a wall
crossing. Every record carries ``data_regime="synthetic"`` (a curriculum draw).

COUPLING TO AFFORDABILITY (W2_4) -- why the confound is REAL and consistent
--------------------------------------------------------------------------
The DD selection is not free-floating: it is correlated with the SAME hidden
affordability the household-budget twin (W2_4) already draws. A customer's hidden
``organisation`` latent is a blend of (a) an idiosyncratic conscientiousness draw
(a low-income customer CAN be highly organised -- organisation is not income) and
(b) the affordability signal from ``draw_household_budget`` (income decile). Both
DD adoption AND the true arrears hazard fall as organisation rises, so organisation
is a genuine COMMON CAUSE (a back-door path) of channel and outcome -- the textbook
shape of a confound. Because it is read from the same W2_4 budget, a customer who
is affordability-stressed in the budget twin is consistently the customer who is
less likely to be on DD and more likely to fall into arrears here -- one coherent
hidden person, not two contradictory draws.

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md -- non-negotiable, the 01:09Z incident)
--------------------------------------------------------------------------------
Every stochastic element draws from THIS subsystem's OWN named, seeded substream
(``_substream(base_seed, name)`` -> an isolated ``random.Random`` seeded from a
STABLE sha256 of ``W2_10_dd_attribution::<name>::<base_seed>``). It NEVER touches
the global ``random`` module and can NEVER shift another subsystem's sequence --
population_draw, life_events, household_budget and sme_distress stay byte-identical
no matter how much this one is advanced (proven by the isolation tests). The W2_4
coupling reads ``draw_household_budget`` (its OWN isolated substreams), so drawing
a DD profile never perturbs the budget twin either. Each mechanism draws from its
OWN named substream, so a future mechanism APPENDS a name and can never shift an
existing one.

DETERMINISTIC REPLAY (C-S2): same ``(customer_id, seed)`` -> byte-identical
profile every run, across processes (sha256/md5, never Python's salted ``hash()``).

BASELINE vs CURRICULUM (R13) / anti-goal-seek (R12, Law A)
---------------------------------------------------------
The SELECTION STRENGTH, the organisation->arrears protection, and the genuine DD
treatment effect are DIAGNOSTIC CURRICULUM instruments -- director-authored,
NEVER tuned toward a company P&L, a target arrears rate, or a target gap. The
whole point of the atom is that reality does NOT hand you the selection/treatment
decomposition; tuning these to make a gap "look right" would defeat it.

ANCHORS & HONEST SIMPLIFICATIONS (R10, dated 2026-07-13; provenance:
docs/market_research/dd_attribution_confound_w2_10.md + the atom's own DISCOVER
passes recorded in docs/design/maturity_map.yaml, W2_10)
-------------------------------------------------------------------------------
- ANCHORED [L]: UK payment-method mix ~74% direct debit / 13% standard credit /
  13% prepayment (Ofgem, 2026, recorded in the W2_10 DISCOVER pass). Modelled here
  as a BINARY DD-vs-non-DD world with ``_TARGET_DD_SHARE=0.74``; non-DD folds
  standard-credit AND prepayment together (26%). SIMPLIFICATION (R10): prepayment
  has its own distinct physics (pay-as-you-go, self-disconnection -- W2_8's scope)
  and is not separated here; this atom's confound is DD-vs-everything-else.
- ANCHORED [L] direction only: standard credit carries a HIGHER Ofgem price cap
  because it "reflects the additional costs and risks in servicing" that cohort --
  the real regulator's own methodology already treats payment-method cohorts as
  structurally different-risk populations. That is the DIRECTION this module
  encodes (non-DD => higher arrears risk); the MAGNITUDE split into selection vs
  treatment is NOT published (see next).
- SIMPLIFICATION (R13, deliberately un-anchorable): there is NO published
  decomposition of the DD arrears gap into SELECTION vs TREATMENT -- that missing
  decomposition IS the trap, and real suppliers cannot see it either. So
  ``_SELECTION_STRENGTH``, ``_ORG_ARREARS_PROTECTION_K`` and
  ``_DD_TREATMENT_MULT`` are director-curriculum diagnostics, overridable, never
  claimed as measured and never tuned toward a gap.
- ANCHORED [L] plausibility band only: ~5.3 million people live in households in
  debt to their energy supplier (Citizens Advice, ~19% of GB households). The
  population realised arrears rate here is a DIAGNOSTIC that should land in a
  plausible band around that scale (R12 sanity flag, not a target).
- SIMPLIFICATION (R10): channel is modelled as a STATIC per-customer selection
  (organised customers select INTO DD). The DYNAMIC variant the atom's FRAME pass
  named -- failing payers being pushed OFF DD over time, landing their bad debt in
  the credit cohort -- is the SAME confound by a time-varying mechanism; it is an
  acknowledged extension (would make ``payment_channel`` event-responsive, per the
  FRAME note), not silently assumed away. Either mechanism produces the identical
  selection bias this atom exists to expose.
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from simulation.household_budget import draw_household_budget

STREAM_NAMESPACE = "W2_10_dd_attribution"

# Named RNG substreams -- one per stochastic mechanism (C-S2). Adding a future
# mechanism APPENDS a name; it can never shift an existing substream's sequence.
_SUBSTREAMS: Tuple[str, ...] = (
    "organisation",       # idiosyncratic conscientiousness (organisation is not income)
    "selection",          # DD-adoption Bernoulli draw
    "arrears_realisation",  # the realised arrears outcome under the ACTUAL channel
)


# ---------------------------------------------------------------------------
# CURRICULUM constants (R13 diagnostics) -- see ANCHORS above. Overridable.
# ---------------------------------------------------------------------------

# ANCHORED [L]: 74% of UK consumers pay by direct debit (Ofgem, 2026). Binary
# DD-vs-non-DD; non-DD folds standard credit + prepayment (26%).
_TARGET_DD_SHARE = 0.74

# Weight of the affordability signal (W2_4 income decile) inside the organisation
# latent vs the idiosyncratic conscientiousness draw. Organisation is CORRELATED
# with affordability but NOT determined by it (a low-income person can be highly
# organised) -- so the idiosyncratic part carries the majority weight.
_AFFORDABILITY_WEIGHT = 0.40      # W2_4 coupling weight
_IDIOSYNCRATIC_WEIGHT = 0.60      # own-substream conscientiousness weight

# SELECTION (R13, un-anchorable): how strongly organisation predicts DD adoption.
# P(DD | organisation) = sigmoid(intercept + strength * (organisation - 0.5)).
# The intercept is set so P(DD) ~ _TARGET_DD_SHARE at the mean organisation (~0.5).
_SELECTION_STRENGTH = 3.0
_SELECTION_INTERCEPT = math.log(_TARGET_DD_SHARE / (1.0 - _TARGET_DD_SHARE))  # logit(0.74)

# ARREARS hazard for a FULLY DISORGANISED (organisation=0), non-DD customer, over
# the observation window. Organisation protects multiplicatively: exp(-k * org).
# _DD_TREATMENT_MULT (<1) is the GENUINE causal benefit of DD automation -- the
# ONLY thing that legitimately belongs to the channel. delta_true derives from it.
_BASE_ARREARS_HAZARD = 0.28
_ORG_ARREARS_PROTECTION_K = 1.20   # exp(-1.2) ~ 0.30x arrears for the most organised
_DD_TREATMENT_MULT = 0.85          # DD genuinely removes ~15% of arrears (automation)


# ---------------------------------------------------------------------------
# Named RNG substreams -- the C-S2 heart of this module.
# ---------------------------------------------------------------------------
def _substream(base_seed: int, name: str) -> random.Random:
    """Return an ISOLATED ``random.Random`` for a named mechanism substream.

    Seed is a STABLE sha256 of ``W2_10_dd_attribution::<name>::<base_seed>`` (never
    Python's per-process-salted ``hash()``), so the same (base_seed, name) yields
    the same stream across processes -- a hard C-S2 requirement. Each name seeds an
    independent generator, so a draw here can never consume from, or shift, any
    other substream (of this or any other subsystem).
    """
    key = f"{STREAM_NAMESPACE}::{name}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _base_seed_for(customer_id: str, seed: Optional[int]) -> int:
    """Resolve the base seed. Stable md5 of the customer_id when no explicit seed
    is given (the built-in ``hash()`` is salted per process and would break replay).
    """
    if seed is not None:
        return seed
    return int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _arrears_prob(organisation: float, on_dd: bool) -> float:
    """The hidden TRUE arrears probability (the structural equation, answer key).

    p = base * exp(-k * organisation) * (dd_mult if on_dd else 1). Organisation is
    the CONFOUND channel (it lowers arrears AND raises DD adoption); dd_mult is the
    only genuinely causal DD effect. Clipped to [0, 1].
    """
    p = _BASE_ARREARS_HAZARD * math.exp(-_ORG_ARREARS_PROTECTION_K * organisation)
    if on_dd:
        p *= _DD_TREATMENT_MULT
    return max(0.0, min(1.0, p))


DIRECT_DEBIT = "direct_debit"
NON_DD = "standard_credit"  # non-DD: standard credit + prepayment folded in (R10)


@dataclass(frozen=True)
class CustomerDDProfile:
    """One customer's full hidden DD-attribution truth (world-side ground truth).

    The company reads ONLY ``payment_channel`` and ``had_arrears`` (the OBSERVABLE
    ingredients a naive channel-attribution analytics aggregates). Everything else
    -- ``organisation``, ``dd_selection_prob``, ``income_decile`` and the two
    structural arrears probabilities -- is the ANSWER KEY, harness-only.
    """
    customer_id: str
    # -- OBSERVABLE (what a real supplier's billing system records) -----------
    payment_channel: str          # DIRECT_DEBIT | NON_DD
    had_arrears: bool             # realised outcome under the ACTUAL channel

    # -- ANSWER KEY (HIDDEN causal truth; company must NEVER read these) -------
    organisation: float           # hidden latent in [0, 1]
    dd_selection_prob: float      # P(on DD | organisation) -- the selection model
    income_decile: int            # from the coupled W2_4 budget (hidden)
    true_arrears_prob_dd: float   # structural P(arrears | do(DD))
    true_arrears_prob_non_dd: float  # structural P(arrears | do(non-DD))
    data_regime: str = "synthetic"

    # -- OBSERVABLE accessors -------------------------------------------------
    @property
    def on_dd(self) -> bool:
        return self.payment_channel == DIRECT_DEBIT

    # -- ANSWER KEY -----------------------------------------------------------
    def counterfactual_arrears_prob(self, on_dd: bool) -> float:
        """The do-operator: this customer's arrears prob FORCED onto a channel,
        holding organisation fixed. The company can never see this -- it only ever
        observes the realised outcome under the ONE channel the customer is on."""
        return self.true_arrears_prob_dd if on_dd else self.true_arrears_prob_non_dd

    def individual_treatment_effect(self) -> float:
        """The GENUINE per-customer causal effect of DD on arrears probability:
        P(arrears | do(non-DD)) - P(arrears | do(DD)) >= 0. This is the honest
        thing the DD channel is responsible for; ``delta_true`` is its mean."""
        return self.true_arrears_prob_non_dd - self.true_arrears_prob_dd


def generate_dd_attribution(
    customer_id: str,
    seed: Optional[int] = None,
) -> CustomerDDProfile:
    """Generate one customer's hidden DD-attribution truth, deterministically.

    Deterministic in ``(customer_id, seed)`` (C-S2). Selection and the arrears
    realisation draw from this subsystem's OWN named substreams; the organisation
    latent additionally reads the coupled W2_4 budget's income decile (its own
    isolated substreams) so the confound is consistent with the affordability twin.
    """
    base_seed = _base_seed_for(customer_id, seed)

    # -- organisation latent: idiosyncratic conscientiousness (own substream)
    #    blended with the coupled W2_4 affordability signal (income decile). --
    idiosyncratic = _substream(base_seed, "organisation").random()  # U(0,1)
    budget = draw_household_budget(customer_id, base_seed=None)      # W2_4 coupling
    affordability = (budget.income_decile - 1) / 9.0                 # decile -> [0,1]
    organisation = (
        _IDIOSYNCRATIC_WEIGHT * idiosyncratic + _AFFORDABILITY_WEIGHT * affordability
    )
    organisation = max(0.0, min(1.0, organisation))

    # -- SELECTION: organised customers select INTO DD (own substream) --------
    dd_selection_prob = _sigmoid(
        _SELECTION_INTERCEPT + _SELECTION_STRENGTH * (organisation - 0.5)
    )
    on_dd = _substream(base_seed, "selection").random() < dd_selection_prob
    channel = DIRECT_DEBIT if on_dd else NON_DD

    # -- structural arrears probs (answer key) + realised outcome (own sub) ----
    p_dd = _arrears_prob(organisation, on_dd=True)
    p_non_dd = _arrears_prob(organisation, on_dd=False)
    p_actual = p_dd if on_dd else p_non_dd
    had_arrears = _substream(base_seed, "arrears_realisation").random() < p_actual

    return CustomerDDProfile(
        customer_id=customer_id,
        payment_channel=channel,
        had_arrears=had_arrears,
        organisation=round(organisation, 6),
        dd_selection_prob=round(dd_selection_prob, 6),
        income_decile=budget.income_decile,
        true_arrears_prob_dd=round(p_dd, 6),
        true_arrears_prob_non_dd=round(p_non_dd, 6),
    )


def draw_dd_cohort(
    n: int,
    id_prefix: str = "DDC",
    seed: Optional[int] = None,
) -> List[CustomerDDProfile]:
    """Draw a cohort of ``n`` hidden DD-attribution profiles (deterministic).

    Each customer gets a distinct id; ``seed`` (when given) offsets the per-customer
    seed so a whole cohort is reproducible as a unit without collapsing to one draw.
    """
    profiles: List[CustomerDDProfile] = []
    for i in range(n):
        cid = f"{id_prefix}{i:06d}"
        s = None if seed is None else seed + i
        profiles.append(generate_dd_attribution(cid, seed=s))
    return profiles


# ---------------------------------------------------------------------------
# The two effects the coupled triad scores. delta_true is the ANSWER KEY (causal);
# the naive effect uses OBSERVABLES ONLY -- exactly what the C12 twin will compute.
# ---------------------------------------------------------------------------

def population_true_treatment_effect(profiles: Sequence[CustomerDDProfile]) -> float:
    """``delta_true`` -- the mean genuine causal effect of DD on the arrears
    probability, via the do-operator over the population (ANSWER KEY). This is the
    honest ceiling on what a DD-discount business case could legitimately claim."""
    if not profiles:
        return 0.0
    return sum(p.individual_treatment_effect() for p in profiles) / len(profiles)


def population_naive_channel_effect(profiles: Sequence[CustomerDDProfile]) -> float:
    """``delta_naive`` computed the way a NAIVE company analytics would -- from the
    OBSERVABLES ONLY (``payment_channel``, ``had_arrears``): the observed arrears
    rate among non-DD customers minus the observed rate among DD customers.

    This intentionally reads NO hidden field. It over-states the DD benefit because
    the DD cohort is pre-selected clean -- exactly the trap. Provided here as the
    world-side DEMONSTRATION of the confound; the live ``delta_naive`` in the
    coupled triad is the C12 twin's own computation from the same observables.
    """
    dd = [p for p in profiles if p.on_dd]
    non_dd = [p for p in profiles if not p.on_dd]
    if not dd or not non_dd:
        return 0.0
    rate_dd = sum(p.had_arrears for p in dd) / len(dd)
    rate_non_dd = sum(p.had_arrears for p in non_dd) / len(non_dd)
    return rate_non_dd - rate_dd


def naive_ingredients(profiles: Sequence[CustomerDDProfile]) -> dict:
    """The raw OBSERVABLE ingredients the C12 twin needs to build ``delta_naive``
    itself -- per-channel counts and arrears counts, no hidden field touched. The
    twin (or the coupling harness) forms delta_naive from these and the gap against
    ``population_true_treatment_effect`` later (COUPLED_TRIAD; gap_metric)."""
    dd = [p for p in profiles if p.on_dd]
    non_dd = [p for p in profiles if not p.on_dd]
    return {
        "n_dd": len(dd),
        "n_non_dd": len(non_dd),
        "arrears_dd": sum(p.had_arrears for p in dd),
        "arrears_non_dd": sum(p.had_arrears for p in non_dd),
        "dd_share": (len(dd) / len(profiles)) if profiles else 0.0,
    }
