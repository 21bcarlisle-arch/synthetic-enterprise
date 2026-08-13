# WORKER FINDING (QUEUED) — a saturation edge was the grid's own end, and the caveat built on it ships false

**Severity:** BLOCKING · **Lane:** D_billing_metering

**Found by:** the D28 LANE-3 DISCOVER/FRAME tick, 2026-08-13, as a by-product of testing
whether the population-side predictor D28 declares missing is constructible. Queued per
SELF-INTERRUPT DISCIPLINE — the fix lives in `tools/couple_w2_11_d5.py`, which is the
`file_scope` of an atom at `loop_stage: idle`, so this tick may not write it.

**Status:** CLOSED 2026-08-13 by the RUNG-1c blocking draw, with the FIRST of the two
options below — the one that removes the class. Full derivation and the seed-by-seed
numbers are in `docs/design/simplifications/D28_the_detection_gap_is_quantised_by_this_books_placement.yaml`
(note 1 of 1); what the repair actually did is in the closing section of this document.

## Observed, with evidence

`DIMENSION_DRIFT_RESOLUTION["detection"]` declares `saturates_above: 17` and a collapsed
run `(17, 18, 19, 20, 21)`. Both were measured on `dense_drift_grid`, whose span is
`DRIFT_GRID_SPAN_DAYS = BILLING_CYCLE_SPREAD_DAYS = PERIOD_SPACING_DAYS = 21`. **+21 is
the last point the grid has.** The declared edge and the declared run both end exactly
there.

Scored past the grid this tick (`build_scenario` + `score_triad`, n=300, seed 7):

| `organ_terms_drift_days` | `detection` gap | `flagged_size` |
|---|---|---|
| +17 | 0.029629257846483303 | 254 |
| +21 | 0.029629257846483303 | 240 |
| +22 | 0.029629257846483303 | 237 |
| +30 | 0.048383858662919096 | 197 |
| +60 | 0.13725490196078433 | 89 |
| +83 | 0.16176470588235295 | 69 |
| +104 | 0.16176470588235295 | 69 |

Seeds 11 and 23 agree (+21 → +30 → +84: 0.069897 → 0.081320 → 0.182292, and
0.013205 → 0.011463 → 0.132743). The reading does not saturate above +17. It saturates at
or below `max(days_late) - DEFAULT_RECONCILIATION_GRACE_DAYS` = 84/85/85 on seeds 7/11/23.

`dense_drift_grid`'s docstring defends its width — "a drift larger than one cycle moves
every invoice past the next account's place in the book, so nothing about the population is
left to resolve." For this dimension that is measurably false: the flagged set moves at
every integer step from +17 to +83.

**It ships.** `detection_resolution_caveat()` interpolates the field into "the reading
SATURATES below -6d and above +17d — every supplier whose terms are more wrong than that
publishes ONE figure … Do not read a movement in this number as days of company error", and
that string is stamped into `det.note` **and** `det.components["drift_resolution_caveat"]`
— the component the ledger writer, the live wiring and the dashboard read (D34/D35: the
consumers read `components`, never the prose). The *below* half is independently confirmed
by this tick. The *above* half is false, and it is worse than no caveat, because it tells
the reader a movement is unreadable in a region where it is readable.

## The class

D28 fixed this grid's **density** provenance (book-derived, one integer per day) and left
its **extent** a harness constant. Its two sibling counterfactual-company knobs do not have
this defect: `book_recon_drift_grid` derives `lo` **and** `hi` from the records, and
`book_memory_grid` is complete rather than merely dense. `dense_drift_grid` is the only
grid in `COUNTERFACTUAL_KNOB_ROUTE` whose width is a declaration.

This is D31's own class — an edge that is a property of where the sweep happened to stop —
recurring on the register D28 re-derived to close exactly that class for this knob. A
book-derived grid is not book-derived if only its step size is.

## Inferred, and NOT established

That the same extent argument is safe for the **ageing** dimension, which shares
`dense_drift_grid`. Ageing publishes 43 distinct readings across ±21 and collapses nowhere,
so it has no declared edge to be wrong — but nobody has asked whether it moves past +21
either, and the differential witness that stops this register being an "everything is
quantised" excuse rests on that same 21-day window. Worth one sweep when this is drawn.

## The fix, when drawn

Either give the terms grid an extent from the book, mirroring `book_recon_drift_grid`
(`hi = max(days_late) - grace + 1`, `lo = min(days_late) - grace - 1`, which also lands
D28's owed predictor — the lower edge is exact on all three seeds and the upper is a
one-directional bound), **or** declare the sweep's span in the register and refuse a
`saturates_*` whose run abuts the grid edge. The second is the cheaper control and the
first is the one that removes the class.

**Run the fires-test first**: on HEAD, a rule that refuses an edge abutting the grid end
must red on `detection`'s shipped `saturates_above: 17` and stay green on
`detection_latency`'s `saturates_below: -19` (interior).

