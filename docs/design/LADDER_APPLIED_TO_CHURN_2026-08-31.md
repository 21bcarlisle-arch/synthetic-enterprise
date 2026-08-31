# The validation ladder applied to churn — where the variable stands on each of the four rungs

**Canon:** `docs/staging/DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31.md`.
**Instrument:** `tools/measure_churn_heterogeneity.py` (new). **Control:**
`tests/architecture/test_churn_carries_per_customer_signal.py` (new, seven mutations proven).
**Subject:** `docs/reports/ladder_churn_factors.json` + `..._svt_segment_decisions.json` — **1,410
decisions across both departure routes, 82 departures, 2016–2025**, captured for this assessment.
**Every live figure on this page is the CONTINUOUS-satisfaction capture** — item 1, landed the same
day — and those two files now hold it, carrying `company_churn_estimate` as well so the belief legs
below are reproducible from the tree rather than from a run that has gone. The pre-item-1 BUCKETED
capture is in git history only; every reading still shown from it is marked superseded where it
appears. The published readings are `docs/reports/ladder_churn_ceiling_vs_belief.json`, and
`tests/architecture/test_the_ladder_page_quotes_the_report.py` fails if this page and that artefact
drift apart — which they had, for six hours, on the renewal table below.

The canon requires every world variable to *say where it stands*. This is churn saying it.

| rung | verdict | on what evidence |
|---|---|---|
| **0 — red lines** | **DOES NOT EXIST** | there is no wide feasible range for churn anywhere in the repo; the narrow published band is doing both jobs |
| **1 — level** | **PASSES, top-down, and stale** | fitted onto the band's high endpoint, 10/10 years, by a per-year scalar — on a population that has since lost 69% of its rows |
| **2 — mechanism** | **PASSES ON DIRECTION, NOT ON MAGNITUDE** | the price-side split is +100.75pp / −53.99pp; the sensitivity that sets its size is unidentified by its own docstring |
| **3 — heterogeneity** | **PASSES, ON TWO OF SIX FACTORS** | oracle AUC 0.6760 against a null of [0.4184, 0.5780]; bill shock and action propensity carry it, and two factors contribute nothing |

---

## Rung 3 first, because it had never been measured and it is the thesis

**Reading: the world's own realised hazard discriminates who leaves at AUC 0.6760, against a
permutation null of [0.4184, 0.5780] (median 0.4986, 2000 shuffles). It clears.** So there *is*
something to infer. Rung 3 passes.

Four things make that reading mean what it says rather than something flattering.

**It is an ORACLE reading, not a model score.** The score is the world's own realised departure
probability for each household at each decision — ground truth the company may never see. So
**0.6760 is the ceiling.** No company model can beat the hazard that generated the outcome. That
number is the missing denominator for a month of company-side results.

**It is stratified by year AND route, and both exclusions are load-bearing.** Two of the terms
reaching the renewal hazard (`sim_level_anchor`, `sim_market_opportunity`) take one value per
calendar year. And the two routes run mean hazards **5.7× apart** — 0.211 at a renewal, 0.037 at an
SVT segment. Pooled across routes the same reading is **0.7445**: a score that knew only which
product a household sat on would discriminate, and **that is product structure, not a hidden reason
of anyone's own.** The 0.069 difference is the size of what is being excluded, and it is printed
rather than asserted.

**It carries its null.** 82 departures is a small population and an AUC on it wanders. The null
shuffles labels *inside* each stratum, preserving each stratum's departure count and destroying only
the pairing — beating an across-stratum shuffle would only prove that years and products differ,
which they do and which nobody asked.

**It covers the whole book, which took a repair to be able to say.** See rung 1: C1b added a
departure route the capture could not see, and 61% of this book's departures are on it.

### Where the signal is, and where it is not

**Renewal route — 144 decisions, 32 departures. AUC 0.7400, null [0.3794, 0.6206].**

