**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `A45_the_canon_is_a_standing_subject`

# A publication refusal lifted because a sentence moved, not because the two sides became independent

**Found:** 2026-08-30, running the publisher's gate scope after clearing the publish blockers.
Three red tests in `tests/tools/test_couple_value_based_pricing.py` are the symptom; they are
**correctly red and must not be made green against the new answer.**

Filed BLOCKING on the definition: *"a control or instrument in this area is untrustworthy, or a
published figure may be wrong."* Both apply.

## What the refusal is for

`tools/couple_value_based_pricing.shared_calibration_holds()` asks whether the company's churn
estimator and the world's churn response *"still descend from ONE series"*. If they do, the
published belief-vs-truth gap is refused as evidence of inference, with this reasoning in the
module itself:

> The number above is a real measurement of a real disagreement; what it is NOT is evidence that
> the company inferred anything. Published without this, a median of a couple of percentage points
> reads as "the company nearly knows the world" — which is exactly what two calibrations of one
> series look like, and exactly what a reader will quote it as.

That is the thesis's central guard. `publishable_as_evidence_of_inference` is literally
`not provenance["co_calibrated"]`.

## It flipped today, and the mechanism is a string match

```
co_calibrated: False
  world     cites_the_series=False   source=simulation/market_switching_propensity.py
  company   cites_the_series=True    source=company/crm/market_conditions.py
witness: "DESNZ electricity switching series 2015-2025, cross-referenced with the Ofgem
          Consumer Engagement Survey"
```

`cites_the_series` is `witness in <file>.read_text()` — one sentence, one file.

The world's side stopped containing that sentence today because the anchor work **removed a false
claim**, and removing it was right. `market_switching_propensity._savings_to_rate`'s docstring now
says:

> IT IS NOT CALIBRATED TO THE DESNZ SWITCHING SERIES AND ITS DOCSTRING CLAIMED IT WAS until
> 2026-08-30 ... this curve at each year's own savings runs 2.04x below the published record on
> the 2017-2024 mean, and wrong in shape as well as level.

So the sentence was a lie and deleting it is a correction. **But the refusal was keyed to the
sentence, so deleting the lie lifted the refusal.**

## And the sides are, in substance, MORE coupled than before — not less

The world's departure level no longer comes from that curve at all. It comes from
`simulation/departure_level_anchor.YEAR_LEVEL_ANCHOR`, fitted onto `market_departure_rate`, which
reads `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`. That artefact's
own provenance mentions **Ofgem 7 times, ElectraLink 3, DESNZ 2**.

The company's side (`company/crm/market_conditions.py`) says of itself: *"Ofgem Consumer
Engagement Survey, DESNZ switching statistics, Cornwall Insight ... from the same public
DESNZ/Ofgem series) but is reimplemented independently."*

So both sides now descend from the published GB domestic switching record. The world arguably
descends from it **more** genuinely than yesterday, when its claim to do so was false.

**The record therefore says "independent" at the exact moment the two sides became more
co-calibrated, and a published figure is now cleared to be presented as evidence of inference.**

## Why the module's own fail-closed doctrine did not save it

`shared_calibration_holds` is explicitly fail-closed and says so:

> A witness file that cannot be read leaves the pair recorded as CO-CALIBRATED and therefore
> unpublishable, because "we could not check" is not "they are independent" — an unavailable check
> is a failed check.

That covers an **unreadable** file. It does not cover a file that reads perfectly and is no longer
the subject. The world's level moved to another module and the witness stayed pointed at the old
one — the "control keyed to a structure that moved" class, failing in the dangerous direction:
silently certifying independence rather than silently refusing.

## What is owed, and what must NOT be done

**Must not:** update the three tests to expect `publishable_as_evidence_of_inference is True`.
They currently encode the correct property and would be cementing a false lift. They are red
because the world moved, which is what a control keyed to a property is supposed to do.

**Owed:** re-point the world-side witness at where the world's departure level actually comes from
— `simulation/departure_level_anchor.py` and the commons artefact behind it — and re-derive
`co_calibrated` from that. On the evidence above it should come back TRUE, the refusal should
reinstate, and the three tests should go green again for the right reason.

Then the harder question, which is the real one and is not mine to answer alone: **if the world's
level is now the published record and the company's estimator is the same published record, the
belief-vs-truth gap may not be publishable as inference evidence at all until one side is genuinely
independent of it.** That is a question about what the project can claim, so it is recorded here
and raised rather than resolved.

## Bound on the blast radius

`docs/observability/value_based_pricing_arms.json` carries
`publishable_as_evidence_of_inference` and `co_calibrated_from`, and the verdict paragraph carries
the co-calibration clause. Whether today's flip has already reached a published surface depends on
whether that artefact regenerated since the anchor landed — and publishing has been down all day,
which for once is the reason to think it has not. **Not verified either way here**, and it is the
first thing to check when publishing recovers: if a run has published with the refusal lifted, the
site is making a claim this finding says it cannot support.
