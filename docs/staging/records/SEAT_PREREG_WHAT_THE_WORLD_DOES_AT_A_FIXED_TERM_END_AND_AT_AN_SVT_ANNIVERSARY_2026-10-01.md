**Severity:** LATENT · **Lane:** B_commercial (world side: `simulation/`) · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon (upstream world fidelity)

# Pre-registration: what the world does at a fixed-term end, and at an SVT anniversary

Claim `a-passive-fixed-term-end-is-a-decision-point-in-the-world`. Filed 2026-10-01 ~06:50 BST,
BEFORE any figure below is computed. Subject:
`WORKER_FINDING_THE_WORLD_ROLLS_NO_DEPARTURE_AT_A_PASSIVE_FIXED_TERM_END_THOUGH_THE_LICENCE_MAKES_IT_A_DECISION_POINT_2026-10-01.md`.

## Knowledge first: done, and it establishes no rate

`docs/market_research/first_renewal_departure_rate_small_gb_supplier.md` already ran the search.
The one route-conditioned published figure is Ofgem's 2019 End of Fixed Term trial: control arm
**external 6%, internal 14%, overall 19%** within six weeks, on a 17-year-tenure incumbent book
selected for high roll-over. Nothing publishes the rate for a small supplier's switched-in book.
`FIRST_RENEWAL_DEPARTURE_PRIOR` stays `None`.

## The question the item did not ask: what "passive" means

The item reads "65% of term ends get no exit" as a defect. But the world's partition at a term end
is **active (shops) / passive (does nothing)**, and leaving is a kind of shopping. A household that
does nothing cannot depart at a term end, in the world or in the trial. The trial's 81% who did
nothing also left at 0%. **The quantity the licence makes a decision point is the term end as a
whole**: P(exit at term end) = P(active) × P(exit | active). A passive branch that also rolls a
departure would count one exit route twice.

There is a second confusion. `rolls_active_renewal` is also consulted at the acquisition
anniversary of a household already on SVT. That is not a term end in law, so the "65%" may not be
a share of term ends at all.

## The measurement

One world: PB4's run at `aed6bf966` (`/var/tmp/se-pb4-shock-out/run.log`). World code is
byte-identical to HEAD `55d343a35` (`git diff --stat aed6bf966 HEAD -- simulation/ sim/ company/`
is empty). No new run. Electricity leg, resi accounts. Every non-first boundary at an acquisition
anniversary is classified:

- **FIXED END:** the term closing at the boundary is a fixed term.
- **SVT ANNIVERSARY:** the boundary closes an SVT stint.

The outcome is **active** if the next term is fixed and **passive** if it is SVT. An **exit** is a
`[CHURN]` line for that account dated at the boundary. `[CHURN-SVT]` lines are counted separately:
they are the C1b inertia route.

## Predictions

- **P1.** SVT anniversaries are at least 30% of all the draws `rolls_active_renewal` makes, so "65%
  of term ends" overstates the passive share at genuine fixed ends.
- **P2.** At fixed ends outside the FTC withdrawal window, the passive share is 55–75%.
- **P3.** The exit rate at fixed ends outside the window is 8–18%: above the trial's 6% external
  floor on the least mobile book. The internal/external split among those who act, 0.36 in the
  world, is close to the trial's 6/19 = 0.32.
- **P4.** Exits at SVT anniversaries (an active re-draw, then a churn) are non-zero, and number at
  least 25% of the run's `[CHURN-SVT]` count. That is a second exit route for SVT households
  beside the C1b hazard.

## Decision rule, written now

- **If P3 holds** (exit rate at fixed ends ≥ 6% outside the window): no passive departure roll is
  added. It would double-count, and the item's "flatters the company" is not shown at the fixed
  end. Done is this finding plus a control that a genuine fixed end CAN produce an exit.
- **If the rate is below 6%:** the world undershoots the published floor even on an inert book. A
  term-end roll is warranted. It goes on the whole term end, not on the passive branch, and its
  size is a named gap.
- **P4 is measured, not changed.** That is the item's instruction for the duplication question.
