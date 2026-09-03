# PRE-REGISTRATION — what publishing the re-draw MEAN must and must not move

**Filed:** 2026-09-03, BEFORE the edit and before the mutation run.
**Subject:** `tools/generate_value_arms_data.py` `_verdict_stability` / `_current_world_contrast` /
the headline narrative, and the door `site/test_the_baseline_comparison_reaches_the_reader.py`.

## What I already measured, and when

Not a prediction — stated so the predictions below are not confused with it. At
`a59a46bc7` (= `origin/main`) I read the live `site/data/value_arms.json` and the composed
`headline`. The withheld branch already reaches the reader with the point estimate (£2,336), the
date, the re-draw RANGE (£451 to £2,434), the spread (£991) and the 2-of-3 count. It does **not**
carry the re-draw MEAN. The mean exists in the payload as `bound.mean_gbp` = £1,450.64 and no
reader meets it, and no control asserts it should.

## Why the mean is not decoration

A range tells a reader how far the quantity moves. It does **not** tell them WHERE IN THAT RANGE
the published draw fell. £2,336 against a span of £451–£2,434 reads as "somewhere in there"; the
same £2,336 against a re-draw mean of £1,451 says the run made a HIGH draw. That is the same
flattering-direction defect the withheld verdict was filed for, one layer along: we withheld the
binary and left the reader unable to see that the surviving point estimate is itself the
favourable end of its own family.

## Predictions

**P1.** Adding `redraw_mean_gbp` to `_verdict_stability` will change **no existing verdict**.
`redraw_resolving`, `stable`, `resolved` and `verdict_withheld_because`'s existing clauses are all
computed off `values` and `_resolvable`, none of which I am touching. Specifically: the live block
will still publish `resolved: null` and `verdict_stability.stable: false`.

**P2.** `redraw_mean_gbp` will equal `bound.mean_gbp` to floating-point equality on the live
artefact (£1,450.6408126666695), because both are the arithmetic mean of the same three seed rows.
If they DIFFER, my premise that these read the same rows is wrong and the whole edit is wrong —
that is the refutation condition, and I will stop and file rather than reconcile them by rounding.

**P3 (the mutation).** Deleting the mean from the withheld narrative sentence must turn the new
door leg RED and leave every other rung in that door GREEN. If more than the new leg reds, the
mean is load-bearing somewhere I did not intend and I will say so.

**P4 (the equivalence risk, named up front).** The unanimous witness in
`test_the_verdict_is_withheld_when_the_floors_own_redraws_reverse_it` does not reach the withheld
narrative at all, so it CANNOT witness the mean assertion. If I assert the mean only on the
straddling subject, that assertion has exactly one witness and is satisfied by a function that
prints the mean unconditionally. I predict this is acceptable and here is why, stated before the
fact rather than after: the mean is a DISCLOSURE, not a judgement — printing it unconditionally is
the correct behaviour, so there is no second state for a witness to occupy. I am recording this so
that "it only has one witness" is met with a reason already on the record instead of a rationalisation.

## What must NOT happen

- `_resolvable`'s semantics must not change, for this contrast or any other it gates. The drawn
  direction says so explicitly and those other figures are covered by no pre-registration.
- No new compute leg. The subject is the live artefact's own three seed rows.
- The `CLEARS` / `DOES NOT CLEAR` branch must be left alone: it states a verdict off a stable
  family, where "which end of the range" is not the reader's problem.

---

# GRADED, 2026-09-03, after the runs — beside the predictions, not over them

**P1 — HELD.** Feed regenerated and diffed key-by-key against the committed one. `resolved` stayed
`null`, `verdict_stability.stable` stayed `false`, `redraw_resolving` stayed `2`. No verdict moved.

**P2 — HELD, to float equality.** `sum(values)/len(values)` == `bound.mean_gbp` ==
`1450.6408126666695`, checked before the edit was built on. The premise stands.

**P3 — HELD, and tighter than predicted.** Mutant: the mean deleted from the headline sentence
only. Result: `1 failed, 77 passed, 1 skipped` — the single red was the new leg at
`site/test_the_baseline_comparison_reaches_the_reader.py:2115`. Nothing else moved, so the mean is
load-bearing exactly where intended and nowhere else. A second mutant hard-coded `where = "ABOVE"`;
the low-draw witness in `tests/tools/…::test_the_verdict_is_withheld_when_the_floors_own_redraws_reverse_it`
went red and 97 others stayed green.

**P4 — REFUTED, in my favour's opposite direction, and the prediction was the weaker call.** I
predicted the mean assertion would have one witness and argued that was acceptable because a
disclosure has no second state. On building it I found there IS a second state and P4 talked me
close to missing it: the *placement* (`ABOVE` / `BELOW` / `exactly AT`) is a judgement, not a
disclosure, and hard-coding `"ABOVE"` would have passed every assertion the straddling subject can
make while being false for any run that drew low. The control now carries a second subject — the
same straddling floor with a £1,200 point estimate, which still clears the £991 spread (so the
withheld branch is reached) but sits under the £1,451 mean. Recorded here rather than quietly
fixed: the reasoning in P4 was sound about the number and wrong about the sentence, and "there is
no second state for a witness to occupy" is precisely the sentence that precedes an equivalence.

**What I did not predict, and did not cause.** Regenerating the feed also moved six
`realised.is_the_published_supplier` keys. I established by running HEAD's own generator that this
is pre-existing at HEAD and independent of my edit, and filed it as
`SEAT_FINDING_THE_COMMITTED_FEED_STATES_A_SUPPLIER_COMPARISON_THAT_REGENERATION_WITHHOLDS_2026-09-03.md`
rather than letting it ride unnamed inside this commit. The constraint "no unpredicted figure moves
silently" was met by naming it, not by preventing it — the feed is generated wholesale.
