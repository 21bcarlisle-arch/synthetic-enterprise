**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: grading the world's power price record against the electricity page, by regime (2026-11-24)

Written by the delivery seat on 24 Nov 2026, BEFORE the probe below has run. It answers item 2 of the
05:40 addendum to the director's steer of 24 Nov (signed text `452de5285`), carried by
`docs/staging/WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`.
The page is `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`, landing with
the result. Same form as the gas grade (`SEAT_PREREG_GRADE_THE_WORLDS_GAS_PRICE_RECORD_...`, `4abe9cf16`).

## What is graded, and against what

- **The world's record** is what every run settles against: Elexon's System Sell Price, half-hourly,
  2015-11-07 to 2025-06-07 (`sim/cache/elexon_ssp_full.json`, 168,026 periods). SSP is the imbalance
  cash-out price. The world uses it as THE wholesale price.
- **The traded price** is Elexon's Market Index Data (MID), the volume-weighted price of short-term
  exchange trades per period (APX/EPEX and N2EX), joined by `sim.market_index_history.volume_weighted_mid`.
  It starts 2016-09-12. It is a short-term traded price, not the day-ahead auction; that is a stated gap.
- **The mechanism inputs** are published: GB SAP daily gas (`sim/gas_data/sap_daily.csv`, from 2018);
  DUKES 5.10.C fleet CCGT efficiency by year (HHV); DESNZ gas emission factor 0.1829 tCO2/MWh_th; CPS
  £18/t; EUA annual EEX auction VWAP × ECB FX for 2018-2020; UK ETS civil-penalty prices for 2021-2024,
  each taken in the year its futures were traded (the £83.03 labelled 2023 is used for 2022, and so on;
  see `eu_uk_ets_carbon_price_series_2026-08-03.md`). No UKA spot series is held; that is item 3's gap.
  2025 has no allowance figure held, so the carbon checks stop at 2024-12-31. Elexon FUELHH by fuel and
  by interconnector (signed: negative is export).
- **Regimes**, by date, as the chain and gas grades: pre-crisis 2016-09-12..2021-06-30 (2018-01-01 for
  the gas checks); crisis 2021-07-01..2023-06-30; post-crisis 2023-07-01..2025-06-07 (2024-12-31 for
  the carbon checks).

## Each check is one mechanism the page names

| # | Mechanism (page section) | Statistic |
|---|---|---|
| E1 | The world's price is the imbalance price, not the traded price (§0, §8) | monthly-mean MAE and bias, SSP − MID |
| E2 | Gas SRMC with carbon sets the price (§1, §2) | monthly MID − SRMC (clean spark spread at fleet efficiency): median; MAE with carbon against gas-only |
| E3 | CfD/RO bidding below zero; negative prices (§3) | negative half-hours per year, SSP and MID |
| E4 | Scarcity and the BM (§7) | half-hours above £500 per regime, SSP and MID |
| E5 | The BM adds within-day noise the traded market does not have (§7) | mean within-day SD, SSP ÷ MID |
| E6 | Interconnectors, and the 2022 exports (§5) | annual net flow by country, TWh (FUELHH) |
| E7 | Nuclear availability (§4) | annual nuclear TWh (FUELHH) |
| E8 | Wind displaces gas from the margin (§6, §8) | monthly correlation of MID − SRMC against FUELHH wind share |
| E9 | Weather-driven demand (§8) | MID winter/summer ratio of monthly means |

## Predictions, filed before the run

- **E1** pre MAE ≤ £4 with bias in [−£1, +£4]; crisis MAE £8-30; post MAE ≤ £6. (Partly known: the
  2026-10-25 page shows SSP annual means within a few pounds of published day-ahead means.)
- **E2** pre median spread in [−£5, +£10]; crisis median above +£10 with MAE more than twice pre; post
  median in [−£5, +£15]. Carbon lowers the MAE against gas-only SRMC in all three regimes.
- **E3** MID: ≤ 5 negative half-hours in each of 2016-2018; ≥ 50 in 2023; ≥ 150 in 2024. SSP has at
  least 3 × MID's count in every year 2017-2024.
