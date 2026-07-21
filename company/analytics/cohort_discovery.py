"""D-SEGMENT company-side cohort discovery -- the BELIEVED half of the
coupled-triad segmentation pair (SEGMENTATION_GENERATOR_BUILD_PLAN.md step 3;
`docs/design/SEGMENTATION_RECONCILIATION_FRAME.md` §0 CANONICAL WALL RULING).

CANONICAL WALL RULING (verbatim, director console 2026-07-21): "Segmentation
ground truth lives entirely behind the wall. The company starts with
public-data priors only (EPC, census -- what a real supplier could obtain),
and discovers everything else exclusively through acquisition and ongoing
interaction, scored on the belief-vs-truth gap. No segment label, attitude,
or sensitivity ever crosses the wall directly."

This module builds the company's BELIEVED cohort for a customer from TWO
kinds of input, both genuinely obtainable by a real UK energy supplier:

  1. PUBLIC PRIORS -- `PublicPriorObservation` -- what a supplier can get from
     signup + an address alone: the customer's REGION (self-disclosed /
     postcode-derived), TENURE (self-disclosed at signup -- real suppliers
     routinely ask homeowner-vs-tenant for tariff/billing-eligibility reasons;
     FRAME §0's own words: "tenure IS a public prior the company holds from
     day one"), and heating_fuel (readable per-account via an EPC certificate
     + gas MPRN lookup, "the one Need axis readable per-account" per the wall
     map) -- all THREE known to high accuracy from day one. accommodation/
     cars/NS-SeC are census facts published only AT AREA LEVEL (the wall
     ruling's own phrase for the REST of the census block) -- a real supplier
     does not ask "how many cars do you own" at signup, so the company's
     belief for an INDIVIDUAL customer on those three axes is the NATIONAL
     census-area MARGINAL (the modal category is the point estimate), not
     that customer's true individual value -- a genuine, structural,
     never-fully-closing gap, not a bug to "fix" by reading more accurately
     than a real supplier could.

     THE CONCRETE COUPLED-TRIAD GAP THIS BUYS (FRAME §0's "consequence for
     the recoupling"): the company KNOWS tenure, yet has no mechanism here
     that conditions accommodation/cars/nssec belief ON that known tenure
     (no fused conditional structure exists company-side, matching the fusion
     register's own conservative-crossing default) -- so a real, measurable,
     non-tautological gap opens between the flat national prior this module
     holds and the SIM's TRUE tenure-conditioned block distribution
     (`simulation.population_draw`'s own tilted block draw), worst where the
     true conditional distribution diverges most from the flat national one
     (e.g. social_rent's true accommodation mix skews hard to flats). That
     is exactly what `tools/couple_cohort.py` measures.

  2. INTERACTION OBSERVABLES -- `InteractionObservation` -- signals a supplier
     accumulates over the relationship: a rate-change churn-response estimate
     (the observable proxy for price_sensitivity: `SimInterface.
     get_churn_estimate`, per the wall map) and the channel the customer
     actually used to make contact (the observable proxy for channel_pref).
     Both REFINE the belief once evidence exists; absent evidence, the belief
     stays at its national marginal (C-S1: the discovery is allowed to see
     partial/absent observables, it never assumes a complete batch).

green_stance is STRUCTURALLY EXCLUDED: `BelievedCohort.green_stance` is
always None. There is NO real-world observable for it (attitudes are never
openly observed jointly with fabric/tech/behaviour -- landscape section E gap,
`population_fusion_assumptions_register.json`) -- this module must never grow
a green_stance inference, however tempting a "proxy" might look, because
inventing one would BE the wall violation this module exists to avoid.

EPISTEMIC WALL. This module imports NOTHING from `simulation.*` / `sim.*` (the
generic scan, `tools/epistemic_verifier`, enforces this on every company/
file) and calls NO `SimInterface` method itself -- callers (the HARNESS,
`tools/couple_cohort.py`) are responsible for gathering observable inputs and
constructing `PublicPriorObservation` / `InteractionObservation`, exactly the
separation `couple_w2_4_c6.py` already uses for C6_affordability_inference
(the company module works on an observation dataclass, never touches the seam
directly -- one less place the wall could be crossed by accident).

The census/EPC PRIOR TABLES below are this module's OWN independently-sourced
constants -- duplicated, per the WALL DISCIPLINE convention already
established by `simulation/population_draw.py`'s own duplicated-constants
precedent, NOT imported from `simulation.population_draw` (that import would
itself be the violation). Small numeric differences from the SIM-side
generator's own tables are expected and honest -- this is the company's own
belief, built blind to the SIM's generator, not a mirror of it (R15
independence: the two sides must be separately authored for the measured gap
to be real, not a tautology).

R12/R13: nothing here is tuned toward any measured gap. The belief thresholds
are domain-reasoned (what genuinely counts as evidence of high price
sensitivity), set blind to the SIM curriculum's own marginals.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

# ---------------------------------------------------------------------------
# Axis taxonomy -- structural, mirrors the schema's level names so a
# `BelievedCohort` and the harness's SIM-truth `Cohort` are directly
# comparable cell-for-cell. Duplicated (not imported) per the WALL DISCIPLINE
# convention -- see module docstring.
# ---------------------------------------------------------------------------
TENURE_LEVELS: tuple[str, ...] = ("own_outright", "own_mortgage", "private_rent", "social_rent")
ACCOMMODATION_LEVELS: tuple[str, ...] = ("detached", "semi", "terraced", "flat", "caravan")
CARS_LEVELS: tuple[str, ...] = ("0", "1", "2plus")
NSSEC_LEVELS: tuple[str, ...] = ("higher", "intermediate", "routine_semi", "unemployed_student")

# ---------------------------------------------------------------------------
# The company's OWN census/EHS AREA-LEVEL priors (independently duplicated;
# see module docstring). These are the company's DAY-ONE, undiscovered belief
# for tenure/accommodation/cars/nssec -- a flat national marginal, because
# real open census data publishes these facts at AREA level, not per
# individual (the wall ruling's own distinction). The MODAL category is the
# point-estimate belief; the full distribution is exposed too (`*_prior`
# dicts) for a harness that wants the TV-distance belief vector directly
# rather than a collapsed point estimate.
# ---------------------------------------------------------------------------
TENURE_PRIOR: Dict[str, float] = {
    "own_outright": 0.2275, "own_mortgage": 0.195, "private_rent": 0.19, "social_rent": 0.16,
}
ACCOMMODATION_PRIOR: Dict[str, float] = {
    "detached": 0.23, "semi": 0.26, "terraced": 0.26, "flat": 0.24, "caravan": 0.01,
}
CARS_PRIOR: Dict[str, float] = {"0": 0.235, "1": 0.424, "2plus": 0.341}
NSSEC_PRIOR: Dict[str, float] = {
    "higher": 0.35, "intermediate": 0.24, "routine_semi": 0.29, "unemployed_student": 0.12,
}


def _modal(prior: Dict[str, float]) -> str:
    return max(prior, key=lambda k: prior[k])


# ---------------------------------------------------------------------------
# Observable inputs -- what the harness gathers on the company's behalf.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PublicPriorObservation:
    """Facts a real supplier holds from signup + an address, from day one.

    `region`: self-disclosed / postcode-derived -- known exactly.
    `tenure`: self-disclosed at signup (FRAME §0: "tenure IS a public prior
    the company holds from day one") -- known exactly when disclosed; Optional
    because a real signup can leave it blank (C-S1: an absent observable is
    simply absent, not a zero -- the belief then falls back to the national
    tenure prior's modal category).
    `heating_fuel`: EPC certificate + gas MPRN lookup -- "the one Need axis
    readable per-account" (wall map). Optional: a real EPC/MPRN lookup can
    fail (property not yet EPC-registered, no gas connection recorded).
    """
    customer_id: str
    region: str
    tenure: Optional[str] = None
    heating_fuel: Optional[str] = None


@dataclass(frozen=True)
class InteractionObservation:
    """Accumulated relationship signals -- OBSERVABLE-ONLY, gathered by the
    harness via `company.interfaces.sim_interface.SimInterface` (this module
    itself never touches the seam -- see module docstring).

    `churn_estimate`: the company's own `get_churn_estimate(...)` output for
    this customer's most recent rate-change renewal (the price_sensitivity
    proxy named in the wall map). None if the customer has never faced a
    rate change yet.
    `contact_channels_used`: the channel(s) the customer has actually used to
    contact the supplier (the channel_pref proxy). Empty if no contact has
    happened yet.
    """
    customer_id: str
    churn_estimate: Optional[float] = None
    contact_channels_used: Sequence[str] = field(default_factory=tuple)


# Price-sensitivity discovery thresholds -- domain-reasoned bands on the
# company's OWN churn-estimate output (a probability in [0, 0.95] per
# `SimInterface.get_churn_estimate`'s own docstring), set blind to the SIM
# curriculum's price_sensitivity marginals (R15 independence / R12 no
# goal-seek: never tuned to move the measured gap).
_PRICE_SENSITIVITY_HIGH_THRESHOLD = 0.45
_PRICE_SENSITIVITY_LOW_THRESHOLD = 0.15


def _infer_price_sensitivity(churn_estimate: Optional[float]) -> Optional[str]:
    """None (no belief yet) until a real rate-change response exists."""
    if churn_estimate is None:
        return None
    if churn_estimate >= _PRICE_SENSITIVITY_HIGH_THRESHOLD:
        return "high"
    if churn_estimate <= _PRICE_SENSITIVITY_LOW_THRESHOLD:
        return "low"
    return "medium"


# channel_pref: the MODE of channels actually used, mapped onto the schema's
# 3-level taxonomy. A real supplier's own contact-channel taxonomy is richer
# (email/app/webchat/post/branch); this collapses them the same way a
# real CRM's own reporting layer would, not a fabricated new taxonomy.
_CHANNEL_TO_PREF: Dict[str, str] = {
    "app": "digital", "web": "digital", "email": "digital", "webchat": "digital", "digital": "digital",
    "phone": "phone", "ivr": "phone",
    "post": "assisted", "branch": "assisted", "in_person": "assisted", "assisted": "assisted",
}


def _infer_channel_pref(contact_channels_used: Sequence[str]) -> Optional[str]:
    if not contact_channels_used:
        return None
    counts: Dict[str, int] = {}
    for ch in contact_channels_used:
        mapped = _CHANNEL_TO_PREF.get(ch, None)
        if mapped is None:
            continue
        counts[mapped] = counts.get(mapped, 0) + 1
    if not counts:
        return None
    return max(counts, key=lambda k: counts[k])


@dataclass(frozen=True)
class BelievedCohort:
    """The company's BELIEVED cohort for one customer. Every field is either
    a genuinely-observable read (region, heating_fuel) or a discovered/prior
    belief (tenure/accommodation/cars/nssec/price_sensitivity/channel_pref).
    `green_stance` is ALWAYS None -- structurally excluded, see module
    docstring. This dataclass MUST NEVER be constructed from, or compared
    against, `simulation.population_draw.Cohort` inside company/ code -- that
    comparison is the harness's job (`tools/couple_cohort.py`), which sits
    OUTSIDE the wall by design."""
    customer_id: str
    region: str
    heating_fuel: Optional[str]
    tenure: str
    accommodation: str
    cars: str
    nssec: str
    price_sensitivity: Optional[str]
    channel_pref: Optional[str]
    green_stance: None = None


def discover_cohort(
    prior_obs: PublicPriorObservation,
    interaction_obs: Optional[InteractionObservation] = None,
) -> BelievedCohort:
    """Build the company's believed cohort for one customer from its own
    observables. `interaction_obs` is optional (C-S1: a brand-new customer
    with zero interaction history yields a belief resting entirely on the
    public-prior modal categories -- a real, honest, un-refined starting
    belief, not an error)."""
    if interaction_obs is None:
        interaction_obs = InteractionObservation(customer_id=prior_obs.customer_id)

    # tenure: directly disclosed (FRAME §0) -- falls back to the national
    # modal category only when genuinely undisclosed (C-S1). accommodation/
    # cars/nssec have NO discovery mechanism here (no fused conditional
    # structure company-side, matching the fusion register's conservative
    # default) -- they stay at the flat national prior REGARDLESS of the
    # tenure the company already knows. That gap (known tenure, un-conditioned
    # block belief) is the concrete measurement `tools/couple_cohort.py` takes.
    tenure = prior_obs.tenure if prior_obs.tenure in TENURE_LEVELS else _modal(TENURE_PRIOR)

    return BelievedCohort(
        customer_id=prior_obs.customer_id,
        region=prior_obs.region,
        heating_fuel=prior_obs.heating_fuel,
        tenure=tenure,
        accommodation=_modal(ACCOMMODATION_PRIOR),
        cars=_modal(CARS_PRIOR),
        nssec=_modal(NSSEC_PRIOR),
        price_sensitivity=_infer_price_sensitivity(interaction_obs.churn_estimate),
        channel_pref=_infer_channel_pref(interaction_obs.contact_channels_used),
    )


def believed_book_distribution(axis: str, population: List[BelievedCohort],
                               levels: Sequence[str],
                               fallback_prior: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """The company's believed distribution over one axis's levels across a
    population -- the vector the harness feeds into `background.gap_metric.
    belief_gap`. A None belief (price_sensitivity/channel_pref pre-discovery)
    falls back to the axis's own national prior share (if given) rather than
    silently dropping the customer -- C-S1, an unresolved belief still counts
    as SOME belief (the un-refined prior), not an absence from the book."""
    if not population:
        raise ValueError("believed_book_distribution: empty population")
    counts: Dict[str, float] = {lvl: 0.0 for lvl in levels}
    for bc in population:
        value = getattr(bc, axis)
        if value is None:
            if fallback_prior is None:
                raise ValueError(
                    f"believed_book_distribution: {bc.customer_id} has no {axis} belief "
                    "and no fallback_prior was given"
                )
            for lvl in levels:
                counts[lvl] += fallback_prior.get(lvl, 0.0)
            continue
        if value not in counts:
            raise ValueError(f"believed_book_distribution: unknown level {value!r} for axis {axis}")
        counts[value] += 1.0
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("believed_book_distribution: degenerate population (zero total weight)")
    return {lvl: v / total for lvl, v in counts.items()}
