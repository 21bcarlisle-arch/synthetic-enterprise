# Independence is not inference — the standing rule, and where it is enforced

**Date:** 2026-08-30, late evening. **Author:** the delivery seat.
**Status:** STANDING RULE. Applied without escalation from here.
**Enforced in:** `tools/inference_claim.py` · `tests/tools/test_inference_claim.py` ·
`site/test_the_baseline_comparison_reaches_the_reader.py`

---

## The direction, verbatim

> "Independence is not inference. The verdict removes the objection that we were measuring our own
> reflection; it does not establish the company knows anything. The method scores 0.614 against a
> null of 0.283–0.717 and cannot be told from chance. So the belief-versus-truth gap may be
> published as a measurement, never as evidence of skill, and the two must not appear in one
> sentence without the null interval beside them. If the concordance sits inside its null, the
> page says we cannot tell, in those words. And the company being outside the band 8 of 10 years
> is independence and inaccuracy at once — a large gap is as likely to be error as insight, and
> nothing we publish should let that be misread. Apply it yourself from here; don't bring me the
> next instance."

## What it corrects, and it was in the code as an identity

`shared_calibration_holds` was rebuilt earlier the same day to answer, from numbers, whether the
company's estimator and the world's response descend from one record. It came back INDEPENDENT.
The flag that consumed it read:

```python
"publishable_as_evidence_of_inference": not provenance["co_calibrated"],
```

and the verdict paragraph read:

> "The two sides no longer share a calibration source, so that gap now speaks to the company's own
> inference."

So the codebase encoded *independent therefore inferring* as an identity, in a field name and in a
sentence. Independence removes ONE objection — that the gap is two fits of one series disagreeing
about noise. It supplies no evidence for the positive claim. The live method scores **0.333 against
0.133–0.867 on six decisions**: it cannot be told from chance in either direction.

**Correcting the sentence would have left the rule nowhere**, and the next surface to quote the gap
would have had to rediscover it. So the rule has one owner.

## The rule, as three claims that are not the same claim

1. **The gap is a measurement**, and is always publishable as one. Nothing here withholds it.
2. **The gap is evidence of skill only if BOTH legs hold**: the two sides were arrived at
   independently, AND the method's own ranking clears the interval a random signal produces on
   this many decisions. Necessary and not sufficient, each of them.
3. **A large gap is not a large result.** The company sits outside the published band in 8 of 10
   years, by up to 17.3pp. That is *why* it is independent. A company that is simply wrong produces
   the same number as one that knows something, so every surface quoting the gap carries that
   clause.

   > **CORRECTED 2026-08-31, beside its subject rather than over it.** The first sentence stands;
   > the second half of this claim was **wrong**, and so was the count. Reading the distance as
   > *inaccuracy* requires the company's number and the band to count the same thing, and they do
   > not: the company's acted belief is `prior × ratio ** w`, where the ratio comes from realised
   > over predicted departures **on this supplier's own book** — a book-level departure hazard,
   > while the band is the GB market's switching rate. A supplier that retains better than average
   > sits far outside the band without being wrong about anything. The clause is withdrawn and the
   > distance now publishes as a distance, with `accuracy_reading_available: false` and its reason.
   > The **independence** leg is untouched, because that band test asks only whether this side's
   > series *is* the record — which needs no commensurability.
   >
   > The count "8 of 10 years, by up to 17.3pp" was separately stale: it measured the hand-authored
   > multiplier table replaced on 2026-08-31, and it is now computed live rather than written down.
   >
   > `docs/design/THE_ACTED_BELIEF_IS_A_BOOK_QUANTITY_2026-08-31.md`.

Composed from two `is True` tests and nothing else:

```python
supported = (independent is True) and (clears is True)
```

`None` — the fail-closed value on either leg — can never satisfy it. A missing skill reading, an
absent null spread, an unreadable artefact and an undecidable side all resolve to `None`. There is
no string, docstring or witness anywhere in the composition, for the same reason
`shared_calibration_holds` no longer has one.

