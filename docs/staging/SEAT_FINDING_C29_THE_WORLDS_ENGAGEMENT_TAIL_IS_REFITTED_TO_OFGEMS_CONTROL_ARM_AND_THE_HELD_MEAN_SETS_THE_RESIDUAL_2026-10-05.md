**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables`

# The world's engagement tail is refitted to Ofgem's control arm, and the held 35% mean sets the residual

Claim `c29-refit-the-worlds-per-renewal-engagement-to-ofgems-sustained-engagement-control` (step 1 of
the order in `SEAT_FINDING_C29_THE_WORLDS_ENGAGEMENT_TAIL_IS_TWICE_TOO_STICKY_…`). At draw time the
duplicate-work note named this same id as already held. The only holder was this invocation (`ps`
showed no rival seat or `surgical_land` on the subject), so the note was the draw's own write.

## What moved

`simulation/household_segments._ACTIVE_RENEWAL_PROBABILITY_BY_ENGAGEMENT`: 0.65 / 0.15 / 0.02 →
**0.50 / 0.24 / 0.20**. The shares 0.45 / 0.35 / 0.20 are unchanged (R13), and so is the population
mean (0.349). The 3+-year default cohort now chooses within 17 months at **0.338**, against Ofgem's
0.33; it was 0.150. Within-cohort persistence is now **×1.26**, against the source's ×0.94; it was ×2.64.
The fit, the table and the prediction graded against the pre-registration are in
`docs/market_research/does_a_households_renewal_engagement_persist.md` §5.

## The residual, said plainly

×1.26 is just above the ~×1.18 the source's interval admits. It is the floor while the sourced ~35%
mean is held: the mean keeps ACTIVE near 0.50. Free the mean and the best fit is flat 0.26, which
deletes the archetypes and lowers the book's choose rate to 0.26. That is a level move, and level
is R13's lever, so this refit does not take it. My pre-registered ×1.1–1.2 was wrong.

## What now disagrees downstream

- **C29's grading** (ρ 0.73 vs 0.19, lift +0.545) was measured in the old spread. Step 2 of the order is
  to re-grade the lift with `python3 -m tools.c29_engagement_ranking`. The spread is now much narrower,
  so expect the lift to shrink a lot. If it falls inside the shuffle null, the frame's refutation
  clause applies. **The planted arm, which needs no run, is already measured:** the lift is +0.511 at 5
  anniversaries (estimate ρ 0.671 against the channel's 0.161), down from +0.740. The null arm is
  still exactly 0.000. That is still far above the 0.10 refutation line. But ρ grades the ranking,
  not what the ranking is worth. The trait now runs 0.50 to 0.20 where it ran 0.65 to 0.02, so a
  decision that reads the estimate has much less margin to protect. The book arm needs a run in this
  world before it says anything.
- **The value arms** predate this commit. `simulation/` is in `ARMS_SUBSTRATE_PATHS` and this path has
  no exemption, so the page's code guard already refuses to call them the world as it is now. The
  page fails closed. Re-taking them is a separate, multi-hour job.
- `site/data/engagement_separation.json` is regenerated in this commit. Its headline no longer
  says the disengaged "almost never shop": at 0.20 a renewal, that stopped being true.

Control: `tests/simulation/test_the_default_tail_chooses_at_ofgems_control_rate.py`. Restoring the
old triple reds it (0.149, ×2.63), and so does putting DISENGAGED alone back to 0.02 (0.212, ×2.42).
