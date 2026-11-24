**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `SPINE_3_gas_storage_crisis_regime`

# Result: the world's gas record has the right level outside the crisis and none of the gas page's mechanisms below a month, and the forward gas draw is noise around a level (2026-11-24)

Pre-registered in `SEAT_PREREG_GRADE_THE_WORLDS_GAS_PRICE_RECORD_AGAINST_THE_GAS_PAGE_BY_REGIME_2026-11-24.md`,
committed as `4abe9cf16` before the probe first ran. The page graded against is
`docs/market_research/how_the_gb_gas_price_forms_nbp_and_sap_2026-11-24.md`. The probe is at the end of this
record; it is read-only and takes seconds.

## The numbers

World = `load_nbp_history()` (monthly TTF proxy, flat over days), what every run reads. SAP = GB System
Average Price. Forward = `generate_gas_scenario_prices(2026, 2027, "baseline_2025")`, graded against
post-crisis SAP.

| | pre-crisis 2018-01..2021-06 | crisis 2021-07..2023-06 | post-crisis 2023-07..2025-06-07 | forward 2026-27 |
|---|---|---|---|---|
| G1 monthly MAE, £/MWh (bias world − SAP) | 0.58 (+0.18) | **16.40 (+16.02)** | 1.27 (+0.32) | level £25.00 against post SAP £30.78 (−19%) |
| G2 winter/summer, world · SAP | 1.12 · 1.16 | **0.93 · 1.19** | 1.13 · 1.20 | 1.07 |
| G3 SD of daily log returns, world · SAP | 0.032 · 0.073 | 0.061 · 0.176 | 0.019 · 0.037 | **0.501** |
| G3' within-month only (post-hoc), world · SAP | **0.000** · 0.070 | **0.000** · 0.172 | **0.000** · 0.037 | — |
| G4 days > 1.5 × 30-day median, world · SAP | 1.20% · 1.12% | 4.29% · 7.71% | 0.00% · 0.00% | **10.29%** |
| G6 lag-1 autocorrelation, world · SAP | 0.998 · 0.909 | 0.990 · 0.972 | 0.993 · 0.984 | **0.005** |

**G5**, Jun-Sep 2022: world £139.79/MWh, SAP £87.02/MWh, SAP 37.7% below the world.
Per-year monthly MAE: 2018 0.74, 2019 0.47, 2020 0.21, 2021 3.68, **2022 29.07**, 2023 1.06, 2024 1.03,
2025 H1 2.20.

## Predictions against outcomes (kept as filed)

| Check | Predicted | Outcome | Held? |
|---|---|---|---|
| G1 pre | MAE ≤ £1.5 | 0.58 | held |
| G1 crisis | £15-35, world above | 16.40, +16.02 | held |
| G1 post | ≤ £2 | 1.27 | held |
| G2 SAP pre | 1.2-1.6 | 1.16 | **missed**: the pre-crisis GB winter premium is smaller than I expected |
| G2 world vs SAP, pre and post | within ±0.10 | 0.04, 0.07 | held |
| G2 crisis gap | > 0.20 | 0.26 (world puts summer ABOVE winter) | held |
| G2 forward | 1.00 ± 0.03 | 1.07 | **missed**: no seasonal mechanism exists in the generator, so this is the random placement of its storm days in two years, not a season |
| G3 SAP, three regimes | 0.03-0.08, 0.08-0.20, 0.03-0.07 | 0.073, 0.176, 0.037 | held |
| G3 world ≤ 0.03 and ≤ 0.4 × SAP | all regimes | 0.032/0.44×, 0.061/0.35×, 0.019/0.51× | **missed** in pre and post. My model of the reader was wrong: a monthly step once in thirty days gives a daily SD of about the step ÷ √30. G3' (post-hoc, labelled) removes the month-boundary days. The world's within-month movement is then exactly zero in every regime. |
| G3 forward ≥ 0.25, ≥ 4 × SAP | | 0.501, 13.5× | held |
| G4 SAP | 0.2-2%, 2-8%, < 1% | 1.12%, 7.71%, 0.00% | held |
| G4 world ≤ 0.5% | all regimes | 1.20%, 4.29%, 0.00% | **missed**, same reader cause: a month step stays above 1.5 × the trailing median for up to 30 days. These are level steps, not spikes. G4 as written cannot separate a step from a spike, and that is a defect of the statistic. |
| G4 forward ≥ 1% | | 10.29% | held |
| G5 SAP ≥ 40% below world | | 37.7% | **missed**, narrowly. The direction and size hold. |
| G6 SAP ≥ 0.90, world ≥ 0.95, forward ±0.05 | | all three | held (the forward one is a check by construction) |

Fifteen rows: ten held, five missed. Two of the misses (G3 world, G4 world) are the reader, my own
statistic meeting a step series. Two (G2 SAP pre, G5) were my priors, wrong by small margins. One
(G2 forward) was sampling noise that I treated as exact.

