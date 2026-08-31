**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# The company beside its ceiling, on one population at last — and it holds no belief about 61% of its own departures

**Found:** 2026-08-31, on the first capture that carries the company's independent churn belief on
the same rows as the world's own hazard. Instrument: `tools/measure_churn_heterogeneity.py`.
Ceiling: `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md`.

## Why this reading did not exist before today

The company's renewal-belief AUC has been published as **0.4653** and the world's ceiling measured
at **0.6760**, and **those two numbers could not be subtracted**: different populations, different
runs, pooled versus stratified. Two true numbers whose legs are different populations do not have a
difference, and this repository has published that mistake before.

This is both legs on **one capture, the same 144 renewal decisions, the same year×route strata, the
same within-stratum shuffle, the same seed.**

## The reading

**Renewal route — 144 decisions, 32 departures.**

| | AUC | null 95% | verdict |
|---|---|---|---|
| **CEILING** — the world's own hazard | **0.7400** | — | the most any model could do |
| `saas.churn_model.build_churn_risk` | 0.6815 | [0.3946, 0.6089] | orders who leaves — **but see below** |
| `company.crm.churn_model.estimate_churn_probability` | **0.4988** | [0.3829, 0.6241] | **we cannot tell** |

**The one belief that is independent of the outcome cannot be told from chance.** 0.4988 sits
almost exactly on the middle of its null. And the null is [0.383, 0.624] — **0.24 wide** — because
32 departures is a thin population, so this is not "the company is poor"; it is *"on 32 departures
this instrument cannot resolve whether the company knows anything."* Both halves of that sentence
are the finding.

**The belief that scores 0.6815 seeds the world's own roll.** `roll_lifecycle_event` takes
`build_churn_risk`'s number as `effective_p_retain` and then the roll is graded against it. Its
reading measures whether the world's adjustment chain preserves the ordering of the base rate it
was handed — a real property, but not evidence the company predicts anything. **No ratio is
published for either belief**, and the tool refuses each with its own named cause rather than
rounding a percentage that would read as a finding.

## The structural fact, and it is larger than either number

**50 of 82 departures — 61% — happen on the SVT route, and the company forms no belief about that
route at all.**

`saas.churn_model.build_churn_risk` is indexed on renewal anniversaries. `run_phase2b`'s SVT branch
builds its hazard with bill shock, price response and dissatisfaction all set to 0.0 and consults no
company estimate. There is no number to grade — not a gap in the capture, an absence in the company.

So the company's churn model is scored on the minority of departures it can see, and is **blind by
construction to the majority**. A supplier whose customers mostly leave by drifting off the default
tariff, and whose churn model only fires at renewal anniversaries, is not mis-calibrated. It is
looking somewhere else.

## And the SVT route's own per-factor table must not be quoted uncorrected

With exposure divided out — an SVT segment runs 1 to 92 days and a longer one is simply more time
in which to leave — **neither `sim_svt_inertia` nor `sim_action_propensity` alone clears its null,
while the composed hazard does.** The route's discrimination is in the product, not in either term.

This **corrects the landed ladder assessment**, which listed action propensity as one of the two
factors carrying rung 3 on the strength of its uncorrected 0.6421. On the renewal route (no
exposure confound) its contribution of +0.0527 stands; on the SVT route it does not, and the
assessment's "two factors carry rung 3" is narrower than published: **bill shock is solid, and
action propensity is solid only where exposure is not in the way.**

## What is owed

1. **A company belief on the SVT route.** This is the single largest gap between the company and its
   own book. A real supplier can see who is on its default tariff and for how long — years-on-SVT
   and segment length are both observable, and the company forms no view on either.
2. **More departures before the renewal leg is read again.** At n=32 the null is 0.24 wide and no
   company-side change could be detected. The reading is honest and it is nearly uninformative; a
   longer window or a larger book is what makes it say anything.
3. **Correct the assessment's rung-3 factor claim**, per the exposure paragraph above.

## Severity

**LATENT.** No published figure is wrong: the belief AUC already reaches the site with its interval,
and this adds the ceiling beside it rather than contradicting anything. What is new is that the
comparison is now *possible* and that its answer on the independent leg is **we cannot tell** — and
that a majority of departures were never in the company's field of view.
