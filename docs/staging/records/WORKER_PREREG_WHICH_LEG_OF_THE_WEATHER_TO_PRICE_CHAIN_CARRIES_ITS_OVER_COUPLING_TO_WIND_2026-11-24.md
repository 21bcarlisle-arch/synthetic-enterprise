**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: which leg of the weather-to-price chain carries its over-coupling to wind (2026-11-24)

Item 4, step (ii) of the weather-to-price steer, held by
`WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`.
Filed and landed before the probe below is run.

## What "too strong" means here

The grade said the weather coupling is "two to five times too strong, wind above all". It read that
from **correlations**: the price anomaly against the wind anomaly is −0.82 to −0.86 in the chain, and
−0.15 to −0.41 in the record. A correlation is not a strength. It mixes the slope with every driver
of price the chain lacks, such as outages, interconnector flows and the balancing market. A chain
whose price is a deterministic function of weather and gas will correlate near −1 with wind at any
slope.

**So coupling is defined here as a slope.** It is the OLS slope of the daily price anomaly on the
daily national wind-speed anomaly, in £/MWh per m/s. An anomaly is the value minus its calendar-month
mean. The correlation is reported beside it, but the verdicts below read the slope.

## The arms: one leg swapped at a time

The base is the step-1 refit with carbon in its floor (`d424b78095`). The probe reproduces its
constants before it runs anything.

| Arm | Demand | Renewable | What it isolates |
|---|---|---|---|
| A | weather (degree-day fit) | weather (power curve × whole-window fleet) | the chain as refitted |
| B | real INDO | real AGWS wind + solar | the price leg alone |
| C | weather | real | the renewable leg (A against C) |
| D | real | weather | the demand leg (A against D) |

Also recorded for each regime:
- the renewable leg directly, as real and chain mean MW and MW per m/s;
- the price leg directly, as £/MWh per GW of real renewable anomaly, for the record and for arm B.

The regimes and the monthly demand-weighted grade are the grade's own.

## Predictions, filed before the run

- **W1. The over-coupling survives as a slope.** Arm A's slope per m/s is at least 1.5 times the
  record's, in both the pre-crisis and post-crisis regimes. *If it is under 1.5 times in either
  regime, most of the grade's "two to five times" was missing noise, not strength.*
- **W2. The fleet is misallocated by year.** Before the crisis, the chain's mean renewable MW is
  above the record's. After it, the chain's is below. The cause is one whole-window fleet scale
  against a fleet that roughly tripled.
- **W3. The price leg over-couples on its own.** In arm B, £/MWh per GW of real renewable anomaly
  is at least 1.3 times the record's, before and after the crisis. The candidate cause is missing
  interconnector damping. *Refuted if B is within ±30% of the record. In that case the fix belongs
  in the generation leg, and an interconnector term is not the next build.*
- **W4. Real renewable improves the month.** Arm C beats arm A on monthly MAE before and after the
  crisis.
- **W5. The correlation gap is mostly missing drivers.** Arm B's correlation with wind is at or
  below −0.6 before the crisis, even with real inputs.

Whatever the result, nothing in the world changes in this step. It decides which leg the next build
touches.

## The probe

It runs from the repo root, against `sim/` and `simulation/` modules that are checked to be
blob-identical to origin first. Call it as `python3 probe.py uka.json`, where `uka.json` is the
`auctions` array of `docs/market_research/uk_ets_allowance_auction_clearing_prices_2021_2025.json`.

