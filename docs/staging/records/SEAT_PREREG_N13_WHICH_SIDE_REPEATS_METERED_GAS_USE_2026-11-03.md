**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** none — N13, sixth cold read

# Pre-registration: which side repeats last year's metered gas use, the world or the bill (2026-11-03)

**Written before any measurement.** The finding is
`docs/staging/SEAT_FINDING_THE_SIXTH_COLD_READ_FINDS_METERED_GAS_USE_REPEATING_LAST_YEARS_MONTH_TO_THE_DECIMAL_ON_A_THIRD_OF_GAS_LEGS_2026-11-03.md`.
The book is the one published at 85b044be54, run `run_output_08f267b666_20261102T173915Z.json`.

## What I have read so far (code, no numbers)

- `simulation/run_phase2b.py` makes one `adopt_book(ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS)`
  call, before the loop. `sim.weather_hdd` resolves a gas premise's sky from a bare id through that
  book. An id the book does not hold reads the 1991–2020 monthly normal. That normal is the same
  number in every year.
- B7's incoming occupant (`OCC-*`) is admitted inside the loop, after that call.

## Predictions

1. **World side (explanation 1).** For OCC-098fe5fa8b46g, the settled monthly gas demand repeats
   year on year to 0.1 kWh, as the bill does. The bill is faithful to a flat world, and nothing
   relabels an estimate as actual.
2. That leg's sky is a climate normal (`from_normal` true), because its id is not in `_BOOK` when
   `get_hdd` first resolves it.
3. **Book-wide.** A repeating gas leg is a leg whose id was not adopted, and the split is close to
   perfect: at least 90% of the 114 repeating legs are unadopted, and at least 90% of adopted legs do
   not repeat.
4. The 114 legs include `SYN`/`PROS` ids as well as `OCC` ids. So "not adopted" covers more than
   occupiers, probably households admitted mid-run (trickle or acquired cohorts). I do not know their
   share, and I predict nothing about it.

**What would refute this.** The world's demand moves with the weather while the bill repeats. That
is explanation 2, on the company side. A mixed split would mean both explanations hold on different
legs.

**Reverse:** delete this file.
