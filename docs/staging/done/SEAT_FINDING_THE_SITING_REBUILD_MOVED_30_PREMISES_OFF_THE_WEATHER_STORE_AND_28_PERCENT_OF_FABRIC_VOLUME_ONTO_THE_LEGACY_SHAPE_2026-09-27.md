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

## Remedy, 2026-09-27 evening — step 2 landed, step 1 stopped on the quota

- **Control landed:** `tests/simulation/test_every_settling_domestic_premise_reads_a_complete_stored_cell.py`
  reuses the runner's own predicate (`fabric_eligibility` + `WeatherWorldSource.available`),
  with no trace generation, in about 9 s. It was red at HEAD with **42 names**, as predicted. It
  lands as `xfail(strict=True)`: the commit that completes the store turns it XPASS→red, and that
  commit must delete the marker. A second test proves the refusal branch can fire, by withdrawing
  one fabric-driven premise's cell.
- **Pull:** `--build` took HadUK temperature for all 118 new cells (339 held), then ERA5 for 8.
  At cell 9 Open-Meteo returned the **DAILY** 429 (resets at UTC midnight). 110 cells are still owed.
- **NEW, and it matters more than the quota: a half-built store is WORSE than the old one.**
  With that partial store on disk the control read **100** off-store, not 42, and all 100 resolved
  to a real cell id. The HadUK pass writes every new cell temperature-only. A premise then snaps to
  its OWN incomplete cell rather than a complete neighbour within 5 km, and is refused. So an
  interrupted build moves about 58 more premises onto the legacy shape. The builder's "temperature
  first keeps the store honest if interrupted" is true of the STORE and false of the BOOK.
- **So nothing was landed from the pull.** The partial store (8 ERA5 cells plus 118 temperature-only)
  is preserved at `/var/tmp/weather_store_partial_2026-09-27/`. The shared tree's copy was put back
  to HEAD bytes, so no run reads the degraded store.
- **To finish:** after 00:00 UTC, copy those three files back into `sim/weather_world/`, re-run
  `python3 -m tools.build_weather_world --build` (it resumes: only the ERA5-less cells are pulled),
  repeat on each quota reset until it says no cell is still needing the archive, then land the three
  store files together with the removal of the xfail marker. Never land a store the control does not pass.
- **Owed, separately:** the builder should not store a book cell until it is complete, or the
  reader should snap to the nearest COMPLETE cell. Either would make an interruption harmless. Which
  one is right is a design call, and it is not made here.

## Remedy, 2026-09-28 01:19–02:25 BST — 63 more cells, 47 still owed, nothing landed

- Resumed in an ISOLATED worktree (`/var/tmp/wx-store-2026-09-28`, detached at 51d7add67), not the
  shared tree, so no run read the partial store at any point.
- **The quota has two limits, not one.** The first pass stopped at cell 33/110 on the HOURLY bucket.
  After the hour reset, it stopped at 31/78 on the DAILY one. So about 63 ten-year cells a day, and
  about 32 an hour. The builder's own stop message named both limits correctly.
- The store now holds 284/339 cells with ERA5. Of the 55 temperature-only cells, 8 are outside the book,
  so **47 book cells are owed**. Progress is saved back to `/var/tmp/weather_store_partial_2026-09-27/`.
- The control (`--runxfail`, in the worktree) reads **44** off-store on this partial store, against
  42 at HEAD. It is still worse than HEAD, so it is still not landable, and the shared copy is untouched.
- **Armed:** `weather-store-resume-0929.timer` (user, transient) fires 2026-09-29 00:05 UTC. It runs
  `~/.cache/synthetic-enterprise/weather_store_resume_2026-09-29.sh`, which resumes the pull in
  that worktree and waits out one hourly reset if it needs to. It then runs the control and hands off
  `land-the-completed-weather-store` on a pass, or `weather-store-pull-still-incomplete` on a fail.
  It lands nothing itself. The timer is used because a continuation written now would expire (6 h) before the reset.
  Reverse it with `systemctl --user stop weather-store-resume-0929.timer`.
