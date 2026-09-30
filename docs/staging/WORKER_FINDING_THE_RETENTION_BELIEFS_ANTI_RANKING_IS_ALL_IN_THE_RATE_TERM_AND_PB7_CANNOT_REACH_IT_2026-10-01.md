**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `PB7_the_company_learns_what_it_can_now_see` (release against), `B8_discovered_price_sensitivity_holdout` (where the next build lives)

# The retention belief's anti-ranking is all in the rate term, and PB7's learning cannot reach it

**2026-10-01, autonomous worker, item `name-the-input-that-anti-ranks-the-retention-belief`.** The grade, the tables and the predictions (landed first, `b6224d6d0`) are in `docs/staging/records/SEAT_PREREG_THE_NEXT_AB_ON_THE_SINGLE_ROLL_WORLD_WHAT_A_SEED_VARIES_2026-09-30.md` § "What orders the belief".

## What was found

1. **One term carries the whole −0.383.** Among direct-debit first renewals at pin `a322166cc` (338 rows, 57 distinct accounts), the value arm's retention belief anti-ranks the world's `p_retain`. Split into the terms of `enriched_churn_estimate`, all of it is `rate_estimate` (`churn_model.estimate_churn_probability`). Holding that term at its book mean turns the correlation to **+0.331**.
2. **The other terms cannot carry it, and one of them is inert on this path.** `payment_estimate` is 0.05 for every account. The engagement factor is one value per year: `value_based_renewal.decide_margin` calls `enriched_churn_estimate` with **no `payment_method`** (nor behaviour, satisfaction, bill-shock or arrears input), and that is still so on origin. The market-pressure multiplier is correctly signed; holding it makes the ranking worse (−0.419).
3. **Inside the rate term, no single input carries it.** The offer's move is the largest contributor, but it is not inverted: the belief and the world both fall as the raise grows. The inverted inputs are the account's standing features. Within a renewal year, tenure and bill size rise with the belief and fall with the world. These input-level figures come from a log rebuild with a median belief error of 0.088, so they rank the inputs and do not measure them.

## What it releases

**PB7 can be released against this.** Its learning rule, the engagement factor learned from the company's own leavers by channel, is not the cause and cannot be the fix, for two independent reasons:
- The value arm does not read the factor at all (no `payment_method` is passed).
- Even wired in, the factor is one scalar per channel. It cannot reorder accounts within direct debit, and that is where the −0.383 lives.

PB7's open residuals (PB8's source, the two-sided objective, a PB1-scale book) are unaffected by this finding.

## What the next build is, and the question to ask first

- **The fix belongs to the rate term.** Its direction is set by `RATE_SENSITIVITY` 0.8 / `GAS_RATE_SENSITIVITY` 0.6 × the size scale (Ofgem TDCV reference, sourced), with `TENURE_DISCOUNT_PER_YEAR` 0.01 and the bill-stress term. B8's frame lists these as hardcoded population constants. `B8_discovered_price_sensitivity_holdout` is the atom where the company learns its own rate response, so that is where the build goes. It is not PB7.
- **A frame question first, for the director as practitioner, not to build on.** Within a renewal year, the WORLD's `p_retain` falls with tenure (−0.32) and with bill size (−0.27). The industry expectation is the opposite: the CMA 2016 inertia finding says longer tenure means less switching. If the world is right on this book, the company must learn it. If it is not, that is a world-fidelity finding, and teaching the company to fit it would teach it an artefact. Measuring what drives the world's own `p_churn` at a first renewal settles which. That is a world-side read, and it is not done here.
- **A pairing caveat.** The roster keys the belief by (account, term_start). A dual-fuel account therefore contributes whichever leg was scored last (61 of 317 rebuilt rows matched a gas leg), paired with a household-level world `p_retain`. Every ranking grade in this record inherits that. It has not been measured.