## And "we cannot tell", in those words

Held as `inference_claim.CANNOT_TELL`, so a softer synonym cannot drift in beside a flag that still
says False. `cannot_tell_sentence()` computes whether a reading is inside its interval **from the
three numbers**, not from an `inside_the_null` flag the artefact carries: a flag is one more thing
that can rot, and the page must not be able to disagree with the arithmetic. It returns `None` when
the reading clears its null, so a render has nothing to decide and the caveat cannot become a
constant.

Applied to **two** figures on the capabilities page — the method concordance the director named,
and the belief AUC beside it. The AUC is the same class: a rank statistic on a handful of
departures, printed next to a claim about what the company knows. Applying it there rather than
waiting for that instance to be named is what "standing" means.

Live readings, for the record: concordance **0.333** inside **0.133–0.867** → the page says we
cannot tell. AUC **0.130** against **0.24–0.76** → outside, so it *does* clear its null, in the
unflattering direction, and the phrase correctly does not appear.

## Mutations, observed rather than intended

Ten run in all; the two that did not fire were established as equivalences rather than assumed to be.

| mutation | observed |
|---|---|
| `and` → `or` in the composition | **4 red** (predicted 2 — the conjunction is load-bearing in the undecidable branch too) |
| `(clears is True)` → `bool(clears)` | **0 red**, then 4 — see below |
| absent reading recorded as a failed one | **3 red** |
| `CANNOT_TELL` softened to "the evidence is early" | **1 red** in the unit suite, **1 red** through the door |
| interval dropped from the sentence | **1 red** |
| accuracy clause dropped | **1 red** |
| the page drops the `cannot_tell` render | **1 red** (door) |
| the page re-derives it from `inside_the_null` | **1 red** (door) |
| the page renders it unconditionally | **0 red** — equivalence: `prose(null)` is the empty string |

`bool(clears)` is an equivalence for everything `skill_reading` produces — it emits only
`True`/`False`/`None`, and `bool(None)` is already False. But `inference_claim` also takes an
INJECTED reading, and a JSON field carrying `1`, or a caller passing a truthy string, is how a
non-answer becomes an answer. `test_a_TRUTHY_NON_BOOLEAN_is_not_an_answer` makes the defensive line
load-bearing and the mutation now fires four ways.

## What this changed in the record

* `publishable_as_evidence_of_inference` keeps its name and gains the second leg. The name always
  meant "may this be published as inference evidence"; what it required was wrong. Keeping the name
  means every reader gets strictly more conservative, never less.
* Two new fields report the legs APART — `sides_are_independent` and `the_method_clears_its_null` —
  because they fail for different reasons and need different work: the first is fixed by re-fitting
  one side off a series the other cannot read, the second only by scoring more decisions. One flag
  hid which was binding.
* A test that **asserted the defect** was re-keyed.
  `test_the_refusal_LIFTS_when_the_sides_stop_sharing_a_source` held the codebase to
  `publishable is True` on independence alone. A test that pins a defect is worse than no test: it
  makes fixing it look like a regression. It is now
  `test_INDEPENDENCE_ALONE_DOES_NOT_LIFT_THE_REFUSAL`, with
  `test_the_refusal_LIFTS_when_BOTH_legs_are_satisfied` as the other half of the null.

## What is NOT decided here

Whether either leg can be discharged. The world's side is the published record by construction, so
independence today rests entirely on the company's estimator being **wrong** rather than on it
being independently derived — which is a weak form of the property, and the accuracy clause exists
so no reader takes it for a strong one. The honest discharge is
`shared_calibration_holds.what_would_discharge_it`: the company estimator re-fitted from its OWN
observed departures, which is what a real supplier has and this one does not yet use. That is a
piece of work, not a wording change.

**And the skill leg cannot be discharged by anything except more decisions.** Six is six. The
funnel that costs us the other fourteen is published on the page beside the figure.
