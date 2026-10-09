**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `the-evening-non-cooking-stack-against-hes-time-of-use`

# The evening non-cooking stack against HES time of use: the dishwasher and daylight lighting move onto HES, electronics already sits on it, and S2 falls 0.561 -> 0.528

Delivery seat (executor), 2026-10-09. Decided blind to company results: nothing below reads a
company figure. Pre-registration: `docs/staging/records/SEAT_PREREG_THE_EVENING_NON_COOKING_STACK_AGAINST_HES_TIME_OF_USE_2026-10-09.md`
(landed `a208dd212`, before any world-side run). The lighting addendum below was written after the
baseline read and before the lighting arm was built.

## What HES says about the hour (sources, read at source)

- **Intertek R66141 Fig 245** (all days, all households, no electric heating): the mean hourly load
  by end use, read by pixel colour. The reading reproduces HES's annual tables to 5–7%.
- **Figs 404–408**: the dishwasher's daily load curve, by household type.
- **CAR, *Further analysis of HES: Lighting*, p.25**: daytime lighting from April to September,
  09:00–18:00, averages **24 W**. The annual mean is 59–63 W (518–550 kWh/yr).

| End use | HES peak | HES share 18:00–24:00 | World before | World after |
|---|---|---|---|---|
| Lighting | 21:00 | 0.536 | 21:00, **0.787** | 21:00, **0.667** |
| Electronics (AV+ICT) | 20:00–21:00, flat 18–21 | 0.389 | flat 17–21, 0.418 | unchanged |
| Dishwasher | 19:00 | 0.397 | 21:00, **0.924** | 20:00, **0.429** |

HES's whole home does not peak at 20:00: it is flat at about 585–600 W from 17:00 to 20:00. The
17:00 hour is cooking, and the late evening is lighting.

## The three end uses

1. **Dishwasher: MOVED.** The world started every cycle between 18:00 and 23:00. A cycle now starts
   on HES's curve (the mean of the five household types), shifted half a cycle earlier, inside
   waking hours (`ApplianceSpec.load_by_hour`, `start_weights`). Energy per cycle and the cycle
   count are untouched: 78 kWh/yr per home before and after. HES's 00:00–06:00 delay-timer starts
   (0.10) cannot happen while the household sleeps, so their weight goes to the waking hours. That
   is named as a SIMPLIFICATION in the code.
2. **Lighting: MOVED in part.** The world lit nothing in daylight: summer-daytime lighting was 0.02
   of the annual mean, against CAR's 0.39. Now, awake and home in daylight, a light switches at
   occupancy × 0.19. 0.19 is the share that reproduces CAR's ratio, solved from two linear arms
   (0 and 1). The per-person kW is rescaled to hold annual lighting at 156 kWh/yr. Only the hour
   moves. The level is still not established (ECUK 137–430).
   **Named gap: night and base-load lighting.** CAR (p.24) measures an 8.2 W always-on lighting
   base (72 kWh/yr, ~13% of lighting), and HES puts 0.115 of lighting in 00:00–06:00. The world
   switches nothing on while the household sleeps, so it puts 0.025 there. That is most of the
   remaining 0.13 gap to HES's 0.536. It is not moved here. A base load would raise S1, which is
   already high (see below), so it needs its own one-variable read.
3. **Electronics: NOT MOVED. Within the rule, on HES's shape.** Share 0.418 against 0.389. The
   evening is flat, as HES's is (h21/h18 1.00 against 1.09). The daytime is a little emptier than
   HES's (h18/h12 1.77 against 1.60). Neither difference crosses the decision rule.

## Predictions graded (same 2,431 gas no-PV homes, seeds 17/29/41, C1 2022, one process)

| # | Prediction | Result | |
|---|---|---|---|
| 1 | Lighting peak hour 20–21; h21/h18 1.2–2.0; share 18–24 within ±0.10 of HES | 21; 1.50; **0.787 (+0.25)** | first two held, **share wrong** |
| 2 | Electronics evening flat; h18/h12 1.8–3.0; share 0.40–0.50 | 1.00; **1.77**; 0.418 | held, except h18/h12 just under |
| 3 | Dishwasher share 18–24 ≥ 0.90 | 0.924 | held |
| 4 | Dishwasher alone: S2 −0.005 to −0.025, S3 within ±0.01, S4 within ±15 | **−0.0213**, +0.0011, +2.5 | held |
| L1 | Lighting share 18–24 falls to 0.60–0.70 | 0.667 | held |
| L2 | Annual lighting within ±3% | 156 → 156 | held |
| L3 | Lighting alone: S2 −0.010 to −0.025 | **−0.0118** | held |
| L4 | Lighting alone: S3 −0.005 to −0.02, away from SERL | **−0.0174** | held |

