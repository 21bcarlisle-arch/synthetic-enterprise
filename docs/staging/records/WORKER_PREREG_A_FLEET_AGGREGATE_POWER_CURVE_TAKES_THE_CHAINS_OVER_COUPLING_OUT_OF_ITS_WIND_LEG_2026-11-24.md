**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does a fleet-aggregate power curve take the chain's over-coupling out of its wind leg? (2026-11-24)

**Item 4, step (iii)** of the BLOCKING finding
`WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`.
This is filed before the probe runs. The probe has had one smoke run, on 60 days, which asserted
finiteness and printed nothing numeric.

**Knowledge (K8).** The new §6a of `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`
(landed with this record) covers three things. It gives the published method: Staffell and Pfenninger
2016, a Gaussian-smoothed farm curve with σ = 0.6 + 0.2·w, and speeds corrected as w′ = αw + β. It says
what the world does instead: one turbine on a 10 m daily mean over four towns. And it says why the arm
takes the form below.

## The question, and what was measured before

The coupling arm (`64fd7f5f8`) found that the chain's renewable MW moves 2.3-3.9× the real fleet's per
m/s of national wind-speed anomaly. With real renewable output in its place, the price slope comes
within 0.75-1.4× of the record. The candidate is the curve's shape: one turbine at the national mean
ramps far more steeply than a dispersed fleet. The single question here is **whether a fitted
fleet-aggregate curve removes that excess, and whether the per-year fleet (W1_7) does anything
alongside it**.

## Design

- **Base.** As in the coupling arm: the step-1 refit with carbon in the floor (A0/A1/A2 = 0.2916 /
  1.0792 / 2.8242, reproduced and asserted), with carbon passed as CPS plus the allowance price (UKA
  auction means from May 2021). Demand and solar are the chain's own. **Only wind changes.**
- **Aggregate curve.** CF(w) = E[P(a·w + b + ε)], ε ~ N(0, σ), where P is the world's own turbine curve.
  (a, b, σ) are **fitted on 2016-01-01..2019-12-31 only**, against AGWS wind normalised by its own
  calendar-year mean, so the fit sees the shape and never the level. Mid-2021 onwards is out of sample
  for the curve.
- **Two variables, crossed:** curve {single, aggregate} × fleet {whole-window, per-year}. A = single +
  whole (the chain as it stands), G = single + per-year, F = aggregate + whole, E = aggregate +
  per-year. The per-year fleet is mean-matched within each calendar year: W1_7's definition, re-derived
  for the curve in use. **Its level is in sample by construction.** The slopes are within-month
  anomalies, and the per-year fleet does not supply them.
- **Coupling is a slope**, unchanged: £/MWh of daily price anomaly per m/s of national wind-speed
  anomaly, within the month.
- Every loaded `sim/` and `simulation/` module is asserted blob-identical to `origin/main` before the
  run.

## Reference values already on the record (`64fd7f5f8`)

| Regime | Record slope | A slope | A wind MW/(m/s) ratio | A MAE | Real-renewable arm C: MAE · slope | Gas-only null MAE |
|---|---|---|---|---|---|---|
| Pre | −1.65 | −7.62 | 3.9× | 6.75 | 5.96 · −2.26 | 5.4 |
| Crisis | −16.3 | −30.1 | 2.8× | 24.33 | 17.16 · −12.3 | 24.5 |
| Post | −9.12 | −14.6 | 2.3× | 9.29 | 7.35 · −6.87 | 6.7 |

## Predictions (filed before the run)

| # | Prediction | Refuted if |
|---|---|---|
| F1 | The aggregate curve carries the fix: F's wind MW per m/s is ≤ 1.6× the record's in all three regimes | any regime > 1.6× |
| F2 | F's price slope is ≤ 2.0× the record's before the crisis and ≤ 1.3× after it | either bound broken |
| F3 | E beats A on monthly MAE in all three regimes | any regime E ≥ A |
| F4 | E still loses to the gas-only null before the crisis (≥ 5.4) and after it (≥ 6.7), and beats it in the crisis (< 24.5) | any of the three |
| F5 | The per-year fleet alone does not fix the slope: G's wind MW per m/s stays ≥ 2.0× the record's in all three regimes | any regime < 2.0× |
| F6 | The fitted σ exceeds Staffell-Pfenninger's within-farm σ at the mean transferred speed (0.6 + 0.2·mean(w′)) | fitted σ ≤ that |
| F7 | The aggregate fraction's daily correlation with AGWS wind is ≥ the single curve's | lower |

