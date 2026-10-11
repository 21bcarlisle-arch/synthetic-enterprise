**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the hedge volume reads only what the company holds (2026-10-11)

Claim `the-hedge-volume-reads-only-what-the-company-holds`. Written BEFORE either arm ran.

## The change (one variable: the volume the desk is handed)

`simulation/run_phase2b._company_eac_estimate` stops summing the settled fold's true kWh and stops
multiplying the declared EAC by `household_demand_register.eac_multiplier_for_date`; the gas leg stops
multiplying the registry AQ by `gas_eac_multiplier_for_date` **for the hedge** (the world's gas demand
still uses the multiplied AQ -- that is the household, not the company's belief). Both fuels instead
ask `company.interfaces.sim_interface.supplier_annual_volume_kwh`, handed only register reads the
company holds (the change-of-supply opening read plus each month whose read ARRIVED before the term
starts, per `simulation/meter_reads.simulate_read`) and the registry EAC/AQ. It annualises the most
recent advance spanning 6-24 months (the one nearest a year) against the published monthly profile;
before such an advance exists it returns the registry figure.

## Instrument

`/var/tmp/forecast_audit/drive.py`'s 40-founder production run, one seed, the same arguments in both
arms, each in its own worktree (HEAD `99f4c5742` before; the change after). Graded: each
`decide_term_hedge` volume against the next 12 months' settled kWh from the term start (held back).
Hedge cost: the run's `total_capital` (sum of `capital_cost_gbp`) and the summed `hedge_pnl_gbp`.

## Predictions (MAPE / mean signed error of the hedge volume, %)

| cell | before (expected, the finding's table) | after (predicted) |
|---|---|---|
| electricity, first term | ~8.8 / +8 | ~13 / -2 (the registry, F1's row: unbiased, noisier) |
| electricity, later terms | ~1.9 / 0.0 | 2-5 / within +-2 (an advance over arrived reads, profile-weighted) |
| gas, first term | ~8.2 / +8 | ~14 / -4 (registry) |
| gas, later terms | ~7.2 / +6.5 | 3-7 / within +-3 (the AQ now learns from gas reads) |

- **Pooled bias** falls from about +5% toward 0; pooled MAPE moves by less than 3 points either way.
- **`total_capital`** falls by 2-8% (naked volume down on first terms and every gas term). Sign is the
  firmer half of this prediction; the size is soft.
- **Summed `hedge_pnl_gbp`** moves by less than 10% of its own magnitude: it is settled on actual
  volume x the hedge fraction, so only via the desk's fraction decisions.
- **What would refute the frame:** later-term electricity MAPE above 6% (the read-arrival model starves
  the advance), or `total_capital` RISING (the volume was under-, not over-stated somewhere I have not
  looked).

## Result (graded as written; the predictions above are unedited)

Both arms: `drive.py 40 400`, one seed, each in its own worktree. **One harness change, made before
either arm produced output and applied to both:** the patched 400 customer-year budget is off the
measured run-cost curve, so `_box_admission` declared no weight and the box queue refused it for four
hours. The driver now declares the `sim_run` class weight. That changes when a run starts, not what
it computes. Each arm made 798 hedge decisions and the same 606 were graded, matched one to one by
(account, term start, fuel). The truth is the settled kWh of the 12 months from the term start.

| cell | n | before MAPE / signed | after MAPE / signed | predicted after | verdict |
|---|---|---|---|---|---|
| electricity, first term | 34 | 10.0 / +9.1 | **7.8 / +6.8** | ~13 / -2 | **refuted**: the registry over-forecasts here; the multiplier only added to it |
| electricity, later terms | 374 | **10.0 / -4.1** | **5.3 / +3.0** | 2-5 / within +-2 | **refuted on both sides**, see below |
| gas, first term | 15 | 10.1 / +9.9 | 7.3 / -0.6 | ~14 / -4 | bias held; MAPE refuted (better than predicted) |
| gas, later terms | 183 | 11.2 / +10.5 | 6.3 / +3.9 | 3-7 / within +-3 | MAPE held; bias just outside |
| pooled | 606 | 10.4 / +1.4 | **5.8 / +3.4** | bias toward 0, MAPE within 3 points | **both refuted**: MAPE fell 4.6 points and the pooled bias ROSE |

| hedge cost | before | after | change | predicted | verdict |
|---|---|---|---|---|---|
| `total_capital` (GBP) | 1,652.27 | 1,656.11 | **+0.2%** | -2 to -8% | **refuted, and in the named refuting direction** |
| electricity capital | 1,022.89 | 1,069.92 | +4.6% | (down) | refuted |
| gas capital | 629.38 | 586.19 | -6.9% | (down) | held |
| summed `hedge_pnl_gbp` | 1,092.02 | 1,091.93 | -0.01% | <10% | held |
| net margin (GBP) | 36,368.42 | 36,358.83 | -9.59 | -- | -- |

**Why it was refuted.** My frame came from the finding's table, which had later-term electricity at
1.9 / 0.0. On this book the old trailing sum was **10.0 / -4.1**. It under-stated the volume whenever
the twelve-month window held less than a year of supply, because it summed whatever days the window
held and never annualised them. That is exactly the refuting case I named in advance: the volume was
UNDER-stated somewhere I had not looked. Annualising the advance removed the under-statement, which
raised the electricity naked volume and its capital, and roughly cancelled the gas saving. The pooled
bias rose because the old electricity under-forecast had been offsetting the gas over-forecast.

**What is left, and it is the company's own error now.**
- Later-term electricity sits at +3.0% and gas at +3.9%: an advance annualised on the published
  monthly profile over-states this world's year. For gas, that is the open season finding's heavier
  world summer (`SEAT_FINDING_A_GAS_HOMES_SEASON_MISS_IS_THE_WINTER_AND_LIGHTING_IS_THE_ONE_TERM_OFF_ITS_SOURCE_2026-10-09.md`).
- First-term electricity at +6.8% is the registry's own over-forecast. The median error is 1.7%, so a
  few accounts carry the mean.

**`demand_estimation_log`.** 31 rows in both arms. Before: all 31 "graded" at a mean |error| of 1.6%,
the trailing year against the run-average year. After: 19 graded against the year that followed, at
**3.5%**; 12 are ungraded because the run did not settle their year ahead, and each says so.
