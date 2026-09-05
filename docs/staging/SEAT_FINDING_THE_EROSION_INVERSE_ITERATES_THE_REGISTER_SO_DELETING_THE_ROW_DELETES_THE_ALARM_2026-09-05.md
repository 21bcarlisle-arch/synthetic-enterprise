**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The erosion inverse iterates the register, so deleting the row deletes the alarm

**Filed by the delivery seat, 2026-09-05, as a PRE-REGISTRATION — written before the measurement
below was run, so that the prediction could be refuted.**

`eroded_dispositions()` landed earlier today (`c5d37a190`) and closed the hole the direction
named: a dispositioned row whose census hit has disappeared. It is wired into `--check`, it is
mutation-proved, and it is green on the live tree. This document is about the hole in **its own
premise**.

## The claim it rests on

Its docstring says so explicitly, and the sentence is the whole reason it is not a tautology:

> **THE DISPOSITIONS FILE IS THE HIGH-WATER MARK**, and that is why this is not a tautology. The
> obvious implementation — remember last run's hit count and refuse a drop — would read the
> census's own prior output to decide whether the census is right […] Checking today's derivation
> against it is checking source against judgement, not against yesterday's source.

That argument is correct **only if the high-water mark cannot fall.** Nothing makes it so. The
implementation is `for key in sorted(disp)` — it iterates the register. A key that is not in the
register is not a subject of any rung, so **removing the row removes the alarm that the row's hit
vanished.**

## The prediction, written before running anything

Take a live row that is currently a hit. Delete the row from the register AND the hit from the
census — the two halves of one erosion, which is what any sweep that stops a path being seen
looks like once somebody tidies the register to match. Predicted: `undispositioned`,
`eroded_dispositions`, `unasked_loader_rows`, `unguarded_real_hits` and `census_is_vacuous` all
return clean, and `--check` exits 0.

## The measurement

Against the live tree (50 rows, 50 hits, 211 state paths), victim `.atom_stall_tracker.json`:

```
  undispositioned    -> []
  eroded_dispositions -> []
  unasked_loader_rows -> []
  unguarded_real_hits -> []
  census_is_vacuous   -> None
```

Not refuted. Every rung is green on a subject that has left the class in silence — which is the
exact sentence the erosion inverse was built to make impossible, one level up.

## Why this is not hypothetical

**It has already happened here, and it is recorded in this module's own docstring.** `c30738d77`
annotated all 46 rows; `9857c0edb` rewrote the file nine hours later from a pre-sweep copy and
deleted 33 of the annotations; the merge diffed its resolution against the rewriting side's own
copy, so neither side could see the loss. `--check` was green throughout. That event deleted
*fields*, and `unasked_loader_rows()` now catches that shape. The same rewrite deleting whole
*rows* is still invisible, and a rewrite from a stale copy is exactly the operation that drops
rows.

Note the second-order shape: `eroded_dispositions()` **refuses** a row whose path the census can
no longer resolve. Deleting that row is therefore the cure for its own refusal. A control whose
red can be cleared by deleting the evidence is a fail-open with an extra step.

## What is being built

`removed_dispositions()` — the register's own low-water guard. A key present in the register at
`HEAD` and absent from the working copy must be recorded in a `_retired` section with a non-empty
reason.

**No census-shape exception, deliberately.** The tempting rule is "allow the removal if the path
is gone from the tree anyway". That is precisely the fail-open above: `eroded_dispositions()`
already refuses the path-gone case *because a genuinely deleted carrier and a census gone blind
are indistinguishable from the census alone*. Handing the path-gone case a free pass here would
let row-deletion clear that refusal. The module's established position is that only an **authored**
sentence can tell those apart, which is what `declassified` does for the sibling rung, and
`_retired` is the same shape.

The baseline is `git show HEAD:<register>` — an authored, tracked, reviewable file, so this is
still judgement, not yesterday's derivation. It bites at commit time, against the working copy,
which is where the gates run and where `9857c0edb` would have been stopped. An unreadable
baseline emits a refusal naming that it could not be established; it never reports clean.

## Discharge

**Discharged:** `background/self_clearing_alarm_census.py::removed_dispositions`,
`background/self_clearing_alarm_census.py::load_retired`,
`docs/design/self_clearing_alarm_dispositions.json`,
`tests/background/test_the_register_can_lose_a_row_and_take_the_alarm_with_it.py` — the low-water
guard is built, wired into `main() --check` alongside the other four rungs, and mutation-proved
against the replay above: the same victim deletion that returned clean from all five rungs now
returns a named refusal. The `_retired` escape hatch carries the `str(x or "").strip()` treatment
so a JSON `null` reason cannot fall open. Discharged 2026-09-05 by the delivery seat, which landed
the repair this document specified.
