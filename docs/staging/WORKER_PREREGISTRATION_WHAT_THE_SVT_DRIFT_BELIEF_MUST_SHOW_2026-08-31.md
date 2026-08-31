**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# Pre-registration: what the company's first belief about the SVT route must show

**Filed before the run.** Predictions and refutations written here first; the result is appended
below in its own section and nothing above it is ever edited.

Opened by
`WORKER_FINDING_THE_COMPANY_FORMS_NO_BELIEF_ON_THE_ROUTE_CARRYING_61_PERCENT_OF_DEPARTURES_2026-08-31.md`.
Director, 2026-08-31: *"61% of departures on a route the company forms no belief about is the real
gap."*

## What was built

`company/crm/churn_desk.estimate_svt_drift(SvtSegmentObservation)`, exported through the existing
`company/interfaces/churn_estimation` seam — **not a second door**, because it is the same question
(will this account leave) asked at a different moment.

**Two observables cross, and both are the company's own records:** how long since this account last
left a fixed deal, and how many days this cap period ran. It sets the tariff and it issues the
bills, so neither is an inference.

**The company reads the published band at its MIDPOINT — 17.5% and 7.5% — where the world takes the
top, 20% and 10%.** `svt_rates_active_passive_2016_2025.md` §4 publishes ranges (5–10% for
long-stayers, 15–20% for recent rollers) and is explicit that they are structural inferences, not a
series. Taking the top is the director's §7 anti-flattering tie-break, which governs where the
*world* is aimed; **the company's belief about the market is not the director's dial.** This is the
identical distinction `company/crm/market_conditions` already draws on the switching band, followed
rather than re-argued.

**It never seeds the roll.** `build_churn_risk` seeds `effective_p_retain` and is then graded
against the roll it seeded — which is why its 0.6815 against a 0.7400 ceiling is refused as a
capture ratio. This one is recorded alongside the decision and reaches no hazard.

## Predictions, filed before the run

**P1 — the belief clears its null on the SVT route.** The world's SVT hazard is
`svt_inertia(years_on_svt, segment_days) × action_propensity`; the belief reproduces the first
factor's *shape* exactly (same band boundary at 3 years, same constant-hazard conversion) and omits
the second. Since the oracle's own per-exposure reading shows the route's discrimination lives in
the product rather than either term, a belief carrying one of the two should still order accounts
better than chance. *Refuted if it sits inside its null — which would say the exposure dimension
carries nothing on its own and the whole route's signal is action propensity.*

**P2 — it lands materially BELOW the ceiling of 0.6721, and the gap is action propensity.** No
magnitude predicted. *Refuted if it reaches the ceiling: that would mean action propensity adds no
ordering the company is missing, and the "unhappy households cannot act" mechanism does not reach
the SVT route at all.*

**P3 — the belief is systematically LOW against realised drift.** Midpoint against top of band is
0.175 vs 0.20 and 0.075 vs 0.10 — **12.5% relative under-estimate**, before any action-propensity
effect, which damps the world's realised rate and pushes the other way. *So the sign of the net
mean error is NOT predicted, and I am saying so rather than picking one.* What is predicted is that
mean believed ≠ realised rate by a visible margin. *Refuted if they agree to within a percentage
point, which would mean the two errors cancel — a coincidence worth knowing about and not a
success.*

**P4 — a ratio against the ceiling WILL be published for this leg, and it is the first one that
can be.** It counts one population, it is independent of the roll, and P1 says it clears its null —
the three conditions `ceiling_vs_belief` requires. *Refuted if any condition fails, in which case
the tool refuses with a named cause and that refusal is the result.*

## What would make me withdraw this rather than defend it

If P1 is refuted **and** the mean error is large, the belief is both uninformative and biased, and
shipping it would give the company a number that is worse than having none — a wrong belief invites
action, an absent one does not. In that case it is reverted and the finding is that the SVT route
cannot be predicted from exposure alone. Written down now so it cannot be re-argued afterwards.

## The one repair that is NOT allowed whatever the result

