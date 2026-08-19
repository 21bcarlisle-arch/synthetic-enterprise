# WORKER FINDING — the sibling detection axis keeps the free-literal floor that was just derived away on the belief side, and the new control cannot fail on it

**Severity:** LATENT · **Lane:** D_billing_metering

**Discharged:** `tests/tools/test_couple_w2_11_d5.py::test_the_axis_population_is_walked_and_holds_the_sibling`,
`tests/tools/test_couple_w2_11_d5.py::test_the_detection_floor_is_derived_and_the_band_is_what_it_admits`,
`tests/tools/test_couple_w2_11_d5.py::test_the_declared_null_control_cannot_derive_the_detection_floor`,
`tests/tools/test_couple_w2_11_d5.py::test_the_class_control_fires_on_its_own_named_defects`,
`tests/tools/test_couple_w2_11_d5.py::test_an_empty_axis_population_is_a_violation_and_not_a_pass`,
`tests/tools/test_couple_w2_11_d5.py::test_the_axis_walk_reads_both_key_spellings`
— 2026-08-19 worker tick, H27 Expert Hour #41, BUILD on `tools/couple_w2_11_d5.py`.
All three repair items taken, and **item 1 was taken differently from how it was
written, because the derivation this document proposed does not work.**

**The observation is confirmed, re-measured before building rather than trusted.**
150 was a free literal: nothing derived it and no note said what it was the smallest
n *of*. Over the books a sound floor admits, **126 of 295** upper-edge readings fall
outside the (70, 88) this entry declared. The floor decided the verdict, exactly as filed.

**(1) THE PROPOSED DERIVATION IS REFUTED, and this is the correction the record owed.**
This document said the derivation "has the input it needs" because `lower_edge_invariant`
is already declared. It does not. That edge is a BOUND — attained by any invoice paid on
its due date — so every book has hundreds of witnesses and it is **green from n = 4 on all
five seeds**. A null control that never breaks inside the probe range has no break for a
search to find; the derivation would have returned its own starting point, which is the
TRUNCATED failure this module's own checker already names. Floored at 4, three of five
seeds read an upper edge of -5 — no movable case at all — and the band would then have had
to widen to (-5, 88) to stay true, i.e. a reading dominated by books with nothing in them.
`lower_edge_invariant` stays exactly what it was: the soundness control, not the floor-finder.

**What does break is the LAW-side invariant**, and it is the one the belief axis already
floors on — the drawn book must present the invoice span the four scenario constants predict,
read with no draw, no seed and no register. On these five seeds it first holds and keeps
holding at **n = 51** (per-seed 8/14/17/51/13, seed 3 binding) against the belief axis's 17 on
its own three. That the floor moves with the SEEDS as well as the builder is itself new, and
is why one probe range could not have served both axes.

**The band follows the floor, never the reverse (R12):** `upper_edge_range` (70, 88) → (49, 88),
because 49 (seed 41) and 55 (seed 7) at n = 51 sit on books the null control passes and the
shipped floor was excluding them. The soundness control stays GREEN on all 30 books the new
floor admits, which is what makes this a measurement the old floor was hiding rather than
draw noise.

**(2) The population is DERIVED, not enumerated** — `draw_size_axis_population` walks every
register entry declaring an axis under either key spelling, in either register, and
`check_axis_floors_are_derived` grades *which axes get graded*. The emptiness of that walk is
itself a violation, because a derived population that derives nothing is the enumerated loop's
own fail-open shape with a walk in front of it. `measure_axis_null_control_floor` now takes its
axis as an argument instead of naming one: a measurement that names its own subject can only
ever have the subject it names, which is precisely why the sibling went unfloored.

**(3) The missing mutation is in**, and it is the one no existing mutation in this battery
asked — every other perturbs an entry the loop already visits; this one perturbs *which entries
the loop visits*. An axis declared and absent from the measurement fires by name. Four more
carry it: the shipped 150 against the derived 51; an axis with no probe range (an underivable
floor must be a finding, never a silent skip); an empty population; and a fourth axis added to
a third dimension, which fires by construction rather than by anyone extending a tuple.

**Both key names are accepted and NEITHER is renamed.** This document flagged the divergence as
"worth collapsing"; it is not — nine call sites to buy nothing the walk does not already buy
(SIMPLICITY GUARD). The divergence is now harmless rather than fixed, pinned by a test, and
recorded here so it is not re-found as a defect.

**NOT DONE, and R11 is NOT claimed: the register change moves a published sentence that this
commit does not republish.** The saturation caveat interpolates `upper_edge_range` and the book
count, so the Proof door's detection row should now read "across 30 books … +49..+88" and still
reads "across 25 books … +70..+88". That sentence enters the gap ledger only as a side effect of
a live simulation run, and there is no persisted live book to re-score, so no publish step in
this tick could have carried it. The gap-ledger reconciler already carried this pair on its
refresh-work list *before* this change; the drift is tracked by a live mechanism rather than left
silent, and the next scheduled run clears it. Carried as owed item (A) on the atom's hold note.

