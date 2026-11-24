**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: refitted with carbon in its floor, the chain stops counting carbon twice after 2021, and it ties the gas-only null in the crisis but still loses to it either side (2026-11-24)

Item 4, step 1 of the weather-to-price steer, held by
`WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`.
The prediction was filed before this ran, in
`WORKER_RESULT_CARBON_EXPLAINS_THE_CHAINS_PRE_CRISIS_BIAS_AND_ITS_MULTIPLIER_ALREADY_CARRIES_IT_AFTER_2021_2026-11-24.md`
§4: "with carbon in the floor and the multiplier refitted, post-crisis monthly MAE ≤ £11 (no worse than
without carbon) and the pre-crisis bias stays within ±£5. If the post-crisis error stays above £15,
(a) is refuted."

## What changed: one variable

The variable is the carbon term in the floor during the fit. Everything else is the shipped fit:
`simulation/run_phase3b_recalibration.py`'s own `_build_dataset` (157,106 half-hours, 2016-03-01 to
2025-06-07, NBP gas, INDO demand, AGWS wind and solar), its `_fit_form` (closed-form least squares for
A0/A1/A2), and its selected `X_TIGHT = 0.70`, `p = 2.0`. Carbon is the carbon arm's primary series:
CPS £18/t plus the EUA VWAP to 2020, and from May 2021 the month's UK ETS auction VWAP, carried back
over Jan-Apr 2021.

Two controls, both asserted in the probe:
- A refit with carbon at zero reproduces the shipped constants (A0 0.326998, A1 1.334629,
  A2 3.828327).
- The shipped arm reproduces the graded chain exactly.

Grading is the carbon arm's: the same chain, monthly, weighted by real INDO demand, by regime.

## The fit

| Fit (half-hourly, full window) | A0 | A1 | A2 | MAE | R² |
|---|---|---|---|---|---|
| shipped (carbon 0) | 0.3270 | 1.3346 | 3.8283 | £32.79 | 0.419 |
| **refit, carbon in floor** | **0.2916** | **1.0792** | **2.8242** | **£31.53** | **0.438** |

The slope falls by a fifth and the scarcity kicker by a quarter. That is the multiplier giving back
what it had been carrying for the missing carbon.

## The grade (monthly, demand-weighted, £/MWh)

