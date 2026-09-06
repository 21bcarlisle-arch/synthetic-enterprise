**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: is R1's selection-corrected verdict stable across draws of the same book?

*Delivery seat, 2026-09-06, claim `the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.
Written BEFORE the across-runs sweep was implemented or run. Nothing below is an observation.*

---

## Why this measurement, and what is already known

The selection correction landed (`f53c90b85`). The corrected verdict on the current book **clears**:
ceiling +0.6127, p95 +0.5529, p=0.0249, margin +0.0598.

`SEAT_FINDING_R1S_CEILING_WAS_A_SELECTED_MAXIMUM_AND_THE_CORRECTED_VERDICT_FLIPS_ON_TWO_HOUSEHOLDS`
established **by hand, on four run outputs**, that this verdict crosses 0.05 on a difference of two
households in the rung — p=0.0746 at n=71, p≈0.025–0.03 at n=69, all four drawn from the same
population at the same base seed. That is the finding's whole reason for staying BLOCKING.

**It is on no surface.** `site/data/delivery.json` carries the hedge *"a figure that clears by a
tenth of itself **will move** with the next draw of the book"* — a prediction — where we hold an
observation that it **did** move, to the other side of the line. The instrument measures one book
and has no notion that another draw disagrees.

So: make the flip a measurement the instrument takes, not a sentence a finding remembers. The four
hand-measured runs are known and are excluded from grading below; what is unknown is what the
**whole recent series** does, and that is what is graded.

## The measurement about to be made

For each of the K most recent run outputs in `docs/reports/` (same population, same base seed),
re-run the entire pair sweep and the selection-corrected null, and record `(n, ceiling, p95,
p_value, clears)`. Report whether the verdict is **unanimous** across them. Publish the answer
beside the headline figure.

## The predictions, fixed now

**P1 — the verdict is NOT unanimous across the recent series.** At least one run reads `cannot tell`
and at least one reads `clears`. (The four hand-measured runs already show both, so this is close to
known for K large enough to include the 09-04 run; it is stated so that a *unanimous* result — which
would mean my sweep is not reproducing the finding — refutes me loudly rather than quietly.)

**P2 — restricted to the 2026-09-06 run outputs alone (all of which I expect at n=69), the verdict
IS unanimous `clears`.** This is the one I am least sure of and it is the point of the exercise: if
runs of the same day at the same n disagree, the instability is worse than "two households" and the
finding understates it.

**P3 — the reported ceiling takes FEW distinct values across the series: at most 4 distinct values
of `n` and at most 5 distinct ceilings across K=8 runs.** Runs of the same population differ only in
which households happened to carry both pair fields, so the sweep should land on the same winner
repeatedly. If the ceiling is all over the place, the instability is not about coverage at all and
P3's refutation is the more important result.

**P4 — the full-coverage rung reads `cannot tell` on EVERY run in the series, with n=213 on every
one.** It is the rung with the power and it has never cleared. If it clears on any run, my
implementation is wrong rather than my prediction.

**P5 — `n` for the pair rung falls in [65, 75] on every run**, and the number of runs reading
`clears` is between 4 and 8 of 8. Stated as a range so a wild answer refutes it.

## What this measurement CANNOT detect, stated before it runs

These are not independent books. They are consecutive run outputs of the **same population at the
same base seed**, differing in how far the simulation had got and therefore in which households
carry both fields of a pair. So the spread across them **understates** the sampling variability of a
genuinely re-drawn book, and it is not a bootstrap. What it does establish is the thing that matters
for a gate: *the published verdict is not a property of the world, it is a property of which run
output the instrument happened to read.* It cannot say what the ceiling would be at full coverage,
and it must not be published as if it could.

Nor can it separate "coverage moved" from "the population moved" — the base seed is constant, so I
expect the former, but a run whose recovered trait spread differs materially would mean the latter
and I will report it if seen.

## The grading rule, fixed in advance

- P2 and P3 are the load-bearing ones; both are graded on the printed table and refutations get
  written beside the result, in the finding, not in a revision of this file.
- A unanimous `clears` across the whole series would refute P1 and would mean my sweep disagrees
  with the finding's hand measurement — in which case the sweep is wrong until proven otherwise, and
  the discrepancy is the result.
- The instability figure gets published **whichever way it falls**, including the case where it
  turns out the verdict is stable and the finding's "flips on two households" was the artefact of
  four cherry-picked runs. That would be the most valuable outcome here and it is not the one I
  expect.
