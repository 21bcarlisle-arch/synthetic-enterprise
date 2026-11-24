**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_2_generate_futures`

# The forward gas draw is independent daily noise, with no season and no persistence

Found by the delivery seat, 24 Nov 2026, grading the forward gas draw against the gas page
(`docs/market_research/how_the_gb_gas_price_forms_nbp_and_sap_2026-11-24.md`). Numbers:
`docs/staging/records/SEAT_RESULT_GRADING_THE_WORLDS_GAS_PRICE_RECORD_AGAINST_THE_GAS_PAGE_BY_REGIME_2026-11-24.md`.

**What.** `sim/scenario/gas_scenario_generator.generate_gas_scenario_prices` draws every day as an
independent Gaussian from one of two regimes, picked by a fresh Bernoulli each day, plus random
"dunkelflaute" days. Against post-crisis GB SAP (`baseline_2025`, 2026-27):

- daily log-return SD 0.501 against 0.037 (13.5×);
- lag-1 autocorrelation 0.005 against 0.984;
- 10.3% of days above 1.5 × their trailing-30-day median, against 0.0%;
- no seasonal term (its 1.07 winter/summer ratio is where its random storm days fell).

**Why it is LATENT, not BLOCKING.** Forward runs are held behind the correctness stretch, and no
published figure reads this draw today. It becomes BLOCKING the day a forward run prices a hedge or
a fixed tariff on it. A supplier would then face daily gas risk that GB does not have, and would
not face the seasonal and cold-spell risk that GB does have.

**What the page says a forward draw must show** (mechanism, not level): persistence (storage and
linepack, lag-1 ≈ 0.9+); a winter premium set by continental storage (§4); cold-spell and supply
shocks that persist for days, and are coupled to the world's own weather and wind (§6); and a hub
basis that can open when the interconnectors saturate (§5). The level and its band are
curriculum, the director's (R13). This finding does not set them.

**Not to be done before the K8 electricity page.** The gas and power draws must share their
weather. The rebuild is one design across both, item 4 of the BLOCKING steer finding. This row puts
the gas half of the evidence on file for it.

**Done means** a forward gas draw whose daily, seasonal and persistence statistics sit within the
post-crisis SAP regime's, graded by the probe in the result record, with its level read from the
curriculum.

## The record's weather coupling, measured (worker, 24 Nov 2026)

The design above asks for cold spells "coupled to the world's own weather" but gives no size. Here is
the record's size, measured against the world's own temperature and wind
(`sim.weather_price_chain.load_daily_record`, origin `d38233386`), so the rebuild has a target that
is not a picked number. Day-on-day change in log SAP against the day-on-day change in temperature,
heating season (Oct-Mar), by calendar year:

| Year | % change in SAP per °C | 95% CI | corr with Δwind | R² (temp + wind) | n |
|---|---|---|---|---|---|
| 2018 | −1.03 | [−2.03, −0.02] | +0.14 | 0.069 | 179 |
| 2019 | −0.79 | [−1.28, −0.29] | −0.18 | 0.057 | 178 |
| 2020 | −0.51 | [−0.87, −0.16] | −0.09 | 0.047 | 174 |
| 2021 | −0.91 | [−1.43, −0.39] | +0.01 | 0.079 | 175 |
| 2022 | −1.90 | [−3.44, −0.35] | −0.10 | 0.033 | 175 |
| 2023 | −0.44 | [−0.80, −0.08] | −0.13 | 0.032 | 181 |
| 2024 | −0.42 | [−0.62, −0.22] | −0.25 | 0.105 | 182 |
| 2025 (to 7 Jun) | −0.27 | [−0.56, +0.02] | −0.13 | 0.039 | 89 |
| pooled | −0.81 | [−1.09, −0.53] | −0.04 | 0.025 | 1,340 |

- **The sign is the same in every year, and the interval excludes zero in seven of eight.** A day 1°C
  colder than the day before raises SAP by roughly 0.3-1.9%. The pooled figure is about 0.8%.
- **It is small.** Weather explains 3-10% of daily variance. That fits the page (§1, §6): the margin
  is LNG and the continent, and weather adds demand on top of it. A rebuild that makes GB gas a
  weather-set price would overstate the coupling, just as the power chain overstated wind.
- **Wind is weaker and its sign is not stable** (negative in 6 of 8 years, at most −0.25). The
  power-burn route (still days) is real in the page's mechanism, but it does not show at daily scale
  in this record once temperature is in.
- **Basis, stated.** The temperature and wind are the world's own series, not a gas-demand-weighted
  national CWV. A CWV-based coefficient would probably be larger. That is a belief, not a
  measurement (page GAP: no published per-degree coefficient).

So a "done" forward draw should also carry a heating-season temperature slope inside the pooled
interval, with the post-crisis years (−0.27 to −0.44) as its regime, and the same sign every year.
The script is below; it is read-only and is run from the repo root.

```python
import sys, csv, numpy as np
sys.path.insert(0, '.')
from sim.weather_price_chain import load_daily_record
r = load_daily_record()
T = {str(d)[:10]: t for d, t in zip(r['dates'], r['temperature_c'])}
W = {str(d)[:10]: w for d, w in zip(r['dates'], r['wind_speed_ms'])}
sap = {x['settlementDate']: float(x['systemAveragePrice']) for x in csv.DictReader(open('sim/gas_data/sap_daily.csv'))}
print("year  slope %/degC (Oct-Mar, day-on-day)  95% CI   corr(dlogSAP,dWind)  joint R2")
rows = []
for y in list(range(2018, 2026)) + ['all']:
    ds = sorted(d for d in sap if d in T and (y == 'all' or d[:4] == str(y)))
    a=[];b=[];c=[]
    for p, q in zip(ds, ds[1:]):
        if int(q[5:7]) in (10,11,12,1,2,3) and (y=='all' or p[:4]==q[:4]):
            a.append(np.log(sap[q]/sap[p])); b.append(T[q]-T[p]); c.append(W[q]-W[p])
    a=np.array(a); b=np.array(b); c=np.array(c)
    X=np.column_stack([np.ones_like(b), b]); beta,res,_,_=np.linalg.lstsq(X,a,rcond=None)
    e=a-X@beta; se=np.sqrt(e.var(ddof=2)/((b-b.mean())**2).sum())
    X2=np.column_stack([np.ones_like(b), b, c]); b2,_,_,_=np.linalg.lstsq(X2,a,rcond=None)
    r2=1-((a-X2@b2)**2).sum()/((a-a.mean())**2).sum()
    print(y, f"{100*beta[1]:+.2f}", f"[{100*(beta[1]-1.96*se):+.2f},{100*(beta[1]+1.96*se):+.2f}]", f"{np.corrcoef(a,c)[0,1]:+.2f}", f"{r2:.3f}", len(a))
```
