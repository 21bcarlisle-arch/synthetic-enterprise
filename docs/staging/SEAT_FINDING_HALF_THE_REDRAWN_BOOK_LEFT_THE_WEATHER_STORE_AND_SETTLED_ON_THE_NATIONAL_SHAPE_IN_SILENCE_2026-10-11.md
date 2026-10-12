**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# Half the redrawn book is off the weather store, and that is what the "pinned providers" are

**Fate (2026-10-12, clear-the-decks):** ATOM -- weather store extension for the 496 missing cells is still incomplete: tests/simulation/test_every_settling_domestic_premise_reads_a_complete_stored_cell.py is still a strict xfail at HEAD (P2)

Claim `world-household-consumption-is-too-steady-year-on-year`. Pre-registration, landed before
the store was touched:
`docs/staging/records/SEAT_PREREG_HOW_MUCH_OF_THE_YEAR_ON_YEAR_GAP_IS_THE_WEATHER_STORE_NOT_REACHING_THE_BOOK_2026-10-11.md`.

## What was found

The forecasts finding (`SEAT_FINDING_THE_COMPANY_HOLDS_SIX_CONSUMPTION_FORECASTS_..._2026-10-11.md` §3)
called `legacy_pc1_rescaled` and `population_70_30_split` the world's "pinned providers", with
0.01% and 0.00% median year-on-year change, about half the book. **They are not a modelling
choice. They are a coverage hole.**

- In the graded run (`7379375f6`), **278 of the 280** `legacy_pc1_rescaled` electricity premises
  are legacy because `fabric_eligibility` refused them `no weather archive for this customer's
  location`. The other two are non-domestic. 282 premises carry that refusal in all.
- `python3 -m tools.build_weather_world --list` at `018da11e2`: **600 cells the book occupies,
  496 of them never held by the store.** The store was completed for the earlier book
  (`f0ba399a4`, "every book cell"); the book was redrawn after it and nothing re-extended it.
- A gas premise with no cell reads the 1991–2020 monthly HDD normal
  (`sim.weather_hdd.hdd_reading`, `from_normal=True`), which is the same number in 2018 and 2022:
  131 of 290 gas premises at HEAD. That is the 0.00% and the 0.43% p90 (the leap day).
- **It was not silent, and I said it was in my first draft.** `tests/simulation/test_every_settling_domestic_premise_reads_a_complete_stored_cell.py`
  asks exactly this of the whole book. It has been a strict `xfail` since 2026-10-07 with 86 names
  and 164 missing cells, because the ERA5 pull outruns Open-Meteo's daily quota
  (`SEAT_FINDING_THE_TERM_LOOPS_MEMORY_THAT_SCALES_WITH_ACCOUNTS_IN_THE_BOOK_2026-10-07.md`). The
  hole has since grown to 282 refused premises and 496 missing cells. What nobody had connected is
  that this parked hole IS the forecasts finding's "pinned half of the book": the year-on-year
  steadiness the forecasts finding measured is mostly this, not a property of any demand model.

So W1_14's L2 sentence, "every premise the run settles reads its own cell", was true of the book
it was measured on (seed 20260724, 250 premises) and is false of the book the run now settles. The
map row already says the store covers one draw; the draw changed.

## Severity

LATENT, not BLOCKING: the limitation is recorded and accepted by the strict `xfail` above. It does
make every figure that rests on weather response, year-on-year change or the fabric/legacy split
a reading of a half-weathered book, and the forecasts finding's level ranking with it.

## Being repaired

`tools/build_weather_world --build` is extending the store to the book's cells (HadUK temperature
from the local grids, done; ERA5 wind/cloud/precipitation from Open-Meteo, one cell at a time,
stopping on the daily quota). Log: `/var/tmp/se-weather-pull.log`, worktree
`/var/tmp/se-weather-pull` (locked). When the store reports every book cell complete it lands
with the strict `xfail` removed, so the existing control reds on the next uncovered cell, and the run is re-graded against the
pre-registration.

## What this does NOT close

Extending the store moves those premises onto providers that already vary with weather. The
fabric premises vary 0.5% (electricity) and 2.9% (gas) a year against NEED's 14.7%. The remaining
gap is **household change** (occupancy, behaviour) and **the 2022 price response**, and neither is
sized by any published evidence the knowledge layer holds net of change of occupier and EAC/AA
artefacts. Both are GAPs; no world term is written for them by this claim.
