**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the code that makes the weather store reproducible was never in a commit, and the control written to catch exactly that claim was blind to a numbered heading

Worker seat, 2026-09-17. Claim `make-the-per-cell-weather-store-reproducible-then-wire-it`.

The item directed steps 1–4 of §6 of
`SEAT_RESULT_THE_ARCHIVE_BREADTH_PULL_IS_THE_REFUSED_DESIGN_AND_ITS_PER_CELL_SUCCESSOR_CANNOT_BE_REPRODUCED_2026-09-16.md`.
**Steps 1 and 2 were already done on disk by a prior worker and had reached no ref at all.** What
this turn did is establish that, re-measure the result first-hand rather than believe it, land it,
and repair the control that let the false landing claim stand.

## 1. THE PREMISE THE ITEM RESTED ON IS SPENT, AND NOT THE WAY THE ITEM THOUGHT

The item told me to fix `_write()` to emit `level_c`, `decomposition` and `regimes.json`, and to
answer where the store's summer temperature came from "since HadUK daily is October–March only".

All of that was already done, in the working tree, unlanded. `docs/staging/WORKER_RESULT_THE_PER_
CELL_WEATHER_STORES_TEMPERATURE_RE_DERIVES_EXACTLY_AND_THE_WRITER_HAD_A_THIRD_DEFECT_NOBODY_HAD_
SEEN_2026-09-16.md` records the work and says, in §8 under the heading `## 8. WHAT LANDED`, that
five files landed. **None of the five was in any commit on any ref:**

```
git log --all --oneline -- tools/build_weather_world.py       -> (empty)
git log --all --oneline -- tools/validate_weather_world.py    -> (empty)
git log --all --oneline -- sim/weather_world.py               -> (empty)
git log --all --oneline -- tests/tools/test_the_weather_store_writer_and_reader_are_inverses.py
                                                              -> (empty)
git log --all --oneline -- tests/tools/test_the_weather_store_validator_cannot_pass_a_skipped_leg.py
                                                              -> (empty)
```

`git log --all -S validate_weather_world` returns three commits and every one of them is a staging
**document** naming the filename in prose. The code itself had reached no branch, no fork, nothing.
This is the same shape as
`WORKER_RESULT_THE_RUN_OUTPUT_RESOLVER_WAS_AUTHORED_TESTED_AND_SALVAGED_TO_NO_BRANCH_AND_THE_DOC_
SAYING_IT_LANDED_WAS_UNTRACKED_2026-09-16.md` — authored, tested, correct, and invisible to git.

**So the item's own framing was right for a reason it did not name.** "No committed code regenerates
it" was true. The cause was not that the code was unwritten; it was that the code was unlanded, and
a document asserting otherwise is what stopped anyone looking.

## 2. THE OPEN QUESTION IS ANSWERED, AND BY COUNTING

The item repeated the premise that HadUK daily is October–March only. **It is false of this machine.**
Under `~/.cache/synthetic-enterprise/haduk_grid/`:

| variable | monthly 1 km daily grids in 2016-01..2025-12 | months covered |
|---|---|---|
| `tasmin` | 120 | all twelve |
| `tas` | 120 (of 270 on disk; the rest are 1991–2015) | all twelve |
| `tasmax` | 120 | all twelve |

120 = 10 years × 12 months. October–March is what `fetch_haduk_grid.HEATING_SEASON_MONTHS` *pulls*
for the heating-season product; it was never a limit on what CEDA serves or on what is here. There
is no shoulder-month seam, so the store's `cells.json` naming HadUK as the temperature source for
all twelve months is coherent. The prior worker had already corrected both docstrings beside the
claim; I re-counted rather than take the correction's word.

## 3. STEP 2'S EXIT CONDITION, MEASURED FIRST-HAND

I ran `tools/validate_weather_world.py` against the real 7.9 MB store — 360 monthly grids, 240
seconds. It never writes the store.

```
PASS  the three artefacts agree: 156 cells, 156 regimes, 569868 rows, every key known to all three
PASS  every regime spans the window: 156 regime(s) x 3653 days, 2016-01-01..2025-12-31, no gaps
PASS  the stored temperature is an anomaly: 156 cell(s) centred on zero, worst |mean| 0.00000 C
FAIL  every cell carries the ERA5 columns: 18 of 156 cell(s) hold temperature only -- 65754 rows
PASS  temperature re-derives from HadUK: 1709604 value(s) compared, 100.0000% within 0.001 C,
      worst |diff| 0.0000 C
4 passed, 1 failed, 0 could not run
```

**1,709,604 values, worst disagreement 0.0000 C.** The prior worker's headline reproduces exactly.
The extractor's own docstring figure — 310 crossed min/max cell-days — reproduced as 310. The
store's temperature half is byte-reproducible from code that is now committed.

