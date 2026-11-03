**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** none — N13 cause 2

# Result: the weather store now covers every record of the book a run settles; temperature complete, ERA5 partial (2026-11-03)

**Pre-registration:** `docs/staging/records/SEAT_PREREG_REBUILDING_THE_WEATHER_STORE_OVER_THE_DRAWN_BOOK_2026-11-03.md`
(written before the rebuild). **Probe:** `/tmp/wxrebuild/probe.py`, run from the repo root with
`SE_DRAW_POPULATION=1`. **Cause:** N13's second, in
`docs/staging/records/SEAT_RESULT_N13_THE_WORLD_REPEATS_GAS_USE_BECAUSE_HALF_THE_BOOK_HAS_NO_SKY_2026-11-03.md`.

## Step 1, the HadUK temperature pass (`--build --limit 0`, 8.5 min, no network)

| | before | after | predicted |
|---|---|---|---|
| settled records with no temperature series | 490 of 1,052 | **0** | 0 — held |
| of which gas | 227 of 477 | **0** | 0 — held |
| cells in the store | 341 | **836** | about 836 — held |
| 2022 annual HDD, the 227 former-normal gas premises | 2,086.1 (the normal) | **1,813.4 mean**, −13.1% (min 1,410, median 1,790, max 2,568) | −10% to −25% — held |
| of those, a premise reading the same HDD on 15 Jan 2018 and 15 Jan 2022 | 227 | **0** | 0 — held |

The maximum, 2,568, is above the normal. Those are upland or northern cells, colder than England &
Wales, and they read the normal before as well. So the normal was wrong in both directions, not just
biased high.

The pass also swapped 1,277 crossed HadUK min/max cell-days, the same interpolation artefact as the
310 the docstring records; it scales with the number of cells. The series file is 34 MB, up from
18 MB, because the store keeps the 247 cells the book has left (`_write` unions them on purpose).

## The control

`tests/sim/test_the_hdd_leg_reads_the_premises_own_cell.py::test_the_store_covers_every_record_of_the_book_the_run_settles`
asks every record the runner adopts, not the 18-point roster. **Mutation:** with the 11 Oct store
restored, it goes red with "490 of 1052 settled records have no sky". On the rebuilt store it is
green. A redraw without a rebuild reds it and names the count.

## Step 2, the ERA5 archive (wind, cloud, precipitation)

These are needed by the fabric path, not the HDD leg. Until they are present, temperature-only cells
still refuse fabric eligibility. **At this landing, 496 of the book's 589 cells still lack them**
(`SE_DRAW_POPULATION=1 python3 -m tools.build_weather_world --list` prints the count). The pull is
one Open-Meteo request per cell at a 20 s spacing, it resumes, and the hourly bucket has stopped it
at about 23 cells before. Prediction 4 is that it does not finish in one turn.

The 522 tests that touch the store, the HDD leg or the weather inputs pass on the rebuilt store
(3 xfailed).

**Reverse:** `git revert` the landing that carries the three `sim/weather_world/` files. This file
is deleted with it.
