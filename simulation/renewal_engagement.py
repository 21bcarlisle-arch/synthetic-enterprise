"""The WORLD's renewal-engagement physics — whether a household actually shops.

WHY THIS FILE EXISTS (KNIFE pass 3, `A_composition_lift` step 20; disposition
register §3o). The same shape `B3_world_needs_its_own_cap_physics` cut twice
already — §3a for the price-cap schedule, §3g for the churn ceiling — found a
third time, inside the CRM-builder group of `simulation/run_phase2b.py`.

Before this, `run_phase2b` imported `company.crm.churn_model.is_active_renewal`
to roll the dice on whether a customer engages at renewal, and
`company.crm.churn_model.PASSIVE_CHURN_CAP` to clamp what that customer's
GROUND-TRUTH churn probability may reach. The company's own module labelled the
second one, in its own source, `# SIM ground-truth cap for passive churn rolls`
— a world constant filed on the company's side of the wall and imported back
across it, which is precisely §3g's finding restated.

Neither is a company belief. A real supplier does not roll a dice to decide
whether its customer shops around; it OBSERVES the outcome afterwards, from its
own books — did this account take a new fixed deal, or roll onto the standard
variable tariff. The roll is the world's, the observation is the company's, and
`event["is_active_renewal"]` is how the observation reaches the company. That
ordering is what this module restores.

WHY THE CAP IS DUPLICATED AND NOT SHARED. `PASSIVE_CHURN_CAP` here is the
world's cap on what a passive roller's real churn probability may reach.
`company.crm.churn_model.PASSIVE_CHURN_CAP` stays exactly where it is, unchanged,
as the company's ESTIMATE of that cap — it has a live company-side reader
(`estimate_passive_churn_probability`), so it is not a donated residual. Today
the two agree at 0.10 and no simulated outcome moves.

WHAT IS DELIBERATELY NOT HERE: a test pinning the two constants equal. That
would restore in the suite exactly the coupling this cut removes from the code —
the refusal recorded for `B3` (the cap schedule), `B7` (the hedge floor) and
§3g (the churn ceiling), for the fourth time here. The readings MAY drift; drift
is a finding for the harness to report, never something the suite pins shut
(R12). Independence is asserted by mutation instead — see
`tests/simulation/test_renewal_engagement.py`.

NO NUMBER MOVES. 0.35, 0.10 and the 2022 crisis year are the values the company
module already carried, and `rolls_active_renewal` reproduces
`is_active_renewal`'s draw exactly — same seed string, same comparison — so the
world's sequence is bit-for-bit what it was. What changed is who depends on whom.

THE READ DIRECTION. This module imports nothing from `company/` or `saas/`. Had
the physics been moved here with a company import intact it would have traded a
class-(b) crossing for a class-(a) one, the strictly forbidden direction, which
is at zero and stays there.
"""

from __future__ import annotations

# ~65% of domestic/SME customers roll to SVT by inaction at term end (passive).
# SVT inertia data: Ofgem Consumer Engagement Surveys 2018-2019; CMA 2016 investigation.
PASSIVE_RENEWAL_RATE = 0.35         # probability a renewal is "active" (picks a new fix)

# The world's ceiling on a passive roller's realised churn probability. Passive
# rollers are inert: whatever the rate move, only so many of them actually leave.
PASSIVE_CHURN_CAP = 0.10

# Crisis years (2022 in UK): no fixed deals available — ALL renewals are forced
# passive, because suppliers withdrew fixed tariffs as wholesale costs exceeded
# the Ofgem price cap.
CRISIS_PASSIVE_YEARS = frozenset({"2022"})


def rolls_active_renewal(
    term_start_str: str,
    seed: str,
    active_probability: float | None = None,
) -> bool:
    """Return True if this renewal is an 'active' choice, False if a passive SVT roll.

    `active_probability` defaults to the flat population-wide PASSIVE_RENEWAL_RATE
    (35%) when not supplied. The caller may thread a per-customer probability here
    instead (`simulation/household_segments.py`'s engagement archetype), so a
    household's active/passive/disengaged trait is persistent across its whole
    tenure rather than a fresh coin-flip every renewal.

    Crisis years force all renewals passive regardless of the probability passed.
    """
    import random as _rnd
    year = term_start_str[:4]
    if year in CRISIS_PASSIVE_YEARS:
        return False
    threshold = PASSIVE_RENEWAL_RATE if active_probability is None else active_probability
    return _rnd.Random(f"active_renewal_{seed}").random() < threshold


def passive_churn_cap_for(active_renewal: bool) -> float | None:
    """The world's churn cap that applies to this renewal, or None if it is active.

    An active renewer shops the market and the full churn physics applies to them
    unclamped; only the inert SVT roller gets the cap.
    """
    return None if active_renewal else PASSIVE_CHURN_CAP


__all__ = [
    "CRISIS_PASSIVE_YEARS",
    "PASSIVE_CHURN_CAP",
    "PASSIVE_RENEWAL_RATE",
    "passive_churn_cap_for",
    "rolls_active_renewal",
]
