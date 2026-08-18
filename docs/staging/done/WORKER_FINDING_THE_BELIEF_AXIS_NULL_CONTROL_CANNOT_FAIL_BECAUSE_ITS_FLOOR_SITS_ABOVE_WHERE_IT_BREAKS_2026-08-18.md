# WORKER FINDING — the belief draw-size axis cannot fail on its own floor, and the floor sits above two draw sizes where the null control is green and the declared band is false

**Severity:** BLOCKING · **Lane:** D_billing_metering

**Discharged:** `tests/tools/test_couple_w2_11_d5.py::test_the_axis_floor_is_derived_and_not_declared`,
`tests/tools/test_couple_w2_11_d5.py::test_the_floor_control_fires_on_a_floor_that_was_chosen`,
`tests/tools/test_couple_w2_11_d5.py::test_the_floor_derivation_cannot_pass_by_being_unavailable`,
`tests/tools/test_couple_w2_11_d5.py::test_the_floor_derivation_reads_no_declaration_it_grades`,
`tests/tools/test_couple_w2_11_d5.py::test_widening_the_axis_below_its_floor_turns_the_verdict_red`,
`tests/tools/test_couple_w2_11_d5.py::test_the_band_shipped_before_this_repair_is_false_at_the_derived_floor`
— 2026-08-18 worker tick, BUILD on `tools/couple_w2_11_d5.py`, all three repair items taken.
Re-measured before building rather than trusted: the null control first holds on all three seeds
at n = 17, the declared band first holds at n = 19, and the shipped floor was 24 — three numbers,
none derived from another, exactly as filed.

**(1) The floor is DERIVED.** `measure_belief_axis_null_control_floor` returns the smallest n from
which every seed's drawn invoice span equals `predict_event_age_span_from_constants`'s (30, 92)
*and keeps equalling it above* — the start of the green tail, not the first green point.
Independence is the point and is tested: the derivation reads the four scenario constants and no
declared band, invariant or floor, so `check_belief_axis_floor_is_derived` is a trial and not the
register agreeing with itself. It runs on `main()`'s default path (~60 predictor books, no
scorer), because a control over the axis that lives only in the test suite is a control the
publishing run never meets.

**(2) The missing mutation is in**, both directions and both entries:
a floor above the derivation (24 — the shipped one) fires naming the excluded window
`n = [17..23]`; a floor below it (14) fires for admitting books where the sweep moves the law;
mutating only `belief_population_mix` fires on the sibling, which is how this class survived D28.
`test_widening_the_axis_below_its_floor_turns_the_verdict_red` is leg 3 itself — the axis, not
the register, is what moves. Two fail-shapes of the derivation are pinned too: a probe range whose
own bottom is already green (a search starting above the break, returning its own first element)
and a probe range where nothing is green (an unavailable derivation is a FAILED one, never a quiet
pass on the declared literal).

**(3) The band follows the floor**, not the reverse: `above_edge_range` widened (-328, -308) →
(-333, -308) on both entries, which is what the derived floor admits. `own_saturates_above` is
unchanged at -308 and still the edge of the read range, so
`test_the_belief_edges_move_on_the_draw_size_alone`'s asymptote assertion holds unchanged.
`below_edge_range` is unmoved at (-371, -342) — measured, not assumed. Both floor literals now
carry their derivation beside them at the declaration site, which is what leg 2 said was missing.

22 targeted tests green. R12: no published number moved or was tuned — the caveat a reader meets
is still re-derived from the scored book on every call. **STILL OPEN**, filed as this document's
own lead and NOT discharged here: D31 lead (b), the sibling detection axis
(`draw_size_axis`, floor 150, `lower_edge_invariant: -6`) has never had its own null-control floor
measured, and every member of this class so far has turned up one register over.

**Raised:** 2026-08-18, worker tick, D31 DISCOVER pass 3 (LANE 3 idle draw). Full evidence and
the sweep tables: `docs/design/simplifications/D31_the_recon_grid_saturates_beyond_this_books_window.yaml`,
note 3.
**Owner:** `tools/couple_w2_11_d5.py` — the `file_scope` of `H27_payment_belief_gap`
(`loop_stage: harden`) as well as of D30/D31, so this is drawable now.
**Intended rank (P-1):** top of `D_billing_metering`, immediately behind
`WORKER_FINDING_THE_BELIEF_BAND_CENSUS_IS_BLIND_TO_THE_POPULATION_THAT_SETS_THE_EDGE_2026-08-18` —
this is the repair that document asked for, inspected one level up, and it is the same class
its own landing was meant to close.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE). The draw that found it was
DISCOVER/FRAME only and `file_scope` is closed to it.

## What was observed

Measured at HEAD `394bd6322` in a detached worktree (`git worktree add --detach`), through the
shipped `build_scenario` / `measure_belief_window_resolution` /
`measure_belief_band_population_axis` / `check_belief_band_population_axis`. Seeds 7/11/23. No
scorer call anywhere; nothing in `file_scope` was edited. Both `file_scope` paths carry another
lane's uncommitted work in the desk tree, which is why every figure below was taken at HEAD
instead.

`DIMENSION_DRIFT_RESOLUTION["belief"]` and `["belief_population_mix"]` were repaired on
2026-08-18 so that their saturation edges carry a scope and a draw-size axis:

```python
"own_draw_size_axis": {
    "n_customers": (24, 40, 60, 120, 300, 600, 1200),
    "seeds": (7, 11, 23),
    "above_edge_range": (-328, -308),
    "below_edge_range": (-371, -342),
    "invoice_span_invariant": (30, 92),
},
```

