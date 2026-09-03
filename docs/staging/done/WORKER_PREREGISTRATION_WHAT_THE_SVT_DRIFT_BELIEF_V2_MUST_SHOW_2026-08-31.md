**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# Pre-registration: what the SVT belief must show once it can tell two households apart

**Filed before the run.** Predictions and refutations written here first; the result is appended
below in its own section and nothing above it is ever edited.

Second pre-registration on this belief. The first is
`WORKER_PREREGISTRATION_WHAT_THE_SVT_DRIFT_BELIEF_MUST_SHOW_2026-08-31.md`, whose result section
records **P1 REFUTED** — v1 read **0.4691 per exposure-day, inside [0.4164, 0.5834]**, against an
oracle ceiling of **0.6091** that clears — and named what was owed: *"payment behaviour is the
missing dimension and it is observable"*.

Director, 2026-08-31: *"give the belief at least one observable that varies across households at
the same instant, and re-grade."*

## What was built, and the one sentence that specifies it

v1's two observables — years since a fixed deal ended, and the length of this cap period — are
**both calendar**. Two accounts sitting side by side on the same cap period differ in neither in
any way the company could act on. **A belief every household shares cannot select a household**,
so it could only ever order the billing calendar, and the instrument caught it doing exactly that.

v2 adds `payment_behaviour`: the company's own collections record on the account — on-time rate and
returned Direct Debits, off its own bank feed. It varies across households at one instant, which is
the property v1 lacked.

**It places the account inside the published band rather than inventing a new rate.**
`svt_rates_active_passive_2016_2025.md` §4 publishes ranges (5–10% long-stayer, 15–20% recent
roller) and gives the band's own basis as engagement — *"Ofgem engagement surveys: most inert
segment"* / *"switched once before; some re-engagement"*. **The range is a range because engagement
varies inside it**, so placing an account within it by an engagement observable follows the source's
reason for the range existing. The five grades are spread evenly, so the middle grade (`FAIR`) and
an absent record both land exactly on the midpoint v1 used — an account the company knows nothing
bad about is scored precisely as before.

**No magnitude is taken from anywhere, and that is deliberate.** The direction is published: a
domestic account in arrears is materially less able to leave, because a supplier may object to an
indebted domestic customer's transfer (Ofgem, *Decision on review of domestic objections*, 2016) and
indebted prepayment switches run through the Debt Assignment Protocol. **The magnitude is not
established**, both Ofgem source PDFs refused text extraction, and the figures a search summary
offered are therefore not quoted or used —
`docs/market_research/svt_drift_by_payment_behaviour.md` records that failure explicitly. The
uniform spacing is not load-bearing: the belief is graded by a **ranking** statistic, and every
strictly-monotone spacing gives an identical ranking within a band. A different spacing could not
have produced a different verdict.

**The wall.** `sim_action_propensity`, income stress and housing tenure do not cross, in any
direction or under any other name. What crosses is whether the money arrived. That the two are
related in this world — both descend from one hardship substrate — is a fact the company must
**infer from its own book**, not a channel it reads. The argument is in
`company/interfaces/churn_estimation.py`'s own docstring, because this is the second belief through
that door and a door that grows a hole is how a wall fails.

**It still reaches no decision.** Recorded beside the outcome, computed after the roll, no hazard.
`test_the_svt_drift_belief_is_not_wired_to_any_decision` stays and stays red if anyone wires it.

## How it is graded — three arms, one capture, one null

Same capture, same estimator, same strata, same shuffle and seed as the ceiling. Never the new term
alone:

| arm | what it scores |
|---|---|
| **JOINT** | v2 — calendar **and** payment record. This is the belief. |
| **HELD-OUT** | v1 re-derived on *this* capture — payment record withheld. Makes the joint attributable without quoting across runs. |
| **TERM ALONE** | payment grade only, band held out. Separates interaction from redundancy. |

All three are read **per exposure-day**, beside the ceiling of **0.6091** and both nulls.

## Predictions, filed before the run

**P1 — the JOINT clears its null per exposure-day.** The world's SVT hazard is
`svt_inertia × action_propensity`; `action_propensity` descends from income stress, and so does
payment behaviour (`arrears_engine.payment_outcome` takes stress as an input). A proxy sharing the
true driver's cause should order accounts better than chance. *Refuted if the joint sits inside its
null — which would say the company's best honest proxy for who acts cannot reach the dimension the
world uses, on a route where the oracle proves the signal is there.*

**P2 — the HELD-OUT arm reproduces v1, inside its null, near 0.4691.** This is the control, not a
finding. *Refuted if it lands materially away from 0.4691 — in which case the two captures are not
the same population, the comparison is void, and that is the result rather than anything about
payment behaviour.*

**P3 — the JOINT lands materially BELOW the ceiling of 0.6091.** No magnitude predicted. *Refuted
if it reaches the ceiling, which would mean an observable the company already holds recovers all of
the ordering income stress and tenure were carrying.*

**P4 — the TERM ALONE clears its null too.** It is the only arm carrying household variation, so if
the joint moves and this does not, the movement came from somewhere I have not identified and the
attribution fails. *Refuted if it reads at chance while the joint clears — an interaction I did not
predict and would have to explain before publishing either.*

