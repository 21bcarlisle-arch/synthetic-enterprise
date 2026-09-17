**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# FINDING: the weather store validator's ERA5 leg grades every stored cell, the builder only ever fills the ones the book occupies, and 8 of the 18 it fails on can never be reached by running it

Worker seat, 2026-09-17, after landing `8a746a18f`. Found while sizing step 3 of
`SEAT_RESULT_THE_ARCHIVE_BREADTH_PULL_IS_THE_REFUSED_DESIGN..._2026-09-16.md` §6.

## 1. THE TWO POPULATIONS

`tools/validate_weather_world.check_era5_coverage` iterates `cells["cells"]` — every cell in the
store, which `_write` deliberately keeps as the **UNION** of the book and whatever the store already
held, because a departed cell's centre is recorded nowhere else.

`tools/build_weather_world.build` derives its work list from `book_cells()` alone:

```python
todo = [c for c in cells.values() if not _has_era5(held.get(c["cell_id"], []))]
```

`cells` there is today's book. So the builder can only ever fill a cell the book currently occupies.

**Measured on the real store, this turn:**

| | count |
|---|---|
| cells the validator grades (store union) | 156 |
| cells the builder would consider (today's book) | 149 |
| cells with temperature only — the leg's FAIL | 18 |
| …of those, still in today's book (reachable by `--build`) | **10** |
| …of those, no longer in the book (**unreachable**) | **8** |

## 2. WHY THIS IS A CONTROL THAT CANNOT GO GREEN

The ERA5 leg is fail-closed and reports a FAIL, which is right. But **running the producer beside it
cannot clear that FAIL**, and not because of a network failure or a bad coordinate — because 8 of the
18 cells are outside the only population the producer iterates. The leg will stay red after a
complete, successful, 25-minute pull, and the next reader will reasonably conclude the pull failed.

This is the population-mismatch class: a control and its producer answering over two different sets,
with a single number published across both. It is not the builder's union logic that is wrong —
keeping a departed cell's rows and centre is correct and deliberately commented. It is that **the two
sides were never asked to name the same population out loud.**

## 3. WHAT STEP 3 ACTUALLY COSTS, WHICH IS NOT WHAT THE ITEM SAYS

The item says "pull wind, cloud and precipitation for the 18 of 156 cells that carry temperature
only". A `--build` run today would instead:

* fill **10** of those 18, and
* additionally pull the **65 book cells the store has never held**, because they too fail
  `_has_era5` — about 22 minutes at the measured 20 s pause, on top of the ~3 minutes for the 10.

So "six minutes of pull" is the wrong estimate by roughly 4x, and the exit condition it implies —
a green ERA5 leg — is unreachable at any duration.

## 4. THE REMEDY IS A DECISION, NOT A REPAIR, WHICH IS WHY THIS IS FILED RATHER THAN FIXED

Three options, and they are genuinely different products:

1. **Grade what the builder serves.** Scope the ERA5 leg to cells in today's book, and report the
   departed-but-bare cells as a separate, named line. Honest, and it makes the leg passable.
2. **Serve what the validator grades.** Widen `todo` to the same union `_write` already uses, so a
   departed cell keeps a complete series. Costs a pull for cells no customer needs today.
3. **Say the store is book-scoped and stop keeping departed cells' rows.** Cheapest, and it
   forfeits the ability to answer for a premise the book held last week — which `_write`'s own
   comment gives as the reason the union exists.

**Option 1 is the recommendation**, because the store's purpose is to answer for the book and the
union exists as an archive rather than as a service level. But the choice decides what "complete"
means for a 7.9 MB artefact that is still not landed, so it is named here rather than picked
quietly — and picking it silently is precisely the shape this project's knowledge-first rule exists
to stop.

## 5. WHAT THIS DOES NOT CHANGE

The temperature half still re-derives bit-exactly (1,709,604 values, worst |diff| 0.0000 C, measured
this turn). Nothing here touches that, and nothing here is a reason to overwrite the store. The
producer, reader and validator are all committed as of `8a746a18f`, so this finding is checkable by
anyone from a clean checkout — which was not true of any statement about this store before today.
