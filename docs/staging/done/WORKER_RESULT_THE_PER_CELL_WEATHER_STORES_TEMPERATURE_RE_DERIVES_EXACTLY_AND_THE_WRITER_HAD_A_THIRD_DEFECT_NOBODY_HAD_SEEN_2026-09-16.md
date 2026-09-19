**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the per-cell weather store's temperature re-derives EXACTLY from committed code, the writer had a third defect nobody had seen, and the artefact still must not be landed

Worker seat, 2026-09-16. Claim `make-the-per-cell-weather-store-reproducible`.

The item directed: fix `tools/build_weather_world.py` so it can regenerate `sim/weather_world/`,
then re-derive and diff against the bytes on disk. **Both halves are done. The code is landed; the
7.9 MB artefact is deliberately not, and the reason has changed.**

## 1. THE HEADLINE: the temperature half is bit-exact

`extract_temperature` — the function that was dead code — was run over the store's own 156 cells
against the HadUK 1 km daily grids under `~/.cache/synthetic-enterprise/haduk_grid/`, and every
stored value was reconstructed as `stored_anomaly + level_c` and compared:

| field | values compared | mean difference | worst \|difference\| |
|---|---|---|---|
| `temperature_min_c` | 569,868 | +0.00000 | **0.00000** |
| `temperature_mean_c` | 569,868 | +0.00000 | **0.00000** |
| `temperature_max_c` | 569,868 | +0.00000 | **0.00000** |

**1,709,604 values, zero disagreement, zero stored cell-days the grids do not cover.** The
extractor's own docstring claim — "310 of 569,868 cell-days, 0.05%" crossed min/max — reproduced
exactly as 310. So the half of the store that was called unreproducible is not merely
reproducible; it is byte-reproducible from code that was already in the tree and had never been
called.

## 2. THE PREMISE BOTH DOCSTRINGS RESTED ON IS FALSE, AND IT IS FALSE BY COUNTING

`sim/weather_world.py` and `tools/build_weather_world.py` both said temperature came from ERA5 for
all twelve months, because:

> "HadUK-Grid has daily 1 km temperature already on this machine, but only for October-March."

`tasmin`, `tas` and `tasmax` each hold **120 monthly 1 km daily grids covering 2016-01 through
2025-12** — twelve months of every year. October–March is the window `fetch_haduk_grid` *pulls*
for the heating-season product (`HEATING_SEASON_MONTHS`); it was never a limit on what CEDA
serves. There was no shoulder-month seam to avoid, the store's own `cells.json` had named HadUK as
the temperature source since the day it was built, and two docstrings argued against the artefact
sitting beside them for eight days. Corrected in both, beside the claim rather than over it.

## 3. A THIRD DEFECT, WHICH NEITHER PRIOR NOTE SAW: the resume read a regime id as a cell id

The 09-16 seat result recorded two defects. There were three, and the third is the one that would
have destroyed the artefact:

`daily.csv.gz` is keyed by **regime** (`R00`…). `_existing_rows` read that key as a **cell id**.
So all 156 held cells read as missing, `--build` would have re-pulled every one of them over the
network, and the rewritten file would have carried regime ids and cell ids in the same column.
The tool was not merely unable to rebuild the store — running it would have corrupted it while
reporting success.

Four further things were repaired: `build` now calls `extract_temperature` (and runs it *before*
the archive pull, so an interruption leaves temperature complete and ERA5 partial rather than
leaving cells holding ERA5 temperature under a `cells.json` naming HadUK); `_write` emits
`level_c`, `decomposition` and `regimes.json`; `_has_era5` asks whether a cell has the archive
columns rather than whether it has any rows at all (under the old question every cell would read
as finished the moment the temperature pass created its rows); and `_write` keeps a cell the book
has dropped instead of deleting it, because the cell's centre is recorded nowhere else.

## 4. THE DIFF AGAINST THE BYTES ON DISK

Committed writer, fed the store's own contents, in an isolated copy:

| artefact | result |
|---|---|
| `cells.json` | **IDENTICAL, 25,134 bytes.** Every `level_c`, both source strings, all 156 entries. |
| `regimes.json` | 1 line of 162 differs — the `measured` field, changed deliberately (§5). |
| `daily.csv.gz` | 55 of 569,868 rows differ, **every one of them only in the text of a signed zero**. |

