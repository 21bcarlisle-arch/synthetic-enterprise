**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

*LATENT and not BLOCKING, deliberately: the one published figure this refutes — the SVT per-factor
table quoting `sim_action_propensity` at 0.6421 ALONE — is corrected on the ladder page in the same
commit that files this, and the old table is kept marked superseded rather than deleted. No control's
verdict is invalidated and nothing else published rests on it.*

# The company forms no belief on the route carrying 61% of departures — and where it does form one independently, it reads at chance

**Filed 2026-08-31, worker tick, Lane 0.** Instrument: `tools/measure_churn_heterogeneity`.
Control: `tests/architecture/test_the_ceiling_and_the_belief_count_one_population.py` (7 mutations
proven). Artefact: `docs/reports/ladder_churn_ceiling_vs_belief.json`. Written up in
`docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md`, §"The company beside the ceiling".

---

## The finding, in one table

One capture — `ladder_churn_factors_continuous_satisfaction.json`, verified row-for-row against
`run_output_latest.json` on all 144 realised hazards. One stratification (year × route). One
permutation null, same seed, same shuffle, fed to the same estimator for every leg.

| route | decisions | departures | CEILING | company belief | verdict |
|---|---|---|---|---|---|
| renewal | 144 | 32 | **0.7400** | `company_churn_estimate` **0.4988** | **inside its null** |
| renewal | 144 | 32 | 0.7400 | `build_churn_risk` 0.6815 | clears, **but seeds the roll** |
| svt_segment | 1,266 | **50** | **0.6721** | — | **no belief exists** |

**Two things, and the second is the bigger one.**

1. **On the renewal route the company's independent belief carries no ordering.**
   `company.crm.churn_model.estimate_churn_probability` is the only company-side belief that does
   not feed `effective_p_retain`. On the same 144 decisions where the world's own hazard scores
   0.7400, it scores **0.4988 inside a null of [0.3829, 0.6241]**. Its *level* is fine — mean
   believed 0.2713 against a realised 0.2222 — it simply does not say which household goes.
2. **On the SVT route there is nothing to grade.** 50 of the book's 82 departures — **61%** — leave
   by drifting off the standard variable product, and no company belief is formed about any of them.

## Why (2) is structural and cannot be closed by capturing more

* `saas.churn_model.build_churn_risk` is indexed on **renewal anniversaries**: `_renewal_periods`
  walks `acquisition_date + n × 365 days`. A segment boundary is not an anniversary, so there is no
  entry to record.
* `simulation/run_phase2b.py`'s SVT branch builds its hazard with `bill_shock_base=0.0,
  price_response=0.0, dissatisfaction_response=0.0` and **consults no company estimate**. The
  comment at the site already said it: *"there was no renewal decision to estimate a churn
  probability FOR."*

**This is a model that never looked, not a model that looked and failed.** A low AUC on that route
would have been the better news, because it would mean an estimator existed to improve.

## Why the tempting comparison was refused, twice, in code

The ladder page correctly refused to put the published 0.4653 beside 0.6760 — different
populations, different runs. That refusal is now mechanical rather than prose:
`measure_churn_heterogeneity.ceiling_vs_belief` emits a "fraction of the ceiling captured" **only**
when all three of one-population, independent-of-the-roll, and clears-its-own-null hold. On this
book neither belief qualifies:

* `build_churn_risk` scores 0.6815 and **seeds the world's roll** — `roll_lifecycle_event` starts
  `effective_p_retain` from that same number. The world's strongest oracle factor on that route is
  `sim_bill_shock_base` (+0.1335) and the belief is a pure function of the bill-shock count. That
  leg measures the world's adjustment chain preserving the ordering it was handed; it says nothing
  about inference and must never be quoted as if it did.
* `company_churn_estimate` is inside its null, and the ratio it yields is **−0.5%** — a percentage
  with the authority of a measurement and the content of noise. Refused, not rounded to zero.

## What else moved, and it is a correction

**The exposure offset removed both SVT per-factor readings.** Segments run 1–92 days. Per
exposure-day the route still clears (0.6091, null [0.4159, 0.5850]) — but `sim_svt_inertia` reads
0.4629 alone and `sim_action_propensity` 0.5067 alone, **both inside their null**, while the
composed hazard clears. The earlier claim that action propensity "is the strongest single
discriminator on the route that now carries most of the departures" is **withdrawn**: it was
crediting a term with what the billing calendar was doing. The ladder page keeps the old table
marked superseded rather than deleting it.

## What this does not say

It does not say the company's churn model is badly built, and it does not say the company is worse
than the world — **independence is not inference**, and a belief that seeds the roll is not evidence
either way. It says there was real signal to find on both routes, that the one belief gradeable
independently found none of it, and that on the route carrying most departures no belief is formed
at all.

## Next, and it is not a re-tune

The two carrying oracle factors are both observable to a supplier — bill shock (it issues the bill)
and action propensity (payment behaviour, arrears, tenure). `estimate_churn_probability` already
takes a rate-move term, a bill-stress term and a tenure term. **So the question is not what the
company would need to see; it is why what it already sees produces no ordering.** That is the next
measurement, and it is a decomposition of the company's own estimator against the same 144
decisions — not a change to any constant. R12: every figure here is a diagnostic.

---

## MERGED IN, 2026-08-31: a duplicate of this finding was filed independently and is retired into it

`WORKER_FINDING_THE_COMPANY_FORMS_NO_BELIEF_AT_ALL_ABOUT_61_PERCENT_OF_ITS_DEPARTURES_2026-08-31.md`
(landed `9b3aa883b`, minutes after this one) is the same defect, found the same way, from the same
capture. **The staging root is a ranked work queue, and two entries for one item mis-rank it** — so
the duplicate is deleted rather than left beside this. This one is kept because it carries the
control, the persisted artefact and the sharper next step; nothing is lost but the second copy.

**The one thing the duplicate said that this did not, carried across:**

> **The renewal leg cannot be re-read usefully until there are more departures.** At n=32 the null
> is **[0.383, 0.624] — 0.24 wide**. No company-side improvement short of an enormous one could
> move a reading outside that band, so *"we cannot tell"* here is a statement about the
> **instrument's resolution**, not a verdict on the company. Re-running the same measurement after
> a company change and reading the difference would be reading noise. A longer window or a larger
> book is what makes this leg say anything, and that is a precondition on the next measurement
> rather than a caveat under it.

Same class as `project_instrument_resolution_is_seventeen`: what the instrument *could* have
detected is part of the reading, and both this finding's legs are near that limit — the renewal leg
by departure count, the SVT leg by having no belief to grade at all.
