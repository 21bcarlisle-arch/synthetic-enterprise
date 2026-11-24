**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the weather-to-price chain loses to a gas-only null at the month and the quarter, in every regime (2026-11-24)

**Pre-registration.** `WORKER_PREREG_GRADE_THE_WEATHER_TO_PRICE_CHAIN_ON_THE_RECORD_BY_REGIME_2026-11-24.md`.
It landed in `2a24f6c54`, before this run.

**How it was run.** The probe was run exactly as carried in that record. It ran from the repo root
of the shared tree, whose `sim/` chain modules are byte-identical to origin's. It took 26 s over
3,337 days.

**Steer answered.** Items 1-2 of
`docs/staging/advisor/DIRECTOR_STEER_GRADE_THE_WEATHER_TO_PRICE_CHAIN_ON_THE_RECORD_NOW_SO_FORWARD_YEARS_ARE_NOT_HELD_BY_IT_2026-11-24.md`.
Nothing in the chain was changed.

## Verdict: not fit for forward years on hedging and pricing

**P1 (monthly) and P2 (quarterly) fail in all three regimes.** A one-line regression of daily SSP on
the NBP gas price prices a demand-weighted month better than the chain does, before, during and
after the crisis.

| Regime | Days | Real mean £/MWh | Chain mean | Chain monthly MAE / median APE | Gas-only null monthly MAE / median APE | Chain monthly bias |
|---|---|---|---|---|---|---|
| Pre (2016 to Jun 2021) | 1,921 | 46.1 | 34.2 | £12.4 / 25.9% | £5.4 / 9.8% | −£12.0 |
| Crisis (Jul 2021 to Jun 2023) | 708 | 166.3 | 178.9 | £31.5 / 18.8% | £24.5 / 13.4% | +£12.1 |
| Post (Jul 2023 on) | 708 | 77.5 | 75.3 | £10.2 / 10.1% | £6.7 / 5.5% | −£2.1 |

**The fleet does not help.** The year-aware variant (W1_7 per-year fleet) is worse in every regime
at the month, with median APE of 44%, 21% and 22%.

**Read this beside it.** The null is fit in-sample, with an intercept, so it absorbs any constant
level the chain omits. The chain is also fit on the whole record, through `sim/price_engine.py`'s
calibration. The comparison is fair as a test of "does the chain add anything at the month". It
is not a claim that a gas-only model is a good world.

## Volatility, coupling and spells against the record's 90% band

| Statistic | Pre | Crisis | Post |
|---|---|---|---|
| Daily std | PASS | PASS | PASS |
| Weekly std | PASS | FAIL-high | PASS |
| Monthly std | FAIL-high | FAIL-high | FAIL-high |
| Daily 99th percentile | FAIL-low | PASS | FAIL-high |
| Daily 1st percentile | FAIL-low (chain −£5, real £14) | FAIL-low | FAIL-low |
| Cold-and-still premium (real / chain) | PASS (1.78 / 2.14) | PASS (1.99 / 1.97) | PASS (1.87 / 1.93) |
| Lag-1 autocorrelation | FAIL-high (0.47 against 0.27) | PASS | PASS |
| Lag-7 autocorrelation | FAIL-low | PASS | PASS |
| Price anomaly against temperature | FAIL-low (−0.38 against −0.16) | FAIL-low (−0.49 against −0.23) | FAIL-low (−0.56 against −0.20) |
| **Price anomaly against wind** | **FAIL-low (−0.82 against −0.15)** | **FAIL-low (−0.83 against −0.33)** | **FAIL-low (−0.86 against −0.41)** |
| Half-hourly 99.9th percentile | FAIL-low (£113 against £441) | PASS | PASS |
| Half-hourly within-day std | FAIL-low | FAIL-low | FAIL-low |

**Correction, beside the claim: the quarterly-std band is void.** In the pre-crisis and
post-crisis regimes, the real quarterly std lies *outside its own* bootstrap band. Pre-crisis,
the real value is 11.98 and the band runs 5.73 to 9.73. The bootstrap glues three randomly drawn
months into a pseudo-quarter, so it mixes seasons and understates quarter-to-quarter spread. Its
verdicts are dropped. The monthly band does contain the real value in every regime.

## Predictions against outcomes (filed before; kept as written)

| Prediction | Outcome |
|---|---|
| P1/P2 pass before and after the crisis and fail in it | **Wrong.** They fail in all three regimes |
| Daily volatility FAIL-low before and after the crisis | **Wrong.** It passes. The excess is at the *monthly* scale and it is high |
| Cold-and-still premium FAIL-high; real ratio 1.3-1.6x | **Wrong.** It passes in every regime. The real ratio is 1.78-1.99x |
| Lag-1 autocorrelation FAIL-low | **Wrong.** FAIL-high before the crisis; passes after |
| Half-hourly 99.9th percentile FAIL-low, at least in the crisis | Wrong in the crisis (it passes); FAIL-low before the crisis |
| Largest cause sits in the top gas quintile | **Half right.** The crisis error does concentrate there (mean error +£67 in the top gas quintile, −£21 in the bottom). The pre-crisis error does not: it is a flat negative bias across every gas quintile |

## Causes, ranked by the evidence here (to be decided by the gas and electricity pages, not by this table)

1. **The weather coupling is two to five times too strong, wind above all.** This fails in every
   regime, and it is the one defect that also explains the monthly volatility FAIL-high. A windy
   or still month swings the chain's monthly price far more than the record's.
   - Candidates the page must weigh: the missing interconnector term, which imports into scarcity
     and exports into surplus and so damps both; the power curve and fleet scale; and residual
     demand mapping too steeply into price.
   - The fattened low tail points the same way: the chain's daily 1st percentile is negative
     where real prices were not.
2. **Pre-crisis level bias of −£12/MWh.** It is flat across gas quintiles and rises by year (MAE
   £11.9 in 2017, £20.8 in 2021). This is what a missing carbon cost looks like: Carbon Price
   Support plus an EU ETS price that rose from about €5 to over €50 over the same years. That
   matches the 05:39 addendum's suspect. **Not yet attributed.** The carbon arm is to be graded
   with and without, with its prediction filed first.
3. **Crisis mis-scaling at high gas.** +£67/MWh mean error in the top gas quintile. This is the
   gas-floor and residual-to-price mapping candidate.
4. **Within-day shape too flat.** Within-day std is about 40-70% of real in every regime. This is
   `intraday_shape`'s, not the chain's.

**Known error, until fixed** (FORWARD_YEARS_RECOMMENDATION §3). Every forward figure formed from
this chain carries a monthly cost-of-supply error of 10-26% median APE, depending on regime. That is
worse than a gas-only regression.

## What this does to the order of work

**Nothing is rebuilt from this record.** The 05:40 addendum puts the deep gas page first, then the
electricity page (merit order, carbon, interconnectors, CfD and RO, nuclear, scarcity), then the
rebuild in order of the largest gap. This grade gives that rebuild its starting ranking, and it
gives the pages two questions to answer:

- Why does GB price respond to wind far less than a closed-system merit order would?
- How much of the pre-crisis gap is carbon?

**Raw output:** reproduce it with the probe. It was not committed, being 26 s to regenerate.
