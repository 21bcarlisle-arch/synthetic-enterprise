**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: carbon explains the chain's pre-crisis bias, and the chain's fitted multiplier already carries carbon after 2021, so the term cannot be switched on as calibrated (2026-11-24)

Item 3 of the weather-to-price steer, now held by
`WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`.
The prediction was filed before this arm ran, in
`SEAT_RESULT_GRADING_THE_WORLDS_POWER_RECORD_AGAINST_THE_ELECTRICITY_PAGE_BY_REGIME_2026-11-24.md` §2:
"with CPS and the allowance in its merit order, the chain's pre-crisis monthly bias moves from −£12.0 to
within ±£4, and its pre-crisis monthly MAE falls from £12.4 to ≤ £7. The crisis and post-crisis errors
fall by less."

## What changed: one variable

The chain's reduced-form gas floor, `(gas + carbon × 0.184) / 0.50`, has a carbon term that every
chain call leaves at 0.0 (`sim/price_engine.py` `gas_floor_price`). The arm sets that term and changes
nothing else: same chain, same default parameters, same whole-window fleet, the same TTF-proxy gas, and
months weighted by real INDO demand as the grade weighted them. The zero arm reproduces the grade to
the penny (asserted in the probe; table row "none").

Carbon = CPS £18/t + allowance. 2016-2020: the EUA auction VWAP × ECB FX already in
`sim/merit_order_reconstruction.py`. From May 2021: the month's volume-weighted UK ETS auction clearing
price, from `docs/market_research/uk_ets_allowance_auction_clearing_prices_2021_2025.json` (new today:
116 auctions, transcribed from the UK ETS Authority's reports and checked against three of their own
totals). Jan-Apr 2021 had a live UK ETS and no auction. The primary arm carries May's first price back.
The zero-fill variant is reported beside it as a sensitivity only, because it was not named primary
before the run.

## The numbers (monthly, demand-weighted, £/MWh)