**Raised:** 2026-08-18, worker tick, while LANDING the repair for
`WORKER_FINDING_THE_BELIEF_AXIS_NULL_CONTROL_CANNOT_FAIL_BECAUSE_ITS_FLOOR_SITS_ABOVE_WHERE_IT_BREAKS_2026-08-18`
(now in `docs/staging/done/`). That document names this as its own still-open lead; a lead
that lives only inside an archived document is not drawable, which is why it is re-raised
here as a finding of its own rather than left as a sentence in `done/`.
**Owner:** `tools/couple_w2_11_d5.py` — the `file_scope` of `H27_payment_belief_gap`
(`loop_stage: harden`) and of D28/D30/D31, so this is drawable now.
**Intended rank (P-1):** top of `D_billing_metering`'s LATENT band, behind any BLOCKING item.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE). The tick that found it was landing
a different repair; widening the control is a BUILD of its own.

## What was observed

Measured in the working tree at the commit that lands the belief-axis repair, through the
shipped register and checker. No scorer call; nothing was edited to produce these readings.

**The belief side is now derived. The sibling is not.** `DIMENSION_DRIFT_RESOLUTION` carries
two draw-size axes, authored one atom apart for the same reason:

| | belief / belief_population_mix (D30) | detection (D28) |
|---|---|---|
| axis key | `own_draw_size_axis` | `draw_size_axis` |
| smallest `n_customers` | **17 — DERIVED** | **150 — a free literal** |
| null control | `invoice_span_invariant: (30, 92)` | `lower_edge_invariant: -6` |
| `floor_probe_range` | `(10, 30)` | **absent** |
| floor put on trial by a control | yes | **no** |

Read off the live register rather than the prose:

```
belief                | floor= 17 | probe= (10, 30) | keys= [above_edge_range, atom,
                        below_edge_range, floor_probe_range, invoice_span_invariant,
                        n_customers, seeds]
belief_population_mix | floor= 17 | probe= (10, 30) | keys= [...same...]
detection             | draw_size_axis: n_customers=(150, 300, 600, 1200, 2400),
                        seeds=(7, 11, 23, 3, 41), upper_edge_range=(70, 88),
                        lower_edge_invariant=-6            <- no probe range, no derivation
```

**The control's own population is two of three.** `check_belief_axis_floor_is_derived`
iterates `for dim in ("belief", "belief_population_mix")` — a hand-written pair, and its
docstring says so plainly ("it applies to BOTH belief entries, because the axis is shared").
The detection entry has a draw-size axis with the same shape and the same failure mode and
is not in the loop. So the repair that closed *"a floor that can be pushed up until the
declared band comes true"* closed it on the two dimensions that were being looked at, and
the third kept it.

**Why 150 is the same shape of literal 24 was.** D28's own comment records the upper edge as
"measured 70..88 across 25 books with the book's SHAPE held fixed, and still moving at the
swept grid's last point on 3 of 5 seeds at n=2400" — i.e. the axis is explicitly NOT
saturated at its top. Nothing beside the literal derives 150 from `lower_edge_invariant`, and
no note anywhere states what 150 is the smallest n *of*. It is exactly the artefact the
belief-side repair was built to make impossible: the input that decides the verdict, chosen
rather than derived, and untouched by any mutation in the battery.

## Why this is worth a BUILD and not a comment

This is the fourth consecutive time this class has been found one register over from where it
was last fixed: D28 derived the detection *edges* and left the belief ones; D30 derived the
belief edges and left both floors free; the 2026-08-18 repair derived the belief floor and
left the detection floor free. Each repair was real and each stopped at the boundary of the
dimension in front of it. The generalising move — and the R10 reading, since an
absurdity-class defect may not be closed with an instance fix — is to stop enumerating
dimensions in the checker and let the population be **every register entry that declares a
draw-size axis**, so a fourth axis added later is covered by construction rather than by
whoever remembers to extend the tuple.

## The repair, and it is small

1. **Derive the detection floor the same way**, or state at the declaration site what 150 is
   the smallest n of, with the measurement beside it. The null control is already declared
   (`lower_edge_invariant: -6`), so the derivation has the input it needs: the smallest n from
   which the lower edge reads -6 on every seed *and keeps reading it above*.
2. **Make the checker's population derived, not enumerated:** walk every entry carrying a
   draw-size axis under either key rather than the literal pair, and assert the population is
   non-empty (an enumerated loop that silently covers nothing is the fail-open shape).
3. **Add the mutation that would have caught this:** a register entry that declares an axis
   and is *absent from the checker's population* must fire. That is the case that makes the
   two-of-three hole impossible to reintroduce, and it is what neither existing battery asks —
   every current mutation perturbs an entry the loop already visits.

R12: no published number moved and none was tuned. Nothing here is a figure; the defect is in
the register's literals and the coverage of the control over them.

## Recorded so it is not re-measured

* The two axis keys differ in name (`own_draw_size_axis` vs `draw_size_axis`) for no reason
  either declaration states. Any derived-population walk has to accept both, and that
  divergence is itself worth collapsing while the population is being changed.
* `below_edge_range` on the belief entries is unmoved at (-371, -342) and was re-measured
  during the floor repair — it is not part of this finding.
