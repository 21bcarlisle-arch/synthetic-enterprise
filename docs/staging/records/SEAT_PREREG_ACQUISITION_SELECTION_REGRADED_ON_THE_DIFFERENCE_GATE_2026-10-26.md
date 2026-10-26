# Pre-registration: acquisition selection re-graded now that a group's own read needs a difference

*Seat, 2026-10-26. Filed before the build below ran. Not revised after it.*

**Question.** `e847cd123` made `effect_for_channel` read a group's own offer effect only where it is
powered AND differs from the rest of the book beyond its 95% bound. `tools/grade_acquisition_selection`
now asks that rule for its `own_read` column. Do the published P1-P4 verdicts and own-read groups of
`SEAT_PREREG_ACQUISITION_P1_P4_ON_THE_FUNNEL_SOURCED_DECISION_SET_2026-10-09.md` still stand?

**Run.** Same seeds as 9 Oct: train 1001-1100, fresh 101 and 202, noise 301-320, all three arms, cut
GBP 7.5/MWh, built and graded at origin `86f5cdca4` (`build` then `grade`).

**Predictions.**
1. **P1-P3 still fail everywhere and P4 still holds.** The new rule can only move a group from its
   own read to pooled. Pooled (+0.016) is an order of magnitude below the ~+0.15 break-even, and on
   9 Oct no cut was offered anywhere, so no decision can become a cut.
2. **The own-read set empties.** The three groups read on their own on 9 Oct (`campaign_win`, `0y`,
   never-active) are each most of the book, so their gap to the rest is small against its bound.
   `campaign_win` is over 99% of decisions; I expect its rest is too small to differ from.
3. **The value columns are identical to the penny**, because no decision changes.

A refutation of any of these is recorded beside this file.

## Result, 2026-10-26. Recorded beside the predictions, which are not revised.

Built and graded at `86f5cdca4`: 122 seeds per arm, about 81,500 training decisions per arm (64,000 on
9 Oct, because the world has moved since then), and 15,000-17,000 needed per arm.

- **Prediction 1 HOLDS.** P1, P2 and P3 fail in all 18 rows (3 arms x 3 observables x 2 margin ends)
  on both fresh seeds, and P4 holds. No cut is offered anywhere. At the 0.14 end, never offering
  beats always offering by about GBP 8.7-8.8 per decision, and at the 0.019 end by about GBP 10.9-11.2.
- **Prediction 2 HOLDS: the own-read set is empty in every arm.** The three groups that read on their
  own under the power-only rule are the same three as on 9 Oct. Each is powered, and each reads pooled
  because its gap to the rest of the book is inside the bound:
  | group | gap to the rest (arm I) | 95% bound |
  |---|---|---|
  | `campaign_win` | +0.0334 | +/-0.1174 |
  | `0y` on default | -0.0100 | +/-0.0180 |
  | never actively renewed | -0.0067 | +/-0.0148 |
  The other two arms are within 0.001 of these. My reason for `campaign_win` was wrong. It is not
  "the whole book": 274 decisions (`None` and `move_in`) make up a rest. The gap clause refuses it
  because that rest is too small to bound a difference, not the whole-book clause.
- **Prediction 3 HOLDS, measured as a one-variable comparison.** On these same sets, the grader was
  re-run with `effect_for_channel` put back to the power-only rule. All 18 rows are identical in every
  value column, cut set and P verdict. The only thing that moves is the `own_read` flag on those three
  groups. The seed-noise SD of the lead is 0.0 under both rules. The learned rule equals never offering on
  every noise seed, so its lead has no spread. P3's two-SD test is never reached, because P2 fails first.

**What this changes in the 9 Oct record.** Only the "own-read groups" column of its table: under the
difference gate it is now *none* in every arm. Its verdicts, its economics (a perfect read would still
offer nothing) and its value figures stand. The groups that differ most from the pool (`2y+` on default,
+0.032 to +0.034 learned, and ever actively renewed, +0.020) are still short of power. So nothing about
targeting a save offer by acquisition selection has moved.