| Arm | Pre MAE · bias · median APE | Crisis MAE · bias | Post MAE · bias |
|---|---|---|---|
| none (as graded) | 12.38 · −11.97 · 25.9% | 31.52 · +12.09 | 10.25 · −2.11 |
| CPS only | 6.83 · −4.12 · 13.0% | 33.93 · +20.02 | 10.70 · +5.85 |
| **CPS + allowance (primary)** | **7.14 · +3.08 · 12.3%** | **53.16 · +49.71** | **23.44 · +23.23** |
| CPS + allowance, Jan-Apr 2021 zero | 6.62 · +1.68 · 11.9% | 53.16 · +49.71 | 23.44 · +23.23 |
| gas-only null (the grade's) | 5.4 · — · 9.8% | 24.5 | 6.7 |

Pre-crisis bias by year, none → primary: 2016 −12.2 → −2.1; 2017 −7.7 → +2.5; 2018 −8.0 → +5.7;
2019 −12.9 → +4.7; 2020 −16.2 → −0.4; 2021 H1 −17.8 → +11.5 (−3.4 zero-filled).

## Predictions against outcomes (kept as filed)

| Filed | Outcome | Held? |
|---|---|---|
| Pre-crisis bias −£12.0 → within ±£4 | +3.08 | **held** |
| Pre-crisis MAE £12.4 → ≤ £7 | 7.14 | **missed** by £0.14 (6.62 under the zero fill, which is not the filed arm) |
| Crisis and post-crisis errors fall, by less | they rise: 31.5 → 53.2, 10.3 → 23.4 | **wrong in sign** |

## What it shows

1. **Missing carbon explains the pre-crisis bias. That attribution is now made, not only suggested.**
   With nothing fitted, carbon takes the bias from −£12 to +£3 and halves the error. The year-by-year
   growth of the bias, which the grade flagged, is gone. CPS alone does about two thirds of it.
2. **The chain still loses to the gas-only null before the crisis** (median APE 12.3% against 9.8%).
   Carbon is not the whole gap. The weather coupling, 2-5 times too strong, is the next candidate.
3. **After mid-2021 the term makes the chain much worse, and I cannot yet say for certain why.** Ranked
   by evidence:
   (a) **The multiplier already carries carbon.** `A0/A1/A2` were fitted with carbon at 0.0 against
   SSP over 2016-03..2025-06 (`sim/price_engine.py` docstring). Fitted by MAE over every half-hour, a
   floor that lacks carbon gets a multiplier that makes up for it on average. The chain was nearly
   unbiased after the crisis without carbon (−£2.1) and £12 low before it, which is that compromise:
   too low when carbon was cheap, about right when it was dear. Adding carbon then counts it twice.
   Evidence for: the sign and the regime pattern. Evidence against: none yet.
   (b) **The crisis gas input is TTF, not SAP.** It overstates GB gas by 29% in 2022
   (`the_worlds_gas_price_record_splices_daily_sap_from_2018_2026-11-18.md`), so the chain was already
   +£33 in 2022 before carbon. Carbon scaled through a multiplier above 1 adds to that. This explains
   part of the crisis rise, and none of the post-crisis rise (basis ≤1% after 2023).
   (c) **Gas off the margin more often after 2023** (the power grade's E8: corr −0.64 with wind share),
   so a carbon cost that is charged in full every hour overstates it. Plausible. It is second order
   next to (a), because the same applies, more weakly, before the crisis, where the arm works.
4. **The one-variable test that separates (a) is a refit:** refit `A0/A1/A2` on the same window with
   carbon in the floor, then grade. Prediction, filed here before it is run: with carbon in the floor and
   the multiplier refitted, post-crisis monthly MAE ≤ £11 (no worse than without carbon) and the
   pre-crisis bias stays within ±£5. If the post-crisis error stays above £15, (a) is refuted.
   This is item 4's first step, the rebuild, and it is a baseline refit decided on fidelity only.

## What this does NOT establish

- Nothing in the world changed. The chain still runs with carbon at 0.0, and no run reads anything new.
- `sim/merit_order_reconstruction.py` still names 2022-2024 as allowance gap years (CPS only) because
  "no same-calendar-year market carbon price could be sourced". That is now false: the auction series
  sources it. Filling them changes the merit-order engine, which no live run uses, and it is item 4's
  to make with the refit, not this record's.
- The allowance is a monthly auction average applied flat to every day of the month.

## The probe

Read-only. Run from the shared repo root (the cache is there), whose `sim/` modules were checked
identical to `origin/main` by blob hash before the run: `python3 probe.py uka.json`, where `uka.json`
is the `auctions` array of the series file. It ran in about 3 minutes.

```python
"""Carbon arm of the weather-to-price chain grade (steer item 3). Read-only; run from the repo root.
One variable: the reduced-form gas floor's carbon term (sim.price_engine.gas_floor_price), which every
chain call leaves at 0.0. Arms: none (as graded), CPS only, CPS + allowance. Everything else is the
grade's own chain (derive_price_on_record's demand and renewable, default params, whole-window fleet)."""
import json, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, ".")
from sim.weather_price_chain import derive_price_on_record, load_daily_record  # noqa: E402
from sim.price_engine import synthetic_price  # noqa: E402
from sim.merit_order_reconstruction import ets_carbon_price_gbp_per_tonne, CPS_CARBON_GBP_PER_TONNE  # noqa: E402

UKA = json.load(open(sys.argv[1]))
m = defaultdict(lambda: [0.0, 0.0])
for x in UKA:
    k = x["date"][:7]; m[k][0] += x["allowances"] * x["clearing_gbp_per_t"]; m[k][1] += x["allowances"]
uka_month = {k: a / b for k, (a, b) in m.items()}
FIRST = min(uka_month)

def allowance(month, fill):
    y = int(month[:4])
    if y <= 2020:
        return ets_carbon_price_gbp_per_tonne(y)          # EUA auction VWAP x ECB FX (2026-08-03 page)
    if month < FIRST:                                       # Jan-Apr 2021: UK ETS live, no auction yet
        return uka_month[FIRST] if fill == "carry_back" else 0.0
    keys = sorted(k for k in uka_month if k <= month)
    return uka_month[keys[-1]]                              # a month without an auction carries the last

REGIMES = {"pre": ("2016-01-01", "2021-06-30"), "crisis": ("2021-07-01", "2023-06-30"), "post": ("2023-07-01", "2099-12-31")}
d = derive_price_on_record()
dates, real, gas, dem, ren = d["dates"], d["real_ssp"], d["gas_price"], d["demand_mw"], d["renewable_mw"]
w_real = load_daily_record()["demand_mw"]  # the grade weights months by REAL INDO demand

def arm(carbon_fn):
    return np.array([synthetic_price(float(gas[i]), float(dem[i]), float(ren[i]),
                                     carbon_price_gbp_per_tonne=carbon_fn(dates[i][:7])) for i in range(len(dates))])

arms = {"none": d["derived_price"],
        "cps_only": arm(lambda mo: CPS_CARBON_GBP_PER_TONNE),
        "cps_plus_allowance": arm(lambda mo: CPS_CARBON_GBP_PER_TONNE + allowance(mo, "carry_back")),
        "cps_plus_allowance_jan_apr21_zero": arm(lambda mo: CPS_CARBON_GBP_PER_TONNE + allowance(mo, "zero"))}
assert np.allclose(arms["none"], arm(lambda mo: 0.0)), "the zero arm must reproduce the graded chain"

def monthly(x, k, w):
    s, n = defaultdict(float), defaultdict(float)
    for xi, ki, wi in zip(x, k, w): s[ki] += xi * wi; n[ki] += wi
    ks = sorted(s); return ks, np.array([s[q] / n[q] for q in ks])

out = {}
for reg, (a, b) in REGIMES.items():
    msk = (dates >= a) & (dates <= b); mk = np.array([x[:7] for x in dates[msk]])
    ks, gr = monthly(real[msk], mk, w_real[msk])
    out[reg] = {"months": len(ks)}
    for nm, p in arms.items():
        _, gm = monthly(p[msk], mk, w_real[msk])
        e = gm - gr
        yrs = defaultdict(list)
        for kk, ee in zip(ks, e): yrs[kk[:4]].append(ee)
        out[reg][nm] = {"mae_monthly": round(float(np.mean(np.abs(e))), 2), "bias_monthly": round(float(np.mean(e)), 2),
                        "median_ape_monthly": round(float(np.median(np.abs(e) / np.abs(gr))), 4),
                        "bias_by_year": {y: round(float(np.mean(v)), 2) for y, v in sorted(yrs.items())}}
out["allowance_used_gbp_per_t"] = {y: round(allowance(f"{y}-06", "carry_back"), 2) for y in range(2016, 2026)}
print(json.dumps(out, indent=1))
```
