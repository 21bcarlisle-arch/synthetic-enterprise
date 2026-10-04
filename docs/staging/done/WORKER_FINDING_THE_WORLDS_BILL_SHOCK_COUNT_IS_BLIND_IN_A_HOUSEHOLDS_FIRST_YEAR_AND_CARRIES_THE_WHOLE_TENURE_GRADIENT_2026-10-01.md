**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` (where the next build lives: a world-fidelity gap), `B8_discovered_price_sensitivity_holdout` (do NOT fit this; release against)

# The world's bill-shock count is blind in a household's first year, and it carries the whole tenure gradient

**2026-10-01, autonomous worker, item `what-drives-the-worlds-retention-at-a-first-renewal`.** The predictions (landed first as `33e9c1ba3`), the per-term table and the re-paired grade are in `docs/staging/records/SEAT_PREREG_THE_NEXT_AB_ON_THE_SINGLE_ROLL_WORLD_WHAT_A_SEED_VARIES_2026-09-30.md` § "What drives the world". The scripts are in `/var/tmp/se-world-terms-out/`. Pin `a322166cc`. No simulation was run.

## Verdict: a world-fidelity gap, not a feature for the company to learn

The previous finding (`WORKER_FINDING_THE_RETENTION_BELIEFS_ANTI_RANKING_IS_ALL_IN_THE_RATE_TERM…`) asked one question first: within a renewal year, the world's `p_retain` falls with years on supply (−0.32) and with bill size (−0.27). Is the world right? **It is not, and one term carries both gradients.**

1. **The bill-shock base cannot fire in a household's first year.** `saas.customer_reaction.score_experience_signals` (`yoy` mode, as called by `saas.churn_model.build_churn_risk`, which `simulation/customer_events.roll_lifecycle_event` uses as the world's bill-shock base) compares each month with the same month a year earlier. At a first anniversary none of the 12 counted months has a prior year, so k = 0 on **156 of 156** tenure-1 rows. A household the world first decides at a later anniversary (it decides at one anniversary in five) carries a mean of **6.86 shocked months out of 12**. Retention: **0.775 at tenure 1 against 0.651 at tenure 2+.**
2. **Hold the bill-shock hazard at its book mean and both gradients vanish:** tenure −0.346 → **−0.009**, bill size −0.272 → **+0.003**. Housing tenure and income stress (`A`) move the bill gradient by 0.07. The £-scaled price response and the satisfaction tenure terms carry nothing measurable.
3. **Most of the company's "anti-ranking" is this artefact.** Score the belief against the world with only that hazard held: the pooled correlation goes from **−0.336 to +0.197**, and within cells from −0.374 to −0.132. Re-pairing dual-fuel legs does not change the original −0.383: every pairing gives −0.38 to −0.41.
4. **The published record points the other way on both counts.**
   - **Tenure.** Ofgem engagement surveys (`docs/market_research/svt_rates_active_passive_2016_2025.md`) put SVT 3+-year stayers at ~5–10%/yr switching against ~15–20% under 3 years. CMA 2016 found inertia. The world reverses this.
   - **Bill size.** Ofgem/BMG 2024 Table 3 bounds the spend–switching correlation within −0.07 to +0.05 (`is_there_a_bill_level_at_which_switching_rises.md`). The world's −0.27 is outside that band.
   - **And the quantity itself is already ruled the wrong one.** `docs/market_research/what_bill_shock_is.md` (2026-09-01) says that for a direct-debit household, differencing two bills "measures something that household did not experience". Every row in this population is DD. The trigger also takes `abs()`, so a bill that falls 15% year on year counts as a shock. That is not measured here.

## What the next build is, and where

**`PB4_engagement_separated_from_elasticity`** is the W2 atom whose open residual (b) is "a bill shock makes a disengaged household look". It is the nearest owner of the world's bill-shock → departure path. No map row names `departure_risks.py`, `saas/churn_model.py` or `saas/customer_reaction.py` in its `file_scope`. B7's "shocks" are income shocks, and PB5 owns only the £-scale of the price response, which this measurement shows carries neither gradient. So the build must widen PB4's scope to those three files. **Knowledge first:** the build re-derives the world's bill-shock hazard from `what_bill_shock_is.md`. For DD, that means a material change to the DD amount or a balance the household does not understand; for standard credit, the bill. It must be defined so that it can fire in a household's first year, against the quote or first DD, and it must decide whether a fall is a shock. It must not patch the year-on-year window, because that would fix the instance and keep the wrong quantity. Once rebuilt, re-run this item's `analyse.py` against the new world. Done when the tenure gradient is no longer carried by an artefact (sign and size come from whatever term remains). It is a diagnostic, never a target.

**`B8_discovered_price_sensitivity_holdout` must NOT fit the world's tenure or bill gradient.** Turning the company's rate term toward them would be learning an advantage from a world defect. The company's tenure discount (−0.01/yr) has the published sign. The within-year residual of −0.13 after the hold is the part B8 may legitimately work on. The company's own +0.33 against bill size is also outside the published ±0.07, which makes it the candidate to look at there.

## Not done here

- No `simulation/`, `saas/` or `company/` code change. No map row was written, so PB4's scope widening is left to the build that needs it.
- The `abs()` falls-as-shocks share was not measured. It needs per-period bills, which the C0 log does not carry.
- The input-level holds come from a rebuild (median |error| 0.017). The three pairs that miss by more than 0.05 are all on the price term, which carries neither gradient.
- Side note, not pursued: the world's departure hazard reads a `saas/` module for its bill-shock base.
