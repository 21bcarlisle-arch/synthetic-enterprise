**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** none — N13 cause 2

# Pre-registration: what moves when the weather store is rebuilt over today's drawn book (2026-11-03)

**Written before the rebuild and before any measurement of its effect.** The cause is N13's second:
`docs/staging/records/SEAT_RESULT_N13_THE_WORLD_REPEATS_GAS_USE_BECAUSE_HALF_THE_BOOK_HAS_NO_SKY_2026-11-03.md`.
This is a baseline-world fidelity fix (R13): it is decided by coverage, blind to company results.

## What I have read (no effect numbers yet)

- `python3 -m tools.build_weather_world --list` with `SE_DRAW_POPULATION=1`, at b0351a52cc: the
  book occupies **589 cells**; the store holds 341 (333 with ERA5, 8 temperature-only); **495 book
  cells were never held** and 496 are incomplete. 247 held cells are ones the book has left.
- The HDD leg (`sim.weather_hdd.hdd_reading`) needs only `temperature_mean_c`, which the build takes
  from the local HadUK 1 km grids with no network. The ERA5 columns (wind, cloud, precipitation)
  come from Open-Meteo, one pull per cell at 20 s spacing, and the hourly limit has stopped pulls
  of about 23 cells before.
- The book is deterministic at the default base seed, so a control over it is stable until the
  draw itself changes, and goes red when it does.

## The two steps, in order

1. **Temperature pass** (`--build --limit 0`): HadUK temperature for every book cell, no ERA5.
2. **ERA5 pass** (`--build`): the archive for the incomplete cells, resumable across quota windows.

## Predictions

1. After step 1, **0** records of the settled book (`ELEC_CUSTOMERS + GAS_CUSTOMERS +
   SUCCESSOR_ELEC_CUSTOMERS + ACQUIRED_CUSTOMERS` under the draw) resolve no temperature series,
   against N13's 490 of 1,046. `book_cells` snaps every premise to its nearest LAND cell and the
   store's own snap limit is 5 km, so only a premise more than 5 km from land could remain.
2. The store holds about **836 cells** after step 1 (341 + 495), all of them with temperature.
3. For the gas premises that read the normal before (N13: 227), their 2022 annual HDD from their
   own cell is **10% to 25% below** the normal's 2,086 on the mean, since 2022 was mild and the
   England & Wales normal reads high at urban cells. The earlier book-wide move was 16.4% (W1_14).
   Every one of them has a 2018 and a 2022 January HDD that differ (the world now moves).
4. Step 2 does **not** finish inside one turn: the hourly bucket stops it, and the store is left
   honest (temperature complete, ERA5 partial), with `--list` naming the remainder.
5. Every gas and weather-shaped figure in the next published run moves. I make no prediction of
   direction for the P&L; that is the run's to show, and this rebuild is not decided on it.

## Done means

The store covers the book a run settles: zero book records without a temperature series, and a
control (`tests/sim/`) asked of that book rather than the 18-point roster, which goes red when the
draw moves without a rebuild. The ERA5 remainder is landed as far as the quota allows and the rest
is handed on with its count.

**Reverse:** delete this file.
