# The acted belief is a BOOK quantity, and the accuracy clause was grading it against a MARKET one

**Determination. Delivery seat, Lane 0, 2026-08-31.** The stretch that landed
`docs/staging/SEAT_FINDING_THE_COMPANYS_ACTED_BELIEF_IS_INDEPENDENT_OF_THE_RECORD_AND_WORSE_THAN_IT_2026-08-31.md`
repointed the co-calibration guard's company leg from the prior to the posterior the company
actually prices on, and published the result. It also published a reading of that result —
*"The company's estimator is outside the published band in 4 of 6 years, by up to 16.5pp — so this
is independence and inaccuracy at once"* — without settling whether the two numbers in that
comparison count the same thing. Its own §3 said in the same breath that they might not.

This document settles it. **The answer is (b): the posterior is a belief about this book and not
an estimate of the market rate.** The accuracy clause is therefore withdrawn and replaced, the
independence leg stands with its reason stated, and route (a) is refused for a structural reason
rather than a difficulty one.

---

## 1. The question, as the direction put it

> **(a)** The posterior IS meant to estimate the market rate — in which case the update is
> mis-specified, because a supplier that retains better than average observes fewer departures
> without the market being any less competitive, and the missing piece is a link separating *how
> competitive the market is* from *how retainable my book is*.
>
> **(b)** It is a belief about this book and not about the market — in which case the accuracy
> clause compares a book quantity to a market quantity and must be renamed or withdrawn from the
> page.

Neither route is "widen the band", and neither is "fit a correction factor".

---

## 2. Three arguments, and the third is the one that decides it

### 2.1 What the number is used for is a book quantity, everywhere

`company/crm/competitive_pressure.derived_market_pressure_multiplier(renewal_year)` is the drop-in
for the year table. Its consumers are `enriched_churn_estimate` (lines 104/139) and
`churn_model.estimate_passive_churn_probability`. Both scale **this company's own per-account
probability that this account leaves at renewal**. No consumer anywhere reads it as a market rate.

The single caller that does read it as a market rate is the guard —
`tools/couple_value_based_pricing._company_posterior_readings` converts multiplier back to percent
against the prior rate table and hands it to `_agrees_with_the_record`. That conversion is where a
book hazard acquires a market label, and it acquired it for the guard's convenience rather than
because anything in the company believes it.

### 2.2 The prior supplies the SHAPE; the book supplies the LEVEL

`posterior = prior × ratio ** w`. The prior is the published GB series — a market-wide rate whose
year-to-year movement is the only part of it the company has evidence for. The ratio is
`realised departures / predicted departures` over this company's own closed renewals, precision
weighted. At `w = 0.82–0.89` on 85–368 closed decisions, the ratio is doing most of the work, and
the ratio is definitionally a property of **one book**.

So the *level* of the posterior is a book level. The published band is a market level. The
comparison `_agrees_with_the_record` performs is between two levels that were never the same
quantity. This is the project's own rule, unheeded: *before dividing (or differencing) two numbers,
say out loud what each one counts.* Here it is a difference rather than a ratio, and the failure is
identical.

Concretely: a supplier churn rate decomposes, to first order, as