- **E4** SSP above £500: ≥ 30 pre (partly known: 50 over 2015-20); MID above £500: ≤ 5 pre and ≥ 20
  in the crisis; SSP ≥ 2 × MID in every regime.
- **E5** SSP ÷ MID within-day SD ≥ 1.5 in every regime.
- **E6** France (IFA, IFA2, ElecLink) net NEGATIVE (GB exports) in 2022, positive in 2017-2021 and 2024.
  All interconnectors together negative in 2022. Norway positive in 2022. Ireland (Moyle, EWIC)
  negative in every year.
- **E7** Nuclear 55-72 TWh in 2016 and 35-45 TWh in 2024, a fall of at least 30%.
- **E8** correlation ≤ −0.3 pre and post.
- **E9** pre ratio 1.05-1.35.

## What would change the reading

If E1 holds outside the crisis and E4/E5 fail, the world's level is right but every hedge and tariff
in it meets a tail and a within-day noise that no supplier's traded cost carries. If E2 holds and the
carbon term lowers the MAE, missing carbon is a credible cause of the chain's −£12 pre-crisis bias,
and item 3 has its prediction. If E6 fails, the page's 2022 account is wrong. The result goes to
`docs/staging/records/SEAT_RESULT_...` beside this file, with every wrong prediction kept.

## The probe (filed with the predictions; run from the shared repo root)

