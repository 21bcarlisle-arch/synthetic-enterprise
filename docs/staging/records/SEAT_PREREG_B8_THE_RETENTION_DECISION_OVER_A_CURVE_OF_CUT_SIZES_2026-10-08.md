# Pre-registration: the retention decision over a curve of cut sizes

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-the-retention-decision-over-a-curve-of-cut-sizes`

Filed 2026-10-08 before any run below. The result goes in a separate finding; this file is not edited after the runs.

## The question

At £7.5/MWh the learned decision picks "cut for none", correctly, and the cut would need about +0.048
of P(stay) to pay at a 14% margin (+0.0114 is what the world gives)
(`SEAT_FINDING_B8_THE_LEARNED_OFFER_EFFECT_DECIDES_AND_AT_THIS_CUT_IT_PICKS_THE_RIGHT_FLAT_RULE_NOT_A_BETTER_ONE_2026-10-08.md`).
One cut size cannot say whether a holdout-learned offer EVER beats the right flat rule in this
world. This grades cuts of 2.5, 5, 15 and 30 £/MWh, with the 7.5 result already on file, by the
same procedure: `tools/grade_coin_drawn_holdout.py decide --arm real --cut X`, learned on seed 42 at
4,700 per year, decided on fresh seeds 101 and 202, graded at both margin ends (0.019, 0.14).

## What the mechanism says before running

The world's price response (`simulation/customer_events.churn_position_multiplier`, fed the
household's felt differential against the SVT and scaled by its own bill) is CONVEX in the
differential and its win leg SATURATES. A cut moves the differential down, into the flatter part.
So the stay gained per £ of cut should FALL as the cut grows. The cost of the cut (`c * E` paid to
every household that stays) rises linearly. The break-even effect at 14% is about 0.0064 per £/MWh
of cut; at 1.9% it is about seven times that.

## Predictions

1. **The true effect rises with the cut but less than proportionately.** Effect per £/MWh is highest
   at 2.5 and lowest at 30. Expected ranges: 2.5 → +0.003 to +0.006; 5 → +0.006 to +0.010;
   15 → +0.018 to +0.025; 30 → +0.025 to +0.045.
2. **No cut size pays at either margin end.** At every cut, "cut for all" loses to "cut for none" at
   both 0.019 and 0.14, and the loss grows with the cut.
3. **The learned decision offers the cut on at most 1% of decisions at every cut and margin**, so it
   matches "cut for none" to within £0.05 per decision. At 2.5 the interval may read "undecided";
   that changes nothing.
4. **The best ratio of true effect to break-even effect is at the smallest cut, and it is below 0.5**
   at 14%. So in this world, no uniform cut is worth offering, and a holdout-learned decision cannot
   beat the right flat rule by choosing a cut size.

**What would refute it:** any cut where the learned rule beats "cut for none" by more than £0.10 per
decision on both fresh seeds, or a true effect per £ that rises with the cut (convex in stay, not
concave), or a ratio above 1 at any cut.