> **REFRESHED 2026-08-31, later the same day — this table used to be the BUCKETED world's and was
> the last thing on the page still reading it.** Item 1 made `sim_dissatisfaction_response`
> continuous, and the SVT table below got its superseded banner the same hour while this one did
> not, so the page carried two captures at once and said **+0.0527** here and **+0.0539** eighty
> lines down for the same quantity. The figures below are now `docs/reports/`
> `ladder_churn_ceiling_vs_belief.json`, the same artefact the ceiling-vs-belief section reads, and
> `tests/architecture/test_the_ladder_page_quotes_the_report.py` fails if they drift apart again.
>
> What moved, and it is small everywhere except the row the repair was aimed at: route AUC
> 0.7412 → **0.7400**; bill shock HELD OUT 0.6054 → 0.6066, contribution +0.1358 → **+0.1335**;
> action propensity HELD OUT 0.6885 → 0.6862, contribution +0.0527 → **+0.0539**; price response
> HELD OUT 0.7342 → 0.7143, contribution +0.0070 → **+0.0258**; and dissatisfaction ALONE
> 0.4672 → **0.3806** with ties 92.0% → 0.2% and 3 → 135 distinct values, which is item 1's whole
> point and is worked through below. **The ALONE column for the other three did not move at all,**
> and that is why this went unnoticed: freezing every other factor at its population mean makes a
> factor's own ALONE score invariant to what the others are made of.

| factor | ALONE | HELD OUT | contribution | tied pairs | distinct values |
|---|---|---|---|---|---|
| `sim_bill_shock_base` | **0.7014** | 0.6066 | **+0.1335** | 27.9% | 17 |
| `sim_action_propensity` | 0.5925 *(inside null)* | 0.6862 | **+0.0539** | 27.6% | 9 |
| `sim_price_response` | 0.4836 *(inside null)* | 0.7143 | +0.0258 | **2.1%** | **131** |
| `sim_dissatisfaction_response` | 0.3806 *(inside null)* | 0.7412 | **−0.0012** | **0.2%** | **135** |

**SVT route — 1,266 decisions, 50 departures. AUC 0.6721, null [0.4139, 0.5854].**

> **⚠ THE PER-FACTOR TABLE BELOW IS SUPERSEDED — 2026-08-31, later the same day.** It is kept
> because the correction is the point. These figures do not carry the exposure offset, and once
> exposure is divided out **neither factor clears its null alone** while the composed hazard still
> does. `sim_action_propensity`'s 0.6421 was crediting a term with what the segment length was
> doing. **Quote the corrected table in "The company beside the ceiling" below, never this one.**

| factor | ALONE | HELD OUT | contribution | tied pairs | distinct values |
|---|---|---|---|---|---|
| `sim_action_propensity` | **0.6421** | 0.6057 | **+0.0664** | 36.9% | 10 |
| `sim_svt_inertia` | 0.6057 | 0.6421 | +0.0300 | 17.5% | 127 |

*ALONE* = every other factor on that route frozen at its population mean. *HELD OUT* = only this one
frozen. The null on each route is wide because each route is thin; per-factor figures at 32 and 50
departures order the factors, they do not measure them to three decimals.

**Two factors carry rung 3 and they are not the two the design is about.** Bill shock, and action
propensity — income stress × tenure, a term the C2 design demoted to a *modulator* precisely because
it is not a reason anyone left.

> **AMENDED 2026-08-31 by the exposure offset.** The second half of that sentence used to read "It
> is nonetheless the strongest single discriminator on the route that now carries most of the
> departures." **That is withdrawn.** With exposure divided out, `sim_action_propensity` reads
> 0.5067 ALONE on the SVT route — inside its null. It is the strongest single discriminator on the
> **renewal** route among the non-bill-shock terms (+0.0539), and on SVT it cannot be separated
> from the segment length it was riding. The claim was true of an uncorrected reading and is false
> of a corrected one.

### The two that contribute nothing, and they fail for OPPOSITE reasons

This distinction is the reason `tie_fraction` is on the instrument. Without it, both of these read
as "we looked and there was nothing there".

**`dissatisfaction` is heterogeneity that was discretised away.** `satisfaction_score` has **434
distinct values across the population** (sd 0.096) — genuine, per-household, exactly the "hidden
reasons of their own" the canon asks for. It reaches the hazard as **three values**, and the great
majority of the book gets the same one. The consequence is arithmetic, not statistical: **92.0% of
within-stratum pairs are ties**, a tie scores 0.5, so the variable cannot move an AUC more than 0.04
from chance whatever hazard is attached to it. Its contribution is **+0.0000** — not small, *zero*.
The variation exists in the population and is thrown away between the population and the hazard.

