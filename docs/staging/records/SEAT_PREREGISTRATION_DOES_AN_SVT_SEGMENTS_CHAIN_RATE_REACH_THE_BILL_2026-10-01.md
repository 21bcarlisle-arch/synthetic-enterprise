**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` (Lane 0 delivery)

# Pre-registration: does an SVT segment's chain rate reach the bill above the cap?

Claim `does-an-svt-segment-rate-reach-the-bill-above-the-cap`. Written 2026-10-01 23:27 BST. At
this point I had read the 28AD paired run's `calls[]` rows for PROS-2021-0383 and nothing else.
I had not read the billing path or the settlement records.

Subject: in `/var/tmp/se-28ad-mr/new.json`, the SVT term PROS-2021-0383 that starts 2022-12-17
(electricity, ToU, term_index 1) has `struck` 494.19 and `contracted` 606.37 GBP/MWh. 494.19 × 1.05
= 518.9, which is the published Oct–Dec 2022 inc-VAT cap. So the struck rate already IS the cap,
ex-VAT. The contracted rate sits about 23% above it.

## Predictions

- **Q1. Billing.** The chain's `contracted` rate on an SVT term is NOT what the account is billed.
  The SVT stint is billed off `simulation/svt_product.build_svt_schedule`, which reads `svt_rates`,
  and the chain's figure on an SVT term is a record nothing in settlement reads. Prediction:
  PROS-2021-0383's settled `unit_rate_gbp_per_mwh` over 2022-12-17..2022-12-31 is 494.19 (flat), or
  its ToU split of that, and NOT 606.37. Its `household_charged_unit_rate_gbp_per_mwh` is the EPG
  340/1.05 = 323.8, or its ToU split.
- **Q2. The struck rate.** `svt_rates`' rate is the published cap, never above it. Divided by 1.05,
  it is never above the ex-VAT cap. The EPG enters only as the household-charged leg plus the HMT
  receipt, so the unit leg sits ABOVE the EPG by design (unit = charged + receipt). Prediction: 0
  SVT calls in `calls[]` have struck above the ex-VAT cap.
- **Q3. Consequence.** If Q1 holds, the chain's above-cap `contracted` on SVT terms is not revenue.
  But it may still be read by a COMPANY reader (the portfolio margin feedback, the value arm, or a
  renewal-price comparison) as though it were the rate charged. I predict at least one such reader
  exists. That is the residual defect worth naming, ahead of any billing defect.

Refutation: if any settled day on an SVT stint carries the chain's contracted rate, Q1 is refuted
and the default book is billed above the cap.

## Addendum, 23:45 BST, before the repair's run: what binding writer 4 to SVT moves

Read since the predictions above, and before any run of the repair:
- In `run_phase2b`, an SVT term reaches no dedicated branch. Electricity calls
  `run_hedged_term(..., unit_rate, ...)` and gas calls `run_gas_term(..., unit_rate, ...)`, both
  with the CHAIN's rate. No settlement code reads the segment's `household_charged`/receipt
  legs. So Q1 is refuted on reading. The bytes are being taken (`/var/tmp/se-svt-bill/`, HEAD
  `8c29e03d9`).
- Q2 holds on the 28AD rows: 2,333 of 2,333 capped-year SVT strikes equal the published Ofgem
  cap ex-VAT. 630 contracted rates sit above it (82 accounts, x1.001 to x1.38, 394 electricity
  and 236 gas, none at term_index 0), and 476 of those are above even the inc-VAT cap.

The repair: `svt` joins `CAPPED_TARIFF_TYPES`. For SVT the ceiling is the published cap NOT net of
the EPG, because HMT made the supplier whole on a default tariff. It is multi-register when the
term is sold as ToU (28AD.4). Base: HEAD. New: HEAD plus only that change. Same world.

- **R1.** Domestic capped-year SVT calls with contracted > the published flat cap ex-VAT × 1.001:
  base ≈630, new **0**.
- **R2.** SVT calls with contracted > their own ceiling (multi-register for a ToU account) ×
  1.001: new **0**. At least one ToU SVT call is clamped strictly below the flat cap.
- **R3.** No flat (non-ToU) SVT call in 2022-10..2023-06 is contracted at the EPG ex-VAT. The
  ceiling is not the EPG.
- **R4.** Settled revenue/kWh over each SVT term: in base, some terms bill above the flat cap
  ex-VAT, which confirms Q1 on bytes. In new, none bill above it × 1.01. The 1% allows for ToU
  weighting and standing charges, if `revenue_gbp` carries them. If `revenue_gbp` includes the
  standing charge, R4 is graded on unit rate fields instead, and I say so.
- **R5.** Non-SVT calls: I cannot say how many move. Lower SVT revenue lowers the realised
  margin the portfolio premium reads, so the direction I predict is UP. The mean
  contracted/struck over non-SVT calls with term_index >= 1 starting 2023 or later is higher in
  new than in base.
- **R6.** The number of chain calls moves by under 2%, through churn feedback.