> supplier churn ≈ market switching rate × (that supplier's retention relative to the market)

The update folds both factors into one number and carries no term that could separate them. 2018
reads 3.04% against a band of 19.5–20.0%. Under the accuracy reading that is a 16.5pp error. Under
the book reading it is a sticky book in a competitive year, which is a perfectly ordinary thing for
a supplier to be, and not an error at all. **The published record cannot tell those two apart, and
neither can the guard.**

### 2.3 Route (a) is self-defeating, which is what settles it

Route (a) asks for a link separating market competitiveness from book retainability, stated in
terms a real supplier can observe. Take that seriously and ask what observable could supply it.

A supplier observes: its own book, its own priced renewals, its own realised departures, and the
**published market series**. It does not observe any other supplier's book, its own share of
switches, or who its leavers went to. Its only market-level observable is the published series.

Therefore any link that de-biased the book's ratio into a market estimate would have to use the
published series to do it — and the "market" half of the result would then *be* the published
series again. The independence the stretch just bought would be spent buying back a number the
world's leg already reads out of the same file. Route (a) does not merely require work we have not
done; **it requires the company to re-import the record it just stopped depending on**, and the
guard would score the pair co-calibrated again — correctly.

That is not a reason to widen a band or to fit a factor. It is a reason the quantity is not
available to this company at all, and CLAUDE.md is explicit about what to do with a quantity
nothing establishes: carry the gap, not a placeholder that looks like an answer.

**(a) is refused. (b) is the determination.**

---

## 3. What follows, and what does NOT

### 3.1 The accuracy clause is withdrawn and replaced — not deleted

The clause did a job worth keeping: it stopped a reader taking the *size* of the gap as the *size*
of the insight. Under (b) that job gets bigger, not smaller. The distance to the band is not
evidence of error **and it is not evidence of insight either**, because the two numbers count
different populations, so nothing about the company's competence can be read off their difference
in either direction.

So `tools/inference_claim.accuracy_clause` becomes `record_distance`, reports
`accuracy_reading_available: False` with its reason, and its prose states the distance as a
distance and names both populations. The withdrawal is filed under
`site/data/value_arms.json → withdrawn_claim` by the same route every other withdrawal on that page
takes, so a reader can see the correction rather than find a sentence quietly gone.

**This is the flattering direction and it is stated as such.** Withdrawing "the company is
inaccurate" makes the page read better. What makes it the honest move rather than the comfortable
one is that nothing replaces it: the page does not gain an accuracy reading, it loses the ability
to make one. A measurement is downgraded to *cannot tell*, in those words, which is the fail-closed
direction. If the replacement had said "and by the right comparison the company is accurate", that
would have been the comfortable move, and there is no such comparison available.

### 3.2 The independence leg STANDS, and here is why the same measurement answers one question and not the other

The band test in `_agrees_with_the_record` is a **provenance** test. It asks: *is this side's
series the record?* The posterior equals the record exactly when the book adds nothing — `ratio = 1`
or `w = 0` gives `posterior = prior`, and the prior is the record's rate. The only thing that can
move it off the band is the company's own realised departures, which are not in the record and
cannot be derived from it.

So sitting outside the band demonstrates that the number carries information the record does not.
That is exactly what independence asks, and it does not require the two quantities to be
commensurable — only that one is not a copy of the other.

It does **not** demonstrate the number is wrong. That would require them to be commensurable, and
they are not.

One measurement, two questions, only one of them answerable from it. Both readings were being taken
from the same list of `years_outside_the_band`, which is how a single fact came to support a
conclusion it cannot carry.

### 3.3 The structured companion is published

`tools/generate_value_arms_data._inference_claim` published only `accuracy_clause` — the prose —
and dropped the dict behind it, so `inference_claim.accuracy` read `null` on the published surface
while the reader-facing sentence carried live numbers. A figure a reader can see and nothing
downstream can check is the shape this project has been bitten by repeatedly. The whole
`record_distance` dict is now published, and a door leg fails if the counts in the rendered
sentence have no machine-readable companion beside them.

---

## 4. What this costs, said plainly

The company now holds a competitive-pressure belief that is genuinely its own, inferred from its
own observations — the move from ACCESS to INFERENCE the thesis demands — **and there is no longer
any published series it can be scored against.** Its accuracy is not merely unmeasured; it is
unmeasurable from anything on this side of the wall.

That is the first measured evidence that the epistemic wall costs us something, and it is the
finding, not a defect to route around. It also relocates the whole burden onto the second leg of
`inference_claim`: whether the method's own ranking clears the interval a random signal produces.
That leg is binding, it is currently `false` (0.517 against 0.429–0.572 on 86 decisions), and it is
now the *only* route by which anything the company believes about departures can ever become
evidence of skill. The discharge is book depth. It was already book depth for a different reason;
it is now book depth for the only reason.

---

**Landed with:** `tools/inference_claim.py`, `tools/generate_value_arms_data.py`,
`tests/tools/test_inference_claim.py`, `site/test_the_baseline_comparison_reaches_the_reader.py`,
`site/data/value_arms.json`. Correction filed beside its subject in
`docs/design/INDEPENDENCE_IS_NOT_INFERENCE_2026-08-30.md` §3.
