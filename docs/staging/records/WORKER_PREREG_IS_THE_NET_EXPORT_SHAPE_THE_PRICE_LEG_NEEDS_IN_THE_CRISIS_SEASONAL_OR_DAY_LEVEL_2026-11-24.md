**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: is the net-export shape the price leg needs in the crisis seasonal, day-to-day, or within the day? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next 1 of the annual-mean result (`4984c3dbc`). Filed and landed before the `dm` and `mm` arms run.
**Nothing in `sim/` changes.***

## The question

On SAP, R L0's crisis monthly MAE is £18.46 with no net export, £16.16 with each year's mean net export (`am`),
and £13.29 with the real half-hourly series (`ne`). The £2.87 between `am` and `ne` is the within-year shape. A
forward build gets the annual level from FES. **Which part of the within-year shape carries the £2.87, at what
timescale?**

## Definitions

Each arm replaces each half-hour's FUELHH net export with its mean over the probe's common half-hours, grouped
by a coarser and coarser bucket. Each arm preserves every group's total, and the probe asserts it.

| Arm | Net export each half-hour sees | What it removes relative to the arm above |
|---|---|---|
| `ne` | the real half-hourly value | nothing |
| `dm` | its day's mean | the within-day shape |
| `mm` | its calendar month's mean | day-to-day movement within the month |
| `am` | its calendar year's mean | month-to-month movement within the year (the seasonal part) |

So `ne → dm` is the within-day part, `dm → mm` the day-level part, and `mm → am` the seasonal part. These are
the three timescales a forward build would have to supply.

**A structural fact, stated before the run.** Net export enters x linearly, and the evaluation reads each day's
mean of half-hourly x. So `dm` and `ne` give every day the same evaluated x. `ne → dm` can move a monthly cell
only through the refit's three coefficients.

## Design

- **Probe:** `/var/tmp/wpc_mm/measure_mm.py`, sha256
  `8a3a09a4f97c6cb3cc44482e1ab5f2856ad74349d1664d25eb913c277bbdb3bb`. It is `/var/tmp/wpc_am/measure_am.py`
  (`f29e1f55…`) with the year-mean substitution generalised to a group key of the date's first 10, 7 or 4
  characters. Everything else is unchanged: the same 157,010 common half-hours, form L0, bases R and W, SAP,
  and the same refit and evaluation. It runs in a worktree at origin `4984c3dbc` with `sim/cache` linked in.
- **Seen before filing, and disclosed:** this probe's `ne` and `am` arms have run. Both reproduce
  `/var/tmp/wpc_am/out_ne.json` and `out_am.json` byte for byte (controls). No `dm` or `mm` figure has been
  computed.

## Predictions (R L0 unless stated; monthly, demand-weighted, £/MWh)

| # | Prediction |
|---|---|
| MM-P0 | `ne` and `am` reproduce `4984c3dbc`'s rows byte for byte (**already run: held**, disclosed above) |
| MM-P1 | `dm`'s crisis MAE is within ±£0.50 of ne's 13.29. The within-day part is small. |
| MM-P2 | `mm`'s crisis MAE is at most £14.00. At least 75% of the £2.87 `am → ne` gap is month-level or finer, and most of that is seasonal. |
| MM-P3 | `mm`'s crisis MAE is at most `dm`'s + £1.00. The day-level part is at most £1. |
| MM-P4 | 2022's bias in `dm` and in `mm` is within ±£0.70 of ne's −8.50. The level still carries the bias. |
| MM-P5 | Post-crisis bias in `dm` and `mm` is inside ±£1.5 |
| MM-P6 | `mm`'s pre-crisis MAE lies between am's 4.45 and ne's 4.62, within ±£0.10 of that interval |
| MM-P7 | `dm`'s half-hourly fit MAE is below ne's 31.126 |
| MM-P8 | W L0's `mm` crisis MAE is at most £13.60 (75% of W's 15.32 → 12.79 gap) |

The reasoning is as follows. In 2022 GB exported to France through the summer, while French nuclear was out,
and imported in the winters either side. That is a month-sized pattern, and it sits inside the crisis window
(July 2021 to June 2023). Day-to-day export follows wind, which the leg already sees through x. I therefore
expect the day-level part to matter little to a monthly cell, through the scarcity term's convexity alone. The
within-day part cannot reach the evaluation except through the coefficients (the structural fact above), and
Those coefficients do move with the shape. From `ne` to `am` they go from 0.524 / 0.998 / 1.743 to
0.549 / 0.937 / 2.167 (R), and the scarcity term moves most. So P1 is the least certain of these predictions. I
still expect the within-day part of that movement to be small, because the steep end of x is set by day-sized
swings in wind and demand.

## Decision rule, filed now

- **(a) Seasonal.** P2 holds and `mm` − `am` is at least £2.0 of the gap. A forward build needs the FES annual
  level plus a monthly profile. The next arm asks whether a profile drawn from other years (a climatology,
  leaving the scored year out) carries the crisis gain, or whether only 2022's own months do. If only 2022's own
  months do, the shape is a neighbour's supply shock (French nuclear), not a GB pattern. A forward build then
  cannot carry it without a neighbour-price mechanism, and the crisis shape error is stated beside every forward
  figure.
- **(b) Day-level.** P2 fails, and `dm`'s crisis MAE is at most £14.00. The shape must be conditioned on the day,
  on residual demand or wind (§5a's candidate). The next arm is that conditioned shape.
- **(c) Within the day.** `dm`'s crisis MAE is above £14.00. The coefficients are mis-estimated without the
  half-hourly shape. A forward build needs a half-hourly net-export shape, and the next arm asks what that shape
  follows.
- If none of these is clean, the three parts are reported by regime and no build follows from this arm alone.

Reverse: delete this record.
