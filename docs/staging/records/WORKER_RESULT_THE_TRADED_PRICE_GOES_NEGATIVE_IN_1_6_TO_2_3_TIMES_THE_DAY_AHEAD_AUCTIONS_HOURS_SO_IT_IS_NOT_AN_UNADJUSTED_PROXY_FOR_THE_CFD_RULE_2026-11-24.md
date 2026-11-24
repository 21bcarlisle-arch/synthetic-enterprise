**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the traded price (MID) goes negative in 1.6-2.3 times the day-ahead auction's hours, so it is not an unadjusted proxy for the CfD negative-hour rule (2026-11-24)

Pre-registered in `WORKER_PREREG_HOW_OFTEN_THE_TRADED_PRICE_GOES_NEGATIVE_BY_THE_HOUR_AGAINST_THE_DAY_AHEAD_AUCTION_2026-11-24.md`,
sha256 `040a1fc4…abf952a` at 21:23 UTC, before the probe first ran. **Disclosure:** it was hashed, not
landed, before the run; it lands in the same commit as this record. The probe ran once, read-only, in a
few seconds; its text is below so it can be rerun.

## The numbers

A MID hour is the volume-weighted mean of its two APXMIDP settlement periods. Negative means < £0.
Day-ahead counts are the published ones on the electricity page §3 [press; different auctions].

| Year | Hours in cache (priced) | MID negative hours | In six-hour runs (runs) | Day-ahead negative hours | MID ÷ day-ahead |
|---|---|---|---|---|---|
| 2016 (Sep-) | 2,593 (100%) | 0 | 0 (0) | 0 | — |
| 2017 | 8,603 (99.9%) | 20 | 6 (1) | 0 | — |
| 2018 | 8,655 (99.9%) | 9 | 0 (0) | 0 | — |
| 2019 | 8,627 (99.7%) | 29 | 14 (1) | first on 9 Dec | — |
| 2020 | 8,262 (100%) | 161 | 97 (11) | not held | — |
| 2021 | 8,421 (99.7%) | 31 | 6 (1) | not held | — |
| 2022 | 8,758 (99.9%) | 67 | 32 (5) | 29 | **2.31** |
| 2023 | 8,760 (99.9%) | 203 | 83 (10) | 107 | **1.90** |
| 2024 | 8,784 (100%) | 233 | 92 (11) | 139-149 | **1.56-1.68** |
| 2025 | 8,760 (99.95%) | 237 | 127 (17) | 149-190 | 1.25-1.59 |

## Predictions beside outcomes

| | Filed | Outcome |
|---|---|---|
| P1 | ratio ≥ 1.5 in 2022, 2023, 2024 against every published count | 2.31, 1.90, 1.56-1.68: **held** |
| P2 | 2023 and 2024 ratio in [1.5, 3.5] | 1.90, 1.56-1.68: **held** |
| P3 | 2017+2018 ≥ 10 MID negative hours | 29: **held** |
| P4 | 2023-24, at most half of negative hours in six-hour runs | 41%, 39%: **held** |
| P5 | MID priced in ≥ 99% of hours, every full year 2017-24 | **missed on the calendar.** ≥ 99.7% of the hours the caches hold are priced, but the caches lack 1-6% of hours in 2017-2021 (2020: 8,262 of 8,784). 2022-2024 are complete. The negative counts for 2017-2021 are lower bounds. |

Four of five held. The miss is a coverage defect in the caches, not in MID. The years that carry the
decision (2022-24) are complete.

## What it means

- **Rule (a) fires.** Applied to MID, the AR4-on rule would zero the difference in 1.6-2.3 times as many
  hours as the auction did in 2022-24. MID also goes negative in 2017-18, when no day-ahead hour did.
  A forward levy must source the day-ahead auction, or carry this ratio as its stated error.
- **The ratio is narrowing:** 2.31, 1.90, 1.6, then 1.25-1.59 in 2025. That is not attributed. One
  candidate is more day-ahead negatives as solar grows, with the within-day market's own negatives
  growing more slowly. I cannot yet say.
- **SSP is worse still.** Its negative half-hours run about twice MID's (power grade, 850 and 1,073 in
  2023-24). Testing the rule on the price the world settles at would be the largest error of the three.
- **For pre-AR4 units, the six-hour rule.** 39-54% of MID's negative hours since 2022 sit in six-hour
  runs, in 5-17 runs a year. No published day-ahead six-hour-run count is held, so that leg's error is
  not measured (GAP).

## Limits

Count level only. Which hours match needs the auction's hourly series, which is not held. The published
counts disagree with each other by up to 28% (2025), so the ratio is a band. The hour is built from two
half-hourly MID prints, which is not how the auction clears an hour.

## Probe

```python
import json, collections
files=['sim/cache/elexon_mid_full.json','/var/tmp/se-seat-executor/sim/cache/elexon_mid_2021_2023.json','/var/tmp/se-seat-executor/sim/cache/elexon_mid_2024_2025.json']
hp=collections.defaultdict(lambda:[0.0,0.0]); seen=set()
for f in files:
    d=json.load(open(f)); d=d if isinstance(d,list) else d.get('records')
    for r in d:
        if r.get('dataProvider')!='APXMIDP': continue
        key=(r['settlementDate'],r['settlementPeriod'])
        if key in seen: continue
        seen.add(key)
        v=r.get('volume') or 0
        if v>0 and r.get('price') is not None:
            h=(r['settlementDate'],(r['settlementPeriod']-1)//2); hp[h][0]+=r['price']*v; hp[h][1]+=v
# per year: hours present = distinct (date, (period-1)//2) in seen; negative = priced hour with pv/v < 0;
# six-hour runs = maximal runs of >= 6 consecutive negative hours in the sorted hour list.
```
