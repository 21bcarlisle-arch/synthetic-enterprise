**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R1's ceiling clears its null, and its magnitude is entirely the search

**Found:** 2026-09-06, delivery seat, claim
`r1-ceiling-magnitude-is-a-selected-maximum-with-no-unbiased-estimate`. Repaired in
`tools/r1_inference_ceiling.py`, published through `tools/generate_delivery_page.py`, controlled by
six tests in `tests/tools/test_r1_inference_ceiling.py`. Pre-registered before any of it was run:
`docs/staging/records/SEAT_PREREGISTRATION_AN_UNBIASED_POINT_ESTIMATE_OF_R1S_CEILING_MAGNITUDE_2026-09-06.md`.

---

## The finding, in one line

**Whether** and **how big** are two claims. The selection-corrected null answered the first — R1's
ceiling clears at p=0.0299 — and was read as answering the second. It does not, it cannot, and when
the second is asked properly the published magnitude does not survive: **+0.4793 of the +0.6308 is
the search, and what is left is inside the noise floor.**

## What was wrong

The published ceiling is `max(abs(held_out))` over 45 candidate feature pairs, **ranked on the very
fold it is then reported from**. A maximum overshoots whatever it is the maximum of. Clearing a null
does not un-bias a maximum — the null grades existence, and the two questions were being answered
with one number.

This was not hidden. Two corrections had already landed and each one names the shape without
closing it: the selection-corrected null (which grades existence), and
`held_out_exceeds_in_sample_on_the_reported_winner` (which reports that the winning fit scores 2.8x
better out of sample than in it). Both were correct. Neither touches the magnitude, and A49 gates R3
and R4 on the magnitude.

## The measurement

A **three-way split**, on one global household-level fold assignment honoured by every candidate:
fit on a third, **choose the winner on a second**, score it on a third that neither the fit nor the
choosing has touched. Averaged over the three rotations in which every fold plays every part once,
with a 200-draw null running the identical statistic.

Two details are load-bearing and each was a way to get it wrong:

- The estimate is **sign-aligned to the selection fold, not absolute.** `abs()` has a positive
  expectation under pure noise, so taking it re-introduces the exact bias being removed.
- Folds are assigned **globally, and by sorted position rather than by hashing the id.** The target
  *is* a hash of the id, so a fold drawn by hashing the same string could correlate with the
  quantity being estimated.

## What it returned, on `run_output_3851553ec_20260906T175920Z` (book of 164)

| | figure |
|---|---|
| published ceiling (max of 45, ranked and reported on one fold) | **+0.6308** |
| same fit fold size, still chosen and reported together | **+0.3630** |
| three-way split — choosing separated from reporting | **−0.1164** |
| ...its own noise floor | +0.2362 (p=0.398) |
| three-way split at **full coverage** (n=164, the powered rung) | **−0.1136** |
| ...its own noise floor | +0.1487 (p=0.1741) |
| **the search alone, at a fit fold held fixed** | **+0.4793** |
| shrinkage toward the null median (published, NOT unbiased) | +0.2493 |

**Attribution, one variable at a time.** +0.6308 → +0.3630 is the fit fold shrinking from a half of
the book to a third. +0.3630 → −0.1164 is the selection and nothing else, because the fit fold is
the same size on both sides of that comparison. Neither figure is inferred from the other.

**And the rotations do not agree on which pair wins.** Their estimates run from −0.3686 to +0.0884.
Which pair is "best" is a fact about who landed on the ranking side of the split.

## The honest answer, which is a refusal

**The pair rung has no unbiased point estimate of its magnitude on this book, and the instrument now
refuses rather than publishing one.** 69 households give 5.00 per cell on a three-way fit fold
against the 8 this file already required, and an estimate fold of 19 against the 20 a candidate
needs to enter the sweep at all. `magnitude_three_way_split.estimate` is `None` with a reason that
names its own numbers; the under-powered reading sits beside it, explicitly labelled as direction of
travel and not an estimate.

**The full-coverage rung can carry the split, and there the magnitude is indistinguishable from
zero.** That rung is not under-powered and its answer is not a refusal — it is a measurement, and it
says the recoverable share is inside its own noise floor.

## What this does to A49

A49 must read `magnitude_three_way_split.estimate`, which is `None`. It must not gate R3 or R4 on
+0.6308: that figure is a selected maximum whose de-biased reading is at the floor. The atom's own
note already says a number that flips on two households is not a gate; this is the same conclusion
reached from the other side, and it is stronger — the figure is not merely unstable, its magnitude
is unestablished.

**What closes it is COVERAGE, not a re-run.** The pair fields populated on every household would
give a three-way split roughly 55 per fold and ~14 per cell, over both controls. That is the same
thing the coverage step-function finding asked for, arrived at independently.

## Every pre-registered prediction held

P1 (pair rung refuses for power) — confirmed, at 5.00/cell against a predicted 5.75. P2
(full-coverage answers, `abs(estimate) < 0.25`) — confirmed at −0.1136. P3 (forced pair reading
`< 0.40`) — confirmed at −0.1164, far below, and the opposite sign. P4 (shrinkage is arithmetic,
+0.2454 on the then-current numbers) — +0.2493 on the live ones. P5 (the honest outcome is "no
unbiased estimate") — confirmed.

**What I did not predict** and should have: that the rotations would disagree about the winner at
all. I predicted a smaller magnitude; I did not predict that the identity of the winning pair is
itself a property of the split.

## Controls, and the poison round that proves they can fail

Six tests. The baseline was run through the identical command first, so a kill is a kill and not a
runner error, and each poison asserted its target was present before patching.

| poison | killed |
|---|---|
| `abs(est_score)` instead of sign-aligning | the bias test |
| report from the SELECTION fold (the original defect) | the bias test |
| `magnitude_verdict` never refuses | the both-legs partition |
| estimator hard-wired to zero | the bias test **and** the reachability test |
| `global_folds` collapses every household into one fold | the partition **and** the fold test |

One assertion was found to be a **tautology and fixed before landing**: the fold-independence check
was written against a fixture whose trait is drawn independently of the id, so *every* fold map
passed it. It now carries its own reachability leg — a fold map built by sorting on the target,
which the same assertion must reject.

The partition control asserts **both** legs — a 60-household book refuses and a 240-household book
answers — in one test, so an estimator that collapsed to "always refuse" could not pass half the
file and be believed.

## What is still open

The shrinkage figure (+0.2493) is published **with** the assumption that makes it wrong: it treats
the inflation a best-of-45 suffers under a real effect as equal to the inflation it suffers under
pure noise, and under a real effect the winner is chosen on signal more often, so it over-corrects.
It is a floor on the magnitude, never the magnitude. It is computed because a reader would compute
it themselves from two figures already on the page, and leaving it uncomputed invites someone to
compute it and believe it.
