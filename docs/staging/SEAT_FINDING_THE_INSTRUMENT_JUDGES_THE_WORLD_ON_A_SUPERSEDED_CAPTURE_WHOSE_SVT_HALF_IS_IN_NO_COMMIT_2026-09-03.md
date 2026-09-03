# FINDING — the instrument judges the world on a superseded capture whose SVT half is in no commit

**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Discharged:** `tests/architecture/test_a_capture_may_only_judge_the_world_that_produced_it.py::test_the_LIVE_DEFAULT_passes_both_refusals_whatever_it_is_pointed_at`, `tests/architecture/test_a_capture_may_only_judge_the_world_that_produced_it.py::test_the_BAND_VERDICT_refuses_rather_than_reporting_a_number_off_a_stale_capture`, `tools/departure_population.py`, `tools/measure_departure_level.py`, `simulation/departure_level_anchor.py` — the two refusals this document asked for landed at 5554c2910 and the re-fit with its capture at 712ae5323. The instrument's default is now a capture whose two halves are both committed and which executed under the live anchor block; a stale one is refused rather than read, in either direction of error, and the first leg named above asserts that of whatever the default is pointed at rather than of any named capture. Discharged 2026-09-03 by the delivery seat, which landed the repair this document specified.

*A commit sha and a symbol name are deliberately NOT in backticks above: the discharge parser reads every backticked token on that line as an artefact path and fails closed on one that does not resolve — correctly, and it refused this document's first draft for exactly that. The line carries artefacts; the prose carries everything else.*

*Discharged, not deleted: this document is the reason a whole-book verdict that had reached a direction file as "out of band, HIGH, in 8 of 8" was not acted on in the wrong direction, and the reasoning below is the evidence that the sign was checked rather than assumed.*

BLOCKING by construction, not by choice: this document's own claim is that a measuring instrument
in this area is untrustworthy, and clause 2 of `background/finding_severity` says a finding of that
shape may not grade itself down. `tools/measure_departure_level.py` returns a whole-book verdict
whose sign depends on which working tree it runs in.

**Class:** `figures_on_a_superseded_clock` (primary), `uncommitted_and_orphaned_work` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0
**Subject:** `tools/measure_departure_level.py::DEFAULT_TABLE`,
`docs/reports/c2_departure_factors.json` and its untracked SVT sibling.

---

## What was drawn, and why it could not be done as written

Lane 0 drew: *"Re-fit the departure level anchor so the world's expected departure rate lands
inside the published GB band."* Its premise, quoted from `tools/measure_departure_level.py` at
HEAD: **whole book OUT OF BAND, high, in 8 of 8**, mean expected 22.35% against a published
midpoint of 17.20%, a world that "departs 1.3× harder than the GB record in every year".

That premise is read off a capture that does not describe the code that is live, and half of which
is in no commit. **On the committed capture the direction of the error is the opposite one.**

I did not re-derive the measurement. I ran the instrument the drawn work names, then asked the one
question the drawn work did not: *which capture is it reading, and is that capture the live one?*

## The two captures, measured

`tools/measure_departure_level.py:53` sets `DEFAULT_TABLE = docs/reports/c2_departure_factors.json`.
`world_book_rate_pct()` pairs any table with a `_svt_segment_decisions.json` sibling.

| capture | renewal rows | SVT rows | both halves committed? | 2022 SVT `sim_level_anchor` |
|---|---|---|---|---|
| `c2_departure_factors` | 148 | 1221 | **NO** — sibling is untracked | **3.053619** |
| `c4_whole_book_departure_factors` | 156 | 1373 | yes, both `git ls-files` | **1.0** |

`3.053619` is the 2024 reference-year anchor. `1.0` is `departure_level_anchor.NO_LEVEL_CORRECTION`.
The live block's own comment says which one is right, and says it about this exact year:

> *"The alternative on offer was the reference year's anchor, and this file's own docstring below
> already establishes that borrow is wrong on the one year it fires on: 1.98x, on the record's
> LOWEST year, in the direction that ADDS departures."*

So `c2` is a capture of the defect the live code removed. `c4` ran under the live block.

## The whole book, both captures, against the published band

`published_bands()` from the regulation commons; `world_book_rate_pct()` for the expected level.

| year | published | c2 (superseded) | c4 (committed pair) |
|---|---|---|---|
| 2017 | 13.5–14.0 | 14.58  high by +0.58 | 11.09  **low by −2.41** |
| 2018 | 19.5–20.0 | 21.09  high by +1.09 | 18.97  **low by −0.53** |
| 2019 | 20.7–21.3 | 22.00  high by +0.70 | 20.48  **low by −0.22** |
| 2020 | 22.5–23.0 | 23.94  high by +0.94 | 24.62  high by +1.62 |
| 2021 | 17.9–18.4 | 19.46  high by +1.06 | 16.96  **low by −0.94** |
| 2022 |  2.9– 4.3 | 12.83  high by +8.53 |  2.54  **low by −0.36** |
| 2023 |  8.9–12.5 | 12.87  high by +0.37 |  7.92  **low by −0.98** |
| 2024 | 12.5–16.1 | 16.36  high by +0.26 | 13.84  **IN BAND** |

