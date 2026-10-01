**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` (Lane 0 delivery)

# An SVT segment was billed above the cap by the renewal chain, and writer 4 now binds it

Claim `does-an-svt-segment-rate-reach-the-bill-above-the-cap`. These are results against
`docs/staging/records/SEAT_PREREGISTRATION_DOES_AN_SVT_SEGMENTS_CHAIN_RATE_REACH_THE_BILL_2026-10-01.md`.
Q1–Q3 were written before reading the billing path. R1–R6 were written before the repair's run.
The duplicate-work note at draw time named this same id. The only live holder was this
invocation, so it was the draw's own write and not a rival.

## What was wrong

The default tariff was graded on prices no real supplier could charge. In the world's 2016–2025
run, **630 of 2,333 domestic SVT segments in the capped years were contracted above the published
Ofgem cap ex-VAT**. They covered 82 accounts, sat between ×1.001 and ×1.38, and 476 of them were
above even the inc-VAT cap. Settlement billed exactly that rate.

- The world strikes every SVT segment at the published cap ex-VAT: **2,333 of 2,333**
  (`simulation/svt_product` via `svt_rates`). **Q2 HOLDS.**
- `run_phase2b` passes every SVT term through `decide_renewal_rate`. Writers 1–3 (portfolio
  premium, margin surcharge, value arm) then move it. Writer 4 never clamped it, because
  `CAPPED_TARIFF_TYPES = ("fixed",)`.
- No branch takes SVT out of `run_hedged_term(..., unit_rate)` / `run_gas_term(..., unit_rate)`.
  So the chain's rate IS the billed rate: 2,098 of 2,333 settle at exactly `contracted`, and the
  other 235 at 11/14 × `contracted`, which is the ToU off-peak leg of a pair struck off it.
  **0 settle at anything else. Q1 is REFUTED.** I predicted the chain's figure was an unread
  record. It is the bill. The segment's own `household_charged`/HMT-receipt legs reach no
  settlement code; their only reader is `bill_shock_tracker`.
- Q3 (a company reader mistakes the chain's figure for the charged rate) is moot. It is the charged
  rate.

The named example is PROS-2021-0383, an SVT ToU account, on 2022-12-17. It was struck at 494.2,
contracted at 606.4, and settled at an off-peak rate of 476.4 (= 11/14 × 606.4).

The commons states the scope directly: *"The cap binds default contracts only: Evergreen (SVT),
Deemed, and default fixed-term contracts. A fixed tariff the customer chose is outside 28AD."*
(`docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`). The chain
capped the product the law exempts and left uncapped the one it binds first.

## The repair

- `renewal_rate_chain.CAPPED_TARIFF_TYPES = ("fixed", "svt")`.
- The SVT ceiling is the published cap **not net of the EPG** (`EPG_MADE_WHOLE_TARIFF_TYPES`).
  `get_cap_unit_rate_for_date` and `get_multi_register_cap_unit_rate_for_date` take
  `net_of_epg=`. On a default tariff, HMT paid the supplier the gap between the EPG and the cap.
  The world strikes SVT at the cap with the receipt as its own leg. A ceiling at the EPG would
  have clamped every SVT segment Oct 2022–Jun 2023 to about two-thirds of its lawful revenue.
- An SVT segment sold as ToU is graded at the multi-register benchmark (28AD.4), through the same
  `offers_tou` predicate the 28AD repair uses.
- The control is `tests/company/pricing/test_an_svt_segment_is_held_at_the_published_cap.py`. It
  recomputes the ceiling from `simulation/svt_rates`, not from the chain's helper. Each of three
  mutations reds it: drop `svt` from `CAPPED_TARIFF_TYPES` (5 of 7 red), empty
  `EPG_MADE_WHOLE_TARIFF_TYPES` (4 red), and make `get_cap_unit_rate_for_date` ignore
  `net_of_epg` (4 red). The EPG leg asserts both sides of the partition: SVT is held at the cap
  AND fixed is held at the EPG.

## The measurement: one variable, same world

Base: HEAD `8c29e03d9`, `/var/tmp/se-svt-bill/rows.json`. New: the same plus only this change,
`rows_new.json`. The scripts are `measure.py`, `measure_new.py` and `compare.py` in that directory.

| | base | new | verdict |
|---|---|---|---|
| R1 SVT contracted > flat cap ex-VAT | 630 (476 > inc-VAT) | **0** (0) | HOLDS |
| R2 ToU SVT > multi-register ceiling | 167 of 235 | **0**; 167 clamped strictly lower | HOLDS |
| R3 EPG-window SVT contracted at the EPG | 0 of 335 | **0 of 335** | HOLDS |
| R4 flat SVT settled unit rate > cap × 1.001 | 568 | **0** | HOLDS (graded on the settled rate field, not revenue/kWh, because `revenue_gbp` carries the standing charge, as the pre-registration allowed) |
| R5 non-SVT mean contracted/struck, ti≥1, 2023+ | 0.95160 | 0.95163 (n=33) | HOLDS in sign only; the move is noise-sized |
| R6 chain calls | 3,236 | 3,236 | HOLDS |

Of 2,895 SVT calls, 853 moved: 754 down and 99 up. The 99 rose through the portfolio premium
reading a lower-margin book, and all of them stay under the cap. Of 341 non-SVT calls, 7 moved, by
pennies. PROS-2021-0383 on 2022-12-17 is now 467.0, the multi-register ceiling NOT net of the EPG,
with an off-peak rate of 367.0.

## Handed on, not taken here

1. **`fixed` is in `CAPPED_TARIFF_TYPES` against the commons.** A fixed tariff the customer chose
   is outside 28AD. In 2022 real fixed deals were priced well above the cap. Removing it moves
   every fixed renewal and the value arms' search ceiling, so it is a separate one-variable change.
   The EPG did apply to fixed deals as a per-unit discount, and suppliers were compensated for it.
   The current `min(cap, EPG)` reading for fixed takes that compensation out of revenue, which is
   the same mistake the SVT ceiling avoids here.
2. **1,332 SVT segments are contracted at exactly 0.95 × the cap.** This is a negative portfolio
   premium applied per account to a default tariff. A real supplier sets one SVT price per region
   for its whole book, not one per account. Whether per-account SVT pricing is even permitted is
   `docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md`'s subject. I
   have not read it against this.
3. **`domain_invariants.check_sold_unit_rate_within_cap` has no production caller.** It also
   grades against `min(cap, EPG)`, so it would call every lawful EPG-window SVT segment unlawful
   if it were ever wired. It is a sixth cap implementation, and the VAT-rule shape again.
4. **The segment's `household_charged`/receipt legs never reach settlement.** Revenue is right,
   at cap = charged + receipt. But nothing settled says what the household paid in the EPG window
   except `bill_shock_tracker`'s reading of the term.
