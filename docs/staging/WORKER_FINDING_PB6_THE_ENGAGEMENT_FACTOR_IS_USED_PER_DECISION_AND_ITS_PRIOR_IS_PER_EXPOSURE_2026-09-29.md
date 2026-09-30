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

## Correction and the world repair (2026-09-29, later, worker tick)

**Corrected beside the claim: an SVT stint DOES have a departure path.** Defect 1 above says "an
SVT stint has no departure path at all" and that the double-roll repair must land with a new SVT
departure hazard. That is false at HEAD. C1b's `inertia_hazard_for_term` (`run_phase2b`, the
"AN ACCOUNT ON THE STANDARD VARIABLE PRODUCT CAN NOW LEAVE" block) rolls a departure on every SVT
segment of the decision leg, and the knowledge map's route attribution has it carrying 70-87% of
the world's departures. What SVT has no path for is a *renewal decision*, which is correct. So the
world repair is the single roll alone, and it removes no churn route from any household.

**The seed alignment, verified on the live roster** (the check this finding said it had not run).
All 212 resi electricity terms that are fixed at k >= 1 had a schedule roll of active on
`{household}_{k}`, so `term_index` is the schedule index there. The departure roll then said
passive on 15 of them: 14 direct debit, 1 standard credit, 0 prepayment. That matches the
synthetic 0.94 / 0.93 / 1.00 above.

**Landed:** `household_segments.active_renewal_probability_at_a_decision(customer_id, segment)`.
It returns archetype x channel for resi, the same probability the schedule builders roll, and the
archetype alone for non-resi. The departure branch now asks it. Every resi decision reached is
active, and `PASSIVE_CHURN_CAP` stays reachable for SME renewals, which have no SVT to roll to.
Controls: `tests/simulation/test_a_renewal_is_decided_once.py`, 4 tests, 3 mutations each red.

**What this moves, downstream:** about 7% of reached resi renewal decisions lose the 0.10 passive
cap, so the renewal route's departures rise for direct debit and standard credit. The per-year
level anchor (`simulation/departure_level_anchor.py`) was fitted on captures of the old route, so
it will now read slightly high. Per the knowledge map it is a clamp owed retirement anyway. It is
not re-fitted here. The EH-2 arms were run on the pre-repair world, so they are stale. The next
step on this row is to re-run them on the repaired world. Prediction, filed now: the null arm's
prepayment factor still reads below 1.0, because the prior dominates at n~20 and nothing here
changes the prior. The planted arm still does not recover 0.307, because the plant still acts on
decisions reached and not on departure per decision. Company prior (2) still waits on the
practitioner answer.

## Re-run on the repaired world: queued (2026-09-29 21:27Z, worker tick)

The three arms are queued as ONE serial job, `longjob-pb6-eh2-rerun-repaired-world`, in a worktree
pinned at `b50a03519` (`/var/tmp/se-pb6-eh2r-b50a03519`, contains `19a58b44d`). The order is null,
then planted, then head, and the output goes to `/var/tmp/pb6_eh2r/<arm>.json`. It waits on pid
1592398, the ab5 leg `longjob-ab5-runa2c`, so it never shares the box with that leg's 10.2 GiB peak.
The declared peak is 6500 MB per arm, taken from the 6.1 GiB `run_phase2b` cycle seen at 19:07Z.
Expect the result about 1h10m after the leg finishes, plus roughly 3 x 30 min.

The predictions are the ones filed above, before this launch, and are not restated with any change:
null prepayment factor < 1.0, and planted does not recover 0.307. Grading them is the next step.

## Re-run on the repaired world: null graded, planted and head pre-registered (2026-09-30 00:40Z, seat)

The job's pinned worktree is at `b50a03519` plus one `fork_salvage` commit (`e0a72b11c`, 00:29Z)
that holds only the run's own `docs/observability/` outputs, so the code the arms run is
`b50a03519` and contains the repair `19a58b44d`.

**Null arm (finished 00:21Z): identical to its pre-repair twin in every number.** 20 prepayment
decisions, 4 lost against 6.91, factor **0.537**. Direct debit 29 of 60, standard credit 2 of 5,
book 42 of 91. That is the expected result, not a failure to run the repair: in the null world every
channel multiplier is 1.0, so the band `[p, p·m)` the repair acts on is empty and the two rolls
already agreed. The null arm is the repair's placebo, and it reads as one. **Filed prediction
(null prepayment factor < 1.0): HELD, at 0.537.**

**Pre-registered now, while planted is 20 minutes in and head has not started.** The same
reasoning, applied to the other two worlds: the repair only moves decisions for channels with
m > 1. In planted, that is direct debit (1.110) and standard credit (1.129), not prepayment (0.307).
In head, it is direct debit (1.064) and standard credit (1.083), not prepayment (0.589).

- P1. **Prepayment decisions and losses do not change in either arm**: planted 2 decisions, 0 lost;
  head 10 decisions, 1 lost.
- P2. **Direct-debit losses rise, or hold, in both arms** (pre-repair: planted 32 of 72, head 30 of
  67). A decision in the band loses the 0.10 cap. About 6-10% of reached decisions sit in the band,
  so I expect +1 to +4 losses, and the direct-debit decision count may fall by the same amount
  because a leaver reaches no later renewal.
- P3. **The prepayment factor moves only through the book's ratio**, and moves DOWN, because book
  losses rise while prepayment's do not. Planted reads in [0.55, 0.584]; head in [0.49, 0.530].
  **Filed prediction (planted does not recover 0.307): expected to HOLD.**
- P4. If P1 fails, meaning prepayment counts move, then either the repair reaches prepayment by a
  route I have not traced, or the world diverges downstream of changed departures. That would be
  the more important result.
