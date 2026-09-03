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

---

## BLAST RADIUS: CHECKED, AND IT IS ZERO TODAY (2026-08-30, same evening)

The section above said this was not verified either way and was the first thing to check. Checked
rather than left as an inference:

| where | `publishable_as_evidence_of_inference` | `co_calibrated` |
|---|---|---|
| working tree, regenerated 21:44 | **true** | false |
| **origin/main, committed** | **false** | **true** |

**The refusal is intact on origin.** The flip exists only in the uncommitted working-tree artefact,
because publishing has been refused all day — the outage that cost eleven hours of site freshness
is the same thing that kept this off the record.

And a second, independent bound: `grep -rln "publishable_as_evidence_of_inference|co_calibrated"`
over `site/` and `tools/generate_*.py` returns **nothing**. No published surface reads either key
today, so even had it landed, the claim would have sat in an observability artefact rather than on
a page a reader sees.

**So no published figure is wrong right now, and the finding stays BLOCKING anyway.** The severity
is about the instrument, not about today's exposure: the next successful publish commits this
artefact, and the repair above is what has to land first. The window is exactly as long as the
publish outage, which is now closing.

*Recorded because "we could not check" and "we checked and it is clean" are different sentences,
and the first was standing in for the second.*

---

## REPAIRED 2026-08-30 — and the repair proved my own central claim WRONG

**Discharged:** `tests/tools/test_couple_value_based_pricing.py::test_the_verdict_is_READ_OFF_THE_NUMBERS_and_no_docstring_can_move_it`

Director's ruling: *"A witness that matches one sentence in one file was never a guard; it's a
tripwire that any unrelated edit can move. Rebuild it so it answers the actual question — do the
company's estimator and the world's response descend from the same record — and make it
fail-closed when it cannot tell. It should be impossible for a docstring change anywhere to lift
it."*

### The correction I owe first

**This document argued the two sides are "in substance MORE coupled than before". Rebuilt on
numbers, that is false, and it was reasoned from docstrings — the exact failure the old guard
had.** I read the company's source saying it descends from "the same public DESNZ/Ofgem series",
read the commons artefact citing Ofgem, ElectraLink and DESNZ, and concluded shared descent.
Measured:

| year | world reads | company implies | band |
|---|---|---|---|
| 2016 | 17.60 | **34.94** | 17.0–17.6 |
| 2017 | 14.00 | **30.27** | 13.5–14.0 |
| 2020 | 23.00 | **15.29** | 22.5–23.0 |
| 2022 | 4.30 | **7.08** | 2.9–4.3 |

The world is inside the published band in **10 of 10** years — it is the record. The company is
outside it in **8 of 10**, by up to 17.3 percentage points, and the two series correlate at 0.362
with opposite shapes (the company falls monotonically to 2022; the world peaks at 2020). They are
not two fits of one series. **The sides are genuinely independent, and the refusal lifting was the
right answer reached by a mechanism that could not have known it.**

The finding stands as filed on the mechanism and is withdrawn on the coupling. Kept beside the
original claim rather than edited over it.

### What the guard does now

Two legs, either of which means shared descent, and both fail closed on "cannot tell":

* **(a) both sides' year tables lie inside the published band** — then both ARE the record.
  `all`, not `any`: one side on the record with the other demonstrably off is not shared descent,
  and `any` there is the branch that publishes.
* **(b) the two sides are indistinguishable from EACH OTHER**, closer everywhere than the record's
  own band width. This closes the hole leg (a) leaves: two sides sharing a source that is *not*
  the record — live here, since the company's table "mirrors
  `simulation.market_switching_propensity`, reimplemented rather than re-derived" — would
  otherwise score independent.

Independence therefore requires **both** legs to fail. Nothing in it reads prose: the verdict
carries no `witness` and no `cites_the_series` field, so there is no string for a docstring edit
to match or stop matching.

### Two defects found in my own rebuild, both by running mutations rather than reading code

1. **A float artefact could have lifted the refusal.** The world's 2017 reading — the record read
   straight back out of itself — came to `14.000000000000002` against a band top of `14.0` and
   scored OUTSIDE, i.e. as evidence of independence. Fixed with an epsilon at the band's own
   quoted precision; pinned by `test_a_reading_exactly_ON_the_band_edge_is_INSIDE_it`.
2. **The first set of tests exercised the parts and not the verdict.** Four mutations were run and
   **three survived** — dropping leg (b), `all`→`any`, and `or`→`and` — because every one of them
   lives in the composition line while the tests only drove the two helpers in isolation. Three
   verdict-level controls added; all four mutations now fire, each on its own named test.

### And the three red tests are green for the right reason

They asserted the refusal while reading the LIVE verdict, so they were tests of today's tree and
could never exercise the other branch. `_belief_summary` and `price_belief_gap` now take
`provenance` injectably, so the refusal is tested in both directions rather than in whichever one
the tree happens to be in.

113 passed across the guard, the commons and the CLV coupling; 160 across the value-cycle A/B, the
gap-population class and the coupled-triad gate.
