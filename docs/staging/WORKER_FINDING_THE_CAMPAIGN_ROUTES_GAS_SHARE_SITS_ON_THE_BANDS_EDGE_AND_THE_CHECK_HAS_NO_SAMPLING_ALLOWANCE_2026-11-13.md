**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_21_the_premise_joint_is_fitted_not_drawn_independently`

# The campaign route's gas share sits on the band's edge, and the check has no sampling allowance (2026-11-13)

**What was found.** W2_21's insulation fix stopped reading a missing scheme flag as POOR. After it,
`tools/world_claims` reads the campaign route's `gas_home_share` as **81.25%** of 1,504 homes. The
band is [81.5%, 88.5%]. Before the fix it read 81.95% of 1,518 homes. The founders' route is
unchanged at 84.88% of 3,096 homes.

The campaign wins homes on modelled saving, so fabric changes which homes it wins. The move is 0.7
points. One standard error at n ≈ 1,500 is about 1.0 point (√(0.81 × 0.19 / 1,504)).

**Explanations, ranked by the evidence.**

1. **Sampling noise on a check with no allowance for it.** The band is the published market range,
   applied to a sample of about 1,500 homes as a hard edge. The base was already only 0.45 points
   inside it.
2. **The campaign really does select toward off-gas homes.** Electric-heated homes have larger bills
   and so larger savings. That would be a real selection effect, not a defect. The market band
   describes stock, not campaign wins.
3. **The fix is wrong.** Not supported. Founders are unchanged, and the fix reproduces EHS and HEE
   (see `docs/market_research/wall_insulation_by_dwelling_age_ehs_2023_2026-11-13.md`).

**What retires it.** Give `world_claims.check` a sampling allowance the size of the sample earns:
for example, a verdict of GAP only when the band edge lies outside a 95% interval of the measured
share. Separately, decide whether a stock band is the right claim to make of campaign winners at
all. Naming the gap in `KNOWN_ROUTE_GAPS` keeps it visible. The route reds again if the set
changes.

## Reverse

Delete this file and the `("campaign", "gas_home_share")` entry in `tools/world_claims.KNOWN_ROUTE_GAPS`.