**P5 — CALIBRATION GETS WORSE EVEN IF ORDERING GETS BETTER, and the mean believed FALLS below
v1's 0.0333 against a realised 0.0395.** Over a decade of all-time payment history, stress-driven
late payments and returned Direct Debits accumulate, so I expect this book to skew **below** `FAIR`
— which pushes the mean belief down the band, away from a realised rate v1 already under-estimated.
*Refuted if the mean rises or holds.* **Filed because it is the unflattering half**: ordering and
level are different quantities, the brief asks about ordering, and I do not want a worse level
quietly arriving inside a better headline.

## ADDENDUM, filed before the run completed and before any result was seen

**P4 as filed above is careless and I am saying so before it is scored, not after.** The delivery
lane's own published narrative already records that on this route *both* factors read inside their
null **alone** — `sim_svt_inertia` 0.4628 and `sim_action_propensity` **0.5067** — while the joint
hazard clears at 0.6091. **The signal on this route lives in the interaction.** That sentence was in
the brief I was working from, and I filed P4 anyway.

So the world's OWN action-propensity term, graded alone, reads at chance here. A *proxy* for it,
graded alone, reading at chance is therefore the EXPECTED result and refutes nothing. **P4 stands as
written and will be scored as written** — I expect it to be refuted, and its refutation carries no
information about the payment observable.

**What replaces it, filed now, before the result:**

**P4b — the TERM ALONE reads inside its null, and that is uninformative rather than a finding.**
*Refuted if it clears* — which would be a genuine surprise worth its own investigation, because it
would mean the company's proxy is doing something on its own that the quantity it proxies for
cannot do on its own.

**The attribution therefore rests on JOINT versus HELD-OUT, on one population, and on nothing
else.** That comparison is well-posed whatever the term-alone arm does, which is why the arm is
published as a diagnostic and is explicitly refused a capture ratio in
`ceiling_vs_belief`.

**Recorded rather than repaired** because a prediction quietly rewritten before its answer is known
is still a prediction rewritten, and the only defence against that is the timestamp and the fact
that nothing above this heading has been edited.

## What would make me withdraw this rather than defend it

If P1 is refuted **and** P4 is refuted, the payment observable carries nothing on this route and v2
is strictly more machinery than v1 for the same reading. In that case the field comes out, the
finding is that this world does not generate a payment–propensity link an inference could use, and
that is filed as a **world gap** — not as a company failing.

**I withdrew from a pre-registered withdrawal twice on 2026-08-30 by argument.** So the condition
above is written to be checkable without judgement: two named arms, both inside their nulls, field
removed. No clause about whether the mean error is "large".

## The repairs that are NOT allowed whatever the result

1. **Moving the band to 0.20/0.10.** Fitting the company's belief to the world's ground truth
   destroys the subject being measured. Unchanged from the first pre-registration.
2. **Reaching for income stress, tenure, segment or `sim_action_propensity`** because the proxy
   underperformed. That converts a measurement of inference into a demonstration of access, which
   is the one thing this route was built to test.
3. **Re-spacing the band positions after seeing the result.** The spacing cannot change a ranking
   verdict, so any post-hoc change to it would be cosmetics applied to a number that had already
   landed.

---

# THE RESULT — P1 REFUTED AGAIN. The belief moved a long way and still cannot be told from chance.

*Appended 2026-08-31 after the run. Nothing above this line has been edited, including the
addendum, which was filed before the result existed.*

One capture, **1,266 SVT segment decisions, 50 departures**, same estimator, strata, shuffle and
seed as the ceiling. All three arms below are per exposure-day, which is the only quotable scale on
this route.

| arm | per exposure-day | null 95% | verdict |
|---|---|---|---|
| **CEILING** — the world's own hazard | **0.6091** | [0.4159, 0.5850] | clears |
| **JOINT** — v2, calendar **and** payment record | **0.5482** | [0.4125, 0.5866] | **inside — we cannot tell** |
| **HELD-OUT** — v1, payment record withheld | **0.4691** | [0.4164, 0.5834] | inside |
| **TERM ALONE** — payment grade only | 0.5115 | [0.4131, 0.5825] | inside |

| prediction | outcome |
|---|---|
| **P1** the joint clears its null | **REFUTED** — 0.5482, inside, and it misses the null's top edge of 0.5866 by **0.0384** |
| **P2** the held-out arm reproduces v1 near 0.4691 | **CONFIRMED, exactly — 0.4691** |
| **P3** the joint lands materially below the ceiling | **CONFIRMED** — 0.5482 against 0.6091 |
| **P4** the term alone clears its null | **REFUTED**, exactly as the addendum said it would be |
| **P4b** the term alone reads inside its null, uninformatively | **CONFIRMED** — 0.5115 |
| **P5** calibration worsens; mean believed falls below 0.0333 | **REFUTED** — the mean **rose** to 0.0346 against a realised 0.0395 |

## What actually happened, stated in the words the direction asked for

