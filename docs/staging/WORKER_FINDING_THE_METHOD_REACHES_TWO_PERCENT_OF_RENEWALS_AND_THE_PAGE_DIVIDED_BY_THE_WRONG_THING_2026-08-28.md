**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE13_the_baseline_comparison_carries_its_bound`

# The per-customer arm reaches 2.07% of renewals, and the published page divided by the wrong denominator

Found while looking for something else — why the defending market's effect landed entirely outside
the decisions the company held a belief about
(`WORKER_FINDING_THE_DEFENDING_MARKET_IS_A_LEVEL_EFFECT_AND_MY_PREDICTION_WAS_WRONG_2026-08-28`).
The answer is in the artefact's own renewal funnel, which nothing was reading.

## The measurement

`value_cycle_ab_s1_three_arm.json` → `renewal_funnel.value_arm`:

| stage | renewals | share |
|---|---|---|
| `acquisition_term` — term 0, no prior term to price against | 398 | 32.9% |
| `not_the_arms_commodity` — gas; the arm is fitted to electricity only | 357 | 29.5% |
| `product_not_upliftable` — the drawn book carries no product label | 429 | 35.5% |
| **priced** | **25** | **2.07%** |
| **renewals the world offered** | **1,209** | |

**The company's entire per-customer pricing capability reaches 2.07% of the renewals its world
offers.** Every A/B figure this project has published — the arms comparison, the level-vs-selection
split, the −£9,627 the choosing is now worth — is a statement about those twenty-five decisions and
what they cascade into.

## Defect 1: the published denominator was accounts, and the numerator was renewals

`/capabilities/` rendered, verbatim, until this change:

> "The per-customer arm priced **25** renewals and the flat-at-level arm **34**, out of a book of
> **210** settled accounts."

A renewal numerator over an account denominator. 25 of 210 reads as roughly a **twelfth** of the
book. The honest figure is 25 of 1,209 — **one fiftieth**, six times smaller. The artefact has
carried `renewals_the_world_offered` all along and no consumer read it.

**Not a fabrication and not a rounding**: both numbers are true and neither belongs over the other.
This is the same shape as the error bar published beside a point estimate from a different world
(`WORKER_FINDING_THE_ERROR_BAR_ON_THE_LIVE_HEADLINE_IS_MEASURED_ON_THE_SUPERSEDED_CLOCK_2026-08-28`)
— two correct figures whose ratio is not a quantity.

**Repaired.** The panel now reads *"out of the 1,209 renewals the world offered — 2.07% of them.
The book is 210 settled accounts."* Both facts, neither dividing the other, because concentration
(nine accounts) and coverage (2.07%) are different things and the page needs both.

## Defect 2: the page attributed a three-cause exclusion to one cause, and named the smaller half

The same panel concluded:

> "The drawn population is refused by **one** eligibility guard: it carries no product label … So
> the surface is small by **PLUMBING, not by design**."

The funnel says otherwise. Of the 1,184 unpriced renewals:

- **755 (64%) are deliberate scope** — 398 acquisition terms with nothing to price against, and
  357 gas renewals the arm has never been fitted for. Both are designed limits, each documented at
  its own guard.
- **429 (36%) are the product-label gap** — the one cause the note named.

So the surface is small **by design AND by plumbing, and design is the larger half**. The note
named the smaller cause and generalised from it, which pointed a reader at the wrong repair: giving
the drawn book a product label would recover 36% of the exclusions, not the surface.

**Repaired, and DERIVED rather than rewritten.** `_attribution_sentence` computes the split from
the funnel's own stages, so it restates itself when the funnel moves. `_SCOPE_BY_DESIGN` names
which stages are scope, as data, because "is this exclusion deliberate" is a judgement and a
judgement inferred from a stage name drifts silently.

## Why this matters beyond the two sentences

The director's 2026-08-28 mission says **the enterprise value is the automated method for finding
customers, not the book**. The most basic question about a method is how much of its world it
reaches. That number existed in an artefact, was never published, and the figure standing in for it
overstated coverage sixfold.

It also bounds the defending-market result cleanly. The chase moves ~6 accounts across a
210-account book; the arm holds a belief at 25 of 1,209 renewals. The effect landing outside the
belief surface is close to what proportion alone predicts — so *"the world pressed where the
company was not looking"* is not a claim about the company's attention. It is a statement about the
size of the target.

## What is NOT claimed

- Not that 2.07% is wrong. All three exclusions are defended at their own guards, and one of them
  (`product_not_upliftable`) was settled by a determination on 2026-08-28
  (`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`).
- Not that widening it is right. Two of the three widenings are baseline-world changes, which R13
  reserves to fidelity evidence and never to making an experiment bigger.
- Not that the published A/B figures are wrong. They are correct statements about a surface whose
  size was, until now, published against the wrong denominator.

## R15

Both repairs are mutation-proven in `site/test_the_baseline_comparison_reaches_the_reader.py`:

- `test_the_coverage_denominator_is_renewals_and_not_accounts` — reverting the render to the
  account count reds it; it also asserts the two denominators are not the same number, so it
  cannot pass by them coinciding.
- `test_the_page_says_the_small_surface_is_design_as_well_as_plumbing` — classifying every
  exclusion as by-design reds it, and it carries a population floor of three stages so it cannot
  pass on an emptied funnel.

## WORK THIS CREATES

1. **The 2.07% belongs beside every A/B headline, not only in the decisions panel.** A reader who
   meets "£159,423 vs £154,699" first and the coverage three paragraphs later has already formed
   the impression.
2. **`A48` should score the method on this denominator.** "How reliably does the machine find a
   customer it can create value for" has a natural denominator now, and it is 1,209, not 210.
3. **The gas leg is 29.5% of renewals the arm cannot touch.** Fitting the arm to gas is a COMPANY
   change, not a world change, so unlike the other two it is not R13-reserved. It is the largest
   single widening available without touching the baseline world, and nothing has costed it.

## R11 — verified on the live surface, not on the generator

Fetched `https://poesys.net/data/value_arms.json` after the push (feed `generated_at`
2026-08-28T12:42:36Z):

```
decisions.renewals_the_world_offered        1209
decisions.value_arm_priced                  25
decisions.priced_share_of_renewals_offered  0.0207
decisions.book_accounts_settled             210
```

Both denominators are live and neither divides the other. The rendered sentence is asserted through
the door's own JavaScript in `site/test_the_baseline_comparison_reaches_the_reader.py` — a plain
text fetch of the page cannot see it, because the panel is filled from this feed at load.

## Still live
