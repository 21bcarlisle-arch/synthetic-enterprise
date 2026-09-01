# The validation ladder applied to satisfaction — a cohort share wearing a household's clothes

*Delivery seat, 2026-09-01. Director canon `DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31`,
work item 2: "each existing world variable assessed against the four rungs, with the result stated
on its Knowledge page."*

The third variable assessed, after churn (`LADDER_APPLIED_TO_CHURN_2026-08-31`) and household
consumption (`LADDER_APPLIED_TO_HOUSEHOLD_CONSUMPTION_2026-08-31`). Satisfaction is next because
the director's own choice-and-channel brief puts **customer service at 32% of the switching
decision, second only to price**, with the largest published per-household spread in that research
— and because it is one of the few axes a supplier can both observe (its own failures) and act on,
which is where inference advantage would have to come from if it exists.

**Subject:** `simulation/sim_satisfaction.sim_satisfaction_score` (the producer) and
`simulation/satisfaction_churn.satisfaction_churn_multiplier` (its only consumer).

---

## The headline

**The world's satisfaction score is denominated in one quantity and read as another.** Its
baseline and at least two of its four cohort deltas are *percentage-point differences in the SHARE
of a cohort that reports itself satisfied*. They are applied as decrements to *one household's
satisfaction level*. Those are different quantities, and the entire within-cohort spread that the
difference would account for is supplied instead by a **sha256 of the customer id**.

This settles a question the 2026-08-31 continuity repair explicitly left open. That work recorded
the level mismatch and refused to attribute it:

> *"The thresholds put 0.6% of the book above 0.80 and 11.4% below 0.50, against a published Wave
> 20 distribution of 38% very satisfied and 6% dissatisfied. Whether that is a mis-calibration of
> the cuts or a mis-mapping from a 5-point Likert to this 0-1 latent score is NOT established, and
> picking one would be inventing the answer."*

It is the **mis-mapping**, and the evidence is in the model's own citations rather than in a new
assumption.

---

## The evidence, from the model's own sources

`sim_satisfaction.py` cites Ofgem/Citizens Advice *Energy Consumer Satisfaction Survey* Wave 20
(BMG Research, fieldwork Jan 2025, n=3,854) for three of its terms. Read the citations against the
constants:

| term | what the cited source says | the delta applied |
|---|---|---|
| `BASELINE_SATISFACTION` | net satisfied swings 66%–81% across 20 waves; 80% in Jan 2025 | **0.70** |
| `_PAYMENT_CHANNEL_DELTA` | Direct Debit **82%** satisfied vs Standard Credit **76%** — a 6-point gap | **−0.06** |
| `_INCOME_STRESS_DELTA` | "doing well" **89%** vs "financially vulnerable" **66%** — a 23-point gap | **−0.05 / −0.15** |

The payment-channel delta is the published share gap **exactly**: six points became 0.06. The
baseline is a population share. These are cohort-level proportions used as individual-level
magnitudes.

### The check that needs no assumptions at all

Both gaps come from one survey, one wave, one question. Their **ratio** is therefore a real
quantity, and it is scale-free — it needs no view on what the score's spread should be, no
threshold, no distributional shape:

    published, in probit (standard-deviation) units:   0.2091 / 0.8141  =  0.257
    the world, in its own score units:                 0.06   / 0.15    =  0.400

**The world's payment-channel effect is 1.56× too strong relative to its income-stress effect.**
Both deltas cite the same table. They cannot both be right, whatever the score's spread is.

*(Method: a difference in the share of a cohort above a common cut is a difference in location,
measured in standard deviations, of `Φ⁻¹(share)`. That is the standard reading of a published
proportion as a latent shift and is why the two are comparable at all.)*

### The within-cohort spread is a hash, measured

Over all 96 circumstance combinations the model can express (bill shocks 0–3 × tenure {0,2,5,9} ×
three income-stress tiers × two payment channels), with the per-customer term off:

| | |
|---|---|
| **between-cohort** spread (sd of the cohort means) | **0.1382** |
| **within-cohort** spread (sd of `_individual_variation`) | **0.0234** |
| ratio | **1 : 5.9** |
| share of within-cohort spread that is `sha256("satisfaction_variation_" + customer_id)` | **100%** |

The cited source says the opposite. Wave 20's own finding is that respondents who share the same
coarse classification still split materially underneath it — *"very satisfied 38% vs satisfied 42%,
roughly a 47/53 split"* — and that this holds **within** one payment-type or vulnerability cohort.
Real within-cohort spread is of the same order as between-cohort spread. Here it is a sixth of it,
and all of it is a hash.

---

## Against the four rungs

### Rung 0 — red lines: **NOT BUILT**

No wide feasible range from published evidence exists for this variable, so "not absurd" cannot be
distinguished from "not checked". Owed, and cheap: Wave 20 gives 20 waves of net-satisfied between
66% and 81%, which is a published range and a wide one.

### Rung 1 — level: **FAILS, and the failure is a unit error rather than a calibration**

0.6% of the book sits above the consumer's high threshold and 11.4% below its low one, against a
published 38% very satisfied and 6% dissatisfied. The canon's warning applies to the obvious
repair: moving the thresholds until those shares match would be **clamping an aggregate to pass a
check** — it would produce a green measurement of a world that still cannot represent a satisfied
household, because the score would still have no within-cohort spread to distribute across the
bands.

The honest reading of "0.6% vs 38%" is that it compares **a distribution of cohort means to a
distribution of individuals**, and a distribution of cohort means is always tighter. It is two true
numbers whose ratio is not a quantity — this project's most-filed publishing defect, here inside a
model rather than on a page.

### Rung 2 — mechanism: **FAILS, and it currently runs BACKWARDS**

