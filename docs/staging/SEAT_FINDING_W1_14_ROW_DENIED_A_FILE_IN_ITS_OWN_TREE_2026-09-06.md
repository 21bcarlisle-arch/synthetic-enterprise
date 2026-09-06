# SEAT FINDING — W1_14's row denied a file that was in its own commit's tree

**Date:** 2026-09-06
**Lane:** W1_market_weather
**Severity:** RECORDED — a false factual sentence in the maturity map, load-bearing as the stated
reason for a `file_scope` edit. Nothing published was wrong and no code was wrong; the sentence
inverted the atom's headline finding for the next reader. Found under the Lane 0 delivery claim
`the-weather-cells-reach-the-world-or-w1-14-says-why-not`.
**Status:** FIXED in the same commit — corrected beside the claim in
`docs/design/maturity_map.yaml`, with the ordering evidence and the reason the edit still stands.

## The claim that was wrong

`W1_14_weather_cells_for_household_heat_load` removed `tools/generate_weather_cells_data.py` from
its `file_scope` and justified the removal like this:

> "`tools/generate_weather_cells_data.py` was in this scope until 2026-09-06 and HAS NEVER EXISTED
> in any commit -- a level-0 row's file_scope is checked by nothing, so it named a program no build
> ever wrote."

The file existed. It is not close:

| | commit | time (2026-09-06) |
|---|---|---|
| generator lands | `1ed1e7737` | 18:02:47 |
| the sentence is written | `64e427717` | 22:25:15 |

`git merge-base --is-ancestor 1ed1e7737 64e427717` passes, and
`git cat-file -e 64e427717:tools/generate_weather_cells_data.py` succeeds — the file is present in
the tree of the very commit that says it never existed. It has three commits, a test suite
(`tests/tools/test_generate_weather_cells_data.py`), a caller on a live daemon publish path
(`background/process_run_complete.py:4283`), and a committed output
(`site/data/weather_cells.json`).

Its own docstring names this row:

> "this is the runner named in `W1_14`'s own file_scope that they were frozen against as
> deliberately dormant"

So the file was written **because** this row named it. The row then deleted the name and recorded
that no build ever wrote it.

## Why it mattered — not the file_scope, the headline

The `file_scope` edit itself was right, for a reason the row did not give: the generator is a SITE
publisher, not the sim seam, and the row should name where the seam lands. That reason is now in
the row and the removal stands.

What the false sentence actually cost is the atom's headline. W1_14's finding, and the Lane 0
direction that drew it, both read:

> "nothing in `simulation/`, `company/` or `saas/` imported a line of it, so the world's household
> heat load was not driven by any of it"

That is true, and it is a statement about **the world**. "No build ever wrote the generator"
promotes it into a statement about **the tree**, where it is false. The derivation had already
reached a business surface — the site's Knowledge section, with two maps and a coverage curve —
about four hours before it reached the sim seam. An unpublished derivation and a
published-but-unmodelled one are different states, and this project's product-share reading
depends on telling them apart.

## The lesson is NOT "check file_scope"

That was the control I was about to build, and measuring killed it before it cost anything. Over
the whole map:

- **33** `file_scope` paths do not exist, across **19** rows
- **every single one** is at `level_current: 0`

Which is the documented design, stated in `tests/design/test_maturity_map_contract.py`:

> "ABSENT -- reported, never refusing -- until the build lands the file. That chain is the design:
> unnamed is a defect at the mint, unwritten is a state the build clears."

A `file_scope` path that does not exist is **legal and expected** at level 0. A control asserting
existence would have gone red on 19 rows on its first run, all of them correct, and would have been
allowlisted into uselessness within a day. This is the shape CLAUDE.md warns about — a control that
breeds a register — and the only thing that separated the good version from the bad one was
printing the census first.

The residual defect has no control shape at all: **a false sentence in a comment**, asserting the
history of a path rather than its presence. No gate reads prose. The mechanism that catches this
class is the one that caught it here — the seat's interconnection pass asking, of work that landed
since the last orientation, what else assumes it. Two lanes touched the same subject four hours
apart, and only the seat is positioned to notice they disagreed.

## A second hazard, found by being refused: the map has ~7 bytes of headroom

Writing the correction above red-lined `test_map_within_size_ratchet_when_store_populated`. The
cause is not this correction. Measured at HEAD:

| | bytes |
|---|---|
| ceiling (`MAP_SIZE_CEILING`) | 409,600 |
| map at HEAD `64e427717` | **409,593** |
| headroom | **7** |

The ratchet sums **both halves** — `maturity_map.yaml` (173,372 bytes on disk) plus
`maturity_map_closed.yaml` — deliberately, so that splitting the file could not make it fail-open.
So the live file's own byte count reads far under the ceiling and tells you nothing about how close
you are.

**The consequence for every other lane: the next commit that adds a single comment line to any row
in either half reds `tests/design/` for the whole tree, with the cause in nobody's diff.** That is
the wedge shape this project has paid for repeatedly. It is not hypothetical — it happened to this
turn, and the only reason it did not wedge anyone else is that the correction could be compressed.

This correction landed **net-negative** (409,588 bytes, 12 bytes of headroom — 5 better than it
found). That is a reprieve of one comment line, not a fix. The fix is the one the ratchet's own
message names: *"the register must live in the store, not the map"* — prose accreted into rows
belongs in `docs/staging/` findings and the simplifications store. **This is not filed as a
proposal to raise the ceiling.** Raising it would delete the only control that can see unbounded
accretion into a closed atom, which is precisely what the ratchet exists for.

Not fixed here: this turn's claim is W1_14's, the compression bought the headroom back, and
draining prose from the map is a different subject that should be drawn on its own rather than
smuggled into a weather atom's commit.

## What is unchanged

- The atom stays at `level_current: 1`. The seam is real and the L2 refusal is unaffected.
- `block_reason` stands: L1→L2 needs a coordinate at the draw, owned by W2_18.
- The archive-coverage figures (20.5% / 30.7% / 27.9%, 3.5% joint) are untouched.