**Why F4 expects a loss either side of the crisis.** The arm can at best approach C, and C loses to
the null before and after the crisis on the price leg's own level gaps (the post-crisis −£8 is still
unattributed). F4 is there so that a better curve is not read as a passing chain.

## Decision rule, written now

- **F1 and F3 hold:** the aggregate curve is the next build. Ship it into `sim/weather_price_chain`,
  with the per-year fleet only if E beats F, and cite §6a. Every forward figure then carries the price
  leg's remaining level errors beside it.
- **F1 fails:** the curve's shape is not the excess. The next suspect is the input itself, a 10 m
  daily mean at four towns (§6a), and the build is a better speed series (offshore and upland points,
  or hub height), not a curve.
- **F5 fails:** the per-year fleet moves the slope by itself, and the coupling arm's attribution is
  incomplete. Say so beside it.

## The probe

Run from the repo root: `python3 probe.py uka.json`. `uka.json` is the `auctions` array of
`docs/market_research/uk_ets_allowance_auction_clearing_prices_2021_2025.json`, as before.

```python
"""Item 4, fleet power-curve arm (step iii): does a FLEET-AGGREGATE power curve take the chain's
over-coupling to wind out of its generation leg?

Read-only; run from the repo root: python3 /tmp/fpc/probe.py /tmp/fpc/uka.json [--smoke]
Base = the step-1 refit with carbon in its floor (d424b78095's constants, carbon passed), exactly as the
weather-coupling arm (8e8790de4). ONLY the wind leg changes; demand and solar stay the chain's own.

The aggregate curve is Staffell & Pfenninger's (2016, Energy 114, s.3.1-3.2) form, moved from one farm
to the national fleet: the single-turbine curve P (cut-in 3, rated 12, cut-out 25 m/s, sim/price_engine)
convolved with a Gaussian of width sigma, applied to a transferred speed w' = a*w + b, where w is the
chain's own national input (10 m daily mean over four customer towns). (a, b, sigma) are FITTED on
2016-01-01..2019-12-31 ONLY, against AGWS wind output normalised by its own calendar-year mean, so the
fit sees shape and never level; the crisis and post regimes are out of sample for the curve.

Two variables, crossed (2x2), so each move can be attributed:
  A  single curve, whole-window fleet  (the chain as it stands; the coupling arm's A)
  G  single curve, per-year fleet      (W1_7's fleet alone)
  F  aggregate curve, whole-window fleet
  E  aggregate curve, per-year fleet   (the candidate)
Per-year fleet = the curve's fraction mean-matched to AGWS wind WITHIN each calendar year (W1_7's
definition, re-derived for whichever curve is in use). That level is IN SAMPLE by construction; slopes
are within-month anomalies and are not given by it.
Coupling is a SLOPE, as before: GBP/MWh of daily price anomaly (minus its calendar-month mean) per m/s
of the national wind-speed anomaly."""
import json
import subprocess
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, ".")
import sim.price_engine as pe  # noqa: E402
from sim.merit_order_reconstruction import CPS_CARBON_GBP_PER_TONNE, ets_carbon_price_gbp_per_tonne  # noqa: E402
from sim.weather_price_chain import (_solar_envelope, derive_price_on_record, fit_chain,  # noqa: E402
                                     load_daily_record)
from simulation.run_phase3b_recalibration import (SELECTED_SCARCITY_EXPONENT, SELECTED_X_TIGHT,  # noqa: E402
                                                  _build_dataset, _fit_form)

SMOKE = "--smoke" in sys.argv

# Every loaded sim/ and simulation/ module must be blob-identical to origin/main.
changed = []
for name, mod in list(sys.modules.items()):
    f = getattr(mod, "__file__", None) or ""
    if name.split(".")[0] in ("sim", "simulation") and f.endswith(".py"):
        rel = f[f.index(name.split(".")[0] + "/"):]
        r = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", rel])
        if r.returncode:
            changed.append(rel)
assert not changed, f"modules differ from origin: {changed}"

UKA = json.load(open(sys.argv[1]))
mm = defaultdict(lambda: [0.0, 0.0])
for a in UKA:
    k = a["date"][:7]
    mm[k][0] += a["allowances"] * a["clearing_gbp_per_t"]
    mm[k][1] += a["allowances"]
uka_month = {k: s / n for k, (s, n) in mm.items()}
FIRST = min(uka_month)


def carbon(month):
    y = int(month[:4])
    if y <= 2020:
        al = ets_carbon_price_gbp_per_tonne(y)
    elif month < FIRST:
        al = uka_month[FIRST]
    else:
        al = uka_month[max(k for k in uka_month if k <= month)]
    return CPS_CARBON_GBP_PER_TONNE + al


rows = _build_dataset()
gas = np.array([r["gas_price"] for r in rows])
dem = np.array([r["demand_mw"] for r in rows])
ren = np.array([r["renewable_mw"] for r in rows])
ssp = np.array([r["ssp"] for r in rows])
c = np.array([carbon(r["settlementDate"][:7]) for r in rows])
x = (dem - ren) / pe.DISPATCHABLE_CAPACITY_MW
f = _fit_form((gas + c * pe.EF_GAS_TCO2_PER_MWH_TH) / pe.THERMAL_EFFICIENCY, x, ssp,
              SELECTED_X_TIGHT, SELECTED_SCARCITY_EXPONENT)
REFIT = (f["a0"], f["a1"], f["a2"])
assert abs(REFIT[0] - 0.2916) < 5e-4 and abs(REFIT[1] - 1.0792) < 5e-4, REFIT

d = derive_price_on_record()
rec = load_daily_record()
dates, real = d["dates"], d["real_ssp"]
assert (dates == rec["dates"]).all()
g, wspd = d["gas_price"], d["wind_speed_ms"]
dem_w, ren_w = d["demand_mw"], d["renewable_mw"]
dem_r = rec["demand_mw"]
wind_r = rec["wind_gen_mw"]
ren_r = wind_r + rec["solar_gen_mw"]
years = np.array([int(s[:4]) for s in dates])
cb = np.array([carbon(s[:7]) for s in dates])

p = fit_chain()
solar_w = p.solar_fleet_mw * _solar_envelope(rec["day_of_year"], rec["cloud_pct"])
single = np.array([pe.wind_power_output_fraction(float(w)) for w in wspd])
# The chain's own renewable must be reproduced from its parts before any arm is trusted.
assert np.allclose(p.wind_fleet_mw * single + solar_w, ren_w, rtol=1e-6, atol=1e-3)

# Aggregate curve: E_eps[P(a*w + b + eps)], eps ~ N(0, sigma), by Gauss-Hermite quadrature.
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(41)
GH_W = GH_W / GH_W.sum()
Pv = np.vectorize(lambda v: pe.wind_power_output_fraction(float(v)))
GRID = np.linspace(-15.0, 45.0, 6001)
PGRID = Pv(GRID)


def P(v):
    return np.interp(v, GRID, PGRID)


def agg(w, a, b, s):
    v = (a * np.asarray(w)[:, None] + b) + s * GH_X[None, :]
    return (P(v) * GH_W[None, :]).sum(axis=1)


def by_year_norm(v):
    out = np.empty_like(v)
    for y in np.unique(years):
        m = years == y
        out[m] = v[m] / v[m].mean()
    return out


fit_m = (dates >= "2016-01-01") & (dates <= "2019-12-31")
target = by_year_norm(wind_r)


def loss(theta):
    a, b, s = theta
    if a <= 0 or s <= 0:
        return 1e9
    fr = agg(wspd, a, b, s)
    if (fr[fit_m] <= 0).all():
        return 1e9
    return float(np.mean((by_year_norm(np.where(fr > 0, fr, 1e-9))[fit_m] - target[fit_m]) ** 2))


best = None
for a0 in (1.0, 1.5, 2.0, 2.5):
    for b0 in (-1.0, 0.0, 1.0, 2.0):
        for s0 in (0.5, 1.5, 3.0):
            val = loss((a0, b0, s0))
            if best is None or val < best[0]:
                best = (val, (a0, b0, s0))
theta = np.array(best[1], float)
step = np.array([0.25, 0.5, 0.5])
for _ in range(60 if not SMOKE else 2):  # coordinate descent, halving steps
    improved = False
    for i in range(3):
        for sgn in (1, -1):
            t = theta.copy()
            t[i] += sgn * step[i]
            v = loss(t)
            if v < best[0]:
                best, theta, improved = (v, tuple(t)), t, True
    if not improved:
        step = step / 2
A_, B_, S_ = theta
aggf = agg(wspd, A_, B_, S_)


def whole(fr):
    return fr * (wind_r.mean() / fr.mean())


def per_year(fr):
    out = np.empty_like(fr)
    for y in np.unique(years):
        m = years == y
        out[m] = fr[m] * (wind_r[m].mean() / fr[m].mean())
    return out


shipped = (pe.A0, pe.A1, pe.A2)
pe.A0, pe.A1, pe.A2 = REFIT
idx = range(len(dates)) if not SMOKE else range(60)


def price(rn):
    out = np.full(len(dates), np.nan)
    for i in idx:
        out[i] = pe.synthetic_price(float(g[i]), float(dem_w[i]), float(rn[i]),
                                    carbon_price_gbp_per_tonne=float(cb[i]))
    return out


wind_arms = {"A_single_whole": whole(single), "G_single_peryear": per_year(single),
             "F_agg_whole": whole(aggf), "E_agg_peryear": per_year(aggf)}
prices = {k: price(v + solar_w) for k, v in wind_arms.items()}
pe.A0, pe.A1, pe.A2 = shipped
if SMOKE:
    assert np.isfinite(prices["E_agg_peryear"][:60]).all()
    print("smoke ok")
    sys.exit(0)

REGIMES = {"pre": ("2016-01-01", "2021-06-30"), "crisis": ("2021-07-01", "2023-06-30"),
           "post": ("2023-07-01", "2099-12-31")}


def anom(v, mk):
    mu = defaultdict(list)
    for a, k in zip(v, mk):
        mu[k].append(a)
    mu = {k: np.mean(z) for k, z in mu.items()}
    return np.array([a - mu[k] for a, k in zip(v, mk)])


def slope(y, xx):
    return float(np.polyfit(xx, y, 1)[0])


def monthly(v, mk, w):
    s, n = defaultdict(float), defaultdict(float)
    for a, k, ww in zip(v, mk, w):
        s[k] += a * ww
        n[k] += ww
    ks = sorted(s)
    return np.array([s[q] / n[q] for q in ks])


out = {"fit_window": "2016-01-01..2019-12-31", "a": round(A_, 4), "b_ms": round(B_, 4),
       "sigma_ms": round(S_, 4), "fit_mse_norm": round(best[0], 5),
       "published_farm_sigma_at_mean_transferred_speed": round(0.6 + 0.2 * float(np.mean(A_ * wspd + B_)), 3),
       "daily_corr_wind_vs_agws": {"single": round(float(np.corrcoef(single, wind_r)[0, 1]), 4),
                                   "aggregate": round(float(np.corrcoef(aggf, wind_r)[0, 1]), 4)},
       "curve_table_cf_rel_to_mean": {str(w): [round(float(pe.wind_power_output_fraction(w) / single.mean()), 3),
                                               round(float(agg([w], A_, B_, S_)[0] / aggf.mean()), 3)]
                                      for w in (1, 2, 3, 4, 5, 6, 8, 10, 12)}}
for reg, (a, b) in REGIMES.items():
    m = (dates >= a) & (dates <= b)
    mk = np.array([s[:7] for s in dates[m]])
    w = dem_r[m]
    wa = anom(wspd[m], mk)
    gr = monthly(real[m], mk, w)
    o = {"record": {"price_slope_per_ms": round(slope(anom(real[m], mk), wa), 2),
                    "wind_mw_per_ms": round(slope(anom(wind_r[m], mk), wa), 1),
                    "wind_mean_mw": round(float(wind_r[m].mean()), 1)}}
    for nm in wind_arms:
        pr, wn = prices[nm][m], wind_arms[nm][m]
        e = monthly(pr, mk, w) - gr
        o[nm] = {"wind_mean_mw": round(float(wn.mean()), 1),
                 "wind_mw_per_ms": round(slope(anom(wn, mk), wa), 1),
                 "wind_mw_per_ms_ratio": round(slope(anom(wn, mk), wa) / slope(anom(wind_r[m], mk), wa), 2),
                 "price_slope_per_ms": round(slope(anom(pr, mk), wa), 2),
                 "price_slope_ratio": round(slope(anom(pr, mk), wa) / slope(anom(real[m], mk), wa), 2),
                 "mae_monthly": round(float(np.mean(np.abs(e))), 2),
                 "bias_monthly": round(float(np.mean(e)), 2),
                 "corr_wind": round(float(np.corrcoef(anom(pr, mk), wa)[0, 1]), 3)}
    out[reg] = o
print(json.dumps(out, indent=1))
```
