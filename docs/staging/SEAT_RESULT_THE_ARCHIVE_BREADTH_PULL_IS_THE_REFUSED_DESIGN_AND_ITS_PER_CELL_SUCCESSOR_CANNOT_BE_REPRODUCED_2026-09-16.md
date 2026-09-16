**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the archive-breadth pull is the design the director refused, its per-cell successor cannot be reproduced by any tool in this tree, and the cheap lever landed

Delivery seat, 2026-09-16, in an isolated worktree at `ed66a8e2e`. Claim
`widen-the-weather-archive-beyond-c1-c4`.

The item directed a pull and named a second, cheaper lever. **The pull is refused; the second lever
is landed.** The reason is not a judgement call — it is written down in the very file the item told
me to read first.

## 1. PREMISE: holds, and it was the precondition rather than the work

`1bf4821b6` and `b702a097e` are both ancestors of `origin/main`. That is what the item predicted and
it is what discharges the *precondition*. It does not spend the work: `sim/weather_data/` still holds
**exactly four CSVs** (C1–C4, 3,446 days each), so archive breadth is untouched and the item is live.

## 2. THE PULL THE ITEM DIRECTED IS THE DESIGN THE DIRECTOR ALREADY REFUSED

`tools/pull_book_weather.py` pulls **one archive per property**, naming each file after a customer.
`sim/weather_world.py` — stranded beside it, in the same untracked set the item told me to read
first — quotes the refusal verbatim:

> "The world exists, and a property reads its conditions from it. It doesn't call out to a data
> source when someone wants to bill it. The weather happened; everyone in that place experienced the
> same weather... Two households in the same cell must experience identical weather — that's what
> makes the difference in their demand attributable to fabric and people rather than to two separate
> downloads."

So the stranded set is not one week of work on one problem. It is a **refused design and its
successor, stranded together**, and the item's "READ FIRST, DO NOT REWRITE" was the right
instruction for the wrong reason: reading it is what stops the pull, not what starts it.

**The refusal reproduces itself at real inputs, which is how I checked it rather than taking the
quote's word.** Of the 18 registered supply points, 4 refuse for archive breadth — and those 4
archive ids sit at only **2 distinct coordinates**:

| archive id the resolver picks | coordinate | accounts |
|---|---|---|
| `C_IC1` | (52.4862, -1.8904) | 1 |
| `C_IC2` | (52.4862, -1.8904) | 1 |
| `C_IC3` | (54.5973, -1.1049) | 1 |
| `C_IC3g` | (54.5973, -1.1049) | 1 |

Four pulls, two skies. `pull_book_weather` would have downloaded Birmingham twice and Teesside
twice, and any difference between the two Birmingham series would then be indistinguishable from a
difference in fabric or people. That is the director's sentence, measured, on this book, today.

## 3. THE PER-CELL SUCCESSOR IS RIGHT IN DESIGN AND ITS ARTEFACT CANNOT BE REPRODUCED

`sim/weather_world/` is no longer the empty directory `build_weather_world.py`'s own docstring
records (that self-correction was written 2026-09-08; the store was built 09-09). What is on disk is
**better than the docstring claims and not reproducible by the code beside it**:

* 156 cells, 156 regimes, **one-to-one** — so the regime layer is the identity map, which is what
  REPLAYED weather should be, and no cell's daily wiggle is shared with another's. It is measurement,
  not synthesis. I checked this because "per-cell LEVEL + shared regime ANOMALY" reads exactly like
  the fabrication the director refused, and it is not.
* 569,868 rows = 156 × 3,653 days, the full 2016-01-01..2025-12-31 window, **no missing temperature
  day**. `R00`'s stored annual mean is `-0.0003` and its January/August means are `-4.37`/`+4.98`, so
  the stored series is a true anomaly about the cell's own `level_c` with the seasonal cycle intact.

Three defects, each measured:

1. **`build()` NEVER CALLS `extract_temperature`.** The HadUK per-cell daily extractor is defined and
   is dead code. `build()` calls `get_daily_weather` (ERA5) only.
2. **`_write()` EMITS NEITHER `level_c`, NOR `decomposition`, NOR `regimes.json`** — yet all three
   are on disk. It also writes `"source": "ERA5 / ERA5-Land via Open-Meteo archive, per CELL
   CENTRE"`, while the on-disk `cells.json` says `"temperature: HadUK-Grid 1 km daily (CEDA)"`.
   **The store on disk was not written by the tool in this tree, and re-running that tool would
   overwrite it with a different and worse artefact.**
