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

## Noise or selection: pre-registration (worker, 15 Nov 2026 ~06:10 GMT, filed before the run)

**What each count is.** `gas_home_share` is the homes with a gas meter over all homes on the route, where a
home is one account id with the gas leg's `g` dropped. Re-read at origin c555d5cd8a over the eight seeds:
founders 84.88% of 3,096 homes, campaign 81.25% of 1,504. The page says the band is the published 84-86%
"widened by 3 sd of sampling noise at that pool size", and the pool it names is "about 1,700 homes". The
founders' pool is now 3,096. So the widening is a fixed 2.5 points, sized for neither route.

**The founders-to-campaign gap already argues for selection.** It is 3.6 points with a standard error of
about 1.2 points on the difference, about 3 SE. Noise alone (explanation 1) is the weaker reading before
the run.

**The run.** The campaign route over 24 seeds (the eight plus 61108 to 61123), about 4,500 homes, one
standard error about 0.6 points.

**Predictions:**
- if explanation 2 (real selection) holds, the share stays in **80.0% to 82.5%**;
- if explanation 1 (noise) holds, it moves to **83.5% or above**, near the founders' 84.9%;
- I predict explanation 2.

### Measured: it is selection, not noise (15 Nov ~06:20 GMT)

| campaign draw | homes | gas_home_share |
|---|---|---|
| the eight `SEEDS` | 1,504 | 81.25% |
| 24 seeds (the eight plus 61108-61123) | 4,354 | **79.79%** |
| the 16 new seeds alone | 2,850 | 79.02% |

- **Explanation 2 holds; explanation 1 is refuted.** The share went down, not up toward 84.9%. 16 seeds the
  eight never saw read 79.0%. The campaign's winners carry about 5 points fewer gas homes than the founders.
  At 4,354 homes, 3 SD is 1.8 points, so the gap is real at any allowance the sample earns.
- **My range was refuted at the edge.** I predicted 80.0% to 82.5%; it read 79.79%. The direction held, and
  the size is larger than I said.
- **So the remedy this file first recommended is withdrawn.** A sampling allowance at the route's own pool size
  (3 SD at 1,504 homes is 2.8 points, so a floor of 81.2%) would have turned this claim **green** on the eight
  seeds. It would hide a real effect behind the smaller sample. Not built.
- **The real question, open.** Is a savings-led campaign that over-wins off-gas homes faithful? Off-gas homes
  have larger electric bills, so they model larger savings. But whether such homes actually switch more is
  unestablished here. The page's own §2 source puts challenger books built by switching "at 84-86% gas homes".
  That is weak evidence against the world, not proof. This is W2 world-fidelity work, decided blind to company
  results: the knowledge page first (K8), then the campaign's win model. Until then, the named gap is the
  honest state, and the `KNOWN_ROUTE_GAPS` reason now says so.
- **A second, smaller defect, not built.** The page's widening is a fixed 2.5 points, sized for "about 1,700
  homes". That is about right for the campaign (2.8) and the founders (3,096 homes, 1.9). It is meaningless for
  the 31-home trickle (19 points), which the module already calls "coarse". That is a factual correction to
  the page's pool counts, made with this note. Per-route widening would mostly loosen the trickle, so it buys
  little now.

**Done means now:** the W2 lane establishes from published switching evidence whether off-gas homes over- or
under-switch, then fixes the world's campaign selection or the claim's band for campaign winners. Either way
the `("campaign", "gas_home_share")` entry leaves `KNOWN_ROUTE_GAPS`.
