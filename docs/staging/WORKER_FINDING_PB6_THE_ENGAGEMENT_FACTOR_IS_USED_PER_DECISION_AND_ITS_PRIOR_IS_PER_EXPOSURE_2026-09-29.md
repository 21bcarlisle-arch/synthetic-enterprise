**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `PB6_the_engagement_observable_crosses_the_seam`

# PB6 after EH-2: the factor is used per decision, its prior is per exposure, and the world decides one renewal twice

**2026-09-29.** This is the next step `726502fa7` named: settle whether the engagement rate is per
renewal decision or per unit of exposure, before any remedy on either side of the wall.

## The definition, settled

**The factor is a per-decision quantity because that is where it is used.** It multiplies
`company_est_pre`, the probability that this account leaves AT THIS RENEWAL. That estimate decides
whether a retention offer is made (see EH-4). So the evidence for it has to be per decision, and the
ledger already counts closed fixed-renewal decisions. **The ledger's denominator is right. No
company-side remedy to the likelihood is owed.**

**The prior is the wrong quantity for that use.** CIM w6 reports households that switched in the
last six months. That is a rate per household-time, and it breaks into two factors:

    CIM channel ratio  =  (decisions reached, relative)  x  (departure per decision, relative)

Nothing published separates those two factors. So 0.585 is a prior on the product, applied as
though it were the second factor alone. **That is a named gap, not a constant to re-pick.** Per the
knowledge-first rule, the code must carry it explicitly. Today the docstring names only the
arrears-overlap gap. It does not name this one.

## Measured: in this world, the whole ratio is in the first factor

Two rolls answer "is this household active at this renewal":

- `renewals.build_renewal_schedule` (and the gas leg in `run_phase2b`) rolls
  `rolls_active_renewal(start, f"{household}_{k}", active_renewal_probability_for_customer(h))`.
  That is the archetype x the **channel multiplier**, and it decides fixed term vs SVT stint.
- The departure branch (`run_phase2b` ~2359) rolls
  `rolls_active_renewal(start, f"{billing_account}_{term_index}", active_renewal_probability(level))`.
  That is the **archetype alone**, and it decides uncapped churn vs `PASSIVE_CHURN_CAP`.

The seed string is the same. C1b's comment states `len(terms)` and `term_index` are one index, and
`billing_account` is `household_of(cid)`. **I have not re-verified that on a live schedule.** Given
that, it is one uniform read against two thresholds. Conditional on reaching a fixed term
(`U < p·m`), the departure branch is active iff `U < p`:

    20,000 synthetic households x renewals k=1..5, HEAD world
    prepayment       m=0.589  reached 0.210 of rolls  active|reached 1.000
    direct_debit     m=1.064  reached 0.370           active|reached 0.940
    standard_credit  m=1.083  reached 0.373           active|reached 0.926

For any channel with `m <= 1`, every decision reached is uncapped. For `m > 1`, the band
`[p, p·m)` reaches a fixed term and is then charged the passive cap. **So per decision, this world
makes a prepayment household slightly MORE likely to leave than a direct-debit one.** The channel
effect lives entirely in how many decisions a household reaches. That is EH-2 prediction 3 from the
other side: the decision counts ran 20 / 10 / 2, ordered exactly as the plant.

What follows for the company's reading: with enough evidence, a correct per-decision learner
converges at or above 1.0 for prepayment in this world. The 0.585 prior pulls it the other way.
EH-2's null and head arms both read about 0.53, dragged there by the prior on 10-20 decisions.

## Two defects, one on each side, and neither is the EH-1 rule

1. **WORLD (sim lane, fidelity): one event answered twice.** A household's engagement at a renewal
   has one answer, and today it has two that disagree in the `[p, p·m)` band. The single-roll
   repair (the departure branch reads `active_renewal_probability_for_customer`) makes every
   resi decision reached active. That leaves `PASSIVE_CHURN_CAP` reachable only for non-resi, and
   it exposes the larger gap under it: **an SVT stint has no departure path at all.** A real SVT
   household can switch at any time, with no exit fee. That is where most 2016-2020 switching
   happened, and it is also where CIM's per-exposure rate lives. Repairing the double roll without
   an SVT departure hazard would remove the only churn that passive households face. So the two
   are one sim-lane build, not two. It is a level change to the world's churn, and it is justified
   on fidelity, blind to company results.
2. **COMPANY (declared gap): the prior's quantity.** The CIM ratio is a per-exposure marginal
   applied per decision. Nothing publishes the split. The honest shape is a prior on the
   per-decision factor, centred where the evidence puts it (unknown, so 1.0) with CIM's spread as
   its width. It must not be a re-picked point. That also moves EH-4 (offers withheld from
   prepayment) in the mission's direction. It changes company behaviour, so it lands together with
   the world repair, not before it. Otherwise the company is tuned against a world known to be
   wrong.

## The practitioner question (sent to the director on NTFY)

"When a prepayment customer comes to the end of a fixed deal, are they less likely to switch than a
direct-debit one? Or is their lower switching all in never getting to a fixed deal, sitting on the
default tariff?" No published source separates these. If the answer is "less likely at the
decision too", then some of CIM's ratio belongs in the per-decision factor, and the prior should
keep part of it.

## Next

The world repair in (1) is the next build on this row, in the sim lane, with the practitioner answer
setting how the company prior in (2) is centred. PB6 stays at L2 in build.
