# WORKER FINDING — a NaN reading is a fail-open the undefined-reading guard cannot fire on, and the two collapse predicates then disagree about it

**Severity:** BLOCKING · **Lane:** H_harness

**Found:** 2026-08-17, worker tick, LANE 3 DISCOVER draw on `D33_the_collapse_predicate_is_bit_equality`.
**Not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the defect is in `background/gap_metric.py`,
outside the drawn atom's `file_scope`. Queued here.
**Rank:** backlog. Nothing published is known to be wrong today — see REACHABILITY.

---

## STATUS, 2026-08-17 second tick (rung 1c BLOCKING draw) — THREE OF FOUR CLOSURE CONDITIONS LANDED; ONE IS BLOCKED ON AN ENTANGLED FILE AND THE BLOCKAGE IS NAMED HERE SO THE NEXT TICK DOES NOT RE-DIAGNOSE IT

Severity stays **BLOCKING**: this document's own "what closing it would need" lists four
conditions and one is unmet. What changed is that the half that was *reproduced on shipped
functions* is repaired, and the half that remains is the half this document labels `inferred`.

**LANDED** (`tools/couple_w2_11_d5.py` + `tests/tools/test_couple_w2_11_d5.py`, this tick):

1. ✅ **One derivation, all eight sites.** `_reading_key` / `_same_reading` /
   `_is_undefined_reading` are now the module's only equality on a published reading, used at
   every site this document enumerated (2315-2316, 2331-2332, 3696, 4514-4515, 4617, 4639,
   4844-4846) plus the three undefined-witness sites (3423, 4630, 8375) the enumeration missed —
   those paired an `is None` witness boolean against `undefined_readings`, so a NaN drift would
   have been listed as undefined and simultaneously witnessed as "not undefined".
2. ✅ **The guard closed on non-finite, not `None` alone.** `undefined_readings` now catches
   NaN and ±inf. `_collapse_state` returns `None` — refuses to publish a resolution claim —
   rather than answering `distinct_from_baseline: True` from readings that are not numbers.
3. ❌ **`GapResult` refusing a non-finite `gap`/`raw_gap`/`g0` at construction — NOT LANDED.**
   See the blockage below.
4. ✅ **R15 both ways.** Six tests, every one parametrised over or asserting on *both*
   degenerate values, exactly as this document required. Mutation-proven against the
   pre-repair implementations reconstructed verbatim: the `(nan, nan)` fixture fires on
   `undefined_readings == ()` and on the published `distinct_from_baseline: True`; the
   `(0.0, -0.0)` fixture fires on the two derivations disagreeing and on one company being
   split into two. **Neither fixture is redundant** — a repair fixing only one value is caught
   by the other, which is the property this document asked for by name.

**BLAST RADIUS, measured not asserted** (the `a blast radius counted is not a blast radius
measured` class). `tests/tools/test_couple_w2_11_d5.py`: **500 passed** at the repaired tree,
unchanged from HEAD. Zero declared edges moved, matching the D33 sweep's prediction from
2,264 pairwise comparisons — there is no `-0.0` and no non-finite reading on this book, so
this lands as a guard against a reachable fail-open and *not* as a re-derivation.

### Why condition 3 is not landed, and it is an entanglement, not a difficulty

`background/gap_metric.py` is **dirty in the shared working tree with a different lane's
uncommitted work** — the H27 Expert Hour #30 reserved-name repair (`reserved_component_keys`,
`NORMALISATION_FINDING_COMPONENT_SHADOWS`), which is absent from HEAD
(`git show HEAD:background/gap_metric.py | grep -c reserved_component_keys` → **0**) and spans
six files: `background/gap_metric.py`, `tests/test_gap_normalisation_declaration.py`,
`tests/test_gap_metric_misapplication_class.py`, `tools/couple_cohort.py`,
`tools/generate_proof_data.py`, `site/proof/`. Its hunks sit **inside `__post_init__`, the same
function condition 3 must change.**

`tools/surgical_land` commits the WORKTREE, so any pathspec commit naming `gap_metric.py`
sweeps that whole lane into this one. This is precisely the shape
`WORKER_FINDING_A_BLOCKING_REPAIR_IS_UNLANDABLE_BECAUSE_ONE_FILE_CARRIES_TWO_LANES_2026-08-15.md`
documents, and it is that document's *unresolvable* case: its own escape hatch — "when the
entanglement is a supplier/consumer pair, landing the supplier alone is a coherent commit" —
**does not generalise here**, and it says so: *"two lanes editing the same function still have
no such move."* Adopting a third lane's six-file change without its record is the record/code
inversion that same document spent two commits repairing.

