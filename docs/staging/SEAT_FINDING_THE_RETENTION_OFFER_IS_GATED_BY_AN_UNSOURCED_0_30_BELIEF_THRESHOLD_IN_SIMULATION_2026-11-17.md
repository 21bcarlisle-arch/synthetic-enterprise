**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Claim:** `the-retention-offer-gate-values-a-kept-household-at-what-the-arm-earns` (Lane 0 delivery)

# The retention offer is gated by an unsourced 0.30 belief threshold that lives in simulation/, and candidate A's belief moves a third of the book under it

**Found by** the delivery seat on 17 Nov 2026, reading pair 11111/22222's `desk_belief_by_arm` for
`THE_VALUE_TEST_REDESIGN.md` §12c.

## The defect

`simulation/run_phase2b.py:528` sets `RETENTION_THRESHOLD = 0.30`. At line 4334, `company_est_pre > RETENTION_THRESHOLD`
decides whether a renewal is considered for a retention offer at all. Three things are wrong with it:

1. **It is a supplier decision held in the world's file.** Which households the company tries to keep is the
   company's choice, so it belongs in `company/` (the growth desk), reached through `company/interfaces/`. The whole
   guard around it (`_would_offer`, lines 4334–4560) is orchestrated in `simulation/`, though every quantity it weighs
   comes from `company.interfaces.growth_desk`. This is the wall's direction (W7, "separate the work"), not a leak of
   ground truth: everything it reads is the company's own belief and book.
2. **0.30 has no declared origin.** Nothing in the knowledge layer or the commons establishes it, and it is not in
   `tools/domain_constant_origins.py`'s reach because it lives outside `company/` and `saas/`.
3. **It is a fixed level applied to a belief whose level policy switches move.** With
   `renewal_belief_by_ending_term` on (candidate A), the value arm moves 188 of 575 (seed 11111) and 182 of 569
   (seed 22222) renewals from above 0.30 to below it, and 1 the other way. Nine of §12a's ten value-arm flips are
   households A put at 0.11–0.14 and the twin at 0.30–0.36: A made no offer, and all nine left. That is most of the
   value arm's −£1.21 per household-year.

## The end-to-end check

- *The world is wrong?* The rolls are identical across runs (§12a), so the world answered the same question both times.
- *The maths is wrong?* The threshold test runs before `_would_offer`, and the value test reads the arm's own
  `unit_rate`, which is identical at the flips. So a value-basis change cannot reach these nine. The direction item's
  step 3 was therefore not built.
- *It is not that simple?* SYN-2016-604 is above 0.30 in both runs, so one flip is something else (§12b's open row).
  And the offer itself is still unlogged in these files (§12b re-reads it).

## What the fix is (proposal, knowledge page first)

`docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` §11 (written with this finding)
holds the knowledge. Candidate 1 is a default-off switch that skips the fixed threshold when
`retention_weighs_save_odds` carries the belief into the value test. Candidate 2 calibrates the desk belief's level
before any cutoff reads it. The prediction for candidate 1 is filed in §12c. Moving the gate into the growth desk
is the wall half, and it changes no number.

Reverse: this document only records. Nothing in code changed.