3. **18 of the 156 cells carry temperature only** — wind, cloud and precipitation are empty on all
   3,653 of their days (65,754 rows). The fabric path reads cloud cover, so those 18 cells cannot
   drive it even once the store is wired.

This is the same class as the 09-07 weather-cell artefact that sat "unreproducible for nine days",
which `simulation/weather_cell_siting.py` already devotes three paragraphs to. **Landing 7.9 MB of
artefact that no committed code can regenerate would be re-buying that defect at a larger size**, so
I did not land it. Nothing here is deleted; it stays exactly as found.

## 4. WHAT LANDED: the refusal now names the site, so the pull is targetable

The item's second lever, and it is the one that survives the first being refused.

`fabric_eligibility` received a bare `weather_available: bool` and emitted one identical sentence —
`"no weather archive for this customer's location"` — for **every** refused premise. 213 occurrences
in the settling book, naming 213 nothings. No test pinned that string, which is why it could stay
uninformative for as long as it did.

It now names the archive id it resolved to and the coordinate a pull would be aimed at:

```
no weather archive for this customer's location: resolved to 'C_IC1' at (52.4862, -1.8904),
and sim/weather_data/C_IC1.csv does not exist -- pull that coordinate
```

**The refusal SPLITS, because the two populations need opposite things.** A premise with a real
coordinate is cleared by a pull. A premise carrying `lat: None` is cleared only by a coordinate at
the draw, and telling that reader to "pull that coordinate" would send them to fetch a location
nobody has — so it gets its own sentence saying **no pull can clear this one**. The class split is
the point; a single sentence covering both is the defect being repaired.

`NO_ARCHIVE_REFUSAL` is kept as the leading phrase so the book's coverage grouping still reads, and
`COVERAGE_REFUSAL` (a different refusal — the archive not spanning the window) is untouched.

**Two controls, both mutation-proven.** Reverting the refusal to the single identical sentence turns
both red:

* `test_two_uncovered_premises_do_not_receive_the_same_archive_refusal` — asked of `reason` **alone**
  and not of the verdict, because `customer_id` already differs between any two premises and a
  distinguishability control asked over the union of the fields passes with the defect fully in place
  (R15).
* `test_a_premise_with_no_coordinate_is_not_told_to_pull_an_archive` — holds the split open, so it
  cannot be collapsed back into one sentence without a red.

68 passed in `tests/simulation/test_fabric_demand_path.py`; 2 failed under the mutant.

## 5. WHAT I DID NOT ESTABLISH

* **Whether the 213 figure is still 213.** It is the item's number, over the drawn population, and
  the draw behind it is the same unreproducible `run_output_f4b0b6334_*` draw
  `weather_cell_siting.py` already refuses to re-state. I measured the **registered book** (18 points,
  4 refusals, 2 coordinates) because that population can be re-drawn. Re-stating 213 against a draw I
  cannot reproduce would be inventing a population and reporting it as the old one.
* **Where the on-disk store's summer temperature actually came from.** HadUK daily is October–March
  only, the store is complete for all twelve months, and the producer is not in the tree — so the
  question is open and is the first thing the successor must answer. It is not answered by either
  docstring, and the two docstrings disagree with each other.
* **Whether `tools/validate_weather_world.py` was ever written.** It does not exist; both modules
  cite it as the control that measures the store's resolution against HadUK. A path in a prose
  comment is a reachability edge, so this is still a citation of a validator nothing can run.

## 6. THE NEXT MOVE, NAMED

Not "pull the archive". **Make the per-cell store reproducible, then wire it.** In order:

1. Fix `build_weather_world._write()` to emit `level_c`, `decomposition` and `regimes.json`, and make
   `build()` either call `extract_temperature` or stop shipping it as dead code — whichever the
   answer to §5's open question turns out to be.
2. Re-derive the store from the fixed tool and diff it against the 7.9 MB on disk. **Equality is the
   exit condition**; a difference is the finding.
3. Pull the 18 temperature-only cells' wind/cloud/precipitation.
4. Only then wire `sim/weather_world.py` into `simulation/weather_inputs.py`, behind the refusal
   that now names its site.

Step 2 is what makes this landable at all, and it is why the store stayed on disk this turn rather
than in a commit.
