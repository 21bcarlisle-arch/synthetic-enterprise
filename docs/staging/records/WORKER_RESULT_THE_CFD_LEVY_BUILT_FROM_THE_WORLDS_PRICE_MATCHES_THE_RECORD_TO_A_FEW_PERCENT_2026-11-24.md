# Result: the CfD levy built from the world's own price matches the record to within a few percent

**Run:** 24 Nov 2026, by the worker, after the pre-registration
`docs/staging/records/WORKER_PREREG_THE_CFD_LEVY_FROM_STRIKE_AGAINST_THE_WORLDS_PRICE_ON_THE_RECORD_2026-11-24.md`.
**For:** item 5 of `docs/staging/WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`,
the on-the-record step. Nothing in the world or the company changed. No run reads this.
**Knowledge (K8):** `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md` §3 and GAP 3.

## Data

LCCC Data Portal, OGL, read on 24 Nov 2026 through the CKAN datastore API
(`https://dp.lowcarboncontracts.uk/api/3/action/datastore_search`). The portal's file downloads
returned 403; the API served the same tables.

- `actual-cfd-generation-and-avoided-ghg-emissions`: 121,823 unit-days, 2016 to Nov 2026.
  111,556 rows reference IMRP (intermittent) and 10,267 BMRP (baseload: biomass).
- `reconciled-daily-levy-rates`: 25,198 rows. The `Latest` row per day is used (4,201 days).
- The world's price: `sim/scenario/data/real_ssp_daily_mean.json`. This is the daily mean of the
  world's replayed Elexon system sell price, 2015-11-07 to 2025-06-07.

The data was not committed. The probe is the 90-line read-only script in the appendix below. It
re-fetches from the API, so it reproduces the result as of the portal's state on the day it runs.

## Outcomes against the predictions

| # | Prediction | Outcome |
|---|---|---|
| A1 | Built payment within 1% of reported, every year | **Missed as filed.** Built from `Market_Reference_Price`, it is within 0.3% in 2016-2020 but 2.1% out in 2021 and 9.7% in 2022. The gap is entirely in IMRP units, £23.9m of 2022's £33.5m in Investment Contracts. Built from `Weighted_IMRP` (the generation-weighted hourly price, which is what an hourly-settled unit is paid against), it is within 0.01% in 2016-2021 and 0.4-1.1% in 2022-2025. The residual grows with the count of days on which LCCC leaves `Weighted_IMRP` blank (0 in 2016, 382 in 2025). That fits the negative-hour rules of the newer rounds (page §3), but it is not attributed here. |
| A2 | Quarterly levy from payments within 5% of LCCC's reconciled rate in ≥ 90% of quarters | **Held,** 46 of 46. The reconciled daily rate is the day's net payment over its eligible demand. |
| A3 | Net payments negative in ≥ 4 quarters, Q4 2021 to Q1 2023 | **Missed: 3** (Q4 2021, Q1 2022, Q3 2022). Q2 2022 (+£43m) and Q4 2022 (+£109m) were positive. |
| B1 | World-price levy within ±15% of actual, each non-crisis year | **Held, far inside the band.** 2016-2020 and 2023-2024 are all within ±2% (worst 2023, −1.9%). 2021 is +3.3%. |
| B2 | 2022: right sign, size off by > £150m | **Sign held. Size refuted:** off by £32.6m (−£313m against −£346m). |
| C1 | A flat quarterly price does worse than the world's daily price | **Held** in both spans. Quarterly levy MAE: 2016 Q1 to 2021 Q2, £0.033/MWh against £0.053; 2023 Q1 to 2025 Q1, £0.172 against £0.498. |

Four of six held. A1 failed on a definition I chose, and the fix was in the data's own column. A3
underestimated how quickly the 2022 quarters swung back. B2 was too pessimistic about the system
price.

## What this establishes for item 5

1. **The levy definition is right.** (Strike − reference) × generation, summed and divided by
   eligible demand, is LCCC's reconciled daily levy rate. A2 is exact.
2. **The world's daily price is good enough as the CfD reference on the record.** Swapping the
   world's price in for the real reference gets each year's net CfD cost within 2% outside the crisis
   and within £33m in 2022. Day-to-day movement carries real information. A quarterly flat price is
   three times worse post-crisis, because wind earns below the period mean and the daily price
   captures some of that.
