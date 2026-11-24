**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: the price leg's shape arm, with a non-gas constant and a low-x depth, against its post-crisis level (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next 1 of the build-terms result,
`docs/staging/records/WORKER_RESULT_ON_THE_CHAINS_OWN_FORM_THE_DEMAND_YEAR_TERM_EXPOSES_A_PRICE_LEG_THAT_RUNS_7_POUNDS_LOW_AFTER_THE_CRISIS_2026-11-24.md`
(`ea3a93cc4`). Filed and landed before the probe runs. **Nothing in `sim/` changes.***

## The question

Run on REAL daily x with no chain, the shipped one-leg price form (price = floor × (A0 + A1·x + A2·max(0, x − 0.70)²))
runs £7.2-8.0 low after the crisis on every basis, and £2.3-3.3 low before it. Is that a SHAPE the form cannot
draw, or a LEVEL its inputs carry? The electricity page §1b names two shape candidates: part of the price
does not scale with gas (subsidised and must-run output, wear), and the bottom is deeper when gas is off the
margin. §1b also measured, binned on real CCGT GW, that the price is the same multiple of the floor in every
regime from 6 to 14 GW. That is evidence against a shape cause, and it was read before this filing.

## Design (the leg alone, on real inputs; each form refit by half-hourly OLS on the full record)

| Form | Price | Added column |
|---|---|---|
| L0 | floor × (a0 + a1·x + a2·k) | control: the shipped form, k = max(0, x − 0.70)² |
| L1 | L0 + b0 | a constant in £/MWh that does not scale with gas |
| L2 | L0 + a3·floor·max(0, XL − x)² | a low-x depth that scales with the floor |
| L3 | L0 + both | |

- Two bases, as in the build-terms probe: **R**, the shipped one (x = (INDO − AGWS wind − AGWS solar)/35,000), and
  **W** (x = (INDO − FUELHH wind)/35,000). The common half-hour set is the build-terms probe's (157,010).
- **XL is a rule, not a picked number:** the full-window median of half-hourly real x on that basis.
- Evaluation is the build-terms probe's exactly: daily mean real x, the daily record's gas and carbon,
  monthly demand-weighted MAE and bias by regime (pre to 2021-06, crisis to 2023-06, post, post without 2025).
- Probe `/var/tmp/wpc_shape/measure_s.py`, sha256 `9d53c7cd4f56efb66caa320b84878f7f577fbcfec42c889efa255cf475ac1013`.
  It runs in a worktree at the commit that lands this record, with `sim/cache` linked in.
- **Seen before the run and disclosed:** the L0 rows. They are the build-terms result's leg-on-real rows (R
  5.48 / −3.11, 14.62 / −3.33, 9.84 / −7.99; W 5.07 / −2.26, 17.26 / −6.33, 7.76 / −7.24). No L1-L3 figure was
  computed before this filing.

## Predictions

| # | Prediction |
|---|---|
| S-P0 | L0 reproduces the leg-on-real rows within £0.01 on both bases, and `synthetic_price` within £1e-6 a day |
| S-P1 | L1's b0 is positive and below £10/MWh on both bases, and L1 raises the R pre-crisis bias by at least £1 against L0 |
| S-P2 | L1's R post-crisis bias stays at or below −£5 |
| S-P3 | L2's a3 is negative on both bases (a deeper bottom, not a shallower one) |
| S-P4 | L2 moves each regime's R MAE by less than £1.0 against L0 |
| S-P5 | No form takes the R post-crisis bias inside ±£3 |
| S-P6 | Every form's half-hourly MAE is within 2% of L0's on its basis |

The reasoning behind S-P1 and S-P2: the OLS is weighted in pounds, so the crisis half-hours (floors of
£130-240) dominate it. A constant that does not scale with gas lifts the low-floor years most. Pre-crisis
floors (£34-45) sit below post-crisis floors (£78-97), so a constant should move the pre bias more than the
post bias. The post bias is the larger one, so a constant cannot be its whole cause.

## Decision rule, filed now

- **(a) The shape carries the gap** if any of L1-L3 brings the R post-crisis bias inside ±£3 without raising
  the pre-crisis or crisis MAE by more than £0.50. The build then adopts that form, and the build-terms rerun
  (B1-B3) uses it.
- **(b) The gap is a level, not a shape** if (a) does not fire. Nothing ships. The next arm moves to the leg's
  INPUTS after the crisis: the gas series the record carries against the daily SAP splice, and carbon.
- Either way the end-year clamp arm (Next 2, already measured in `acc387cbe`) and the rerun are unchanged.

Reverse: delete this record.