`WORKER_FINDING_THE_WORLDS_SERVICE_RISK_IS_CANCELLED_BY_A_MODULATOR_THAT_SHARES_ITS_DRIVER_2026-08-31`
measured, on 144 renewal decisions, that the households the world models as **most dissatisfied
leave at a third the rate of the most satisfied** (0.083 against 0.243), because
`corr(dissatisfaction_response, action_propensity) = −0.5188`: two of the four departure risks are
one variable seen twice, and the second cancels the first.

The canon's rung 2 asks whether the variable responds to its drivers the way we understand it
should. It responds with the wrong sign at the outcome. That finding stands and this document does
not supersede it — it adds that the *relative magnitudes* of the surviving drivers are wrong too,
by 1.56× between the only two that carry citations.

### Rung 3 — heterogeneity: **FAILS, and this is the one that matters**

The canon: *"Do individual customers within the population make different choices, for hidden
reasons of their own... Are those reasons ones a supplier could in principle observe or infer
through a channel it actually has?"*

Within a circumstance cohort, the only thing separating one household's satisfaction from
another's is `sha256("satisfaction_variation_" + customer_id)`. **A hash of an identifier is not a
reason of the household's own, and it is unobservable and uninferable by construction** — there is
no channel through which a supplier could learn it, because there is nothing to learn.

This is not a criticism of the term's author, whose own comment is scrupulous about what it is:
*"an honestly-flagged CALIBRATION CHOICE, not a directly published per-customer standard
deviation."* It was added to fix a worse state (every household in a cohort scoring identically)
and it did. The finding is that a placeholder for heterogeneity became **all** of the
heterogeneity, and rung 3 is the rung that asks whether there is anything to infer at all.

Consequence, stated plainly: **on the axis the director's brief puts at 32% of the switching
decision, this world contains no per-customer signal.** Every A/B result that leans on service is
measuring cohort membership.

---

## The repair, and why its parameters are derived rather than picked

The canon requires repairs to go **downward, to the individual model**, never to the aggregate. The
construction that does that, with a published anchor for every parameter:

**Make the score a percentile of the GB satisfaction distribution.** Each household holds a latent
satisfaction; the score is its rank in the population. Then:

1. **Every published share becomes a quantile directly, with no conversion.** 80% satisfied means
   the "satisfied" cut sits at the 20th percentile; 38% very satisfied puts that cut at the 62nd.
   The unit error cannot recur, because a cohort share and a household percentile are then
   different objects by construction and the code has to say which it holds.
2. **Cohort effects become location shifts in standard-deviation units**, read off the published
   shares by `Φ⁻¹`: payment channel 0.209σ, income stress 0.814σ. Both are derived from the cited
   table rather than transcribed from it, and their ratio is right by construction.
3. **The within-cohort spread is DERIVED, not invented** — and this is the part worth stating,
   because the current comment says no source publishes it. That is true and it does not matter:
   two published quantiles of one distribution determine its spread. Wave 20 gives both 80%
   satisfied and 38% very satisfied. Given a shape, those two constraints fix the location and the
   scale. **A number nobody publishes can still be established from numbers people do publish**,
   and that is the difference between deriving a constant and picking one.
4. **The hash is replaced by a draw the household owns** — driven by an attribute it already has,
   so that the variation is something a supplier could in principle infer. Which attribute is the
   open question below, and it is a knowledge question, not a modelling preference.

### What is still open, stated rather than assumed

1. **Which household attribute carries the residual satisfaction variation.** Wave 20 establishes
   that within-cohort spread exists and is large; it does not say what it is *of*. Candidates the
   world already holds: complaint history, contact-centre history, read-estimation error, and the
   company's own service failures. The first two are observable to a supplier by definition, which
   is exactly what rung 3 requires — but "the world already holds it" is not evidence that it
   drives satisfaction, and that evidence has to be found before it is wired.
2. **The distributional shape.** Normal is the default and it is a choice; log-normal or a beta on
   0–1 would fit two quantiles equally well and give different tails. The tails are where the
   churn multiplier's thresholds bite, so this is not cosmetic.
3. **Rung 2's sign.** The repair above changes the *distribution*; it does not by itself fix a
   response that runs backwards. That is the 08-31 finding's own repair and it must land first or
   a better-distributed variable will simply push harder in the wrong direction.

---

## Not done here, and why

**No constant in `simulation/` is changed by this document.** Everything above is a fidelity change
to the churn chain, and this project's own rules say what that needs: a pre-registration filed
*before* the run stating what the level, the spread and the discrimination must show; a
one-variable run so the move can be attributed; and the prediction kept beside the result whether
or not it was right. It also moves every financial figure the project publishes, since satisfaction
multiplies churn and churn drives the book.

**Order.** Rung 2's sign first (the 08-31 finding), then this. Doing them together would change two
variables and forfeit the attribution — which is the rule that exists here precisely because it has
been broken before.

## Where this variable's rung status lives

The same answer the churn document reached, for the same reason: satisfaction's Knowledge page
would be `site/knowledge/how-households-choose`, whose `wall_placement` is *"Public-reality commons
only… no figure produced by this project's simulation appears on this page."* **A rung status is a
simulation reading** — 0.1382 is what this world does, not what Ofgem published — so putting it
there breaks the one property that makes the commons quotable by every lane.

The status therefore lives where a reader of the *variable* meets it: this document, and the
module's own docstring. Three variables now have assessments and none has a machine-readable
status; a register with a control that every world variable names all four rungs is now warranted
by the churn document's own trigger ("when the second and third variables are assessed"). **It is
the next thing owed on this canon item**, and it is deliberately not built here, because building
it in the same pass as the third assessment would be building the watcher out of one afternoon's
work.
