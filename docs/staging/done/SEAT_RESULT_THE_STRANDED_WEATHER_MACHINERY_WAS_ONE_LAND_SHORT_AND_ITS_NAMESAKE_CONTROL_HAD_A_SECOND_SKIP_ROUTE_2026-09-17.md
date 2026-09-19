**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the weather machinery was one `surgical_land` short of existing, and the control named for a fail-open had a second route to it

Delivery seat, 2026-09-17. Claim `make-the-per-cell-weather-store-reproducible`.
Pre-registration: `SEAT_PREREGISTRATION_THE_STRANDED_WEATHER_MACHINERY_2026-09-17.md`, written
before anything below was run.

## 1. THE DRAWN ITEM'S PREMISE WAS TRUE AND STALE BY ONE NIGHT

The item said: fix `tools/build_weather_world.py` so it can regenerate `sim/weather_world/`, because
`build()` never calls `extract_temperature`, `_write()` emits neither `level_c` nor `decomposition`
nor `regimes.json`, and the two docstrings disagree on whether temperature is HadUK or ERA5.

**All three were repaired at 23:35 and 23:38 on 2026-09-16 and none of it had landed.** A worker
lane did the work, did it well, filed
`WORKER_RESULT_THE_PER_CELL_WEATHER_STORES_TEMPERATURE_RE_DERIVES_EXACTLY_...` with a section headed
**"WHAT LANDED"**, and never committed. Reachable from no ref:

    git ls-tree -r HEAD        -- tools/build_weather_world.py sim/weather_world.py  -> empty
    git ls-tree -r origin/main --                (same paths)                        -> empty
    git log --all              --                (same paths)                        -> empty
    git rev-parse HEAD origin/main -> 761daca4c8286d598bb2dcb5eac6da90c377056e (both)

HEAD == origin/main, so this was not the behind-origin illusion. Nine paths were stranded: five
staged-added, one modified in place, three untracked — including the RESULT document asserting they
had landed.

**So the item, drawn from the state of the tree, correctly described a defect whose repair was
already sitting on the disk.** The measurement half was finished; the landing half had never been
begun. Re-deriving it would have been the waste the item's own closing paragraph warns about, so
this turn is the landing, plus the one thing the landing found.

## 2. THE FIVE MUTATIONS RE-RUN, AND THE SIXTH THAT DID NOT FIRE

The stranded finding claims "Mutation-proven, five mutations, all fired". Every factual claim a
drawn or inherited document makes is an un-re-asked prediction, so I re-ran them rather than reading
them. Five of six fired, cleanly attributed to the control that names each defect:

| mutation | control that caught it | fired |
|---|---|---|
| `_existing_rows` reads the regime key as a cell id | reader-hands-back / departed-cell | **yes** (2 red) |
| `build` lets the ERA5 archive win temperature | build-takes-temperature-from-HadUK | **yes** |
| `_write` skips the decomposition (`level_c = 0`) | decomposition leg + writer-output | **yes** (5 red) |
| series keyed by cell id instead of regime | agreement / coverage / window legs | **yes** (7 red) |
| `_has_era5` asks "any rows at all" | temperature-only-cell control | **yes** (2 red) |
| **skipped leg minted as a pass** | *nothing* | **NO — 15 passed** |

## 3. THE DEFECT: A SKIP ARRIVES TWO WAYS AND ONE WAS NEVER ASKED ABOUT

`tests/tools/test_the_weather_store_validator_cannot_pass_a_skipped_leg.py` is named for one
property: a leg that could not run is never counted as a pass. Its own docstring calls that "the
fail-open this module exists to prevent". **The mutation**

    Leg("temperature re-derives from HadUK", None, "not asked for")
 -> Leg("temperature re-derives from HadUK", True, "not asked for")

**passed all 15 controls in that file and its siblings.** Under it the validator prints
`5 passed, 0 failed, 0 could not run` for a store whose most expensive leg never executed.

The cause is a partition with a hole, not a weak assertion. A skip arrives by two routes:

1. **the HadUK cache is absent** — `check_temperature_reproduces` returns a `None` leg. Two controls
   guard this, and they are good ones.
2. **`--no-temperature` was passed** — `validate` constructs `Leg(..., None, "not asked for")`
   itself and the checker is never called. **Nothing asserted over this route at all.**

Route 2 is not the exotic one. The re-derive opens 360 monthly 1 km grids out of a 39 GB cache and
takes minutes, and `--no-temperature` exists precisely so a cheap pass can skip it — so it is the
mode a gate, a cron or a pre-commit hook reaches for, and it is the mode with no control over it.
The two existing tests route around the mutated line completely: `--no-temperature` is exercised
only for its exit code being `0`, which is the same whether the leg is honestly `None` or
dishonestly `True`, and `--require-temperature` reaches the skip by route 1.

**This is the R15 shape where a control is asked over one of two routes to its property and the
untested route is the one production takes.** It is also the second tautology found in this one
module: the stranded finding records the first (a decomposition leg that reconstructed its input
from its own output, so `mean(stored) + level_c == level_c` held for every level).

