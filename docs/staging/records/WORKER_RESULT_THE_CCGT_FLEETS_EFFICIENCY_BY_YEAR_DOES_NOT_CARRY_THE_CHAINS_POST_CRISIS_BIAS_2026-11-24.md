**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the CCGT fleet's efficiency by year does not carry the chain's post-crisis bias (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer. Pre-registered in
`docs/staging/records/WORKER_PREREG_DOES_THE_CCGT_FLEETS_EFFICIENCY_BY_YEAR_CARRY_THE_CHAINS_GROWING_POST_CRISIS_BIAS_2026-11-24.md`,
promoted to origin as `ca6f4c1a27` at 11:32:40 UTC. The probe `/var/tmp/mk23/measure.py` first ran at
11:42:33 UTC, in a clean worktree on that commit. **Knowledge (K8):** DUKES 5.10.C, in
`docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md` §1a. **Nothing in `sim/` changes.***

## The patch reached what it had to

XE scaled gas and carbon by 0.50 / eff(year) on all 157,106 half-hours of the refit, and in the one record
call to `derive_price`. Net export reached the record's two demand calls in both arms, as in X.

## The predictions, and the outcome beside each

| # | Filed | Outcome | Held? |
|---|---|---|---|
| E1 | control reproduces X, 4.89 / 17.02 / 10.38, ±0.01 | 4.89 / 17.02 / 10.38, and a0-a2 = 0.524 / 0.998 / 1.736 | **held** |
| E2 | post-crisis bias moves < £1.5 from +8.23, stays above +6.5 | +8.16 (moved £0.07) | **held** |
| E3 | 2023 falls £0.5-2.5; 2024 and 2025 each move < £1.0 | 2023 +5.56 → +3.97 (−1.59); 2024 +6.94 → +7.27; 2025 +11.25 → +11.65 | **held** |
| E4 | pre-crisis and crisis MAE within ±0.5 of X | 4.94 (X 4.89), 16.94 (X 17.02) | **held** |
| E5 | growth from 2023 to 2025 widens | +5.69 → +7.68 | **held** |

**All five held.** The predictions were made from the published series before the run, and the run did
what the series said it would. That is the main thing this record shows: the question could have been
answered from DUKES alone.

## The numbers

Monthly MAE / monthly bias, £/MWh, all on SAP plus net export.

| Arm | pre | crisis | post |
|---|---|---|---|
| X, control | 4.89 / −0.95 | 17.02 / −1.50 | 10.38 / +8.23 |
| **XE, DUKES efficiency by year** | 4.94 / −0.64 | 16.94 / −1.81 | 10.40 / +8.16 |
| null_S | 4.97 / −1.03 | 17.44 / −9.45 | 9.84 / +8.89 |
| null_T | 5.42 / +1.81 | 24.53 / −9.54 | 6.67 / +0.70 |

Bias by year, X → XE: 2016 −5.56 → −5.42; 2017 +0.21 → +0.60; 2018 +1.36 → +1.59; 2019 +0.27 → +0.58;
2020 −1.12 → −0.63; 2021 −4.68 → −4.38; 2022 −1.10 → −1.03; **2023 +5.56 → +3.97**; 2024 +6.94 → +7.27;
2025 +11.25 → +11.65. Refit: a0-a2 = 0.516 / 0.979 / 1.667, half-hourly MAE 31.15 (X 31.13).

## What it says

1. **Efficiency is ruled out as the second mechanism.** Decision rule (a), as filed. The published fleet
   efficiency moves by 1.5 points across the decade. It peaks in 2023, the year with the smallest
   post-crisis bias, so it narrows that year's gap and widens the growth.
2. **The 0.50 constant is not wrong in any way the chain can see.** The leg has no intercept, so its refit
   absorbs any constant efficiency. That is an equivalence, not a finding. The fleet's real 49% is not a
   defect in the chain.
3. **A GAP stays open.** 2025's efficiency (DUKES 2026 edition) is not held. Held at 2024, it cannot carry
   2025's +11.3. Covering that would need a 2025 fleet about 13% more efficient than 2024's, and no
   published plant change suggests it [calc: +11.3 on a floor near £85].

## Decision

**Nothing ships.** The steer's candidate list loses "a fleet more efficient than 0.50", with this record as
the reason.

**The other named candidate is weaker than the interconnector record put it.** That record named "SSP
against MID". But the electricity page's grade (§10a) already has SSP's post-crisis monthly level within
£1.76 of MID. So the settlement price choice cannot carry an £8 level gap. The same grade found the
traded price **£9.80 below gas-plus-carbon SRMC** after the crisis, which matches the chain's +8.2 in sign
and size. So the question is not which price but **why GB power cleared below the gas plant's running cost
in 2023-25**, rising year by year. Candidates the page allows, none graded: imports at 23-33 TWh setting
the price more often (in X as volume, but not as a price-setter), gas marginal less often (ECIU: 90% to
85%), and hedged or contracted CCGT bidding below the spot SRMC. **Next under item 4:** a K8 note on
that question in §1 and §10a, with those three labelled GAP, then the arm that separates them. Still owed
beside it: the K8 forward-flow section (§5), so that SAP and net export can ship together.