| Arm | Pre MAE · bias · median APE | Crisis MAE · bias · median APE | Post MAE · bias · median APE |
|---|---|---|---|
| shipped, no carbon (as graded) | 12.38 · −11.97 · 25.9% | 31.52 · +12.09 · 18.8% | 10.25 · −2.11 · 10.1% |
| shipped, carbon added (the carbon arm) | 7.14 · +3.08 · 12.3% | 53.16 · +49.71 · 29.5% | 23.44 · +23.23 · 27.7% |
| **refit, carbon in floor** | **6.75 · −5.43 · 11.2%** | **24.33 · +12.29 · 11.6%** | **9.29 · +5.82 · 10.7%** |
| gas-only null (the grade's) | 5.4 · — · 9.8% | 24.5 | 6.7 |

Bias by year, refit: 2016 −8.7, 2017 −5.6, 2018 −5.1, 2019 −3.4, 2020 −6.3, 2021 H1 −2.6; 2021 H2 −1.9,
2022 +26.1, 2023 H1 −1.1; 2023 H2 −2.6, 2024 +4.8, 2025 +16.2.

## Predictions against outcomes (kept as filed)

| Filed | Outcome | Held? |
|---|---|---|
| Post-crisis MAE ≤ £11 | 9.29 | **held** |
| Pre-crisis bias within ±£5 | −5.43 | **missed** by £0.43 |
| Refutation of (a): post-crisis MAE > £15 | 9.29 | **not refuted** |

## What it shows

1. **(a) holds: the shipped multiplier was carrying carbon.** The refit takes the carbon arm's post-crisis
   error from £23.4 to £9.3 and its crisis error from £53.2 to £24.3. Both are lower than the chain
   without carbon. Nothing else changed, so this is attributed.
2. **The refit puts carbon in the floor without wrecking either end.** It is better than the
   shipped chain in all three regimes on MAE (12.4 → 6.8, 31.5 → 24.3, 10.3 → 9.3). The year-by-year
   growth of the pre-crisis bias is gone. What is left is a level of about −£5, and the fit trades it
   against the later years.
3. **It still does not beat the gas-only null outside the crisis.** Before the crisis: 6.75 against
   5.4, median APE 11.2% against 9.8%. After the crisis: 9.29 against 6.7. In the crisis it ties
   (24.33 against 24.5). Carbon was a real gap, and it was not the only one. The next candidate, as the
   grade named it, is weather coupling two to five times too strong (wind above all). That is what
   2025's +£16 looks like as well: the most wind, the largest positive bias.
4. **2022's +£26 is mostly the gas input, not the chain.** The chain prices off TTF, which ran 29%
   over GB gas in 2022 (`the_worlds_gas_price_record_splices_daily_sap_from_2018_2026-11-18.md`).
   Explanation (b) of the carbon record stands, and the refit cannot touch it.

## What this does NOT do

- **Nothing in the world changed.** `sim/price_engine.py` still ships the carbon-zero constants, and
  every chain call still passes carbon 0.0. Shipping the refit is the next step, and it is more than
  swapping constants. The sim needs a time-indexed carbon series that the chain passes. The refitted
  constants without carbon in the call would be worse than either shipped arm. Forward years need a
  drawn carbon in a sourced band, and that band is the director's curriculum (steer item 5).
- `sim/merit_order_reconstruction.py` still names 2022-2024 as allowance gap years. The previous record
  said this step would fill them. It does not. That change belongs with the series the sim will read,
  so that one table, not two, holds the allowance price.
- X_TIGHT and p were held at the shipped selection so that the fit changes in only one variable. A
  re-search of the grid with carbon in the floor is a separate arm.

## The probe

Read-only. It was run from the shared repo root, whose `sim/price_engine.py`, `sim/weather_price_chain.py`,
`sim/merit_order_reconstruction.py`, `sim/gas_prices_history.py`, `sim/renewable_capacity_trend.py`,
`sim/cache_store.py` and `simulation/run_phase3b_recalibration.py` were checked identical to
`origin/main` by blob hash before the run. Run it as `python3 probe.py uka.json`, where `uka.json` is the
`auctions` array of `docs/market_research/uk_ets_allowance_auction_clearing_prices_2021_2025.json`.
It takes about 4 minutes.

```python
import json, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, ".")
import sim.price_engine as pe
from simulation.run_phase3b_recalibration import _build_dataset, _fit_form, SELECTED_X_TIGHT, SELECTED_SCARCITY_EXPONENT
from sim.weather_price_chain import derive_price_on_record, load_daily_record
from sim.merit_order_reconstruction import ets_carbon_price_gbp_per_tonne, CPS_CARBON_GBP_PER_TONNE

UKA = json.load(open(sys.argv[1]))
m = defaultdict(lambda: [0.0, 0.0])
for a in UKA:
    k = a["date"][:7]; m[k][0] += a["allowances"] * a["clearing_gbp_per_t"]; m[k][1] += a["allowances"]
uka_month = {k: s / n for k, (s, n) in m.items()}
FIRST = min(uka_month)

def allowance(month):
    y = int(month[:4])
    if y <= 2020:
        return ets_carbon_price_gbp_per_tonne(y)
    if month < FIRST:
        return uka_month[FIRST]
    return uka_month[max(k for k in uka_month if k <= month)]

def carbon(month):
    return CPS_CARBON_GBP_PER_TONNE + allowance(month)

rows = _build_dataset()
gas = np.array([r["gas_price"] for r in rows]); dem = np.array([r["demand_mw"] for r in rows])
ren = np.array([r["renewable_mw"] for r in rows]); ssp = np.array([r["ssp"] for r in rows])
c = np.array([carbon(r["settlementDate"][:7]) for r in rows])
x = (dem - ren) / pe.DISPATCHABLE_CAPACITY_MW
fits = {}
for name, floor in {"zero": gas / pe.THERMAL_EFFICIENCY,
                    "carbon": (gas + c * pe.EF_GAS_TCO2_PER_MWH_TH) / pe.THERMAL_EFFICIENCY}.items():
    f = _fit_form(floor, x, ssp, SELECTED_X_TIGHT, SELECTED_SCARCITY_EXPONENT); f.pop("predictions")
    fits[name] = f
assert abs(fits["zero"]["a0"] - pe.A0) < 1e-4 and abs(fits["zero"]["a1"] - pe.A1) < 1e-4

REGIMES = {"pre": ("2016-01-01", "2021-06-30"), "crisis": ("2021-07-01", "2023-06-30"), "post": ("2023-07-01", "2099-12-31")}
d = derive_price_on_record()
dates, real, g, dm, rn = d["dates"], d["real_ssp"], d["gas_price"], d["demand_mw"], d["renewable_mw"]
w_real = load_daily_record()["demand_mw"]

def arm(coefs, with_carbon):
    pe.A0, pe.A1, pe.A2 = coefs
    return np.array([pe.synthetic_price(float(g[i]), float(dm[i]), float(rn[i]),
                     carbon_price_gbp_per_tonne=carbon(dates[i][:7]) if with_carbon else 0.0) for i in range(len(dates))])

shipped = (pe.A0, pe.A1, pe.A2)
arms = {"shipped_no_carbon": arm(shipped, False), "shipped_with_carbon": arm(shipped, True),
        "refit_with_carbon": arm((fits["carbon"]["a0"], fits["carbon"]["a1"], fits["carbon"]["a2"]), True)}
pe.A0, pe.A1, pe.A2 = shipped
assert np.allclose(arms["shipped_no_carbon"], d["derived_price"])
# then: monthly demand-weighted MAE, bias, median APE and bias by year per regime, as in the carbon arm's probe
```