```python
"""Item 4, weather-coupling arm, step (ii)a: WHICH LEG carries the chain's over-coupling to wind.
Read-only; run from the repo root: python3 probe.py uka.json. Base = the refit with carbon in its
floor (d424b78095's constants, carbon passed). Arms swap ONE leg of the chain for the record:
  A chain (weather demand, weather renewable)   B real demand + real renewable (price leg alone)
  C weather demand + real renewable             D real demand + weather renewable
Coupling is DEFINED as a slope, not a correlation: OLS slope of the daily price anomaly (value minus its
calendar-month mean) on the daily national wind-speed anomaly, GBP/MWh per m/s. A correlation mixes the
slope with every driver the chain lacks; the slope is the strength the steer asked about."""
import json, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, ".")
import sim.price_engine as pe
from simulation.run_phase3b_recalibration import _build_dataset, _fit_form, SELECTED_X_TIGHT, SELECTED_SCARCITY_EXPONENT
from sim.weather_price_chain import derive_price_on_record, load_daily_record
from sim.merit_order_reconstruction import ets_carbon_price_gbp_per_tonne, CPS_CARBON_GBP_PER_TONNE

UKA = json.load(open(sys.argv[1]))
mm = defaultdict(lambda: [0.0, 0.0])
for a in UKA:
    k = a["date"][:7]; mm[k][0] += a["allowances"] * a["clearing_gbp_per_t"]; mm[k][1] += a["allowances"]
uka_month = {k: s / n for k, (s, n) in mm.items()}
FIRST = min(uka_month)
def carbon(month):
    y = int(month[:4])
    if y <= 2020: al = ets_carbon_price_gbp_per_tonne(y)
    elif month < FIRST: al = uka_month[FIRST]
    else: al = uka_month[max(k for k in uka_month if k <= month)]
    return CPS_CARBON_GBP_PER_TONNE + al

rows = _build_dataset()
gas = np.array([r["gas_price"] for r in rows]); dem = np.array([r["demand_mw"] for r in rows])
ren = np.array([r["renewable_mw"] for r in rows]); ssp = np.array([r["ssp"] for r in rows])
c = np.array([carbon(r["settlementDate"][:7]) for r in rows])
x = (dem - ren) / pe.DISPATCHABLE_CAPACITY_MW
f = _fit_form((gas + c * pe.EF_GAS_TCO2_PER_MWH_TH) / pe.THERMAL_EFFICIENCY, x, ssp, SELECTED_X_TIGHT, SELECTED_SCARCITY_EXPONENT)
REFIT = (f["a0"], f["a1"], f["a2"])
assert abs(REFIT[0] - 0.2916) < 5e-4 and abs(REFIT[1] - 1.0792) < 5e-4, REFIT  # step 1's refit, reproduced

d = derive_price_on_record(); rec = load_daily_record()
dates, real = d["dates"], d["real_ssp"]
assert (dates == rec["dates"]).all()
g, wspd = d["gas_price"], d["wind_speed_ms"]
dem_w, ren_w = d["demand_mw"], d["renewable_mw"]
dem_r, ren_r = rec["demand_mw"], rec["wind_gen_mw"] + rec["solar_gen_mw"]
cb = np.array([carbon(s[:7]) for s in dates])
shipped = (pe.A0, pe.A1, pe.A2)
pe.A0, pe.A1, pe.A2 = REFIT
def price(dm, rn):
    return np.array([pe.synthetic_price(float(g[i]), float(dm[i]), float(rn[i]), carbon_price_gbp_per_tonne=float(cb[i])) for i in range(len(dates))])
arms = {"A_chain": price(dem_w, ren_w), "B_real_dem_real_ren": price(dem_r, ren_r),
        "C_wx_dem_real_ren": price(dem_w, ren_r), "D_real_dem_wx_ren": price(dem_r, ren_w)}
pe.A0, pe.A1, pe.A2 = shipped

REGIMES = {"pre": ("2016-01-01", "2021-06-30"), "crisis": ("2021-07-01", "2023-06-30"), "post": ("2023-07-01", "2099-12-31")}
def anom(v, mk):
    mu = defaultdict(list)
    for a, k in zip(v, mk): mu[k].append(a)
    mu = {k: np.mean(z) for k, z in mu.items()}
    return np.array([a - mu[k] for a, k in zip(v, mk)])
def slope(y, xx): return float(np.polyfit(xx, y, 1)[0])
def monthly(v, mk, w):
    s, n = defaultdict(float), defaultdict(float)
    for a, k, ww in zip(v, mk, w): s[k] += a * ww; n[k] += ww
    ks = sorted(s); return np.array([s[q] / n[q] for q in ks])

out = {"refit": REFIT}
for reg, (a, b) in REGIMES.items():
    m = (dates >= a) & (dates <= b); mk = np.array([s[:7] for s in dates[m]]); w = dem_r[m]
    wa = anom(wspd[m], mk)
    gr = monthly(real[m], mk, w)
    o = {"real": {"slope_per_ms": slope(anom(real[m], mk), wa), "corr_wind": float(np.corrcoef(anom(real[m], mk), wa)[0, 1]),
                  "monthly_std": float(np.std(gr))},
         "leg_renewable": {"real_mean_mw": float(ren_r[m].mean()), "chain_mean_mw": float(ren_w[m].mean()),
                           "real_mw_per_ms": slope(anom(ren_r[m], mk), wa), "chain_mw_per_ms": slope(anom(ren_w[m], mk), wa)},
         "leg_price_per_gw_real_ren": {"real": 1000 * slope(anom(real[m], mk), anom(ren_r[m], mk)),
                                       "B": 1000 * slope(anom(arms["B_real_dem_real_ren"][m], mk), anom(ren_r[m], mk))}}
    for nm, p in arms.items():
        gm = monthly(p[m], mk, w); e = gm - gr; pa = anom(p[m], mk)
        o[nm] = {"mae_monthly": round(float(np.mean(np.abs(e))), 2), "bias_monthly": round(float(np.mean(e)), 2),
                 "median_ape_monthly": round(float(np.median(np.abs(e) / np.abs(gr))), 4),
                 "slope_per_ms": round(slope(pa, wa), 2), "corr_wind": round(float(np.corrcoef(pa, wa)[0, 1]), 3),
                 "monthly_std": round(float(np.std(gm)), 2)}
    out[reg] = o
print(json.dumps(out, indent=1))
```