> **REPAIRED, AND THE REPAIR FOUND SOMETHING WORSE — 2026-08-31, later the same day.** Item 1 below
> was done: `satisfaction_churn_multiplier` now interpolates between its two declared endpoints
> instead of bucketing. Ties fell **92.0% → 0.2%**, distinct values **3 → 135**, and the pre-
> registered predictions were **scored and mostly refuted**
> (`WORKER_PREREGISTRATION_WHAT_A_CONTINUOUS_SATISFACTION_RESPONSE_MUST_SHOW_2026-08-31.md`). The
> whole-book reading did **not** move — 0.6760 → 0.6760 — and the renewal route fell 0.7412 →
> 0.7400, contribution **+0.0000 → −0.0012**.
>
> **The diagnosis in the paragraph above was right that the tie fraction was hiding something and
> wrong about what.** Ordered rather than bucketed, the factor ALONE reads **0.4672 → 0.3806**: the
> point estimate crosses to the *wrong side of chance*, and in this book the households that
> departed were on average **more** satisfied (0.6845) than those that stayed (0.6543). It sits
> inside its null `[0.3794, 0.6206]` — by 0.0012, on the bottom edge — so **we cannot say the term
> is anti-predictive**; what we can say is that there is no evidence it predicts in the right
> direction and the point estimate is on the wrong side.
>
> **The cause is measured and it is not the dose.** `corr(sim_dissatisfaction_response,
> sim_action_propensity) = −0.5188`: `sim_satisfaction` builds satisfaction partly from income
> stress, and `action_propensity` is income stress × tenure, so the households the world models as
> most dissatisfied are the same ones it models as least able to act, and the damping wins about
> three to one. Realised churn by stress tier runs **0.243 / 0.200 / 0.083** for low / moderate /
> high — backwards. Two of the four departure risks are **one variable seen twice**. Filed as
> `WORKER_FINDING_THE_WORLDS_SERVICE_RISK_IS_CANCELLED_BY_A_MODULATOR_THAT_SHARES_ITS_DRIVER_2026-08-31.md`;
> the repair is downward, to `sim_satisfaction`'s drivers, and it is choice-and-channel work.
>
> **This is a TOP-DOWN construction found on the way, named as such per the canon's instruction.**
> The three buckets were not derived from any household's rationale — they are a hand-cut mapping
> onto a published Likert distribution, and the two doses (0.85 / 1.30) remain unsourced and are
> *not* invented here. Fixing the shape did not fix the variable, which is the ladder's own point:
> a rung-3 failure repairs at the individual model, and the individual model is still wrong.

**`price_response` is the opposite and it is the more interesting one.** 131 distinct values, only
**2.1% ties** — full dispersion, nothing discretised — and it still lands at 0.4836 alone and
contributes +0.0070. So the world's price term **moves the level and does not order who leaves.**
That is a genuine rung-2 / rung-3 dissociation: the C3 split shows the price mechanism responds to
its driver with the right sign on both sides (rung 2 passes), while the same term carries almost no
information about *which* household goes (rung 3 does not). Both can be true and here both are.

### A methodological caution, measured rather than waved at

Part of the SVT route's discrimination is **exposure**, not heterogeneity. Segments run from 1 to 92
days and a longer segment is simply more time in which to leave. Measured: segment length alone
scores **0.5868 against a null of [0.4166, 0.5866]** — it clears, but by 0.0002, sitting on its own
boundary. So exposure is present, small, and must be offset rather than counted as a reason.

> **OFFSET, AND IT WAS NOT SMALL WHERE IT MATTERED — 2026-08-31.** "Present and small" is true of
> the *headline*: the route reads 0.6721 uncorrected and 0.6091 per exposure-day, still clearing.
> It is **false of the per-factor table**, where offsetting exposure moves both factors from
> outside their null to inside it. A caution sized on the headline and applied to the factors would
> have been wrong by exactly the amount that mattered. `sim_years_on_svt`, which is what the published inertia band is actually cut on
(under 3 years / 3+), scores **0.4480** — below chance, carrying nothing.

### The second half of rung 3, and it passes too

The canon asks not only whether the reasons differ but whether they are *"ones a supplier could in
principle observe or infer through a channel it actually has."* Both carrying factors clear that:

