**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The ceiling's magnitude has no unbiased estimate on the rung that gates R3 and R4

**Found:** 2026-09-06, delivery seat, claim
`r1-ceiling-magnitude-is-a-selected-maximum-with-no-unbiased-estimate`. Built in
`tools/r1_inference_ceiling.py` (`honest_point_estimate`), published on `/harness/`, recorded in
A49's own gate language.

---

## The defect, and it is NOT the one the selection-corrected null fixed

Yesterday's repair corrected the **null**: the reported figure is the winner of a 45-way search, so
it must be graded against the distribution of *winners*, not of one comparison. That landed and it
holds — on this book the ceiling clears at p=0.0249.

**A p-value is not a magnitude.** `+0.6127` is `max(abs(held_out))` over 45 candidates *ranked on
the very held-out half that scored them*. Whichever candidate's noise happened to point the right
way on those households is the one reported, so the number is biased upwards as an estimate of what
the winner recovers — **and it is biased up even when the ceiling is real**. `clears: true` printed
beside `+0.6127` reads as *"the ceiling is +0.6127"*, and A49 gates R3 and R4 on the magnitude, not
on the verdict. The whole panel answered one of the two questions.

## The fix: a third fold, not an adjustment

Households are partitioned three ways. One fold builds the cell means. One ranks all 45 candidates.
One — seen by neither — is what the winner's score is computed on. Repeated over 40 random
partitions, so the band carries the selection's own variability and not just the estimate fold's.
The estimate is **signed**, oriented by the selection fold, and can come out negative; taking `abs`
of it is itself one of the ways the magnitude got inflated.

**Shrinkage toward the null median (+0.3673) was the other option on the table and is rejected**: it
needs a prior on the effect size to say how far to shrink, there is no published or measured basis
for one here, and it would be a number picked because a number was needed — load-bearing on the
R3/R4 gate within a week.

## What I worked out before running it — and this is NOT a filed pre-registration

**Yesterday's pass filed its predictions in a dated document before implementing. This one did
not, and the difference matters:** everything below was reasoned out while reading the instrument
but never written down before the answer existed, so it is weaker evidence than the previous
finding's table and must not be read as the same thing. It is recorded because one of the two is
checkable against the code and turned out wrong in a way worth having.

Before running, I computed the pair rung's refusal from the constants: 69 households, three folds
of 23, a nominal 2×2 grid, so `23/4 = 5.8` per fit cell against `MIN_HOUSEHOLDS_PER_CELL = 8` —
refuse, and it would take `8 × 4 × 3 = 96` households.

**The refusal is right and the arithmetic is wrong.** It refuses at ~**72**, not 96, because the
grid does not occupy four cells — the median partition occupies three. Assuming the nominal width
rather than measuring the occupied one would have named a coverage requirement a third above the
truth, and it would have been the number the closing work was scoped against. The code measures the
occupied count for that reason.

The two things I did *not* work out in advance are the two that matter most: that below the floor
the pair rung returns **+0.1039** rather than the +0.3–0.45 I would have guessed, and that the
full-coverage rung's honest band **straddles zero**.

## The result

```
pair rung (the gating figure, winner carries ~56 households)
  reported by the ranked sweep       : +0.6127   (clears the corrected null, p=0.0249)
  unbiased point estimate            : NONE -- a three-way split leaves ~6.7 households per fit
                                       cell against the 8 this instrument already requires, and
                                       only 8 of 40 partitions clear it. Needs ~72.
  below that floor, not an estimate  : +0.1039
full-coverage rung (n=213)
  unbiased point estimate            : +0.0641   (5th-95th -0.3174 to +0.2350; 14/40 at or below 0)
  winner mean_recent_margin_rate in 23 of 40 partitions
```

**+0.1039 against a published +0.6127.** The gap is the search. And the rung that *can* carry an
honest estimate puts the ceiling at +0.06 with a band straddling zero — consistent with its own
p=0.8507, which is the first time the two rungs have agreed about anything.

> So A49's premise is worse off than "a number that flips on two households is not a gate". The
> rung carrying the gating figure **has no honest magnitude at all**, and the only rung that has one
> puts it near zero. R3 and R4 cannot be gated on this measurement in either direction.

## The bug the controls caught, which is why they exist

The usable-partitions floor was written as a **count** against the default `repeats`. Called with a
smaller `repeats` it refused a 300-household book whose own refusal message read *"Only 12 of 12
partitions cleared it"* — a refusal contradicting itself in its own text. It is a **share** now, and
the refusal names the threshold it is keyed to so that shape cannot recur silently.

## Evidence

Five controls in `tests/tools/test_r1_inference_ceiling.py`, mutation-proven — each mutation named
its intended killer, and the unmutated baseline was run through the identical command:

| mutation | killed by |
|---|---|
| the estimate fold IS the selection fold (third fold deleted) | `..._the_third_fold_is_not` |
| the estimate is taken as `abs` (unsigned) | `..._the_third_fold_is_not` |
| the per-cell floor removed | `..._refuses_and_a_thick_one_estimates` |
| the magnitude never reaches the headline | `..._as_a_number_or_as_a_refusal` |
| the page's magnitude block deleted | `site/...::test_the_MAGNITUDE_reaches_the_reader...` |

**Reachability is the load-bearing leg**: on a book where a feature genuinely carries the target the
same estimator returns **> +0.35** and picks `f0` as modal winner. Without that, +0.0641 on the real
book would be indistinguishable from an estimator that returns zero for everything — which is
exactly what this instrument's own docstring names as the trap it is most likely to fall into.

## What would close it

**Coverage, unchanged, and now with a number on it.** ~72 households carrying both fields of a pair
against the ~56 the winner has. Nine of the eleven observables are carried by 100 households or
fewer. The instrument is unchanged as the falsifier.
