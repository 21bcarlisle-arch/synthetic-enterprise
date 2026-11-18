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

## Candidate 1 built (18 Nov)

The default-off switch is `retention_skips_the_belief_threshold_when_save_odds_weigh`, selected through
`company.interfaces.growth_desk.retention_considers_the_renewal`. Its control is
`tests/company/crm/test_the_belief_threshold_is_skipped_where_the_save_odds_carry_the_belief.py`. All three
mutations go red: the switch ignored, an unlearned rate admitted, and the cutoff ignored. No standing policy
moves. Still open: candidate 2 (calibration), the wall half (the gate and 0.30 move into the growth desk), and
0.30's origin. Not done here: ordering step 6's flag-0 half. DIRECTION.yaml `not_now` holds it on box memory,
and `vto-offer-reread-watch`'s 10-day deadline (armed 17 Nov 15:06) would expire before flag 1's remaining pairs
plus a flag-0 pass could finish anyway. That is a box re-plan, handed on.

## 18 Nov: what moved, and one correction (claim `the-next-lever-is-built-before-skip1-reads`)

- **Defect 2 is closed.** `RETENTION_THRESHOLD` now lives in `company/interfaces/growth_desk.py` with a declared
  origin (a named simplification, in `tools/domain_constant_origins.py`'s reach). The run loop and
  `saas/reporting/annual_report.py` import that one copy. The saas copy was a second `0.30` that said "must match".
- **Defect 1 is half closed.** The constant is the supplier's now. The guard's orchestration is still in the run loop.
- **Correction to defect 3.** "A's level is too low on this tail" was read from the leavers only. Over the whole
  value arm, A's belief **over-predicts** (O/E 0.46 on pair 1, 0.44 on pair 2), and the twin's does so more
  (0.20). So calibrating lowers the flips (to 0.03–0.04), and §12c's candidate 2 cannot re-offer them. It is built
  default off (`retention_cutoff_reads_the_calibrated_belief`) and not worth a run. 0.30 on the twin's scale is a
  realised risk of about 6%, and the cut has acted as a "top third" selector. The next lever, if skip1 refutes, is
  the cut's own scale. `THE_VALUE_TEST_REDESIGN.md` §12e; knowledge §11g.
- **Disposition, 2026-11-18 05:45Z.** `the-next-lever-is-built-before-skip1-reads` is spent: §12e landed in 7921e93a50
  before `read_threshold_skip.skip1.out` existed, candidate 2 landed default off in a391f32caa (its control is 4/4 green),
  and `/var/tmp/vts-driver/launch_hold_pairs.sh` is on disk and has not been launched. The successor
  `skip1-is-graded-against-s12es-branches` now carries the read.