### The repair, keyed to the property and not to today's answer

A 16th control, `test_a_leg_NOT_ASKED_FOR_is_never_counted_as_a_pass_either`, asks route 2 directly:
the leg must read `None`, must mark `COULD NOT RUN`, and must not appear among the passes. And one
line added to the exit-code control — `main(["--no-temperature", "--require-temperature"]) == 2` —
because a skip is a skip however it arose, and requiring a leg you also declined to run is a
refusal. **Both new assertions go red under the mutation and green at baseline** (16 passed, then 2
failed / 14 passed, then 16 passed on restore).

## 4. THE STORE, MEASURED

`validate_weather_world` against the 7.9 MB artefact on disk, cheap legs:

```
PASS  the three artefacts agree: 156 cells, 156 regimes, 569868 rows, every key known to all three
PASS  every regime spans the window: 156 regime(s) x 3653 days, 2016-01-01..2025-12-31, no gaps
PASS  the stored temperature is an anomaly: 156 cell(s) centred on zero, worst |mean| 0.00000 C
FAIL  every cell carries the ERA5 columns: 18 of 156 cell(s) hold temperature only -- 65754 rows
      with no wind, cloud or precipitation
```

Prediction 5 confirmed: the FAIL is real and it is the correct answer, not a defect in the
validator. The full HadUK re-derive was launched and is reported in §6.

## 5. WHAT LANDED

The machinery, which is what makes landing the artefact later a decision rather than a gamble:
`tools/build_weather_world.py`, `tools/validate_weather_world.py`, `sim/weather_world.py`,
`tests/tools/test_the_weather_store_writer_and_reader_are_inverses.py`,
`tests/tools/test_the_weather_store_validator_cannot_pass_a_skipped_leg.py` (now 16 controls), and
`tools/weather_cell_drivers.py`, whose one-line `longitude` addition is load-bearing —
`book_cells()` reads `grid["longitude"]` and the book's locations are WGS84 while `east`/`north`
are OSGB, so without it the writer cannot run at all.

## 5b. WHAT I REFUSED TO LAND, each for a named reason

*Paths in this section are deliberately written without backticks. `landed_manifest_check` treats
every backticked path between a "what landed" heading and the next heading as a claim that the path
landed, and it refused this commit once for exactly that — a refused path named inside the manifest
section reads as a landed one. The refusal was right and the prose was wrong.*

* **sim/weather_world/ (7.9 MB).** The item's own WHY forbids it and two reasons survive the
  bit-exact temperature result: 18 of 156 cells carry no cloud cover, so the fabric path cannot
  read them and the validator reports a live FAIL; and the ERA5 half cannot be re-derived offline
  at all — re-pulling 156 cells is about an hour of network and would compare today's archive
  against a pull made on another day. A reproducible half does not buy an unreproducible whole.
* **tools/pull\_book\_weather.py.** This is the per-property design the director refused verbatim,
  quoted in sim/weather\_world.py: *"The world exists, and a property reads its conditions from
  it... Two households in the same cell must experience identical weather."* Its own docstring
  says it pulls for "the 135 coordinates the book actually sits on" — per book location, which is
  per property. **It is still on the shared tree's disk, untracked, and it must never be landed.**
  That it survives there is the live hazard: nothing in the tree can refuse a file no ref has seen.
* **A 59-line deletion in the 09-16 SEAT\_RESULT on the accept branch.** The
  shared tree's working copy is *shorter* than HEAD — it lacks a section HEAD carries, so it is a
  stale copy and not holder work, and carrying it would have reverted landed prose. Reset to HEAD.

## 6. WHAT IS STILL OWED

* **The full HadUK re-derive.** Launched in this turn against the real 39 GB cache to test the
  stranded finding's headline claim — 1,709,604 values, zero disagreement. It had not returned when
  this turn ended, so **I am not repeating that claim as confirmed.** It is the stranded lane's
  measurement, not mine, and the next lane should re-run `python3 -m tools.validate_weather_world`
  and record the answer here either way. A prediction filed after the answer is not a prediction,
  and a claim inherited without re-running is not a measurement.
* **18 temperature-only cells** need an archive pull (~6 min at the measured 20 s pause); **65 book
  cells the store never held** need ~22 min. Until then the store answers for a book that no longer
  exists — 156 stored against 149 in the book today, 84 shared.
* **tools/pull\_book\_weather.py needs deleting from the shared disk**, by a lane that can write it.

## 7. THE GENERALISABLE ONE

A RESULT document's section headed **WHAT LANDED** is the single least-re-checked claim surface in
this project, because it is written in the past tense by the author of the work and it reads as a
receipt. This one was false for a night while the repair it described sat staged, and the item that
sent me here was generated from the tree the repair had not reached — so the queue correctly
reported a defect that was already fixed, and would have kept doing so. **`surgical_land` is not the
last step of the work; it is the step that makes the work exist.** Everything before it is a
description of a tree nobody else has.