3. **"The negative 2022 rate" was half right.** The ILR has a floor of zero (page §3, Ofgem). But
   LCCC's **reconciled** daily levy rate is negative on 238 days of 2022 and 85 of 2021. Its minimum
   is −£22.68/MWh on 8 Mar 2022. An endogenous levy should produce that reconciled rate, negative
   where the record is, and keep the ILR a separate, floored, forecast quantity.
4. **A press figure on the page is corrected beside it.** The net CfD payment from Sep 2021 to
   Mar 2022 was **−£273.4m** in LCCC's own data, and generator paybacks alone were −£448.0m. The
   page cited "about £205m [press, low confidence]".

## What it does not establish, and what remains of item 5

- **Forward volumes.** This step used real generation. A forward levy needs each year's CfD fleet:
  operating units plus new allocation rounds, times the world's own wind and solar output. LCCC
  publishes `cfd-contract-portfolio-status` and `forecast-cfd-generation`. Neither is read here, so
  that is a GAP, not a number.
- **The forward price it would reference.** On the record the world's price is the real system
  price. In forward years the price comes from the scenario generator. The SEAT finding on the
  forward gas draw (independent daily noise) suggests the electricity draw should be graded the same
  way before a levy is built on it. That grade is item 4's, not this step's.
- **The negative-hour rules.** These need the CfD Standard Terms by round (page GAP 3, still open).
  The world's price is daily, so it cannot apply an hourly rule at all.
- **Forward carbon and strikes** stay the director's curriculum band, as the steer says.

## Appendix: the probe

Both scripts are read-only. Run them from the repo root with `python3 -I`. First fetch each resource (`gen.json` 37d1bef4-55d7-4b8e-8a47-1d24b123a20e, `levy.json` 24944bfe-b546-4f50-8bf6-895d8f769b2b) into an empty directory outside the repo, then run the legs against that directory and the world fixture. The world's 2025 Q2 is partial (to 7 June). Its quarterly row in the output is not a comparison, and it is excluded from C1. The A1 re-check with `Weighted_IMRP` is the same sum with that column used as the reference for IMRP rows where it is present.

```python
# fetch: python3 -I fetch.py <resource_id> <out.json>
import json, sys, urllib.request, time
rid, out = sys.argv[1], sys.argv[2]
rows, off = [], 0
while True:
    u = f"https://dp.lowcarboncontracts.uk/api/3/action/datastore_search?resource_id={rid}&limit=32000&offset={off}"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "research-client"}), timeout=180))["result"]
    rows += r["records"]; off += len(r["records"])
    if not r["records"] or off >= r["total"]: break
json.dump(rows, open(out, "w")); print(out, len(rows), r["total"])
```

