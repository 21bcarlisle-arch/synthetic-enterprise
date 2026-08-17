# WORKER REPORT — the saturation edge was the grid's own end, and is now the book's

**Severity:** RECORDED · **Lane:** D_billing_metering

**Draw:** RUNG-1c BLOCKING finding (OPS12 clause 3), lane `D_billing_metering`, taken ahead of
the general disposition queue and ahead of the LANE-1 BUILD draw (`H27_payment_belief_gap`) —
which was *not* forked, because its `file_scope` is the same file and a fork on a shared scope
is not a disjoint scope.

**Closes:** `docs/staging/done/WORKER_FINDING_A_SATURATION_EDGE_WAS_THE_GRIDS_OWN_END_2026-08-13.md`
(archived by this tick; its closing section carries the full derivation).

---

## What shipped, and what was wrong with it

`DIMENSION_DRIFT_RESOLUTION["detection"]` declared `saturates_above: 17`.
`detection_resolution_caveat()` interpolated that into a sentence stamped on every published
detection figure — in `det.note` **and** in `det.components["drift_resolution_caveat"]`, which
is what the ledger writer, the live wiring and the dashboard read:

> the reading SATURATES below -6d and above +17d — every supplier whose terms are more wrong
> than that publishes ONE figure … Do not read a movement in this number as days of company
> error.

Measured on the shipped scorer, seed 7, n=300, the detection gap reads
`+17 → 0.0296`, `+30 → 0.0484`, `+60 → 0.1373`, `+82 → 0.1618`. **The caveat told the reader
a movement was unreadable across a 65-day region where it is readable** — worse than no caveat.

**The cause was the grid's EXTENT.** D28 derived this grid's *density* from the book (one
integer per day) and left its *width* at `DRIFT_GRID_SPAN_DAYS = PERIOD_SPACING_DAYS = 21`.
`_measure_collapse_runs` reads saturation off a run **touching an end of the grid** — so the
run `(17..21)` was called saturation because +21 was the last company anyone scored.

## The fix: option 1, the one that removes the class

The extent now comes from the book. `dense_drift_grid` takes `records` and `as_of` and
delegates to `book_recon_drift_grid`, because the two counterfactual knobs are **one
identity**: the reconciliation drift moves the detector's fire date to `due + grace + k`; the
terms drift moves the believed due date by `k`, putting the fire date at `due + k + grace`.
One line, one book, one range of answerable drifts. `DRIFT_GRID_SPAN_DAYS` is **deleted** — an
unused declared width is something for the next grid to reach for.

Grid: `-20 .. +88` (109 companies) instead of `-21 .. +21` (43).

| dimension | declared before | measured now |
|---|---|---|
| `detection` | `saturates_above 17`, 7 runs | **`82`**, 16 runs |
| `detection` | `saturates_below -6` | `-6` — confirmed |
| `ageing` | no collapse, no saturation | **`saturates_above 63`**, 1 run |
| `detection_latency` | `saturates_below -19` | `-19` — confirmed; **undefined at +87/+88** |

n=300, seeds 7/11/23, bit-identical on all three.

## The independent witness, which was in the repo the whole time

`ORGAN_QUERY_GRID`'s `flagged_via_reconciliation` — the **same reading**, off the **same
book**, swept by the sibling knob on a grid whose ends come from the records — has declared
`saturates_below: -6, saturates_above: 82` and `undefined_drifts: (87, 88)` since D31. Two
registers over one quantity in one module, agreeing on the edge only where the grid was
allowed to reach it. Both edges now name their own owner: `-6` stays D28's (the book sits
nowhere near the grace line), `+82` is **D31's** — the book's `as_of` window running out,
which is a different KIND of stop and exactly what D29 built the per-edge field for.

## The correction that matters most: what the honest extent COST

`_check_register_is_differential` demanded an on-path dimension that collapses **nowhere**,
and `ageing` supplied it — 43 distinct readings across ±21. On the book's own extent ageing
saturates above +63, so **no** dimension has a clean sheet and the rule as written would have
failed a register that had just got more honest.

