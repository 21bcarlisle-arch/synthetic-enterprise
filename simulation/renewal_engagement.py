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

NO NUMBER MOVED WHEN THIS FILE WAS CUT, AND ONE HAS MOVED SINCE. The cut itself
moved nothing: 0.35, 0.10 and the 2022 crisis year were the values the company
module already carried, and `rolls_active_renewal` reproduced `is_active_renewal`'s
draw exactly — same seed string, same comparison. **Corrected 2026-09-04, beside
the claim rather than over it:** the crisis-year forcing has since been replaced by
`FTC_WITHDRAWAL_WINDOW`, which runs to 2023-06-30, for the published fidelity reason
recorded at the constant. So the world's sequence is NO LONGER bit-for-bit the
company module's for a boundary in H1 2023, and that divergence is deliberate — it
is the world moving onto the record while the company's ESTIMATE of the same fact
stays where it is, which is exactly the independence this cut exists to allow.
0.35 and 0.10 have not moved.

THE READ DIRECTION. This module imports nothing from `company/` or `saas/`. Had
the physics been moved here with a company import intact it would have traded a
class-(b) crossing for a class-(a) one, the strictly forbidden direction, which
is at zero and stays there.
"""

from __future__ import annotations

from datetime import date

# ~65% of domestic/SME customers roll to SVT by inaction at term end (passive).
# SVT inertia data: Ofgem Consumer Engagement Surveys 2018-2019; CMA 2016 investigation.
PASSIVE_RENEWAL_RATE = 0.35         # probability a renewal is "active" (picks a new fix)

# The world's ceiling on a passive roller's realised churn probability. Passive
# rollers are inert: whatever the rate move, only so many of them actually leave.
PASSIVE_CHURN_CAP = 0.10

# ═══════════════════════════════════════════════════════════════════════════════════════
# THE FTC WITHDRAWAL WINDOW — A SUPPLY-SIDE FACT WITH DATES, NOT A CALENDAR YEAR
# ═══════════════════════════════════════════════════════════════════════════════════════
#
# This used to read `CRISIS_PASSIVE_YEARS = frozenset({"2022"})` and the C1B decision of
# 2026-08-30 named the consequence and parked the repair in one sentence:
# *"2023 at 26.9%. `CRISIS_PASSIVE_YEARS` holds `{"2022"}` only. The published record has
# fixed deals withdrawn until April 2023. Extending the set is a world change with a
# published reason and belongs in its own decision, not folded into this one."*
# This is that decision (2026-09-04).
#
# WHAT THE RECORD ESTABLISHES, and it is about AVAILABILITY, which is what this branch
# models — whether there was a fixed deal to take, not whether the household wanted one:
#   * fixed tariffs withdrawn market-wide as wholesale exceeded the cap ceiling, so no
#     viable fixed product could be offered (`docs/market_research/
#     svt_rates_active_passive_2016_2025.md` §3; switching volumes "2022: near zero
#     (fixed deals withdrawn)");
#   * *"Following the re-emergence of FTCs in the second half of 2023"* — Ofgem, State of
#     the Market April 2025, quoted in `tools/published_tariff_mix.DEFAULT_TARIFF_SHARE`
#     for 2023. H2 2023 begins 2023-07-01, so the last day the record says a household
#     had no fixed deal to take is 2023-06-30.
#
# WHY THE END DATE IS THE RE-EMERGENCE STATEMENT AND NOT THE APRIL 2023 STOCK READING.
# "~29m of ~32m domestic customers on SVT by April 2023" is a STOCK: it says where
# households were, not what was on offer, and a stock stays inverted for months after
# supply returns. The re-emergence sentence is the only published statement about
# availability itself, and availability is this branch's subject.
#
# NOT FITTED, AND CHECKABLE THAT IT WAS NOT. The window's endpoints come from the two
# statements above and from nothing about the generated share. `tools/svt_generated_share_check`
# remains the CHECK and never an input (`simulation/svt_product.py` is explicit that a split
# set to land in range hides the defect it is set to mask). The share this move produces is
# recorded in `docs/staging/SEAT_FINDING_THE_WORLDS_FIXED_DEAL_SHARE_IS_OUTSIDE_THE_PUBLISHED_
# BAND_IN_EVERY_YEAR_2026-09-04.md` beside the prediction written before it was run — including
# that it does NOT bring 2023 into band, which a fitted window would have.
#
# R13: the baseline moves for a fidelity reason, decided blind to company results. The
# direction is known and it runs against us — more households on SVT is a smaller reachable
# surface for the value arm and less measured margin. Recorded here so that a later "it made
# the numbers worse" cannot be read as a reason to undo it.
FTC_WITHDRAWAL_WINDOW: tuple[date, date] = (date(2022, 1, 1), date(2023, 6, 30))


def ftc_withdrawn_at(term_start_str: str) -> bool:
    """True if the published record says no fixed deal was available to take on that date.

    Inclusive of both endpoints: `FTC_WITHDRAWAL_WINDOW[1]` is the LAST day of withdrawal,
    not the first day of supply, because the sourced statement is about the half-year that
    follows it.
    """
    lo, hi = FTC_WITHDRAWAL_WINDOW
    return lo <= date.fromisoformat(term_start_str[:10]) <= hi


def fully_withdrawn_years() -> frozenset[str]:
    """The calendar years the window covers end to end, as year strings.

    DERIVED, never declared. A year is in here only if a household reaching a boundary on
    ANY day of it had no fixed deal to take, so a control keyed to this set is making the
    strongest claim that is true of a whole year. 2023 is deliberately absent: the window
    ends mid-year and half of 2023 had supply, so demanding no fixed term start in 2023
    would be asserting the world stay wrong in the other direction.
    """
    lo, hi = FTC_WITHDRAWAL_WINDOW
    return frozenset(
        str(y) for y in range(lo.year, hi.year + 1)
        if lo <= date(y, 1, 1) and date(y, 12, 31) <= hi
    )


#: The fully-withdrawn calendar years, for the controls that were keyed to a year set before
#: the window existed. It is a VIEW of `FTC_WITHDRAWAL_WINDOW`, not a second home for the
#: fact — widen the window over another whole year and this follows without an edit.
CRISIS_PASSIVE_YEARS: frozenset[str] = fully_withdrawn_years()


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

    A boundary inside the FTC withdrawal window is forced passive regardless of the
    probability passed: there was no fixed deal to take, so the household's own
    willingness to shop does not arise.
    """
    import random as _rnd
    if ftc_withdrawn_at(term_start_str):
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
    "FTC_WITHDRAWAL_WINDOW",
    "PASSIVE_CHURN_CAP",
    "PASSIVE_RENEWAL_RATE",
    "ftc_withdrawn_at",
    "fully_withdrawn_years",
    "passive_churn_cap_for",
    "rolls_active_renewal",
]