The single FAIL is step 3's subject and it is a live refusal, not a note.

## 4. THE CONTROL WRITTEN FOR THIS DEFECT COULD NOT SEE IT

`tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py` exists precisely so a
record cannot say an artefact landed while it is in no commit. Its docstring names the 2026-09-01
instance it was written for. **It was green on this one**, and the reason is one character class:

```python
_HEADING = re.compile(r"^(#+)\s*What landed\b.*$", re.IGNORECASE | re.MULTILINE)
```

`\s*` permits only whitespace between the hashes and the phrase. The offending heading is
`## 8. WHAT LANDED`. The section number is not whitespace, so the heading did not match, the
document returned "makes no landing claim", and all five false claims went ungraded.

**This is not a one-off typo — it is the house style.** Re-asking all 128 records in
`docs/staging/` under a pattern that allows an optional `\d+[.)]`:

* **106** records match the current pattern.
* **22** records head the section with a number and are invisible today.
* Re-grading all 128 under the widened pattern fires on **exactly one**: the 09-16 worker result
  above, naming exactly the five files. **The other 21 told the truth.**

So the widening buys one real defect and no noise, and the defect it buys is the one that cost this
turn its first hour.

**The direction of the change is why it is safe.** It enlarges the population the control grades
rather than adding an exception to it; a narrowing here could only ever hide a claim.

**Mutation-proven, and the proof is keyed to the grammar rather than to today's offender.**
`test_MUTATION_a_NUMBERED_landed_heading_is_graded_like_an_unnumbered_one` asks a synthetic record
with a known-absent path under four heading forms (`## 8. WHAT LANDED`, `## 3. What landed`,
`## 1) What landed anyway`, `## What landed`) and asserts a committed path under a numbered heading
still passes. Narrowing the regex back to `\s*` turns it red. It is deliberately *not* keyed to the
live document: the commit below lands those five files, so a control pinned to that record would go
green because the tree got more honest and could never fire again.

## 5. What landed

* `sim/weather_world.py` — the per-cell store's reader, and the file holding the director's verbatim
  refusal of the per-property pull. Previously untracked.
* `tools/build_weather_world.py` — the writer that re-derives the store. Previously untracked.
* `tools/validate_weather_world.py` — the five-leg validator, three outcomes per leg, a leg that
  could not run is never folded into the pass count. Previously untracked, and cited by both
  modules' docstrings for eight days before it was written.
* `tests/tools/test_the_weather_store_writer_and_reader_are_inverses.py` — 7 controls.
* `tests/tools/test_the_weather_store_validator_cannot_pass_a_skipped_leg.py` — 8 controls.
* `tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py` — the heading
  widening and its mutation proof.

15 of the 15 weather-store controls pass. `python3 -m ruff check` is clean on all six files. The
ruff ratchet reads I001 1308 in a clean extract of the resulting tree and is green; the shared
working tree reads 1307, and that −1 is another lane's uncommitted import fix, which the baseline's
own history records happening five times before.

## 6. WHAT IS STILL OWED, AND WHAT IT IS WORTH

The 7.9 MB artefact is **still not landed**, and one of the two reasons named on 09-16 is now spent
(temperature regenerates exactly, measured above). What remains:

1. **The 18 temperature-only cells** — 65,754 rows with no wind, cloud or precipitation. The fabric
   path reads cloud cover, so these cells cannot drive it. ~6 minutes of pull at the measured 20 s
   pause. This is step 3 and it is the next move.
2. **The ERA5 half cannot be re-derived offline at all.** Re-pulling 156 cells is about an hour and
   would compare today's archive against a pull made on another day. The validator says so on its
   face rather than implying a coverage it does not have.
3. **The store and the book have drifted apart** — 156 stored cells, 149 the book occupies today, 84
   shared. The bytes on disk are a function of a book that no longer exists, which is why a rebuild
   is a real pull and not a formality. `--list` reports both directions.
4. **Step 4 (wiring `sim/weather_world.py` into `simulation/weather_inputs.py`) is not started**, and
   it should not be until 1 and 3 are settled: wiring a store that answers for 84 of the book's 149
   cells would publish a demand shape whose coverage nobody stated.
5. **`tools/pull_book_weather.py` is still untracked on disk** — the per-property design the director
   refused verbatim. It is *not* deleted here: deleting an untracked file is the one genuinely
   irreversible move available in this tree, and `build_weather_world`'s docstring already says
   plainly that the supersession describes an intention rather than a commit. That paragraph stays
   true after this landing.

**Why this landing matters more than its size.** The item's own reasoning is that per-customer demand
inference reaches 4 of 210 settled customers, and this store is the only thing in the tree that moves
that by an order of magnitude. The blocker was never the store's quality — it was that the code
regenerating it existed only on one disk. That is now false, and step 3 is six minutes of pull away
from clearing the validator's one FAIL.
