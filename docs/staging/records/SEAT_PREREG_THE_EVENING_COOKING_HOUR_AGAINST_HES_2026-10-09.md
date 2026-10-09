**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `the-evening-cooking-hour-against-hes-fig-245`

# Pre-registration: the cooking hour (oven, hob, microwave, kettle) against HES's own per-appliance load curves

Worker, 2026-10-09. Decided blind to company results: nothing below reads a company figure. Base:
origin `8c2c68dbe`. Filed **before** any world-side measurement of cooking time of use. Follows
`docs/staging/SEAT_FINDING_THE_EVENING_NON_COOKING_STACK_AGAINST_HES_TIME_OF_USE_2026-10-09.md`,
which left S2 at **0.528 kWh/h at 20:00** (18:30 reads 0.505) against SERL 2022's 0.445–0.485 at 18:30.

## The source: HES per-appliance load curves, read at source

The drawn item pointed at Fig 245's cooking bars (all cooking, all households, 17:00 ≈ 150 W). HES
also publishes each cooking appliance's own curve over its owning households, holidays and workdays
separately. Those are the better source, because the world places each appliance separately:

- **Oven**, Intertek R66141 Figs 432 (holidays) and 433 (workdays), pp.311–312. HES: "mainly used in
  the evening between 17:00 and 18:00".
- **Electric hob**, Figs 440 and 441, pp.317–318. Only 11 homes (Table: appliance counts).
- **Microwave**, Figs 444 and 445, pp.320–321.
- **Kettle**, Figs 448 and 449, p.323.

Read by pixel colour at 250 dpi. The axis was calibrated on each chart's own gridline spacing. All-days
= (5 × workday + 2 × holiday) / 7. **Calibration against HES's annual table** (Table 14 / p.~18,554):
microwave 57 kWh/yr read against 56, kettle 174 against 167, oven 272 against 290, hob 275 against
226 (n = 11). Only the **shape** is used below.

| Appliance (HES) | Peak hour | Share 18:00–24:00 | Share before 16:00 | Share 16:00–22:00 |
|---|---|---|---|---|
| Oven | **17:00** (120 W) | **0.358** | 0.378 | 0.597 |
| Hob | **18:00** (132 W) | **0.410** | 0.388 | 0.603 |
| Microwave | 17:00 (16 W) | 0.328 | — | — |
| Kettle | 07:00 (42 W) | 0.229 | — | — |

All-days hourly W, 00:00 first:

- Oven: 3.7 3.4 4.1 4.8 3.5 4.1 9.6 22.8 27.9 15.5 19.1 26.8 43.9 33.3 23.7 34.6 76.4 120.1 115.9 67.1 43.9 20.5 13.3 6.0
- Hob: 1.2 1.3 3.5 2.2 1.6 4.7 7.4 19.3 35.5 23.6 23.2 29.4 41.3 48.5 30.4 19.1 42.0 109.9 132.0 79.0 69.5 21.4 4.5 2.3
- Microwave: 2.5 2.7 1.6 1.7 2.2 2.2 3.4 7.1 8.0 5.6 6.1 8.5 10.8 7.1 5.0 5.1 8.6 15.9 14.4 12.9 9.5 6.3 4.6 3.2
- Kettle: 2.2 1.6 1.6 1.9 4.0 9.4 24.6 42.1 39.2 30.3 26.5 24.9 27.2 26.2 22.0 24.8 28.0 30.5 25.3 23.3 21.8 18.5 13.2 7.3

**Dating.** These are 2010–11 hours, as for the dishwasher. ECUK dates the level, not the hour.

## The world's mechanism (`simulation/premise_trace.py` `APPLIANCE_CATALOGUE`)

Each start is uniform in its window, moved by the routine offset (and the weekend shift) and clamped
to waking hours:

- oven (32, 42): starts 16:00–21:00, 2.0 kW for 0.60 h, 0.55 a day
- hob (33, 43): starts 16:30–21:30, 1.8 kW for 0.29 h, 0.70 a day
- microwave (20, 43): starts 10:00–21:30, 0.9 kW for 0.10 h
- kettle (12, 45): starts 06:00–22:30, 2.8 kW for ~0.04 h

## Predictions, made before the world is measured

World statistic: each gas-heated no-PV home's mean kWh per hour across 2022 (C1 weather), averaged
across homes, per appliance, from its own events. The same 2,431 homes (n = 1,000 drawn per seed,
seeds 17/29/41) and the same probe as the non-cooking read.

1. **Oven.** World share 18:00–24:00 is **0.55–0.70** (HES 0.358) and share before 16:00 is
   **≤ 0.05** (HES 0.378). The rule is crossed.
2. **Hob.** World share 18:00–24:00 is **0.60–0.75** (HES 0.410). The rule is crossed.
3. **Microwave.** World share 18:00–24:00 is **0.25–0.38**, inside the rule (HES 0.328). Not moved.
4. **Kettle.** World share 18:00–24:00 is **0.22–0.32**, inside the rule (HES 0.229). Not moved.
5. **Oven and hob moved together onto HES's curves** (one change, same homes, same process): S2 falls
   by **0.03–0.08 kWh/h**, to 0.45–0.50. The peak moves EARLIER, to **18:00–19:30**. S1 moves by
   less than 0.003 (no start is allowed asleep). S3 moves by less than 0.01 (the season factor is
   untouched). S4 moves by less than 15 kWh (counts and energy per use are untouched).
6. Run **alone**, the oven carries at least three quarters of the S2 fall. It is 0.49 kWh/day per
   home against the hob's 0.11, after the gas-cooking draw.

## Decision rules (the non-cooking read's, unchanged)

- An appliance's **timing** is moved only where its world share 18:00–24:00 differs from HES's by
  more than **0.10**, or its peak hour by more than **1 hour**. The peak-hour leg is read only where
  the world curve HAS a peak: its largest hour at least 1.25 × the median of its 06:00–22:00 hours.
  A uniform window has no peak hour, and its argmax is noise.
- It is moved only onto HES's published curve, through the dishwasher's `load_by_hour` door, with the
  window opened to the whole day so the curve, not a window, says when. Never onto a value that
  makes S2 pass.
- **No scalar is fitted to SERL.** Whatever S2 reads after the move is the reading.
- SIMPLIFICATION, stated before the run: one all-days curve per appliance, as for the dishwasher. The
  world's own weekend shift moves it; HES's separate holiday curve is not used.
- The gas cooking meal clock (`cooking_period_kwh`) is gas, not electricity, and is out of scope.
