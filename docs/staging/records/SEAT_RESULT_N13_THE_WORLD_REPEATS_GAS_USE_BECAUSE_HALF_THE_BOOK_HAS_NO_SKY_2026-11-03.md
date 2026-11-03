**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** none — N13, sixth cold read

# N13 result: the world repeats the gas use, not the bill. Half the drawn book reads a climate normal (2026-11-03)

**Pre-registration:** `docs/staging/records/SEAT_PREREG_N13_WHICH_SIDE_REPEATS_METERED_GAS_USE_2026-11-03.md`
(landed 9d04f33b7, before any measurement).
**Run:** `run_output_08f267b666_20261102T173915Z.json`, the run behind the 85b044be54 book.
**Scripts:** `/tmp/n13_census.py`, `/tmp/n13_sky.py`, `/tmp/n13_cov.py`. Each was run from the repo
root with `SE_DRAW_POPULATION=1`.

## The side: the world (explanation 1)

The run's `meter_read_log` carries each read's `true_consumption_kwh`, the world's own metered
volume. On whole-calendar-month gas bills, with an actual or prepayment read on both sides of the
year:
- billed repeats: 1,311 of 2,423 pairs;
- world repeats: 1,163 of 2,423 pairs.

My month filter is stricter than the cold reader's, so these pairs are fewer than its 4,413. Of the
79 legs with six or more pairs, 46 repeat on 10% or more of them. On 43 of those 46, the world
repeats as well. The other three are id joins I could not make: two electricity-suffixed ids that
bill gas, and one OCC electricity id. **Nothing relabels an estimate as actual. The bill faithfully
prints a world that does not move.**

OCC-098fe5fa8b46g repeats on 12 of 13 billed pairs and 12 of 13 world pairs. **Prediction 1 held.**

## Why the world does not move: two causes, one mechanism

The mechanism is `sim.weather_hdd.hdd_reading`. A premise with no resolvable sky reads the
1991–2020 England & Wales monthly normal, which is the same number in every year.

| The 79 legs | repeats | no repeat |
|---|---|---|
| OCC leg, not in the book the runner adopted | 15 | 0 |
| premise more than `MAX_SNAP_KM` (5 km) from any cell the store holds | 29 | 0 |
| premise with a sky | 2 | 33 |

1. **Occupier legs are never adopted.** `_admit_incoming_occupant` copies the premise's
   `weather_by_customer` and fabric series. The HDD leg, however, resolves the sky from the bare
   id through `weather_inputs._BOOK`, and `adopt_book` runs once, before the loop. **Prediction 2
   held for this class.** **Fixed in this landing:** `weather_inputs.adopt_record`, called on
   admission, with two controls; the behavioural one is mutation-proven.
2. **The store does not cover the book it serves.** The store was last built on 2026-10-11
   (`sim/weather_world/`). `tools/build_weather_world.book_cells` builds from the book as it was
   drawn at that time, and the book has been redrawn since, for example by the fuel-from-home draw
   of 17 Oct. On today's starting book:
   - **490 of 1,046 records are refused;**
   - that includes **227 of 477 gas premises** and 263 of 567 resi electricity premises;
   - the distance to the nearest held cell is 5.1 / 8.5 / 12.2 / 19.2 / 162.6 km (min / quartiles / max).

   These premises also get no fabric trace. That is why they show up as `population_70_30_split`:
   29 of 30 such legs repeat.

**Prediction 3 was wrong in its stated form.** I predicted that "not adopted" would explain at
least 90% of the repeats. Non-adoption explains 15 of 46. The larger cause, 29 of 46, is store
coverage, which I had not considered. The separation is still clean: every repeating leg but two
lacks a sky, and every non-repeating leg has one. **Prediction 4 held:** the SYN/PROS repeats are
founders as well as later cohorts.

## Residuals

- **PROS-2019-0208g** (36 of 57 pairs) has a sky. From April 2021 it meters exactly 4.5 kWh a day,
  flat. That is a gas leg with no heating term and no seasonal hot water, and nothing on
  `customer_events` explains it. It is not the normal; it is a separate question.
- **SYN-2016-131g** repeats on 1 of 6 pairs, which is at threshold and is noise.

## What is left, and whose it is

Cause 2 is a **baseline-world fidelity fix (R13), decided blind to company results**: rebuild the
store over today's book (`python3 -m tools.build_weather_world --build`). Temperature comes from the
local HadUK grids, which are cached at 39 GB. The ERA5 columns need an Open-Meteo pull, which the
rate limiter has throttled before (W1_14's history). Every gas and weather-shaped figure will move,
so the rebuild needs its own pre-registration. It is handed on, not done here.

There is also no control that the store covers the book a run settles.
`test_every_registered_premise_has_a_cell_whatever_the_curriculum_serves` asks only the 18-point
roster, so it stayed green while half the drawn book went without a sky.

**Reverse:** delete this file.