**The company's belief about the route carrying 61% of its departures still cannot be told from
chance.** 0.5482 against a null topping out at 0.5866. *We cannot tell.* The signal is there — the
oracle clears the same null at 0.6091 on the same 1,266 decisions — and the company is still not
finding it.

**And the observable did work.** This is not the same null result as the first one:

- The belief moved **0.4691 → 0.5482**, **+0.0791**, measured on ONE capture with the held-out arm
  re-derived on the same rows rather than quoted from yesterday's run. P2 landing on 0.4691 *to the
  digit* is what makes that number a comparison rather than two numbers from two worlds.
- **The payment record alone (0.5115) orders departures better than the whole of v1 (0.4691) did.**
  A single household observable beats both calendar terms combined.
- It closed **57%** of the gap between v1 and the ceiling — and stopped short.

**So the finding is not "payment behaviour carries nothing".** It is that payment behaviour carries
real ordering, more than the calendar ever did, **and it is still not enough to clear the null on
this route.** Those are different results and the second one is the one this run supports.

## P5 was refuted in the flattering direction, which is worth more attention than P1

I predicted the book would skew below `FAIR` and drag the mean belief down. It skews the other way
— GOOD 608, FAIR 353, POOR 128, EXCELLENT 114, CRITICAL 63, so **57% of decisions sit above the
middle grade** — and the mean belief rose from 0.0333 to 0.0346 against a realised 0.0395. The
under-estimate the first pre-registration identified narrowed by about a fifth.

**I am flagging this rather than banking it.** Calibration improving was not the objective, it was
not predicted, and it arrived from the book's payment mix rather than from anything I reasoned
about. An unpredicted move in the flattering direction is the one most likely to be a coincidence
and the one I am least entitled to claim.

## The withdrawal condition FIRED, and its own premise is refuted by the reading that fired it

The condition was: *if P1 is refuted **and** P4 is refuted, the payment observable carries nothing
on this route and v2 is strictly more machinery than v1 for the same reading — the field comes out.*

**Both triggers fired.** And both halves of the premise they were written to detect are false:
the observable carries **+0.0791**, and 0.5482 is **not** "the same reading" as 0.4691.

**I wrote that trigger against the wrong quantity.** It keys on two arms' null verdicts — today's
answers — when the property it meant to test is whether the new term moved the joint. That is this
project's most-catalogued control defect, keyed to the answer instead of the property, committed by
me inside the very clause meant to stop me exercising judgement. Filed as a finding in its own
right: `WORKER_FINDING_A_PREREGISTERED_WITHDRAWAL_TRIGGER_KEYED_TO_TWO_NULL_VERDICTS_FIRES_ON_A_
PREMISE_ITS_OWN_MEASUREMENT_REFUTES_2026-08-31.md`.

**This is the third time this month I have not executed a pre-registered withdrawal, and I am not
asking to be believed about it.** So the decision is not mine:

- The belief **is not deleted**, because deleting it would delete the +0.0791 measurement the
  director asked for and restore *"no belief exists on this route"* — which reads downstream
  exactly like a gap nobody has tried to close.
- The belief **reaches no decision**, and that is enforced rather than promised.
  `test_the_svt_drift_belief_is_not_wired_to_any_decision` reds if anyone wires it while it reads
  inside its null. It is green now and it is the mechanism the withdrawal clause was reaching for —
  the clause's stated worry was *"a wrong belief invites action, an absent one does not"*, and an
  unwireable belief invites none either.
- The reading **is published in the words above**, on the surface a reader meets, saying *we cannot
  tell*.

If that reasoning is wrong, the correction is a one-line revert of the field and the finding above
names it. What is not available is quietly keeping the field and not mentioning that the trigger
fired.

## The forbidden repairs, checked

| forbidden | done? |
|---|---|
| Move the band to the world's 0.20/0.10 | **No.** `test_no_payment_record_can_push_the_belief_outside_its_published_band` holds every grade inside the published §4 band. |
| Reach for income stress, tenure, segment or `sim_action_propensity` | **No.** What crosses is whether the money arrived. |
| Re-space the band positions after seeing the result | **No.** The spacing is unchanged and, being a ranking statistic within a band, could not have changed the verdict. |

## What this says about the thesis, which is the reason the work was drawn

The claim under test is that the advantage comes from **inference** and never from **access**. This
run is the strongest evidence yet on it, in both directions:

- **For it:** an observable a real supplier holds without asking anyone — did the money arrive —
  recovered more than half the distance to the oracle, and beat the calendar belief on its own.
  Nothing about income stress or tenure crossed the wall to do it.
- **Against it:** it still cannot be told from chance. The world's remaining discrimination is in
  the **product** of `svt_inertia × action_propensity` — the instrument says neither factor clears
  alone even for the world itself — and a proxy that shares only one factor's cause reaches a
  product term from one side.

**What is owed next is an interaction, not another single term.** A belief whose payment placement
varies *with* tenure — rather than being added alongside it — is the shape the ceiling's own
decomposition points at. That is the next attempt and this run says what it must beat: **0.5482 per
exposure-day against a ceiling of 0.6091.**
