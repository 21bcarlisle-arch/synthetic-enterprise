**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does a leave-one-year-out monthly net-export profile carry the price leg's crisis shape? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is the next arm named in the timescale result (`9a5e85817`), under its rule (a). Filed and landed before
the `cl` arm runs. **Nothing in `sim/` changes.***

## The question

On SAP, R L0's crisis monthly MAE is £16.16 with each year's mean net export (`am`) and £13.53 with each
month's own mean (`mm`). That £2.63 is the seasonal part. A forward build has no future year's own months:
it has an FES annual level and, at most, a profile learnt from other years. **Does a profile learnt from the
other years carry the £2.63? Or does only the scored year's own months carry it, which would make the crisis
shape an event (2022's summer of export while French nuclear was down) and not a GB season?**

## Definition

`cl`: each half-hour in calendar year y and month m sees

  year mean(y) + A(y, m) − Ā(y)

- **A(y, m)** is the leave-one-year-out anomaly. It is the half-hour-weighted mean, over every other year y′
  in the probe's rows that has month m, of (month mean(y′, m) − year mean(y′)).
- **Ā(y)** is the mean of A over year y's own half-hours. Subtracting it re-centres the profile, so year y's
  total is unchanged. The probe asserts that for every year.

So `cl` and `am` carry the same annual level. They differ only in a seasonal profile that a forward draw could
actually have. Year y's own months never enter year y's profile.

## Design

- **Probe:** `/var/tmp/wpc_cl/measure_cl.py`, sha256
  `a8ed792b4abb6df48bf28f2c3f657300958a94fbc62f5bd0a992efcd83249243`. It is `/var/tmp/wpc_mm/measure_mm.py`
  (`8a3a09a4…`) with one arm added. Everything else is unchanged: the same 157,010 common half-hours, form L0,
  bases R and W, SAP, and the same refit and evaluation. It runs in a worktree at origin `92b8e358e` with
  `sim/cache` linked in. `sim/` and `simulation/` are unchanged between `4984c3dbc` and `92b8e358e`.
- **Seen before filing, and disclosed:** this probe's `ne` and `am` arms have run. Both reproduce
  `/var/tmp/wpc_mm/out_ne.json` and `out_am.json` byte for byte (controls). No `cl` figure has been computed,
  and neither has the profile the arm prints.

## Predictions (R L0 unless stated; monthly, demand-weighted, £/MWh)

| # | Prediction |
|---|---|
| CL-P0 | `ne` and `am` reproduce `9a5e85817`'s rows byte for byte (**already run: held**, disclosed above) |
| CL-P1 | `cl`'s crisis MAE is at least £15.50, so it carries under a quarter of the £2.63 (the timescale result's own prediction) |
| CL-P2 | `cl`'s pre-crisis MAE is above am's 4.45, and its post-crisis MAE is above am's 5.58 (also filed in that result) |
| CL-P3 | `cl`'s 2022 bias is within ±£0.70 of am's −8.43. The level still carries the bias. |
| CL-P4 | `cl`'s crisis MAE is at most am's + £0.50 (16.66). A diluted profile neither helps nor badly hurts. |
| CL-P5 | W L0's `cl` crisis MAE is at least £14.78, so it carries under a quarter of W's 2.17 `am → mm` gap |

The reasoning: in the timescale result's month table, every month from 2016 to 2025 outside 2022 is an import
month apart from November 2017, and no recurring season comes near 2022's April-to-November swing. Scored on
2022, a leave-one-year-out profile is built from years without that event, so it should be nearly flat.
Scored on 2021 and 2023, it carries 2022's summer diluted by about one in nine, which is too small to matter.
Outside the crisis, the monthly profile already made the leg worse in `mm` (R post 6.16 against 5.58), so a
profile learnt from other years should hurt there as well, though by less.

## Decision rule, filed now

- **(a) Event, not season.** P1 holds. The forward net-flow term is the FES annual level alone. No monthly
  profile is built. Every forward figure states beside it that a 2022-type neighbour shortfall (£2.6/MWh of
  crisis monthly MAE on this record) is outside the world, until a mechanism prices a neighbour's shortfall.
  Item 4's net-export leg is then complete for the level, and what is left of it is the neighbour mechanism,
  which gets its own K8 section before any build.
- **(b) A recurring season.** `cl`'s crisis MAE is at most £14.85, so it carries at least half the £2.63. A
  forward build carries a leave-one-year-out monthly profile on the FES level. The next arm checks that it does
  not cost pre- and post-crisis accuracy beyond P2's margin.
- **(c) In between** (14.85 < crisis < 15.50). The result is reported by regime, no profile is built from this
  arm alone, and forward figures carry the known error, as in (a).

Reverse: delete this record.