## What it means, mechanism by mechanism (gas page sections)

1. **Level, global LNG/TTF (§3): right outside the crisis.** Monthly MAE is under £1.30 in both calm
   regimes, and the bias is a few pence. The world's level can carry forward-year anchoring.
2. **Interconnection, IUK/BBL saturation (§5): the whole crisis error.** The crisis MAE is
   2022 (£29), and Jun-Sep 2022 alone puts the world 38% above GB. The world prices GB as TTF
   in exactly the months when the pipes were full and NBP decoupled. The seasonal sign flips too:
   the world shows summer above winter (0.93) and GB shows winter above summer (1.19). A supplier in
   the world bought summer-2022 gas at a continental price no GB supplier paid. **Remedy:** switch
   the world to the SAP splice that already exists (held in `not_now` behind the skip pair). That is
   a baseline change for fidelity, decided blind to company results.
3. **Weather-driven demand, storage, linepack (§4, §6): absent below a month.** SAP moves 3.7-17%
   a day within months. The world moves 0.000. Nothing the world's weather does reaches its gas price.
   SAP's lag-1 of 0.91-0.98 says a day's price is mostly yesterday's. So the daily structure is
   persistent shocks, the shape a storage/linepack story predicts, and not noise.
4. **Forward gas draw: none of the mechanisms, and noise in their place.** Its daily SD is 13.5 ×
   post-crisis SAP and its lag-1 is 0.005 against 0.984. One day in ten is a "spike" against none
   in GB after the crisis. Its level is 19% below post-crisis SAP. That level is a curriculum
   matter, the director's (R13), and is not graded as wrong here; the shape is mechanism, and is
   wrong. Each day is an independent Gaussian draw. A hedge or a fixed tariff priced over that draw
   meets daily risk that does not exist in GB gas, and none of the seasonal or cold-spell risk that does.
   **This is the larger finding for forward years.** It is filed as a work item beside this record.

## What this does NOT establish

- SAP is a within-day price; day-ahead NBP, which a supplier buys at, is not held (18 Nov page GAP).
  Every G3/G4 SAP number is an upper bound for the day-ahead series.
- Pre-2018 is ungraded (no daily GB series).
- Nothing here says what a forward gas generator SHOULD draw. The page states the mechanisms it
  must be able to show. The level is curriculum.

## The probe

Run from the repo root. The first block is the pre-registered statistics; the last function is the
post-hoc G3', added after the first run.

```python
import math, statistics as st, sys
from collections import defaultdict
from datetime import date
sys.path.insert(0, ".")
from sim.gas_prices_history import RECORD_END, load_nbp_history, load_sap_daily
from sim.scenario.gas_scenario_generator import generate_gas_scenario_prices
END = date.fromisoformat(RECORD_END)
REGIMES = {"pre": (date(2018, 1, 1), date(2021, 6, 30)), "crisis": (date(2021, 7, 1), date(2023, 6, 30)),
           "post": (date(2023, 7, 1), END)}
world = {date.fromisoformat(r["settlementDate"]): float(r["systemSellPrice"]) for r in load_nbp_history()}
sap = load_sap_daily()
fwd = {date.fromisoformat(r["settlementDate"]): r["systemSellPrice"]
       for r in generate_gas_scenario_prices(2026, 2027, "baseline_2025", seed="gas_scenario")}
def window(s, lo, hi): return {d: v for d, v in s.items() if lo <= d <= hi}
def monthly(s):
    m = defaultdict(list)
    for d, v in s.items(): m[(d.year, d.month)].append(v)
    return {k: st.mean(v) for k, v in m.items()}
def season_ratio(s):
    mm = monthly(s)
    return (st.mean(v for (y, mo), v in mm.items() if mo in (10, 11, 12, 1, 2, 3))
            / st.mean(v for (y, mo), v in mm.items() if mo in (4, 5, 6, 7, 8, 9)))
def logret_sd(s, within_month=False):
    ds = sorted(s)
    return st.pstdev([math.log(s[b] / s[a]) for a, b in zip(ds, ds[1:])
                      if (b - a).days == 1 and (not within_month or a.month == b.month)])
def spike_share(s):
    ds = sorted(s); n = hits = 0
    for i, d in enumerate(ds[30:], 30):
        n += 1; hits += s[d] > 1.5 * st.median(s[x] for x in ds[i - 30:i])
    return hits / n
def lag1(s):
    x = [s[d] for d in sorted(s)]; return st.correlation(x[:-1], x[1:])
# G1: mean(|monthly(world) - monthly(SAP)|) per regime; G2 season_ratio; G3 logret_sd;
# G3' logret_sd(within_month=True); G4 spike_share; G5 Jun-Sep 2022 means; G6 lag1.
```
