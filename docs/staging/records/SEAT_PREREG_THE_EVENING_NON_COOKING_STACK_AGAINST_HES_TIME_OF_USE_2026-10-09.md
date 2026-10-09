**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `the-evening-non-cooking-stack-against-hes-time-of-use`

# Pre-registration: the evening non-cooking stack (lighting, electronics, dishwasher) against HES time of use

Delivery seat (executor), 2026-10-09. Decided blind to company results: nothing below reads a
company figure. Base: origin `70a662dc1`. Filed **before** any world-side measurement. The HES side
is a reading of a published source, so it is stated here as a source, not predicted.

The headcount finding (`SEAT_FINDING_HEADCOUNT_GIVEN_DWELLING_SIZE_2026-10-09.md`) left S2 at
**0.562 kWh/h at 20:00** against SERL 2022's 0.445–0.485 at 18:30. With all cooking removed, the
peak sits at 20:30. The non-cooking evening load is electronics on-mode, lighting and the dishwasher.

## The source: HES time of use, read at source

**Intertek R66141 (HES final report, 2012), Figure 245**, p.193: *Structure of the average hourly
load curve, all days, all households, without electric heating.* This is the mean of the household
load curves, in W per hour, split by end use. The 2-minute data were averaged into 24 hourly values.
It was read by pixel colour from a 250-dpi render, with the axis calibrated on its own gridlines
(0–600 W). Segment borders lose about 2 W each. Script: `/tmp/hestod/bars.py`; the reading is in
`/tmp/hestod/fig245.txt`.

**Calibration of the reading against HES's own tables.** Summed over 24 hours, the read lighting
is 1.397 kWh/day (510 kWh/yr), against Table 25's 537. AV plus ICT is 2.032 kWh/day (742 kWh/yr),
against Tables 26 and 29's 553 + 240 = 793. So the reading is good to about 5–7% in level. Only
the **shape** is used below.

**Dishwasher, Figs 404–408**, pp.294–296: daily average load curve for each of the five household
types, read by eye to about ±3 W. The all-household shape below is their unweighted mean, because
HES publishes no weights for the types.

| End use (HES) | Peak hour | Share 17:00–24:00 | Share 18:00–24:00 | Share 00:00–06:00 | h18 ÷ h12 | h21 ÷ h18 |
|---|---|---|---|---|---|---|
| Lighting | **21:00** (161 W) | 0.591 | 0.536 | 0.115 | 3.54 | **1.63** |
| AV + ICT (on-mode and standby) | **20:00–21:00** (148 W) | 0.451 | 0.389 | 0.118 | **1.60** | 1.09 |
| Dishwasher | **19:00** (68 W) | 0.431 | **0.397** | 0.107 | 1.29 | 1.18 |

Hourly shares (fractions of the day, 00:00 first):

- Lighting: .033 .021 .015 .013 .014 .019 .023 .030 .035 .037 .031 .023 .020 .020 .020 .021 .034 .055 .071 .083 .100 .115 .106 .061
- AV + ICT: .030 .022 .018 .017 .015 .016 .019 .028 .035 .036 .037 .037 .042 .046 .047 .049 .056 .062 .067 .069 .073 .073 .063 .044
- Dishwasher: .035 .015 .015 .019 .014 .009 .008 .027 .042 .055 .058 .050 .043 .049 .054 .043 .033 .034 .056 .090 .076 .066 .054 .055

**HES does not peak at 20:00.** Its whole-home total is flat at about 585–600 W from 17:00 to 20:00.
Cooking makes the 17:00 hour, and lighting makes the late evening.

**Is a 2010–11 shape a dated source for 2022?** For lighting and electronics, the decade changed the
**level** (LEDs, flat screens), and that is already dated through ECUK. Nothing found says it moved
the **hour**. Darkness and being at home set the hour. This is an assumption, stated here. For the
dishwasher, ECUK holds no time-of-use series. HES is the only measured GB time of use for any of
the three.

## The world's mechanism (`simulation/premise_trace.py`)

- Lighting and electronics are switched units. Each unit's stationary probability is
  `occupancy_at`: 0.9 when awake at home, the household's own daytime occupancy on weekday
  09:00–17:00, 0.25 asleep (nothing switched on). Lighting is also gated on dark (sunrise/sunset
  ±0.5 h).
- The dishwasher starts uniformly in half-hours 36–46 (18:00–23:00), shifted by the routine offset
  and clamped to waking hours. It runs 0.70 kW for 1.5 h.

## Predictions, made before the world is measured

The world statistic is the same as HES's: each gas-heated no-PV home's mean kWh per hour across
2022 (C1 weather), averaged across homes, per end use. Lighting and electronics come from the
switched-unit counts, and the dishwasher from its own events. Base seeds 17/29/41.

1. **Lighting.** The world peaks in hour **20 or 21**. Its h21 ÷ h18 is **1.2–2.0** (HES 1.63), and
   its share 18:00–24:00 is within **±0.10** of HES's 0.536. If so, lighting timing is not moved.
2. **Electronics.** The world's evening is flat like HES's (h21 ÷ h18 within 0.95–1.15). Its
   h18 ÷ h12 is **higher** than HES's 1.60, at **1.8–3.0**, because the world's weekday daytime
   occupancy empties the house. Its share 18:00–24:00 is **0.40–0.50** (HES 0.389).
3. **Dishwasher.** The world's share 18:00–24:00 is **≥ 0.90** (HES 0.397).
4. **If the dishwasher alone is moved onto HES's start shape** (one variable, same homes, same
   process), S2 falls by **0.005–0.025 kWh/h**, the peak hour stays at 20:00 ± 0.5 h and stays a
   FAIL, S3 moves by less than 0.01, and S4 moves by less than 15 kWh. The energy per cycle and
   the cycle count are untouched.

## Decision rules

- An end use's **timing** is moved only where its world share 18:00–24:00 differs from HES's by more
  than **0.10**, or its peak hour by more than **1 hour**. Even then, it is moved only onto HES's
  published shape, never onto a value that makes S2 pass.
- The trough (S1), the level and the per-person slope are out of scope. Each is its own variable.
- **No scalar is fitted to SERL.** Whatever S2 reads after the move is the reading.
