**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the net-export shape the price leg needs in the crisis is seasonal, and it is 2022's summer of export (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_IS_THE_NET_EXPORT_SHAPE_THE_PRICE_LEG_NEEDS_IN_THE_CRISIS_SEASONAL_OR_DAY_LEVEL_2026-11-24.md`
(`5a4be139d`), promoted to origin before the `dm` and `mm` arms ran. Probe sha256 `8a3a09a4…`, unchanged.
**Nothing in `sim/` changed.***

## Outcome (monthly, demand-weighted, £/MWh; SAP; form L0)

| Arm | Net export each half-hour sees | R pre | R crisis | R post | R 2022 bias | R hh fit | W crisis |
|---|---|---|---|---|---|---|---|
| `ne` | real half-hourly | 4.62 | **13.29** | 5.99 (−0.30) | −8.50 | 31.126 | 12.79 |
| `dm` | day mean | 4.62 | **13.30** | 6.08 (−0.50) | −8.50 | 30.926 | 13.01 |
| `mm` | month mean | 4.63 | **13.53** | 6.16 (−0.90) | −8.64 | 30.814 | 13.15 |
| `am` | year mean | 4.45 | **16.16** | 5.58 (−0.91) | −8.43 | 30.854 | 15.32 |

The post column gives MAE with bias in brackets. `ne` and `am` reproduce `4984c3dbc`'s rows byte for byte.

**The £2.87 crisis gain the annual level leaves (R), by timescale:**

| Part | Arms | £/MWh | Share |
|---|---|---|---|
| Within the day | `ne → dm` | 0.01 | 0% |
| Day to day within a month | `dm → mm` | 0.23 | 8% |
| Month to month within a year | `mm → am` | 2.63 | **92%** |

For W the same split is 0.22 / 0.14 / 2.17, which puts 86% in the seasonal part.

## Predictions against outcomes

| # | Prediction | Outcome | |
|---|---|---|---|
| MM-P0 | `ne` and `am` reproduce `4984c3dbc` byte for byte | byte for byte | **held** (run before filing, disclosed) |
| MM-P1 | `dm` crisis within ±0.50 of 13.29 | 13.30 | **held** |
| MM-P2 | `mm` crisis ≤ 14.00 | 13.53 | **held** |
| MM-P3 | `mm` crisis ≤ `dm` + 1.00 | 13.53 ≤ 14.30 | **held** |
| MM-P4 | 2022 bias in `dm` and `mm` within ±0.70 of −8.50 | −8.50, −8.64 | **held** |
| MM-P5 | post bias in `dm` and `mm` inside ±1.5 | −0.50, −0.90 | **held** |
| MM-P6 | `mm` pre MAE in [4.45, 4.62] ± 0.10 | 4.63 | **held** (0.01 above ne, inside the tolerance) |
| MM-P7 | `dm` hh fit MAE below 31.126 | 30.926 | **held** |
| MM-P8 | W `mm` crisis ≤ 13.60 | 13.15 | **held** |

Nine of nine held. P1's reasoning was the weakest when filed, and its outcome sits at the edge of the
structural fact: `dm` changes the coefficients (scarcity 1.743 → 1.507) and still moves the crisis cell by
£0.01.

## Decision rule

**Rule (a) fires.** P2 holds, and `mm → am` is £2.63, above the £2.0 bar. The shape the leg needs in the crisis
is month-level.

## What the seasonal part is (descriptive, seen after the run)

This is GB's FUELHH net export, by month, in GW (+ means export), for the years around the crisis. The probe
reads the same series from `/var/tmp/mk22/net_import_hh.json`.

```
       Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
2021  -2.7  -3.5  -2.9  -2.1  -2.8  -3.5  -3.7  -3.9  -2.8  -2.5  -1.6  -2.1
2022  -2.0  -2.9  -2.4  +0.1  +2.4  +2.5  +2.0  +1.3  +3.0  +2.0  +1.3  -1.7
2023  -2.7  -3.6  -3.9  -3.1  -4.3  -2.6  -1.6  -1.9  -1.5  -2.0  -3.3  -1.7
```

Outside 2022, every month from 2016 to 2025 is an import month, apart from November 2017 (+0.1). No recurring
season comes close to 2022's swing. **2022's April to November is one event:** GB exported 1.3-3.0 GW
while French nuclear output was down. No yearly pattern repeats it. That fits a result that was not predicted:
outside the crisis the monthly profile makes the leg worse (R post MAE 5.58 under `am` against 6.16 under `mm`;
W 4.16 against 5.01). Outside 2022, month-to-month movement in net export is noise to this leg.

This is an interpretation of a table seen after the run, not an attribution. The arm below is what tests it.

## What follows

- **For a forward build:** the FES annual level carries the bias. On this record, the shape the crisis needed is
  a neighbour's supply shock arriving as GB demand. A forward draw cannot produce that from a GB climatology. Until
  a mechanism exists that prices a neighbour's shortfall, the forward net-flow term is the annual level alone,
  and every forward figure states that a 2022-type event (£2.6/MWh of crisis monthly MAE on this record) is
  outside it.
- **Next arm (rule (a)'s own), with this table disclosed as seen:** a leave-one-year-out monthly climatology in
  place of each year's own months. My prediction, filed here before it runs: it carries under a quarter of the
  £2.63, and it raises pre- and post-crisis MAE against `am`.

Reverse: delete this record.