* **bill shock** — the supplier issues the bill. Observable by construction, not by inference.
* **action propensity** — income stress and tenure. A supplier sees payment behaviour and arrears
  directly, and tenure is on the account. Inferable through channels the company has.

And `company/crm/churn_model.estimate_churn_probability` already takes a rate-move term, a bill
stress term and a tenure term. **So the world's real signal is one the company can see and already
looks at.**

**What that did NOT establish, and it has since been measured.** The company's renewal-belief AUC
most recently read **0.4653**. It was tempting to put that beside 0.6760 and call the difference the
company's shortfall. **That was refused here and the refusal was right**: the two were computed over
different populations from different runs, and two true numbers whose legs are different populations
do not have a difference. What the ceiling bought was that the comparison became *possible*. It has
now been made, on one capture — see **"The company beside the ceiling"** below.

---

## The company beside the ceiling — one capture, one population, both nulls

*Added 2026-08-31. Instrument: `tools/measure_churn_heterogeneity` (the company leg is fed to the
same `within_strata_auc` and `permutation_null` as the ceiling — same rows, same strata, same seed).
Control: `tests/architecture/test_the_ceiling_and_the_belief_count_one_population.py`, seven
mutations proven. Artefact: `docs/reports/ladder_churn_ceiling_vs_belief.json`. Subject:
`ladder_churn_factors_continuous_satisfaction.json`, the post-repair capture, verified row-for-row
against `run_output_latest.json` on all 144 realised hazards.*

**The two routes are not the same experiment and are read separately. This is the whole design.**

### Renewal route — 144 decisions, 32 departures

| leg | AUC | null 95% | verdict |
|---|---|---|---|
| **CEILING** — the world's own realised hazard | **0.7400** | [0.3794, 0.6206] | clears |
| `saas.churn_model.build_churn_risk` (`churn_probability`) | **0.6815** | [0.3946, 0.6089] | clears |
| `company.crm.churn_model.estimate_churn_probability` | **0.4988** | [0.3829, 0.6241] | **we cannot tell** |

**The middle row is partly tautological and that is stated here, not in a footnote.**
`roll_lifecycle_event` seeds `effective_p_retain` from the same `build_churn_risk` number it then
grades. So 0.6815 does not say the company can pick who leaves; it says **the world's adjustment
chain preserves the ordering of the base rate it was handed**. The strongest oracle factor on this
route is `sim_bill_shock_base` (+0.1335) and the belief is a pure function of the bill-shock count —
the world is reading back the company's own input. Nothing may be inferred from it about inference.

**The bottom row is the one that answers the question, and it reads at chance.**
`company_churn_estimate` is the only company-side belief that does **not** feed the roll —
`roll_lifecycle_event` computes it, stamps it on the event, and never multiplies it into
`effective_p_retain`. On the identical 144 decisions it scores **0.4988, inside its null**. Against
a ceiling of 0.7400 on the same rows: **there was real signal to find on this route, and the belief
the company forms independently of the world's dice finds none of it.** It is not badly calibrated
in level either — mean believed churn 0.2713 against a realised rate of 0.2222 — it simply does not
order *which* household goes.

**No "fraction of the ceiling captured" is published, for two different reasons, and the instrument
refuses both in code rather than in prose.** For `build_churn_risk`, because a capture rate built
from a belief that seeds the roll would publish a tautology as company skill. For
`company_churn_estimate`, because a reading **inside its null** normalised onto a ceiling yields
**−0.5%** — a number with the authority of a measurement and the content of noise. Refused, not
rounded to zero.

### SVT route — 1,266 decisions, 50 departures. **The company forms no belief at all.**

**Ceiling 0.6721, null [0.4139, 0.5854] — it clears. There is signal on this route and nothing on
the company's side is looking at it.** This is structural, not a gap in the capture:

* `saas.churn_model.build_churn_risk` is indexed on **renewal anniversaries** —
  `_renewal_periods` walks `acquisition_date + n × 365 days`. A household drifting off the standard
  variable product at a segment boundary has no entry in it.