```python
"""Grade the world's power record (the SSP replay) against the electricity K8 page, by regime.
Read-only. Run from the shared repo root (the Elexon caches are untracked data there)."""
import calendar, csv, json, statistics as st, sys
from collections import defaultdict
from datetime import date
sys.path.insert(0, ".")
from sim.market_index_history import volume_weighted_mid

MID_FILES = ("sim/cache/elexon_mid_full.json",
             "/var/tmp/se-seat-executor/sim/cache/elexon_mid_2021_2023.json",
             "/var/tmp/se-seat-executor/sim/cache/elexon_mid_2024_2025.json")
END = date(2025, 6, 7)  # the SSP replay's last day
REG = {"pre": (date(2016, 9, 12), date(2021, 6, 30)), "crisis": (date(2021, 7, 1), date(2023, 6, 30)),
       "post": (date(2023, 7, 1), END)}
# Gas-SRMC checks: SAP starts 2018; no allowance price is held for 2025, so they stop at 2024-12-31.
REG_G = {"pre": (date(2018, 1, 1), date(2021, 6, 30)), "crisis": REG["crisis"],
         "post": (date(2023, 7, 1), date(2024, 12, 31))}
EFF = {2018: .4894, 2019: .4878, 2020: .4844, 2021: .4900, 2022: .4911, 2023: .4991, 2024: .4893}  # DUKES 5.10.C HHV
EF = 0.1829       # tCO2/MWh_th gross CV, DESNZ conversion factors 2024
CPS = 18.0        # £/tCO2 from 1 Apr 2016
ALLOW = {2018: 15.34 * .8847, 2019: 24.65 * .8778, 2020: 24.51 * .8897,  # EUA EEX VWAP x ECB FX
         2021: 47.96, 2022: 83.03, 2023: 64.90, 2024: 41.84}            # UK ETS civil-penalty, shifted one year (traded-in-year)

ssp = defaultdict(dict)
for r in json.load(open("sim/cache/elexon_ssp_full.json")):
    ssp[date.fromisoformat(r["settlementDate"])][r["settlementPeriod"]] = float(r["systemSellPrice"])
raw = []
for p in MID_FILES: raw += json.load(open(p))
mid = defaultdict(dict)
for (d, sp), v in volume_weighted_mid(raw).items():
    mid[date.fromisoformat(d)][sp] = v
sap = {date.fromisoformat(r["settlementDate"]): float(r["systemAveragePrice"])
       for r in csv.DictReader(open("sim/gas_data/sap_daily.csv"))}

def days(s, lo, hi): return [d for d in sorted(s) if lo <= d <= hi]
def monthly(s, lo, hi):
    m = defaultdict(list)
    for d in days(s, lo, hi):
        v = s[d]; m[(d.year, d.month)] += (list(v.values()) if isinstance(v, dict) else [v])
    return {k: st.mean(x) for k, x in m.items()}
def srmc(y, mo, carbon):
    g = monthly(sap, date(y, mo, 1), date(y, mo, calendar.monthrange(y, mo)[1]))[(y, mo)]
    return g / EFF[y] + (EF / EFF[y] * (CPS + ALLOW[y]) if carbon else 0.0)
out = {}
for name, (lo, hi) in REG.items():
    ms, mm = monthly(ssp, lo, hi), monthly(mid, lo, hi)
    ks = sorted(set(ms) & set(mm))
    e = [ms[k] - mm[k] for k in ks]
    hh = [(d, sp) for d in days(mid, lo, hi) for sp in mid[d] if sp in ssp.get(d, {})]
    wd = [(st.pstdev(ssp[d].values()), st.pstdev(mid[d].values())) for d in days(mid, lo, hi)
          if d in ssp and len(mid[d]) >= 40 and len(ssp[d]) >= 40]
    wint = [v for (y, mo), v in mm.items() if mo in (10, 11, 12, 1, 2, 3)]
    summ = [v for (y, mo), v in mm.items() if mo in (4, 5, 6, 7, 8, 9)]
    out[name] = {"E1_mae": st.mean(abs(x) for x in e), "E1_bias": st.mean(e), "months": len(ks),
                 "E4_ssp_gt500": sum(ssp[d][sp] > 500 for d, sp in hh), "E4_mid_gt500": sum(mid[d][sp] > 500 for d, sp in hh),
                 "E5_ratio": st.mean(a for a, b in wd) / st.mean(b for a, b in wd),
                 "E9_mid_winter_summer": st.mean(wint) / st.mean(summ)}
# E2 / E8: gas SRMC with and without carbon, against MID, monthly
fuel = defaultdict(lambda: defaultdict(float))  # (y,mo) -> fuelType -> MWh
for fn in ("remainder", "thermal", "zero_carbon_must_run", "carbon_relevant", "biomass"):
    for r in json.load(open(f"sim/cache/elexon_fuelhh_{fn}.json")):
        d = r["settlementDate"]; fuel[(int(d[:4]), int(d[5:7]))][r["fuelType"]] += 0.5 * (r["generation"] or 0)
for name, (lo, hi) in REG_G.items():
    mm = monthly(mid, lo, hi); ks = sorted(mm)
    css = [mm[k] - srmc(*k, True) for k in ks]; cssg = [mm[k] - srmc(*k, False) for k in ks]
    wshare = [fuel[k]["WIND"] / sum(v for f, v in fuel[k].items() if not f.startswith("INT") and v > 0) for k in ks]
    out[name].update({"E2_css_median": st.median(css), "E2_mae_carbon": st.mean(abs(x) for x in css),
                      "E2_mae_gas_only": st.mean(abs(x) for x in cssg), "E2_months": len(ks),
                      "E8_corr_css_wind": st.correlation(css, wshare)})
# E3 negative half-hours per year; E6 net interconnector flow; E7 nuclear
GROUP = {"FR": ("INTFR", "INTIFA2", "INTELEC"), "NL": ("INTNED",), "BE": ("INTNEM",), "NO": ("INTNSL",),
         "DK": ("INTVKL",), "IE": ("INTIRL", "INTEW", "INTGRNL")}
years = {}
for y in range(2016, 2026):
    ds = [d for d in ssp if d.year == y]; dm = [d for d in mid if d.year == y]
    f = defaultdict(float)
    for (yy, mo), v in fuel.items():
        if yy == y:
            for k, x in v.items(): f[k] += x
    years[y] = {"E3_ssp_neg": sum(v < 0 for d in ds for v in ssp[d].values()),
                "E3_mid_neg": sum(v < 0 for d in dm for v in mid[d].values()),
                "mid_days": len(dm), "ssp_days": len(ds),
                "E6_TWh": {g: round(sum(f[k] for k in ks) / 1e6, 2) for g, ks in GROUP.items()},
                "E6_total_TWh": round(sum(v for k, v in f.items() if k.startswith("INT")) / 1e6, 2),
                "E7_nuclear_TWh": round(f["NUCLEAR"] / 1e6, 2)}
print(json.dumps({"regimes": out, "years": {str(k): v for k, v in years.items()}}, indent=1, default=float))
```