**This was NOT deferred for cost.** The measurement that would have justified forcing it says
the opposite of urgent: the live ledger carries **53** `gap`/`raw_gap`/`g0` values across 14
entries and **zero** are non-finite (measured this tick), and no live scorer has been shown to
produce one — this document's own REACHABILITY section already labelled that `inferred`.
Forcing a fail-closed constructor guard through a swap-the-file manoeuvre, on a shared tree
with live concurrent writers, risks destroying another lane's uncommitted six-file change to
close a hole with an empty live population. That trade is not worth taking.

**What unblocks it, in one line:** land the H27 Hour #30 lane (it is complete and carries its
own tests), then `gap_metric.py` is clean at HEAD and condition 3 is a ten-line addition to
`__post_init__` plus its R15 fixture at both degenerate values.

---

## The finding

`tools/couple_w2_11_d5.py::_measure_collapse_runs` carries an explicit fail-open guard, and its
own docstring states what it is for:

> `undefined_readings` is the fail-open this measurement would otherwise have: a dimension whose
> population empties under a drift publishes `None`, and `None != baseline` reads as MOVEMENT —
> an instrument that has stopped reading at all, counted as resolution.

The guard tests for `None`. **NaN is not None**, and it is the other value an instrument that has
stopped reading can publish. Reproduced live on the shipped functions at HEAD 95cc1be06, no
scenario built (`observed-with-evidence`):

```
readings (nan, nan):  _measure_collapse_runs -> ((-1, 0),)      a collapsed run
                      _collapse_state        -> collapsed: False,
                                                distinct_from_baseline: True
readings (0.0, -0.0): _measure_collapse_runs -> ()              no collapsed run
                      _collapse_state        -> collapsed: True
```

Two consequences, and the second is the fail-open:

1. The module's **two** collapse derivations disagree on both degenerate float values, in
   opposite directions — `_measure_collapse_runs` compares `repr()`, `_collapse_state` compares
   `==`, and those are different predicates on `nan` and on `-0.0`.
2. A dimension publishing NaN is recorded by `_collapse_state` as **distinct from baseline** —
   exactly the D28 shape the `None` guard was written to close, arriving through the one value
   the guard does not name.

## And the constructor that should have stopped it is fail-open too

`background/gap_metric.py::GapResult.__post_init__` checks the declared normalisation kind
against the arithmetic. Every comparison against NaN is False, so the check passes. Measured:

```
metric=belief gap=nan  raw_gap=nan g0=1.0 normalisation=divisor   -> CONSTRUCTED gap=nan
metric=belief gap=0.5  raw_gap=nan g0=1.0 normalisation=divisor   -> CONSTRUCTED gap=0.5
metric=belief gap=nan  raw_gap=1.0 g0=nan normalisation=divisor   -> CONSTRUCTED gap=nan
metric=belief gap=nan  raw_gap=nan g0=0.0 normalisation=none      -> CONSTRUCTED gap=nan
```

The second row is the one to read twice: the entry **declares** `divisor`, meaning
`gap = raw_gap / g0`, and `nan / 1.0` is not `0.5`. The D44 declaration control — the whole point
of which is that "each kind carries a relation that can be false, so each one is falsifiable here
rather than only at audit time" — passes a row whose declared relation is false, because the
falsifying comparison involves a NaN.

`GapResult.gap` is typed `Optional[float]` and documented "None only if g0 is degenerate", so the
degenerate case has a designed representation. NaN is a second, undeclared one that every
downstream `is None` check misses.

## Reachability — `inferred`, not observed

No live scorer has been shown to produce a NaN gap; that was not measured. What is measured is
that **nothing between a scorer and the collapse predicates would stop one**: the constructor
admits it, the guard does not name it, and the two consumers then disagree about what it means.
This is filed as a control that cannot fail, not as a wrong published number.

## What closing it would need (R10 — the class, not the instance)

- One derivation shared by all eight comparison sites in `couple_w2_11_d5` (2315, 2316, 2331-2332,
  3696, 4514-4515, 4617, 4639, 4844-4846), so `repr()` and `==` cannot disagree about whether two
  counterfactual companies are one company.
- The undefined-reading guard closed on **non-finite** readings, not on `None` alone.
- `GapResult` refusing a non-finite `gap`/`raw_gap`/`g0` at construction, so the declared relation
  is checked against arithmetic that can falsify it.
- R15 both ways: the control must fire on a NaN reading AND on a `(0.0, -0.0)` pair — a fixture
  using only one passes under a repair that fixes only the other.

## Provenance

Spun out of the D33 DISCOVER pass recorded in
`docs/design/simplifications/D33_the_collapse_predicate_is_bit_equality.yaml` (2026-08-17 note),
which measured 2,264 pairwise readings across both dense sweeps and found the reader-precision
question itself to be a no-op on this book — this is the defect that survived that measurement.
