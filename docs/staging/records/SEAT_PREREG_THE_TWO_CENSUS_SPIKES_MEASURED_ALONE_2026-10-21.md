**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `the-census-peak-is-two-tests-measure-and-shrink-them`)

# Pre-registration: the two census spikes, measured alone, then shrunk without touching the tests

Written 21 Oct 2026 BEFORE either probe ran. Parent: the Result section of
`SEAT_PREREG_THE_CENSUS_PEAK_BY_DIRECTORY_2026-10-21.md` (peak 9,510 MB; 6,939 MB without the
weather-cell test; 5,606 MB without both).

## What each test is, read from the code before measuring

**Weather-cell test** (`test_the_CELL_COUNT_IS_AN_OUTPUT_of_the_draw_...`) calls
`derived_cell_count` -> `space_filling_sample.output_space(sample=200_000)`. That function builds
five output axes over the WHOLE 39.3m (cell, case) grid (`gross`, `solar`, `offset_share`, `retro`,
`turndown`, the `np.where` temporaries, a 5-column `values` stack and its `values[keep]` copy, at
~314 MB per float64 axis), and only THEN draws 200,000 rows. The draw's probabilities are the
grid weights alone, never the values. So **the sample size is not what sets the working set**,
and shrinking `sample` would buy almost nothing. It would also weaken the `> 10 x landed[987]`
bound for no gain. The lever is to draw the rows first and compute the five axes only at them.
The draw is the same `rng.choice` over the same `p`, so the result should be bit-identical.

**Pages test** (`test_every_published_link_is_in_the_manifest`) reads every tracked file and
passes each one through `searchable()`, which `ast.parse`s it. A JSON file parses as a Python
literal. `docs/state/billing_ledger.json` is 60 MB, so its AST is millions of nodes, and that is
built only to then ask whether a URL is in the text. The lever is to ask `PAGES_ROOT in raw`
first, and to call `searchable()` only on files that contain the root. Blanking only removes
text, so it cannot create a URL the raw text lacks. The `argv` rejoin is the one theoretical
exception, and it is checked by comparing the two outputs.

## Predictions (each a separate child process; peak = `ru_maxrss` of that process)

- **W-before:** `output_space(sample=200_000)` alone peaks at **5-8 GB**.
- **W-after:** the rows-first build peaks at **<= 3 GB** (the grid itself), and
  `values`, `weights` and `index` are `np.array_equal` to HEAD's.
- **P-before:** `_referenced_pages_urls()` alone peaks at **1-2.5 GB**.
- **P-after:** prefiltered, it peaks at **< 500 MB**, and the dict it returns is equal to
  HEAD's.

**Refutation:** if W-after is within 1 GB of W-before, the transient is not where I read it. If
the outputs differ, the change does not land, whatever it saves.

**Done means:** both shrinks have landed with the tests unchanged and green, the equality is
shown, and the before and after peaks are written below.

## Result (21 Oct 2026; each arm in its own process under `launch_long_job`)

| arm | before (HEAD `a21223862`) | after | output |
|---|---|---|---|
| W: `output_space(sample=200_000)` | **5,724 MB**, 22.6 s | **2,072 MB**, 10.0 s | `values`, `weights`, `index` all `np.array_equal` |
| P: `_referenced_pages_urls()` | **3,839 MB**, 58.2 s | **180 MB**, 1.0 s | dict equal (36 URLs) |

- **W-before HOLDS** (5-8 GB predicted). **W-after HOLDS** (<= 3 GB). The transient was the
  whole-grid axis build, and the sample size never set it. The test's `sample=200_000` and its
  `> 10 x landed[987]` bound are therefore unchanged.
- **P-before is REFUTED HIGH.** I predicted 1-2.5 GB and it measured 3.8 GB. The AST of a 60 MB
  JSON costs more than I priced. **P-after HOLDS** (< 500 MB). It is also 58x faster.
- **A missing test, found on the way.** A mutation that computed the turn-down axis at the wrong
  degree-days passed every test touching `output_space` (36 green). It was a missing test, not an
  equivalence, because the axis goes to ~0. The new control
  `test_the_ROWS_FIRST_build_is_the_WHOLE_GRID_build_read_at_the_drawn_rows` keeps the old
  whole-grid build as its oracle on ~300 cells, in both the drawn and the every-row branch. It
  reds under that mutation, and under an off-by-one case index.
- **What the census peak should now be:** this is inference, not measurement. The parent's peak
  sample was 9,510 MB. Without both tests it was 5,606 MB. With both, shrunk to ~2.1 GB and
  ~0.2 GB transients over a ~1 GB-base process, it should sit at ~6-7 GB, under the 8.9 GB line.
  The next census night is the measurement. Its timeout (17,400 s, three nights without a
  verdict) is now the binding problem, not its peak. P's 57 s saving is a small part of that.