**A control whose only satisfying state is an under-swept grid rewards under-sweeping.** The
witness is re-derived as **interior resolution**: some on-path dimension must read every
adjacent pair apart across its whole defined interior, its only collapses being its own
saturated tails. `detection_latency` meets it across 105 companies. It is strictly stronger
where the old rule was satisfiable at all, and it cannot be bought back by narrowing the
sweep, because the sweep's ends are now the book's (and `dense_drift_grid` is AST-guarded
against reading the register, plus signature-guarded against being computable without a book).

Stated rather than absorbed, because quietly relaxing a control to green one's own change is
the defect this register exists to catch.

## Two corrections to the finding's own document

1. **Its proposed fires-test does not work.** "Refuse an edge abutting the grid end" reds
   `detection_latency`'s true `-19` (run `(-21,-20,-19)`, abutting `-21`) exactly as hard as
   the false `+17` — *every* saturation run abuts a grid end by definition. What discriminates
   is measurement past the grid, and that is how the fires-test was run: on HEAD, with the
   register untouched, extending the grid produced `detection: measured saturates_above=82
   and declares 17` while `-6` and `-19` stayed green.
2. **Its `lo` formula is wrong.** `min(days_late) - grace - 1` is `-6` on all three seeds;
   adopting it would have deleted the entire negative sweep, taking `detection`'s real `-6`
   edge and `detection_latency`'s `-19` floor with it. `days_late` bounds where the *set*
   changes, not where the *organ is asked*. The lower end is
   `min(issue_date - due_date) - grace - 1 = -20`.

Its "inferred, and NOT established" item — whether ageing moves past +21 — was swept: it does,
and it stops at +63. `ageing_resolution_caveat` now says so; it previously claimed the headline
moved on every drift, full stop.

## R15

The shipped `saturates_above: 17` is now a parametrised mutation and fires by name
(`measured saturates_above=82 and declares 17`). So do: an undeclared collapse, a declared
collapse the sweep reads apart, an understated edge in either direction, an unowned hole, an
undeclared undefined region, and an all-quantised register — the last requiring **both**
interior witnesses to be broken, because one surviving witness is enough and there are two.
The undefined region is admitted only as a **witnessed** bound (`reading is None` exactly where
the latency population is empty, checked per seed; seed 23 still reads at +87 off a population
of 1, and the witness holds because it is a PAIR).

## R12 / R13

No published figure was tuned. `score_triad` and `build_scenario` are untouched by this diff
(no hunk falls in either); the five gap values are unchanged at `k=0`. What moved is what the
instrument admits about itself, and it moved toward admitting more.

## Not done, stated rather than implied

- **No atom was minted.** `D37` was the obvious id and is **already in use** in this module for
  the Proof-door work (`atom D37, H27 Expert Hour #21`) while the maturity map has never
  carried it — a live instance of
  `WORKER_FINDING_A_MODULES_HOURS_CITE_ATOM_IDS_THE_MAP_HAS_NEVER_CARRIED_2026-08-12.md`. Left
  as found rather than compounded with a second meaning for the same id. The reshape both new
  edges owe is D31's, which exists and is `loop_stage: idle`.
- **The published ledger still carries the stale `+17d` string.**
  `docs/observability/coupled_gap_ledger.json`'s `W2_11_payment_behaviour_source` entry is
  written per-run by `run_phase2b`, so it self-heals on the next sim run against this code
  (R2: committed != running). It was NOT hand-regenerated: the CLI's `--write-ledger` defaults
  to `--customers 4000` with no seed, and moving published figures to fix a caveat string would
  be the R13 wall.
- **This commit also carries pre-existing uncommitted work** found in the same file on arrival:
  `atom D38, H27 Expert Hour #22` (`_composer_renderer_bindings`, `renderer_provenance`) with
  its own tests. It is in the same two files as this repair, so no pathspec can separate them;
  the green run below covers both. Flagged rather than silently absorbed.
