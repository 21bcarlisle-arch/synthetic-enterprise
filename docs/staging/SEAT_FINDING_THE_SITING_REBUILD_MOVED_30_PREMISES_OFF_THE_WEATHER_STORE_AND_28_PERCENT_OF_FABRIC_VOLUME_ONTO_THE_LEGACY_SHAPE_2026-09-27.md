**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# FINDING — the siting rebuild moved 30 premises off the weather store, and 28% of fabric volume went back onto the legacy shape

Measured 2026-09-27 with `tools/siting_frame_counterfactual.py`, one variable (the household frame
before and after `d9374ae9e`), same seed, same code, same store. Record:
`docs/staging/records/SEAT_PREREG_WHAT_THE_SITING_FRAME_REBUILD_MOVES_IN_THE_BOOK_2026-09-27.md`.

## What is true

- The per-cell weather store holds the cells the book occupied when it was pulled on 2026-09-17
  (`7d9eabe49`, `tools.build_weather_world.book_cells`). Nothing re-pulls it when a home's
  coordinate moves.
- The siting rebuild kept the account set identical (244 accounts) and moved 75% of homes to a
  new 1 km cell. **30 electricity premises moved 5.1–58.6 km from any stored cell.** They are now
  refused by `fabric_eligibility` and settle on the legacy PC1 shape. Fabric-driven premises fell
  from 132 to 102 of 149.
- Book fabric kWh fell **−28.3% (electricity) and −24.2% (gas)**. The 102 premises driven in both
  arms moved only **+0.31% / +0.51%**, so the siting change itself (new cell weather plus new
  output-area headcount) is a half-percent effect. The rest is who is on the fabric path.
- **Before the rebuild, 12 premises were already off-store at today's HEAD**, so the store had
  drifted from the book before this commit.

## Why it matters

The refusal is honest. It carries its reason into the run's own record, as `fabric_demand_path`
intends. But no control asks whether the settled book is still covered by the store it was pulled
for. So a world change made for a fidelity reason (siting) silently undid a large part of a
different one (fabric-driven settlement), and any comparison across `d9374ae9e` that reads the
book is two variables.

## Remedy (the next item, not done here)

1. Bring the store up to the book again: `python3 -m tools.build_weather_world --list`, then
   `--build`. This pulls the newly occupied cells from the public ERA5/HadUK sources. It spends
   nothing, and the last 23 cells took eleven minutes.
2. One-leg control: every domestic, non-HH electricity premise in the live book resolves to a
   COMPLETE stored cell. It is keyed to the property, not to today's count. It is red today with
   42 names and must be shown able to go green after step 1.
