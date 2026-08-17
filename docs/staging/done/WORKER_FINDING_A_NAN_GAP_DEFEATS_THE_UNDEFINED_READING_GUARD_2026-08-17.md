# WORKER FINDING — a NaN reading is a fail-open the undefined-reading guard cannot fire on, and the two collapse predicates then disagree about it

**Severity:** BLOCKING · **Lane:** H_harness

**Found:** 2026-08-17, worker tick, LANE 3 DISCOVER draw on `D33_the_collapse_predicate_is_bit_equality`.
**Not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the defect is in `background/gap_metric.py`,
outside the drawn atom's `file_scope`. Queued here.
**Rank:** backlog. Nothing published is known to be wrong today — see REACHABILITY.

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