* `run_phase2b`'s SVT branch builds its hazard with `bill_shock_base=0.0, price_response=0.0,
  dissatisfaction_response=0.0` and **consults no company estimate of any kind**. The comment at
  the site already said so: *"there was no renewal decision to estimate a churn probability FOR."*

**So 50 of this book's 82 departures — 61% — leave through a door the company's churn model cannot
see.** That is the finding, and it is a stronger one than a poor AUC would have been: a low score is
a model that looked and failed, and this is a model that never looked. Filed as
`WORKER_FINDING_THE_COMPANY_FORMS_NO_BELIEF_ON_THE_ROUTE_CARRYING_61_PERCENT_OF_DEPARTURES_2026-08-31.md`.

### Exposure is now offset on the SVT route, and it changes what may be quoted

Item 5 below, done. Segments run 1–92 days and a longer segment is more time in which to leave.
Dividing the hazard by segment days — the offset that matches how `sim_svt_inertia` was built, a
published annual rate converted to segment length:

| reading | AUC | null 95% |
|---|---|---|
| SVT ceiling, as published | 0.6721 | [0.4139, 0.5854] |
| **SVT ceiling per exposure-day** | **0.6091** | [0.4159, 0.5850] |
| segment length alone | 0.5868 | [0.4166, 0.5866] |

**The route still clears with exposure divided out — 0.6091 — so the discrimination is not just the
billing calendar.** But the per-factor table changes character completely, and the corrected one is
now what the instrument prints:

| factor | ALONE | HELD OUT | contribution |
|---|---|---|---|
| `sim_svt_inertia` | 0.4629 *(inside null)* | 0.5067 | +0.1025 |
| `sim_action_propensity` | 0.5067 *(inside null)* | 0.4629 | +0.1463 |

**Once exposure is offset, NEITHER factor alone clears its null while the composed hazard does.**
The remaining discrimination on this route lives in the product of the two terms, not in either of
them, and **no single factor from the SVT route may be quoted as carrying it.** The uncorrected
reading — which showed `action_propensity` at 0.6421 ALONE — was crediting a term with what the
segment length was doing. The instrument prints the corrected table with the uncorrected one marked
as superseded, because a caution recorded beside a table is a caution nobody applies.

### What this comparison is allowed to say

* On the renewal route, on one population: **the ceiling is 0.7400 and the company's independent
  belief is 0.4988, inside its null.**
* On the SVT route: **the ceiling is 0.6721 and there is no company belief to compare.**
* **No ratio between the routes, and no whole-book company figure.** The company's belief exists on
  144 of 1,410 decisions; a "company AUC for the book" would have a numerator and denominator
  counting different things. The two readings are published side by side with their populations
  named, which is what the direction asked for.
* It does **not** say the company's model is badly built. It says that on the population where it
  can be graded independently, it carries no ordering information, and on the population carrying
  most of the departures it is not consulted. Those are two different repairs.

---

### The earlier reading, kept beside this one

The first version of this assessment was taken on `docs/reports/c2_departure_factors.json` — the
**pre-C1b, renewal-only** capture, 465 decisions and 79 departures. It read **0.6232 against a null
of [0.4267, 0.5677]**, with bill shock carrying it and the other three inside the null. The
direction of every conclusion survived; two numbers did not, and they are corrected here rather than
quietly replaced:

* **`action_propensity` looked like nothing (+0.0081) and is the second real factor on the renewal
  route (+0.0539).** It was invisible because the route on which it appeared to matter most was not
  in the table. *The SVT figure that used to stand beside it here (+0.0664) is **withdrawn** — that
  reading is uncorrected for exposure and, offset, the factor does not clear its null on that route
  at all. See "Exposure is now offset on the SVT route".*
* **"Three fifths of a household's departure probability is the year" was true of the renewal slice
  and is false of the book.** Over both routes, the between-stratum share of log-hazard variance is
  37.0% across 19 year×route strata, and **the year alone accounts for 4.2%.** The rest is the
  route. The renewal-only figure of 60.2% was a property of a population that had lost 69% of its
  rows, not of the world.

Both corrections point the same way, and it is worth saying plainly: **the first reading was taken
on the population that happened to be in a file, and it answered a narrower question than the one
asked.** That is this project's recurring failure mode, and the defence that worked was the
instrument printing its own population on every run.

---

## Rung 1 — the level, and the 28 August stickiness fix re-examined as the canon requires

**It was done by scaling. Confirmed, and by its own docstring.**

First, a correction of the date, because the record should be right: **there is no 28 August
stickiness change.** The work that made the world's stickiness match the published switching series
is three commits on **2026-08-30** — `3e90ae5e1` (the world took the shape of the series and
normalised its level away), `56718a719` (the departure level becomes a quantity with units), and
`71242c941` (the year-level anchor and the band control). The 28th's commits touch retention offers
and market defence, not the switching level. Everything the canon says about the fix applies; only
the date moves.

**What it is.** `simulation/departure_level_anchor.YEAR_LEVEL_ANCHOR` is a table of ten numbers, one
per calendar year, fitted by bisection so that the world's realised departure rate lands on the
published band. `build_departure_risks` multiplies it into every hazard. It is a **per-year
aggregate scalar**, which is precisely the shape the canon names: *"the one move that is always
wrong: clamping an aggregate to pass a check."*

**The symptom the canon predicts is present, exactly.** The realised level sits on the **exact high
endpoint of the band in 10 years out of 10** (measured in
`WORKER_FINDING_THE_DEPARTURE_LEVEL_CONTROL_HAS_NO_HEADROOM_ABOVE_AND_CANNOT_SIZE_AN_UPWARD_CHANGE_2026-08-30.md`).
Headroom above is +0.00pp in every year; below it runs +0.50pp to +3.60pp. The canon's sentence —
*"a world whose level sits on the exact edge of the band every year has almost certainly been fitted
to that edge"* — describes this without qualification.

### But the canon's CAUSAL claim does not hold for this variable, and that is worth more than agreeing

The canon's diagnosis is: *"A world validated top-down — aggregates pinned to the record — contains
no per-customer signal. Individual variation becomes noise around a forced mean."*

**Measured, and it is not what is happening here.**

| level anchor | population mean p(depart) | within-year oracle AUC |
|---|---|---|
| 0.5 | 0.0278 | 0.6239 |
| 1.0 (flattened) | 0.0552 | 0.6235 |
| 2.0 | 0.1084 | 0.6229 |
| 3.0 | 0.1599 | 0.6226 |
| 5.0 | 0.2573 | 0.6232 |
| 10.0 | 0.4647 | 0.6248 |
| **as fitted (1.52–4.60 by year)** | — | **0.6232** |

*Sweep taken on the renewal route, which is the only route the anchor scales — `svt_inertia`
deliberately does not carry it. Re-measured on the two-route capture, the renewal route reads
**0.7400 as fitted and 0.7400 with the anchor flattened to 1.0** — on the continuous-satisfaction
capture the two are not 0.002 apart, they are the same number to four places, on a different
population.*

**A 20× sweep of the anchor moves the rung-3 reading by 0.002.** The reason is structural rather
than lucky: the anchor is a single multiplier *within* a year, AUC is a *rank* statistic, and a
uniform positive scaling cannot change a ranking. **Deleting the anchor tomorrow would buy exactly
zero rung 3.**

This is stated first and plainly because agreeing with the canon here would have been free and
wrong. The anchor is real debt — for rung 1, where it destroys the headroom that lets a level change
be *sized*, and for rung 2, where a level that cannot emerge cannot be projected past 2025. It is
not the reason the company keeps reading "we cannot tell". Repairing it and expecting the A/B
results to move would be a prediction made against a measurement that already exists.

**And the year is a much smaller part of a household's hazard than the renewal slice suggested.**
Decomposing log(realised hazard) over the whole book: **between-stratum 37.0% across 19 year×route
strata, within-stratum 63.0% — and the year alone accounts for 4.2%.** On the renewal slice alone
the between-year share reads 60.2%, and that figure was a property of a population that had lost 69%
of its rows rather than of the world. Corrected here rather than quietly replaced, because a
between-population correction is the mistake this project keeps paying for.

So the canon's concern is real but smaller than it looks, and it is a *level* problem (rung 1)
rather than a *discrimination* problem (rung 3). Both year terms (`sim_level_anchor`,
`sim_market_opportunity`) are top-down, and together they move 4.2% of the variance in who leaves.

### And the anchor is now stale in a way nothing could see

**C1b (`067a00dfd`) added a second departure route and the anchor is fitted on a table that cannot
see it.** SVT accounts drift off the default tariff at a segment boundary; there is no renewal
decision, so `tools/capture_departure_factors` — which wraps `roll_lifecycle_event` — never records
them. `fit_year_level_anchor`, `measure_departure_level`, `population_anchor._churn_by_year` and the
C2 reason mix all read that table.

Nothing went red. The table still had rows, and every field populated. This is the "controls keyed
to a structure that moved go QUIET, not loud" class, arriving for the fifth time. The C1b author
named it as owed in a comment at the site; the comment was right and nothing acts on a comment.

**Measured, and the size of it is the headline of this section: the renewal population fell from
465 decisions to 144 — a 69% loss — and the book now departs 32 times by renewal and 50 times off
SVT.** So the year anchor is fitted on a table that can see **39% of the departures**, and the C2
reason mix publishes three causes out of four while the missing one is the largest.

**Repaired in this commit** — `run_phase2b` now records `svt_decisions`, every SVT segment decision
with its factors *and its outcome*, which is the denominator that was missing (only the departures
were kept, so no rate on that route could be computed at all). `capture_departure_factors` writes it
to a second file rather than unioning it into the first, because an SVT decision carries no
`churn_probability`, no `sim_price_response` and no `sim_bill_shock_base` — there was no renewal for
any of them to describe, and appending them would let a mean be taken over two populations.

**The re-capture was taken and the rung-3 section above is computed on it.** What is still owed is
the **re-fit**: the anchor's ten numbers were solved against a run in which the renewal roll was the
only way out, and `departure_risks` already says so in its own words — *"the year anchor is now
OVER-FITTED"*. Capture → refit → capture is the loop, and never a widened band.

---

## Rung 0 — it does not exist, and the narrow band is doing both jobs

The canon's rung 0 is *"a wide feasible range from published evidence. Outside it the world is wrong
and the run fails. Wide on purpose: this rung stops crazy answers; it does not tune."*

**There is no such range for churn anywhere in this repository.** The only control on the world's
departure level is `test_the_worlds_realised_departure_rate_is_inside_the_published_band`, whose
band is the published record at the record's own precision — 0.6pp wide in 2016, 3.6pp in 2023.
There is a sibling control asserting the band is *narrower* than the thing it discriminates
(`test_the_band_is_narrower_than_the_thing_it_is_meant_to_discriminate`), which confirms the band is
a rung-1 instrument and was built as one.

**The consequence, and it is exactly what the ladder is for.** With one narrow band and no wide
range, a world that moved to a *defensible but different* level and a world that went *insane* fail
identically. C3 demonstrated this on real numbers: a **+0.11pp** move that shifted **zero**
departures (79 either way) "left the published band", and so would a move ten times larger. There is
no rung on which "not absurd" can be answered separately from "on the anchor", so every deviation
reads as maximum severity and none can be sized.

Building rung 0 is knowledge-first work: the wide range comes from the published record's own
extremes across a longer window and across comparable markets, not from widening the band we have.
**Nothing here is repaired by widening the rung-1 band.**

---

## Rung 2 — mechanism: the direction is established, the magnitude is not

**What passes.** `tools/split_price_response_by_curve_position.py` measured C3's change as
**+100.75pp where the company undercut the market and −53.99pp where it priced above** — the same
world change producing opposite signs by price side. A variable that responds to its driver with the
right sign on both sides is responding to the driver, not replaying a series.
`departure_risks.price_move_symmetry` exists as a callable form of the same property.

**What does not.** The size of that response is set by `_SENSITIVITY_SCALE`, and the module's own
refusal message says it is unidentified: *"every value from 0.87 down reproduces the population mean
exactly, with reason mixes from 99.9% to 56.6% bill-shock, and the only evidenced value overshoots
by 14.9%."* The declared value (0.039520) is a choice inside a flat region of the likelihood. So
rung 2 holds on **direction** and is **unestablished on magnitude**, and the honest consequence is
that any A/B result whose size depends on that scale inherits the ambiguity.

**This matters most for the future.** Rung 2 is what the canon offers as the anchor beyond the
record: *"a mechanism the world must obey, not a number it must match."* A mechanism whose
magnitude is unidentified can hold its shape past 2025 and still be wrong by a factor of two on
level. That is not a reason to delay generative futures; it is the caveat generative futures must
carry, and it is a sharper one than "the future is unanchored".

---

## What this changes, in order

1. **~~Let satisfaction reach the hazard as itself.~~ DONE 2026-08-31 — and it did not buy rung 3.**
   The shape is repaired (ties 92.0% → 0.2%) and the reading did not move (0.6760 → 0.6760). What
   it bought instead is the *diagnosis*: the service risk is cancelled by a modulator that shares
   its driver, and **that** is now the highest-value repair on the page. It is not a re-tune of this
   function — it is `sim_satisfaction` needing a driver income cannot explain (service failures,
   contacts, complaints), which is choice-and-channel work and is where item 1 has moved to. The
   original wording is kept below because the reasoning was sound and the prediction was wrong, and
   the pair is the evidence the experiment preceded its answer.

   *Original:* **Let satisfaction reach the hazard as itself.** The highest-value repair on the page, and it is
   downward to the individuals exactly as the canon requires. `satisfaction_score` varies across
   434 distinct values and arrives at the hazard as three, of which one covers most of the book; the
   result is a **+0.0000** contribution and 92% tied pairs. This is not a modelling choice to be
   re-tuned — it is heterogeneity the population already has, discarded in transit. Knowledge-first
   on the shape: what the published evidence says about how service experience is distributed across
   a domestic book and through which channel a supplier sees it.
2. **Re-fit the year anchor on both routes, and union the routes into the level instruments.**
   `fit_year_level_anchor`, `measure_departure_level` and `population_anchor._churn_by_year` all
   read the renewal table alone. Capture → refit → capture, never a widened band. The C2 reason mix
   publishes three of four causes and is missing the largest.
3. **Build rung 0 for churn** — a wide feasible range from published evidence, so "not absurd" and
   "on the anchor" become two different questions and a level change can be sized.
4. **~~The company-vs-ceiling comparison on one capture.~~ DONE 2026-08-31 — and the independent
   leg reads at chance.** Both AUCs, one population, both nulls, split by route. Renewal: ceiling
   0.7400, `build_churn_risk` 0.6815 (but it seeds the roll, so it measures the world preserving
   its own input), `company_churn_estimate` **0.4988 inside its null**. SVT: ceiling 0.6721 and
   **no company belief exists**, on the route carrying 61% of departures. Section above.
   *What it displaces:* the next question is no longer "is the company poor" — it is **why the
   company's independent estimate carries no ordering at all** when the world's own strongest
   factor on that route, bill shock, is one the company issues the bill for and already reads.
5. **~~Offset exposure on the SVT route~~ DONE 2026-08-31 — and it removed both per-factor
   readings.** Per exposure-day the route still clears (0.6091), but neither `sim_svt_inertia` nor
   `sim_action_propensity` clears alone: the discrimination is in the product. The uncorrected
   per-factor table is superseded and the instrument now prints the corrected one.
6. **Then the anchor's rebuild.** Making the level emerge is right and is rung-1 and rung-2 work. It
   is last rather than first because the measurement above says it buys no rung 3, and doing it
   first would be acting on the causal story rather than on the reading.

## Where a rung status is allowed to live, because the canon and the commons rule collide

The canon says *"each Knowledge page states which rungs its variable currently passes."* Churn's
Knowledge page is `site/knowledge/how-households-choose`, and its own `wall_placement` reads:
*"Public-reality commons only… No figure produced by this project's simulation appears on this page,
and no number on this page was chosen because a number was needed."*

**A rung status is a simulation reading.** 0.6232 is what this world did, not what Ofgem published.
Putting it on that page breaks the one property that makes the commons quotable by every lane.

**Decided, not escalated:** the rung status goes where a reader of the *variable* meets it — this
document, the instrument's own output, and the control's failure message — and the Knowledge page
keeps its wall. What the canon is asking for is that a variable cannot be used without its
validation status visible, and that is satisfied by the status being unavoidable at the point of
use rather than by its location. When the second and third variables are assessed, the natural home
is one machine-readable register with a control that every world variable names all four rungs;
building that for a single entry would be building the watcher before the work.

## What this page does not say

It does not say the anchor's values are wrong, or that the world is mis-calibrated: the fit is good,
which is why every year lands on the endpoint. It does not say the company's model is poor — that
comparison is not yet available on one population and is refused above. And it does not say rung 3
passing means the company knows anything: **independence is not inference**, per the standing rule
in `tools/inference_claim.py`. Rung 3 establishes only that there is something to infer.
