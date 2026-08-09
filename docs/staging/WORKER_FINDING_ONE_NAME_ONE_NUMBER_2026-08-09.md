# WORKER FINDING — aligning the denominators did not make them one number, and that is the answer

**Date:** 2026-08-09 (worker tick) · **Atom:** `D16_ageing_negative_population_is_unexcluded`, L0→L2
**Class:** a real-world quantity published by two dimensions of one instrument under one name.
**Status:** the alignment landed; the name now has exactly one owner; the register that was
built to break was rewritten rather than loosened.

## What the atom asked, and why doing only half of it would have been wrong

D16 offered two remedies: carry D11's exclusion rule across to the ageing dimension, **or** declare
in the published note which of the two figures a reader should take. The honest delivery needed
both, and the reason is the measurement:

Carrying the exclusion across makes the two **denominators** the same population. Measured, at 400
customers:

| | seed 7 | seed 11 | seed 23 |
|---|---|---|---|
| denominators before | 1062 vs 782 | — | — |
| denominators after | 782 / 782 | 776 / 776 | 755 / 755 |
| identical **case set**, not just size | yes | yes | yes |

It does **not** make the two rates one number. Detection reads 0.0269 (21 of 782); ageing reads
0.0090 (7 of 782). Same population, three times apart.

## The residual is entirely belief-side, and it is two honest questions

The remaining difference is not leftover work. The two dimensions ask different things:

* **detection** asks *did the company ever chase this invoice?* Wrongful dunning is an **event**. A
  customer chased in month one was still wrongly chased when the report drops it in month three, so
  the belief population is EVER-FLAGGED.
* **ageing** asks *does the open-item report still show this invoice overdue at `as_of`?* That is a
  **misstatement** question — what a provision, a bad-debt charge or a board pack is built from —
  and the `as_of` snapshot is the right population for it.

Aligning the belief sides too would have destroyed one of the two measures to manufacture agreement
between two numbers. That is the goal-seek R12 forbids, and it was the tempting move.

So the denominators align and **the name does not**: `overstated_arrears_rate` is renamed at every
site to the **ageing-report overstatement at `as_of`**, and "the wrongful-dunning exposure" has
exactly one publisher.

**The relationship is measured, not asserted.** Ageing's numerator is a **strict subset** of
detection's at seeds 7/11/23 and at grace windows 5 and 12 — 7 of 21, 16 of 31, 5 of 13. Every case
the report still overstates was chased; 14 / 15 / 8 more were chased and then dropped from the
report before `as_of`.

## The open question the atom said not to dodge

`DIMENSION_AS_OF_CONTRACT` exempts the ageing dimension because "an invoice really does age". That
justification licenses the **truth** side moving with the clock and says nothing about the belief
side — which here is the `as_of` snapshot, and does move for the same reason the detection headline
did before D11 made it EVER-FLAGGED. **The exemption is broader than its justification**, and that
is now recorded in the register (`belief_side_is_as_of_dependent: True`) rather than left as the
comfortable reading. It is kept, narrowed to what it actually excuses.

## R15 — what was proven, and both ways

* **The band is not a no-op.** Fold the excluded cases back into the denominator, through the same
  scorer on the same inputs, and the rate must move: 0.0090 → 0.0951.
* **The band cannot fail open on unknown truth.** Blank `days_late` on the within-grace successes
  and they must **leave** the scored population, not be assumed paid on time.
* **The register is falsifiable on three lies** — declare the populations divergent (they are now
  one set); declare the numerators identical (the old prose claim); declare the subset in the wrong
  direction (a control checking only "they overlap" would pass on that). Plus a **vacuity guard**:
  an empty ageing numerator is a subset of anything, and would satisfy the declaration for free.
* **One rule, one set.** `never_flaggable` is constructed once and read by both dimensions,
  asserted structurally as well as numerically. A second copy of the rule is how the two dimensions
  came to disagree in the first place.

### The method trap, hit again, in this build

The phrase sweep counted the ageing summary's honest sentence — *"NOT the wrongful-dunning
exposure"* — as **publishing** the name. A bare substring cannot tell a claim from its negation:
the AO2 `"none"` shape, which the immediately preceding tick was itself caught by. The disclaimer's
**form** is now registered and checked, doublespeak is proven not to buy an exemption, and dropping
the disclaimer is proven to fire.

## The sibling half was not left behind this time

`background/live_payment_triad.py` labelled the same rate "the WRONGFUL-DUNNING exposure" in both
its attributed-measures register and its rendered summary — one file over from where the name was
being corrected, which is exactly the shape that has bitten this triad on three consecutive ticks.
Both corrected, under a test asserting the **live** ageing dimension carries the band.

## Found and queued, not fixed on sight

* **`D17_d8_counterfactual_has_no_unattributed_residual`.** The D8 remittance counterfactual's
  anti-rubber-stamp guard rested on one residual: the ageing overstatement it could not explain
  (0.2188 of 0.2803 on the live fixture). D16 measured that residual to be composed entirely of
  cases where the cash arrived past grace — invoices the company was **right** to carry as owed.
  With those excluded, every measure the counterfactual publishes reads `attributed == actual`, and
  the guard guards nothing. The refuted test is **replaced, not repaired**, and names D17 in its own
  docstring so the weakened guard cannot decay into an assumption.
* **`H32_map_size_ratchet_red_on_head`.** See the companion finding.

## R12

Nothing was tuned. The detection balanced error is byte-identical at 0.0134; the ageing
overstatement moved because the population it is measured over moved, and the criterion for that
move was the exclusion **rule's** correctness, never the value it produced.

**Evidence:** 694 tests green across every file touching `gap_metric`, the triad, or the live path
(`tests/tools/test_couple_w2_11_d5.py` 62, `tests/tools/test_d7_ageing_measures.py`,
`tests/tools/test_d6_ageing_metric_shape.py`, `tests/background/test_live_payment_triad.py`, plus
every other coupled-pair suite). `tests/design/` green except the pre-existing map-size ratchet.

## Why H27 is still L2

`depends_on` is dropped and **not** re-pointed a fourth time — the hold note has already fallen into
the dead-mechanism class twice. The 2→3 is drawable and unblocked. It is not taken here for the
reason every prior release gave and this tick has the least right of all to ignore: **this tick
changed the instrument.** It renamed a published quantity and moved the number under it. An Expert
Hour run by the tick that built the change is the reputation-of-the-old-instrument problem in its
purest form. The next promoter runs it fresh, starting at D17.
