# PB4: the SVT drift's engagement gradient is wired, and the pre-registered prediction holds

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` · **Claim:** `pb4-wire-the-sourced-svt-drift-engagement-gradient` (Lane 0)

## The change, one variable

`departure_risks.svt_inertia_hazard` now takes a required `engagement_level`:

- DISENGAGED drifts at **0.54x** the rate of ACTIVE and PASSIVE, which stay equal.
- The others are scaled by 1 / (1 − 0.289 × 0.46) = 1.154. 0.289 is the disengaged share of summed
  SVT drift probability in PB4's capture at `bebf42253`.

So the change moves who drifts and not how many. The source, the bound and the prediction are in
`docs/market_research/does_a_disengaged_household_leave_the_default_tariff_less_at_the_same_tenure.md`,
§4, written before the change.

The archetype reaches the hazard from the run loop's
`engagement_level_for_customer(billing_account)`. That is the same archetype the household's renewal
decisions read. It reaches the hazard through `svt_product.inertia_hazard_for_term`, which had none
before.

No world code changed between `bebf42253` and `85ddd37d8`: `git diff --stat` over `simulation/`,
`sim/` and the capture tool is empty. The re-capture was run from a clean worktree at `85ddd37d8`
plus this change only. The comparison with the baseline capture is therefore one-variable.

## Grading the pre-registered prediction

Expected departures per household are the world's own probabilities summed over both routes, read
by `tools/engagement_separation.by_archetype_both_routes` (from `51bbb4d3d`).

| | Active | Passive | Disengaged | D/A |
|---|---|---|---|---|
| Baseline capture (`bebf42253`) | 0.608 | 0.484 | 0.598 | 0.98 |
| **Predicted** (first order) | 0.651 | 0.543 | 0.404 | 0.62 |
| **Read** (re-capture) | **0.654** | **0.522** | **0.397** | **0.607** |

**CONFIRMED.** D/A is 0.607, inside the pre-registered 0.55–0.70.

- The SVT drift per cap period is now active 0.0288, passive 0.0309, disengaged 0.0138. It was
  0.0247 / 0.0272 / 0.0229.
- Passive reads 0.02 under its first-order figure. That is the second-order route the note named,
  seen from the other side: passive SVT-years fell from 117.1 to 113.1. The engaged leave the
  default sooner, so they accrue less SVT exposure. Disengaged SVT-years rose from 111.5 to 112.7.
- The summed SVT drift probability is 43.72 against 44.53 (−1.8%). The mean is held to first order,
  as stated beside the constant. The residual is the exposure shift above, not a re-levelling.
- Counted departures barely moved (SVT departed 42 against 43; disengaged per household 0.32 against
  0.36). As the D4 finding said, one run's dice cannot resolve this. The world probability is the
  reading.

## What moved downstream, and what it does not settle

- **2022's declared SVT floor on c4** moves from 1.94% to 2.04%, against a 3.06% ceiling. It is
  corrected beside its old figure in `departure_level_anchor.UNFITTED_YEARS`, and the conclusion
  stands. It rises because c4's 2022 drift is only 18.6% disengaged, against the 28.9% the mean was
  held on.
- **The value arms.** The world digest tracks the departure level, so C29's and C34's arms are
  stale against this world until they are re-taken. That is owed, not done here.
- **PB4's published capture** (`docs/reports/pb4_departure_factors.json`) and its page are in
  `51bbb4d3d`, which is not yet on origin. The reduced re-capture is at
  `/var/tmp/pb4_departure_factors_gradient.json`, in the same format. It replaces that file, and
  `python3 -m tools.engagement_separation --write` re-publishes, once `51bbb4d3d` lands.
- **Not settled:** the size of the disengaged gap (0.54 is the bound's weak end), and passive
  against active (the source has two groups).