---

## CLOSED 2026-08-13 — what was built, and one correction to this document

**The fires-test, run on HEAD before the fix, as instructed.** Not in the shape this
document proposed, because that shape does not work: every saturation claim's run abuts a
grid end *by definition* — that is what `_measure_collapse_runs` means by saturation — so
"refuse an edge abutting the grid end" reds `detection_latency`'s `-19` (run `(-21,-20,-19)`,
abutting `-21`) exactly as hard as it reds `detection`'s `+17`. The structural rule this
document asked for cannot separate the true edge from the false one. **What separates them
is measurement past the grid**, so the fires-test was run that way: extending the grid to
the book's own extent on HEAD, with the register untouched, produced

    detection: measured saturates_above=82 and declares 17

and left the `-6` and `-19` edges green — the discrimination this document wanted, from the
first option rather than the second.

**Option 1 was taken: the extent is now derived from the book.** `dense_drift_grid` takes
the records and `as_of` and delegates to `book_recon_drift_grid`, because the two knobs are
one identity — the reconciliation drift moves the detector's fire date to `due + grace + k`,
the terms drift moves the believed due date by `k` and so puts it at `due + k + grace`. One
line, one book, one range of answerable drifts. `DRIFT_GRID_SPAN_DAYS` is **deleted**: an
unused declared width is something for the next grid to reach for.

**The formula in this document's "the fix, when drawn" is wrong in the lower half.**
`lo = min(days_late) - grace - 1` is `-6` on all three seeds, which would have deleted the
entire negative sweep and with it `detection`'s real `-6` edge and `detection_latency`'s
`-19` floor. `days_late` bounds where the *set* changes; it does not bound where the organ
is *asked*. The lower end is `min(issue_date - due_date) - grace - 1 = -20` — the earliest
candidate the detector has, which is the same quantity the sibling grid already used.

**Measured on the book's extent (-20..+88), n=300, seeds 7/11/23, all-seed agreement:**

| dimension | was | is |
|---|---|---|
| `detection` | `saturates_above 17`, 7 runs | **`82`, 16 runs** |
| `detection` | `saturates_below -6` | `-6` (confirmed) |
| `ageing` | no collapse, no saturation | **`saturates_above 63`**, 1 run |
| `detection_latency` | `saturates_below -19` | `-19` (confirmed), **undefined at +87/+88** |

**The independent witness this document did not have.** `ORGAN_QUERY_GRID`'s
`flagged_via_reconciliation` — the SAME reading, off the SAME book, swept by the sibling
knob — has declared `saturates_below: -6, saturates_above: 82` and `undefined (87, 88)`
since D31, because its grid derives both ends from the records. Two registers over one
quantity in one module, agreeing on the edge only where the grid was allowed to reach it.
Both edges now name their own owner: `-6` stays D28's (the book sits nowhere near the grace
line), `+82` is D31's (the book's `as_of` window runs out) — a genuinely different KIND of
stop, which is what D29 built the per-edge field for.

**What it cost, stated rather than absorbed.** `_check_register_is_differential` demanded an
on-path dimension collapsing NOWHERE, and `ageing` supplied it — but only because the grid
stopped at +21. On the honest extent ageing saturates above +63, so *no* dimension has a
clean sheet and the rule as written would have failed a register that had just got more
honest. **A control whose only satisfying state is an under-swept grid rewards
under-sweeping**, so the witness was re-derived as INTERIOR resolution: some on-path
dimension must read every adjacent pair apart across its whole defined interior, its only
collapses being its own tails. `detection_latency` meets it across 105 companies — a
stronger claim than the one it replaces, and one that cannot be bought back by narrowing
the sweep, because the sweep's ends are now the book's.

**The ageing sweep this document filed as "inferred, and NOT established" was run.** It does
move past +21, and it stops at +63: a company under-ageing by more than nine weeks has
carried every invoice below the 30-day bucket floor. `ageing_resolution_caveat` now says so
— it previously claimed the headline moved on every drift, full stop.

**Both shipped caveats were wrong and both are fixed.** `detection_resolution_caveat` now
reads "SATURATES below -6d and above +82d" with 14 interior runs listed, in `det.note` and
in `components["drift_resolution_caveat"]`.

**No atom was minted.** `D37` was the obvious id and it is **already in use** in this
module for the Proof-door work (`atom D37, H27 Expert Hour #21`) while the maturity map has
never carried it — a live instance of
`WORKER_FINDING_A_MODULES_HOURS_CITE_ATOM_IDS_THE_MAP_HAS_NEVER_CARRIED_2026-08-12.md`,
left as found rather than compounded with a second meaning for the same id. The reshape
both new edges owe is D31's, which exists and is `loop_stage: idle`.

**R12:** no published figure was tuned. The five gap values are unchanged at `k=0`; what
moved is what the instrument admits about itself, and it moved in the direction of admitting
more.
