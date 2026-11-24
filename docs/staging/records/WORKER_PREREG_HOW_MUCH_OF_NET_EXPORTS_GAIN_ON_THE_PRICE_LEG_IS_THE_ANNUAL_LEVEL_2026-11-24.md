**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: how much of net export's gain on the price leg is the annual level, and how much is the within-year shape? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next 1 of the K8 forward net-flow note (electricity page §5a, `4f95a02fd`). Filed and landed before the
`am` arm runs. **Nothing in `sim/` changes.***

## The question

On SAP, adding GB's real half-hourly FUELHH net export to INDO took the leg's crisis monthly MAE from £18.46 to
£13.29 and its post-crisis bias from +4.08 to −0.30 (R L0, `c89b0910f`). FES publishes net flow as an annual
total only. A forward build can therefore draw an annual level from the FES band, and it has two options for
the within-year shape: take the record's shape, or leave the shape out. **If the leg sees only each year's mean
net export, how much of that gain survives?**

## Definitions

- **Level:** each calendar year's mean net export over the probe's common half-hours, the same value in every
  half-hour of that year. It preserves each year's total. The probe asserts that before it fits.
- **Shape:** the rest. This is the half-hour-to-half-hour and day-to-day movement around that year's mean.
- **Level share** of a gain is (base − am) / (base − ne). The base is the inputs result's SAP row, which has no
  net export, and ne is `c89b0910f`'s row.

## Design

- **One variable:** the per-half-hour net export added to INDO is replaced by its calendar-year mean. Everything
  else is the `ne` arm unchanged: the same 157,010 common half-hours, form L0, bases R and W, and the same refit
  and evaluation.
- **Probe:** `/var/tmp/wpc_am/measure_am.py`, sha256
  `f29e1f55f7c0900c12180dceef31d7bc25a0a07dd5f9509690d84fae1f7ff3b5`. It is `/var/tmp/wpc_ne/measure_ne.py`
  (`0de881e9…`) with `argv[1]` in {`ne`, `am`} and the year-mean substitution. It runs in a worktree at origin
  `4f95a02fd` with `sim/cache` linked in.
- **Seen before filing, and disclosed:**
  - This probe's `ne` arm has already run. It reproduces `/var/tmp/wpc_ne/out_ne.json` byte for byte (control).
  - The half-hourly fit MAE is 30.99 in base and 31.13 in ne for R, and 31.33 and 31.40 for W. Adding the real
    shape made the half-hourly fit slightly worse.
  - Net export by year is in the `ne` pre-registration. 2022 is +506 MW. Every other year is −1,781 to −3,863.
  - No `am` figure has been computed.

## Predictions (R L0 unless stated; monthly, demand-weighted, £/MWh)

| # | Prediction |
|---|---|
| AM-P0 | `ne` reproduces `c89b0910f`'s rows exactly (**already run: held**, disclosed above) |
| AM-P1 | Crisis MAE is at most £14.99. The level share of the crisis gain is at least two-thirds. |
| AM-P2 | 2022's bias lands within ±£3 of ne's −8.50 |
| AM-P3 | Post-crisis bias lands inside ±£2 |
| AM-P4 | Pre-crisis MAE lands within ±£0.30 of 4.62 |
| AM-P5 | The half-hourly fit MAE is below ne's 31.126 |
| AM-P6 | 2025's bias lands within ±£2 of ne's −7.52 |
| AM-P7 | W L0's crisis MAE is at most £14.46 (two-thirds of W's 17.80 → 12.79 gain) |

The reasoning is as follows. The ne result's biggest moves are year-sized: 2022 is the only exporting year, and
2024-25 import 1.1-1.2 GW more than 2023. Both are level, and both are what the post bias and 2022 bias
responded to. The evaluation reads the daily mean of x, so within-day shape cannot reach a monthly cell. Its
only route is through the refit's coefficients. The day-to-day shape (export on windy days) does reach the
daily x, but it compresses x on days the leg already prices near the floor, so I expect it to be small in money.
P5 follows from the disclosed half-hourly MAEs: the shape raised them, so removing it should lower them.

## Decision rule, filed now

- **(a) The level carries it.** P1 and P3 hold, and pre-crisis MAE does not rise by more than £0.50. A forward
  build then draws an annual net-flow level from the FES band, which is the director's curriculum, and adds
  no shape term. The am − ne gap, by regime, is stated beside every forward figure as the shape the build
  leaves out.
- **(b) The shape carries a material part.** Crisis MAE lands above £14.99 and at or below £16.46. The build
  then needs the level plus the record's within-year shape, conditioned on residual demand (§5a's candidate).
  The next arm is that conditioned shape, pre-registered against this record's am and ne rows.
- **(c) The level alone barely helps.** Crisis MAE stays above £16.46, a gain of less than £2. An annual-level
  build is ruled out, and the next arm is (b)'s conditioned shape.
- If P1 holds but P3 does not, the crisis and post-crisis halves are reported apart and no build follows from
  this arm alone.

Reverse: delete this record.