**Leg 1 — the declared upper band is false at two draw sizes the sweep's own soundness
criterion admits.** The axis carries a NULL CONTROL: the invoice-side span must not move, "or
this sweep would be perturbing the law rather than the sample and every reading above is draw
noise". Per-seed, at HEAD:

| n | per-seed upper edge | invoice span (the null control) | null control green? | inside declared (-328, -308)? |
|---|---|---|---|---|
| 12 | -328, -320, **-333** | (30,92), (30,88), (31,90) | **no** | no |
| **17** | -328, -308, **-333** | (30,92), (30,92), (30,92) | **yes** | **no** |
| **18** | -328, -308, **-333** | (30,92), (30,92), (30,92) | **yes** | **no** |
| 19 | -328, -308, -321 | (30,92) ×3 | yes | yes |
| 24 | -328, -308, -308 | (30,92) ×3 | yes | yes |

The null control first holds on all three seeds at **n = 17**. The declared `above_edge_range`
first holds at **n = 19**. The declared axis floor is **n = 24**. Three different numbers, and
the floor is none of them — it is above all three, and the gap between 17 and 19 is a region
where the sweep is sound by its own stated criterion and the register's declaration is wrong.

Run through the shipped checker rather than by hand, lowering only the floor:

```
floor 24 (shipped): invoice_spans=((30, 92),)  above read (-328, -308)  violations=0
floor 18:           invoice_spans=((30, 92),)  above read (-333, -308)  violations=2
floor 17:           invoice_spans=((30, 92),)  above read (-333, -308)  violations=2
    * belief: declares its above edge inside [-328, -308] ... and the sweep read [-333, -308]
    * belief_population_mix: declares its above edge inside [-328, -308] ... and the sweep read [-333, -308]
```

The null control stays green in both red cases. The verdict is decided by the floor alone.

**Leg 2 — the falsifier was in the discovery note that specified the repair.** D30's 2026-08-18
pass swept n ∈ {12, 24, 40, ...} and its own table records `sat_above = -333` at n=12, seed 23.
The build that followed declared the band as (-328, -308), which excludes -333, and set the
axis floor at 24, which excludes the book that produced it. The note's stated reason for
stopping at 24 is that the invoice span reads [30, 92] "at every n from 24 up" — a real reason,
but it is seven customers wider than the measurement requires, and the extra width is exactly
what removes the counterexample. The reason is also stated only in the discovery record: there
is no comment beside the literal at the declaration site deriving 24 from anything.

**Leg 3 — no mutation in the battery moves the axis. This is the R15 hole.** Seven cases in
`test_the_belief_axis_control_fires_on_its_own_named_defects` mutate the REGISTER and check it
against the fixed shipped-axis fixture; `test_pinning_the_population_hides_the_belief_draw_size_defect`
is the only axis-side mutation and it NARROWS the axis to a single n. Widening the axis
downward — the one perturbation that turns the verdict red — is not in the matrix. So the
input that decides the verdict is the input the mutation proof never touches, and the control's
subject was chosen rather than derived. This is the class the axis was built to close
(a declaration certified only on the population that produced it), recurring inside the repair,
one level out: D28/D30 replaced one un-derived `n` with seven un-derived `n`s.

## Why this is not merely a number being wrong

The band is only wrong over a narrow window, and nobody reads a 17-account book. What is wrong
generally is the shape: an axis whose floor is a free literal can be set anywhere, and the
control has no way to say so, because its own null control is satisfied well below the point
the floor was placed. A later widening for any unrelated reason turns two entries red with
nothing about the world, the book or the register having changed.

R12: no published number moved and none was tuned. The caveat a reader meets is re-derived from
the scored book on every call and is unaffected — the defect is confined to the register's
literals and the control over them.

## The repair, and it is small

1. **Derive the floor, or declare it.** Either compute the axis floor as the smallest n at
   which the null control holds (17 on this book, measured, not written down), or keep 24 and
   state at the declaration site what it is the smallest n of — with the measurement beside it.
   A floor that is derived cannot be chosen to green a verdict.
2. **Add the missing mutation:** lower the axis floor below the declared band's validity point
   and assert the checker fires. That is the case that makes leg 1 impossible to reintroduce,
   and it costs one parametrised entry.
3. **Widen the declared `above_edge_range` to whatever the floor then admits.** If the floor
   becomes 17, the band is (-333, -308) and `own_saturates_above` is unchanged at -308, still
   the large-n asymptote at the edge of the read range, so
   `test_the_belief_edges_move_on_the_draw_size_alone`'s asymptote assertion still holds.

## Two smaller things measured in the same pass, recorded so they are not re-measured

* `dense_drift_grid` has ONE executable statement: `return book_recon_drift_grid(records, as_of,
  grace_days)`. Its grid is bit-identical to the recon grid at every (n, seed) tested. The
  standing lead asking whether its edge moves with the draw was answered by the measurement
  that raised it.
* `book_memory_grid`'s EXTENT does not move with the draw: both extremes are `0` and `-window`,
  added unconditionally and never read off the book, so it is (-400, 0) at every n from 1 to
  300 while its interior goes from 2 points to 62-66. The two grids the lead named as one class
  are structurally different — the recon grid derives both ends from the book and its upper end
  walks; the memory grid derives neither, and everything book-derived is strictly interior.