## The SERL cells (`couple_fabric` / `fabric_gap_ledger.level_and_season_vs_serl`)

| Cell | Before | Dishwasher | Lighting | Both | SERL 2022 | Verdict |
|---|---|---|---|---|---|---|
| S1 trough | 0.1388 | 0.1388 | 0.1388 | 0.1388 | 0.125–0.135 | **FAIL, high** |
| S2 peak | 0.5606 | 0.5393 | 0.5488 | **0.5282** | 0.445–0.485 at 18:30 | **FAIL, high** |
| S3 month max/min | 1.2365 | 1.2376 | 1.2191 | **1.2201** | 1.36–1.47 | **FAIL, flat** (and flatter) |
| S4 annual | 2,657 | 2,660 | 2,658 | 2,660 | crisis-free ≈ 2,674–2,717 | unjudged |

Re-read on the landing base (origin `30c5e0c42` plus this change): identical to every cell above. The
peak is still at **20:00**, and 18:30 reads 0.505, down from 0.513.

**All three red cells remain.** S2 closed 0.032 of its 0.043 excess over the band's top, without a
scalar fitted to SERL. The rest is not the non-cooking stack: lighting and the dishwasher are now on
HES's hours, and electronics already was. What is left in the evening is cooking (HES's cooking
peaks at 17:00, while the world's oven and hob start windows open at 16:00 and 16:30 and close at
21:00 and 21:30) and the level. That is the next one-variable read. The lighting move takes S3 a further
0.017 away from SERL, as L4 predicted: the season is a summer-level problem, and daylight use
raises summer. That reading is reported, not reversed.

## Controls taken (`tests/harness/test_premise_two_level.py`), each move attributed by running each change alone

- Texture counts [3, 13, 27, 43] → [3, 13, 26, 45]: the dishwasher moves p75 (43 → 45), and lighting
  moves p50 (27 → 26). The cell still passes.
- The calmest judged home is now **P0033** (electric storage) at 0.0652, against gas P0018's 0.0653.
  The dishwasher alone causes it. So `test_net_of_both_machines_no_electric_home_is_calmer_than_every_gas_home`
  is a **strict xfail again**: the knife-edge its own comment named, crossed by a 0.1% move.
- P0000 0.1980 → 0.1998. L1.1n worst P0040 1.039 → 1.048 (both together; each alone stays inside).
- The partialled peakiness r: raw +0.554 → +0.623, from the dishwasher, by the same common cause as
  the cooking-fuel draw.
- L1.2 worst P0023 0.500 → 0.563, from the dishwasher, still under the 0.6 band.

## Recorded, not mine

`tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py::test_a_saved_term_ends_and_stayers_renew_after_it`
is red at clean origin `a208dd212`: index 7 of the pinned renewal list differs (PROS-2017-0183 on
2018-06-19 against PROS-2016-0192 on 2018-06-24). It was measured in an origin worktree with no
change of mine. Its likely cause is this morning's retention-offer landings (`b922911b7`,
`aac535f08`). That is not established.

## The lighting pre-registration, filed before the lighting arm was built or run (2026-10-09 09:18, after the baseline read, before the lighting arm ran)

The baseline graded prediction 1 wrong on share: world lighting puts 0.787 of its energy in
18:00-24:00 against HES's 0.536, past the decision rule's 0.10. The cause is visible in the
mechanism. Lighting is gated on dark, so the world lights nothing in daylight. CAR's re-analysis of
HES (*Further analysis of the Household Electricity Survey: Lighting*, p.25) dates daytime lighting:
the mean over households, April-September, 09:00-18:00 BST, is **24 W**. HES Table 25's annual is
537 kWh, a mean of **61 W**. So summer-daytime lighting is **0.39** of the annual mean power.

**The arm.** When awake and home in daylight, a light switches with probability occupancy x delta,
not 0. Delta is set so the world's April-September 09:00-18:00 mean lighting is 0.39 of its annual
mean (CAR's ratio). The per-person lighting kW is rescaled by k, so the annual lighting level is
held. The level is not established (ECUK brackets 137-430 kWh), so this arm moves timing only.

**Predictions:**

- L1. World lighting share 18:00-24:00 falls from 0.787 to **0.60-0.70** (HES 0.536).
- L2. Annual lighting is unchanged within **±3%**.
- L3. S2 falls by **0.010-0.025 kWh/h** with the dishwasher held at its old timing. It stays a FAIL.
- L4. S3 falls by **0.005-0.02**: summer days are longer, so daylight lighting is a larger share of
  summer than of winter. This moves **away** from SERL, and it is reported as the reading.