The signed zero is measured, not assumed. Re-deriving those cell-days from the HadUK grids and
differencing at 3 dp yields `0.0` where the disk holds `-0.0`: over the five months holding them,
912 of 918 values reproduced as exact text and the only 6 mismatches were the 6 signed zeros. The
producer reached the zero from below by an arithmetic route this writer does not take. `-0.0 ==
0.0` is `True` and `float()` erases the distinction before any consumer sees it, so this is a
difference in text and not in the world — but it is the whole of what stops byte-identity, so the
writer now normalises it and says which of the two forms it emits.

## 5. ONE NUMBER I REFUSED TO REPRODUCE

`regimes.json` on disk carries `"measured": "20 regimes reproduce annual space heat to 0.10% mean
/ 0.55% worst cell"`. That is a real measurement of a **20-regime generator**, and nothing in this
tree produces it — the store is the identity map, 156 regimes for 156 cells, and this build
clustered nothing. Pasting that sentence in to force a byte match would have put an unattributable
number exactly where a reader expects this build's own. The writer emits what it did instead.

## 6. THE STORE AND THE BOOK HAVE DRIFTED APART — 84 CELLS SHARED OF 149 AND 156

Not previously recorded, and it decides what `--build` would do if run today:

* the store holds **156** cells; `book_cells()` today returns **149**; **84** are in both.
* **65** cells the book occupies have never been in the store; **72** stored cells the book no
  longer occupies.
* the 84 shared cells agree on their centres **exactly** — worst disagreement 0.000000° — so the
  snap geometry is stable and the drift is entirely in the book's customer locations.

So the bytes on disk are a function of a book that no longer exists. That is not a defect in the
store; it is the reason a rebuild is a real pull and not a formality. `--list` now reports both
directions of the drift instead of printing a cell count that looks complete.

## 7. WHY THE ARTEFACT STILL IS NOT LANDED — and what changed about the reason

The 09-16 seat declined to land 7.9 MB that no committed code could regenerate. That reason is now
half spent: temperature regenerates exactly. Two reasons remain, and they are smaller and named:

1. **18 of 156 cells hold temperature only** — 65,754 rows with no wind, cloud or precipitation.
   The fabric path reads cloud cover, so those cells cannot drive it. `validate_weather_world`
   reports this as a **FAIL**, not a note.
2. **The ERA5 half cannot be re-derived offline at all.** Re-pulling 156 cells is about an hour of
   network and would compare today's archive against a pull made on another day. The validator
   says so on its face rather than implying a coverage it does not have.

**What landed instead is the machinery that makes landing the artefact a decision rather than a
gamble**: a writer that reproduces it, a validator that can refuse it, and 15 controls over both.

## 8. WHAT LANDED

* `tools/build_weather_world.py` — five repairs above; `--list` reports the book/store drift;
  `--no-temperature` for an archive-only pass.
* `tools/validate_weather_world.py` — **new, and it closes a false path**: both docstrings had
  cited this filename for eight days while nothing could run it. Five legs, each fail-closed, with
  three outcomes rather than two — a leg that *could not run* is printed as such and is never
  folded into the pass count.
* `sim/weather_world.py` — docstring corrected beside the claim.
* `tests/tools/test_the_weather_store_writer_and_reader_are_inverses.py` — 7 controls.
* `tests/tools/test_the_weather_store_validator_cannot_pass_a_skipped_leg.py` — 8 controls.

**Mutation-proven, five mutations, all fired, baseline green after each:** reader treats the
regime key as a cell id; writer omits `level_c`; `build` skips the HadUK pass; writer stores raw
instead of the anomaly; writer drops cells the book no longer holds.

**And the controls caught one of mine before it landed.** The validator's first decomposition leg
asked whether `level_c` was the mean of the reconstructed raw series. The only raw series
available inside the store is `stored + level_c`, so that compares `mean(stored) + level_c`
against `level_c` — **true for any level whatsoever**. Shifting a level 3 C left the leg green,
which is how it was found. Whether `level_c` is the right number is a question about the HadUK
grids and belongs to the re-derive leg; what the cheap leg can honestly ask is that the stored
series is centred on zero, and that is what it asks now. The test records the tautology beside the
property that replaced it.

## 9. WHAT IS STILL OWED

* **The 18 temperature-only cells** need an archive pull (~6 minutes at the measured 20 s pause).
  A live FAIL in the validator until then.
* **The 65 book cells the store has never held** need a pull of about 22 minutes before the store
  can answer for today's book.
* **`tools/pull_book_weather.py` is still on disk and still untracked** — the per-property design
  the director refused verbatim. Its deletion belongs in the commit that lands the store, which is
  the commit that has not happened yet.