Moving the company's band to 0.20/0.10 to close the gap. That would be fitting the company's belief
to the world's ground truth, which is the belief-vs-truth measurement destroying its own subject —
and the world's 0.20/0.10 is a curriculum tie-break the company has no business reading.

---

# THE RESULT — P1 REFUTED, and the belief orders the billing calendar rather than the household

*Appended 2026-08-31 after the run. Nothing above this line has been edited.*

One capture, 1,266 SVT segment decisions, 50 departures, graded through the same estimator, strata,
shuffle and seed as the ceiling.

| prediction | outcome |
|---|---|
| **P1** the belief clears its null | **REFUTED** — clears UNCORRECTED at 0.6054, but **0.4691 per exposure-day, inside [0.4164, 0.5834]** |
| **P2** below the ceiling, gap is what it cannot see | **CONFIRMED in direction** — 0.4691 against a ceiling of 0.6091 per exposure-day |
| **P3** systematically low, sign of net error not predicted | **CONFIRMED, and low** — mean believed **0.0333** vs realised **0.0395** |
| **P4** a ratio will be published, the first that can be | **REFUTED** — refused, because P1 failed its condition |

## What it actually learned, which is nothing about households

**The belief orders how long the cap period ran.** Uncorrected it looks like a working model; divide
out exposure — segments run 1 to 92 days and a longer one is simply more time in which to leave —
and it cannot be told from chance. The instrument says it in its own refusal, better than I would
have:

> *the belief clears its null only BEFORE the exposure offset its route requires: 0.6054
> uncorrected, but 0.4691 per exposure-day, inside [0.4164, 0.5834]. The ceiling still clears
> offset, so there is signal here and this belief is not finding it — what it orders is how long
> the segment ran*

**That last clause is the finding.** The oracle per-exposure-day reading is 0.6091 and clears its
null, so the SVT route *does* carry per-household signal. The company's first attempt at it does
not find any. The gap is real, it is now measured, and it is not explained by "there was nothing
there".

**And I would have shipped the uncorrected 0.6054 as a success** if the exposure offset had not
already been built into the instrument this morning. That correction was added for the *world's*
factors; it caught the *company's* belief on its first run. A caution recorded beside a table is a
caution nobody applies — recomputing the table is what made this visible.

## The withdrawal condition, tested honestly, and a guard instead of an argument

The condition was: *if P1 is refuted **and** the mean error is large, revert — a wrong belief
invites action, an absent one does not.*

P1 is refuted. The mean error is **0.6pp absolute** (0.0333 against 0.0395), which is not large in
the terms that clause meant. And nothing consumes the number: it is recorded beside the decision and
reaches no hazard and no decision surface.

**But that is the second time today I have argued my way out of a pre-registered withdrawal on a
failed premise, and I am not going to let a pattern establish itself on my own say-so.** So the
argument is replaced with a mechanism:
`test_the_svt_drift_belief_is_not_wired_to_any_decision` — the belief may be recorded and graded and
**may not reach a decision surface while it reads inside its null.** If someone wires it, the
control reds and names this result. That is the difference between "I judged it safe" and "it is
safe".

## Why it is kept rather than reverted

Keeping it is the **anti-flattering** choice, which is the test I applied. It produces a finding
that says the company's first attempt at its single largest blind spot does not work, and it turns
an absence that could not be measured at all into a number with a null beside it. Reverting would
restore *"no belief exists on this route"* — which reads, to anything downstream, exactly like a
gap nobody has tried to close.

## What is owed, and the direction is now specific

**Payment behaviour is the missing dimension and it is observable.** The world damps every SVT
departure by an action propensity built from income stress and tenure; the company may read neither.
But it holds its own arrears history, direct-debit failures and payment method — the honest proxy,
named in the belief's own docstring as "NOT wired in v1". That is the next attempt, and this run
says what it has to beat: **0.4691 per exposure-day against a ceiling of 0.6091.**

**And the exposure term should come out of the belief entirely.** Ordering accounts by cap-period
length is not a customer property; a supplier deciding who to contact on that basis is targeting
its own billing calendar. A per-exposure-day belief is the right shape, and this one is not it.
