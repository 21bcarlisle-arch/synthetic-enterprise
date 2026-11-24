**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: a net-export profile learnt from other years carries none of the price leg's crisis shape (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_DOES_A_LEAVE_ONE_YEAR_OUT_MONTHLY_NET_EXPORT_PROFILE_CARRY_THE_CRISIS_SHAPE_2026-11-24.md`
(`7f08d5309`), promoted to origin before the `cl` arm ran. Probe sha256 `a8ed792b…`, unchanged.
**Nothing in `sim/` changed.***

## Outcome (monthly, demand-weighted, £/MWh; SAP; form L0)

| Arm | Net export each half-hour sees | R pre | R crisis | R post | R post ex-2025 | R 2022 bias | R hh fit | W pre | W crisis | W post |
|---|---|---|---|---|---|---|---|---|---|---|
| `ne` | real half-hourly | 4.62 | 13.29 | 5.99 | 4.91 | −8.50 | 31.126 | 4.90 | 12.79 | 5.15 |
| `mm` | its month's own mean | 4.63 | 13.53 | 6.16 | 4.96 | −8.64 | 30.814 | 4.72 | 13.15 | 5.01 |
| `am` | its year's mean | 4.45 | **16.16** | 5.58 | 4.64 | −8.43 | 30.854 | 4.58 | **15.32** | 4.16 |
| `cl` | its year's mean + other years' monthly profile | 4.32 | **16.21** | 5.73 | 5.01 | −8.44 | 30.834 | 4.44 | **15.43** | 4.17 |

R's `cl` coefficients are 0.5452 / 0.9418 / 2.143 (`am`: 0.549 / 0.937 / 2.167). The probe asserts that every
year's total net export is preserved. Its control against `synthetic_price` is 1e-13.

**Against `am`, the other-years profile moves R's crisis MAE by +£0.05.** It carries none of the £2.63 that
2022's own months carry, and it is slightly worse. W moves by +£0.11.

## Predictions against outcomes

| # | Prediction | Outcome | |
|---|---|---|---|
| CL-P0 | `ne` and `am` reproduce byte for byte | byte for byte | **held** (run before filing, disclosed) |
| CL-P1 | `cl` crisis ≥ 15.50 | 16.21 | **held** |
| CL-P2 | `cl` pre > 4.45 **and** post > 5.58 | pre 4.32, post 5.73 | **failed** (the post leg held; the pre leg went the other way) |
| CL-P3 | 2022 bias within ±0.70 of −8.43 | −8.44 | **held** |
| CL-P4 | `cl` crisis ≤ 16.66 | 16.21 | **held** |
| CL-P5 | W `cl` crisis ≥ 14.78 | 15.43 | **held** |

Five of six held. **P2 was wrong on the pre-crisis leg.** It reasoned that because `mm` hurt outside the crisis,
a profile learnt from other years would hurt too. Before the crisis, the other-years profile *helps*: R 4.45 →
4.32, W 4.58 → 4.44. After the crisis it hurts R (post ex-2025 4.64 → 5.01) and barely moves W.

## Decision rule

**Rule (a) fires.** P1 holds. On this record the crisis shape is an event and not a GB season: 2022's own
months carry £2.63 of crisis monthly MAE, and a profile from the other nine years carries −£0.05 of it.

- **The forward net-flow term is the FES annual level alone.** No monthly profile is built into it.
- **Every forward figure states beside it** that a 2022-type neighbour shortfall is outside the world. On this
  record that is about £2.6/MWh of crisis monthly MAE on R's leg (W: £2.2). The statement holds until a
  mechanism prices a neighbour's shortfall.
- **Item 4's net-export leg is complete for the level.** What is left of it is the neighbour mechanism (French
  nuclear availability arriving as GB export demand). That needs its own K8 section before any build. It is
  not started here.

## What the profile is (descriptive, seen after the run)

The leave-one-year-out profile is a weak, recurring import season. Re-centred on 2019's level, it reads:

```
       Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
2019  -2.26 -3.20 -3.54 -2.75 -2.74 -2.50 -2.39 -2.42 -1.84 -1.83 -1.77 -2.10   GW, + = export
```

It imports most in February and March and least in September to November. The peak-to-trough swing is about
1.8 GW, against 2022's own swing of about 5 GW from March to September. This shape is what the pre-crisis gain
of £0.13 rides on. **That gain is seen after the run and not attributed.** It is too small to justify building a
profile against the post-crisis cost it brings with it (R +£0.37 ex-2025).

## What follows

- Still owed under item 4, as the timescale result named: (1) B1-B3 rerun on SAP plus net export; (2) R's 2025
  residual against the AGWS windows finding; (3) the neighbour-shortfall K8 section (new, from this arm).
- Rule (a) also says the forward net-flow build is the FES annual level plus nothing. Its build waits on the
  DIRECTION `not_now` hold on SAP, as `c89b0910f` recorded, and is not started here.

Reverse: delete this record.