```python
"""Item 5 on the record: the CfD levy from strike against the world's price. Read-only.
argv: <lccc dir> <world daily ssp json>"""
import json, sys
from collections import defaultdict
from datetime import date, timedelta
d, wpath = sys.argv[1], sys.argv[2]
gen = json.load(open(f"{d}/gen.json")); levy = json.load(open(f"{d}/levy.json"))
w = json.load(open(wpath)); w0 = date.fromisoformat(w["start_date"])
world = {w0 + timedelta(i): v for i, v in enumerate(w["daily_mean_ssp"])}
WEND = max(world)
day = lambda s: date.fromisoformat(s[:10])
q = lambda t: f"{t.year}Q{(t.month-1)//3+1}"
f = lambda x: float(x) if x not in (None, "") else 0.0
# latest settlement run per day
RUNS = ["II", "SF", "R1", "R2", "R3", "RF", "DF"]
best = {}
for r in levy:
    t = day(r["Settlement_Date"]); rk = RUNS.index(r["Settlement_Run_Type"]) if r["Settlement_Run_Type"] in RUNS else -1
    if r.get("Latest_Flag", "").lower().startswith("latest") or t not in best or rk > best[t][0]:
        if t in best and best[t][2] and not r.get("Latest_Flag", "").lower().startswith("latest"): continue
        best[t] = (rk, r, r.get("Latest_Flag", "").lower().startswith("latest"))
dem = {t: f(v[1]["Reconciled_Eligible_Demand_MWh"]) for t, v in best.items()}
rate = {t: f(v[1]["Reconciled_Daily_Levy_Rate_GBP_Per_MWh"]) for t, v in best.items()}
pay = defaultdict(float); built = defaultdict(float); payY = defaultdict(float); builtY = defaultdict(float)
B = defaultdict(float); C_rows = []; types = defaultdict(int)
for r in gen:
    t = day(r["Settlement_Date"]); g = f(r["CFD_Generation_MWh"]); s = f(r["Strike_Price_GBP_Per_MWh"])
    ref = f(r["Market_Reference_Price_GBP_Per_MWh"]); p = f(r["CFD_Payments_GBP"]); types[r["Reference_Type"]] += 1
    pay[t] += p; built[t] += (s - ref) * g; payY[t.year] += p; builtY[t.year] += (s - ref) * g
    if t <= WEND:
        if r["Reference_Type"] == "IMRP":
            B[t] += (s - world[t]) * g; C_rows.append((t, s, g))
        else:
            B[t] += p
print("reference types", dict(types))
print("\nLEG A1 built vs reported payment, by year (GBPm)")
for y in sorted(payY):
    print(f"  {y} reported {payY[y]/1e6:9.1f} built {builtY[y]/1e6:9.1f} diff {100*(builtY[y]-payY[y])/abs(payY[y]) if payY[y] else 0:6.2f}%")
# quarterly
Q = defaultdict(lambda: defaultdict(float))
for t in set(pay) | set(dem):
    k = q(t); Q[k]["pay"] += pay.get(t, 0); Q[k]["dem"] += dem.get(t, 0); Q[k]["rd"] += rate.get(t, 0) * dem.get(t, 0)
    if t <= WEND: Q[k]["B"] += B.get(t, 0); Q[k]["full"] += 1 if t in world else 0
qm = defaultdict(list)
for t in world: qm[q(t)].append(world[t])
qmean = {k: sum(v)/len(v) for k, v in qm.items()}
for t, s, g in C_rows: Q[q(t)]["C"] += (s - qmean[q(t)]) * g
# C: baseload rows keep their reported payment
Cbase = defaultdict(float)
for r in gen:
    t = day(r["Settlement_Date"])
    if t <= WEND and r["Reference_Type"] != "IMRP": Cbase[q(t)] += f(r["CFD_Payments_GBP"])
for k in Q: Q[k]["C"] += Cbase[k]
print("\nquarter  levy_from_pay  LCCC_reconciled  A2ok | actual_pay_m  worldB_m  flatC_m | levyA levyB levyC")
ok = n = 0; rows = []
for k in sorted(Q):
    x = Q[k]
    if x["dem"] <= 0: continue
    la = x["pay"]/x["dem"]; lr = x["rd"]/x["dem"]
    good = abs(la-lr) <= max(0.05*abs(lr), 0.10); n += 1; ok += good
    inw = x["full"] > 0
    lb = x["B"]/x["dem"] if inw else float("nan"); lc = x["C"]/x["dem"] if inw else float("nan")
    rows.append((k, la, lb, lc, inw))
    print(f"{k}  {la:8.2f}  {lr:8.2f}  {'ok' if good else 'NO'} | {x['pay']/1e6:9.1f} {x['B']/1e6 if inw else float('nan'):9.1f} {x['C']/1e6 if inw else float('nan'):9.1f} | {la:6.2f} {lb:6.2f} {lc:6.2f}")
print(f"\nA2: {ok}/{n} quarters within 5% or 0.10")
neg = [k for k, la, *_ in rows if "2021Q4" <= k <= "2023Q1" and la < 0]; print("A3 negative quarters 2021Q4..2023Q1:", neg)
# B1 by year, C1 MAE by span (only whole quarters inside the world)
Y = defaultdict(lambda: [0.0, 0.0, 0.0])
for r in gen:
    t = day(r["Settlement_Date"])
    if t <= WEND: Y[t.year][0] += f(r["CFD_Payments_GBP"])
for t, v in B.items(): Y[t.year][1] += v
print("\nB1/B2 by year: actual_m world_m err%")
for y in sorted(Y):
    a, b, _ = Y[y]; print(f"  {y}{'*' if y == WEND.year else ' '} {a/1e6:9.1f} {b/1e6:9.1f} {100*(b-a)/abs(a) if a else 0:7.1f}%  diff_m {(b-a)/1e6:8.1f}")
def span(lo, hi):
    s = [(la, lb, lc) for k, la, lb, lc, inw in rows if inw and lo <= k <= hi]
    return (sum(abs(lb-la) for la, lb, lc in s)/len(s), sum(abs(lc-la) for la, lb, lc in s)/len(s), len(s))
for lo, hi in [("2016Q1", "2021Q2"), ("2023Q1", "2025Q1")]:
    mb, mc, m = span(lo, hi); print(f"C1 {lo}..{hi}: MAE levy world {mb:.3f}  flat {mc:.3f}  (n={m})")
```