**c2: in band 0, high 8, low 0. c4: in band 1, high 1, low 6.**
Mean published midpoint 15.50. Mean c2 17.89. Mean c4 14.55.

## Why this matters more than a stale number

**1. The drawn re-fit would have been fitted in the wrong direction.** The instruction says the
move "*lowers* it toward the record, so the book gets easier to hold". On the committed capture the
world already sits *below* the record in six of eight years; the correcting move **raises** it, and
the book gets *harder* to hold. Act (d) of the drawn work asked for the trap detector to be
re-registered for a lowering move. Registered that way it would have been pointed at the wrong tail
and would have passed a change that flattered us. That re-registration is now in
`SEAT_PREREGISTRATION_WHETHER_REPOINTING_THE_INSTRUMENT_AT_THE_COMMITTED_CAPTURE_HOLDS_2026-09-03.md`,
written **before** the re-fit is run.

**2. The verdict is a function of the reader's working tree.** With the untracked sibling present,
`world_book_rate_pct()` returns eight years. At clean HEAD it returns a refusal. Same commit, same
command, two answers — the catalogued *green in tree, red at HEAD* shape, here inverted: the tree
is what manufactures the *reading*, and the reading is what the doorbell quoted.

**3. 2022 carried the whole apparent excess.** c2's +8.53pp at 2022 is `3.053619 / 1.0` applied to
a year that is 100% crisis-forced-passive and therefore entirely SVT. Strip that one year and c2's
own remaining spread is +0.26 to +1.09pp — a world marginally hot, not one departing 1.3× harder.
The 1.3× figure is a mean over a year whose anchor the live code had already retired.

## What was NOT established, and is not claimed here

- **Not** that c4 is the capture to fit on. It ran under the live block, but it is one draw; the
  fit's own docstring says capture → fit → capture, and this finding does no fitting.
- **Not** that the world is genuinely low by −2.41pp at 2017. `measure_departure_level` states its
  own resolution and 2017's margin is inside the noise of a 156-renewal capture. Read the margin,
  never the verdict — 2017 (−2.41) and 2019 (−0.22) are not the same claim.
- **Not** that `c2` should be deleted. `tools/fit_year_level_anchor.py`,
  `tools/fit_departure_hazards.py` and `tools/split_price_response_by_curve_position.py` all
  default to it too; that is three more instruments on the superseded clock, and each needs its own
  read before it is moved.

## The repair, and why it is not in this commit

Point `measure_departure_level.DEFAULT_TABLE` at the committed pair, and add the control that makes
this class visible: **the capture an instrument judges on must have executed under the anchor block
that is live, and both its halves must be tracked.** Keyed to the property — it names no capture and
no year, so a new capture passes and a stale one fails, in either direction.

That change moves what a published control judges, so it is pre-registered rather than bundled with
the citation repair this commit had to make. This commit lands the red-clear and the measurement.

## What this commit does land

`tests/architecture/test_switching_rate_commons.py` was **green at HEAD and red in the shared
tree**: `test_every_document_this_file_cites_is_a_document_that_exists` failed because
`WORKER_FINDING_THE_BAND_CONTROL_IS_GREEN_ON_A_POPULATION_THE_BAND_IS_NOT_ABOUT_2026-08-31.md` had
been deleted from `docs/staging/` without being committed, with an untracked copy in
`docs/staging/done/`. The archive move and the citation update land together; the move alone would
red the control for every lane.

The xfail reason on `test_the_whole_book_departure_level_is_inside_the_published_band` carried two
clauses, and 2026-09-03 finds both stale. Clause (1) — *"no SVT sibling, so no whole-book reading
can be taken off it at all"* — was never a refusal in any tree carrying the untracked sibling.
Clause (2)'s mechanism half was voided by `c628cb37d`, which gave `svt_inertia_hazard` a required
`market_switching_multiplier`; the anchor's own `UNFITTED_YEARS[2022]` entry already records that
voiding. Both are kept in the reason beside the live text rather than deleted.

The marker stays. The leg fails on **either** capture, so nothing here lifts it.

## A third, independent corroboration of the direction — and one file deliberately left unlanded

`docs/institutional/knowledge_map.md:114` records a measurement taken on 2026-08-30, before this
finding and by a different route: the world was **3.15× SHORT** per renewal. Short, not hot. That
row and c4 agree on the sign; c2 is the only reading of the three that says the world departs
*harder* than the record. Three sources, two directions, and the odd one out is the capture whose
SVT half is in no commit.

**That row is corrected in the working tree and is NOT in this commit's pathspec, on purpose.**
`knowledge_map.md` currently carries two further uncommitted hunks from another lane — the SLC 27.15
direct-debit duty, the "SLC 27B does not exist" row and the 2016–2026 TDCV series, all sourced from
Ofgem decision letters. Committing the file by pathspec would land that lane's research under this
commit's message and this commit's REUSE block. The pathspec is what stops that, so the row waits
for the lane that owns those hunks, or for the next tick once they are in. A reader who finds the
row already correct in their tree and absent from `git log` is looking at this, not at a lie.
