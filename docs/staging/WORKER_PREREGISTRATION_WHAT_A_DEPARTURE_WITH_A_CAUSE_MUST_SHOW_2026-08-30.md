**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Pre-registration — what a departure with a cause must show, filed before a line of it is written

**Filed 2026-08-30, before any code for C2 exists.** Brief `DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md`
WORK item 5; roadmap step C2 in `docs/design/CHOICE_AND_CHANNEL_ROADMAP.md`. Nothing below has
been measured. It is written now so that a result agreeing with it counts for something, and a
result refuting it cannot be quietly re-read — *a prediction filed after the answer is not a
prediction.*

## The change, in one line

Replace the multiplicative composition in `simulation/customer_events.py`

```
p = p_base · m_price · m_stress · m_sat          (one scalar, one roll, cause destroyed)
```

with a competing-risks form

```
S = Π (1 − p_k)      p = 1 − S      the risk that fires names the departure
```

so that a departure carries the cause that produced it.

## The one-variable design, and why the calibration comes first

Two things could move here — the LEVEL of churn and its DECOMPOSITION — and if both move at once
nothing can be attributed to either. So the cause-specific hazards are calibrated to reproduce
today's population-mean aggregate BEFORE anything else is looked at. That makes the level a
control rather than a result, and the decomposition the only thing that changed.

**P0 (the design check, not a finding).** Population-mean realised churn probability after the
change, against the same run before it: **within ±0.5% relative**. If it is not, the calibration
failed and every prediction below is unreadable. This is the one number that must NOT be
interesting.

## The predictions

**P1 — the upper tail compresses and the middle thickens.**

The first draft of this prediction was *"the count of households decided by the clip falls to
zero"*, and I measured the baseline before filing rather than after. **It is 1 event in 708.**
A prediction about one event is not a prediction, so P1 is restated on the quantity that actually
has a population behind it.

Baseline, measured at HEAD on `docs/reports/run_output_latest.json`, 708 renewal events:

| | value |
|---|---|
| min | 0.0025 |
| median | 0.0334 |
| mean | 0.0606 |
| p90 | 0.1263 |
| p95 | 0.1820 |
| p99 | 0.4179 |
| max | 0.9500 |
| at the 0.95 world cap | **1** |
| departures | 40 of 708 (5.6%) |

The multiplicative form grows without bound and is clipped; the competing-risks form is
`1 − Π(1−p_k)`, which is bounded by 1, concave, and always below `Σ p_k`. With the mean held by
the P0 calibration, a thinner top must be paid for by a thicker middle.

*Prediction: p99 FALLS, the median RISES, and the mean is unchanged (P0).* Refuted if p99 rises,
or if the whole distribution shifts in one direction — that would mean the calibration moved the
level rather than the shape, which P0 is supposed to prevent.

**P2 — the simulated reason mix resembles the published mover mix in SHAPE, not in numbers —
AND CANNOT BE MEASURED ON ONE RUN. This is the most important line in this document.**

**There are 40 departures in a decade run.** Split across five causes that is eight per cause, and
a five-way split on n=40 has intervals wide enough to contain almost any ordering. So a reason mix
computed from a single run is not evidence about the world; it is noise with labels on it, and it
will look exactly like a finding.

*Anything below is a prediction about the mix at adequate n, and I am recording NOW what adequate
means so that it cannot be decided after the numbers are in:* the modal-cause claim needs the
leading cause's share to be separated from the second by more than the bootstrap interval on both.
On n=40 it will not be. **The mix therefore gets measured across seeds, or it does not get
published** — and if the seed budget is not there, the honest output is "we cannot yet say", which
belongs on the page rather than in a footnote.

This is the same bound the level-vs-selection instrument already hit from the other side (61 seeds
× 3 arms to resolve a £1,106 effect, because a decade run prices only ~30 renewals). It is the
same scarcity, and C1's SVT product does not relieve it — C1 gives two thirds of the book NO
renewal decision, which makes term-end departures rarer, not commoner. What C1 adds instead is a
DIFFERENT departure population (inertia churn off SVT, which has no term structure), so the two
kinds must be counted separately and never summed into one "departures" figure.

*The published comparison, for when n is adequate:* Ofgem, January–February 2024, base 174,
multi-code — cheaper tariff 44%, reputation 19%, issues with supplier or tariff 16%, poor service
16%, good service 15%. That is a stated reason among MOVERS and is not a hazard over everybody, so
an exact match is not the test and would be evidence of tuning rather than of fidelity. Its own
base is 174 and its codes are multi-select, so it does not sum to 100 and carries no tight
interval either: this is a weak anchor being compared against a weak measurement, and the only
honest use of it is directional.

*Prediction: price is the MODAL cause of departure, and service-driven departures are a
double-digit percentage share of departures — not a rounding error.*
Refuted if price comes out above 90%, or if service comes out below 5%. Either would mean the
hazards are mis-specified rather than merely uncalibrated.

**P2b — a KNOWN BIAS in the mix, measured before the run rather than discovered in it.**
Filed 2026-08-30 after measuring each factor's realised variation, which is why C2's design work
started with measurement rather than with code
(`WORKER_FINDING_THE_WORLD_CAN_PUNISH_BAD_SERVICE_BUT_BARELY_REWARD_GOOD_AND_A_HASH_DECIDES_WHO`).

Satisfaction is effectively a TWO-state variable in this world, not three: across 19,200 swept
combinations on the live book the protective band (x0.85) is reached in **1.60%**, and only 77 of
150 accounts can ever reach it at all — the gate being the sign of a hash of the customer id.

*Consequence, predicted now:* the decomposition will attribute service-driven DEPARTURES fairly
and will show service almost never PREVENTING one. The reason mix will be right about who left and
silent about who stayed. **If the service share of departures comes out plausible, that is not
evidence the service channel is modelled well** — half of it is missing, and the half that is
missing is the half a supplier can act on.

**P3 — the company gets WORSE at predicting churn, at first.**
`realized_churn_probability` acquires structure the company's features do not carry, and the
company cannot see a cause it was never given an observable for.

*Prediction: `churn_estimate_error_pct` widens.* If it NARROWS, something has leaked — the most
likely leak being a cause label reaching a company module. That would be a wall breach and the
change would be reverted, not kept.

**P4 — the anti-goal-seek guarantee must survive, and it does not survive for free.**
The present form carries `m(d)·m(−d) == 1` at the population mean: being dearer costs departures
in exactly the proportion being cheaper wins them. Nothing in the competing-risks rewrite
preserves that automatically.

*Prediction: a naive rewrite BREAKS it, and the symmetric price-move test reds before it greens.*
Recorded because if it passes first time I should distrust the test rather than congratulate the
code. Without this guarantee re-established, C2 is a licence to make over-pricing cheap again,
which is the exact defect `simulation/competitor_reference.py` was written to close two days ago.

**P5 — departures stop being uniform in time, once C1 lands beside this.**
A fixed-term book should show departures spiking at term ends; a variable book should show a low
steady trickle with no term structure. Today every departure is at a term boundary because every
account has terms.

*Prediction: with the SVT product populated, the departure-date histogram becomes visibly bimodal.*
This one is NOT testable until C1b assigns accounts to SVT, and is filed now so it is not
retro-fitted later as though it had been expected all along. It is also the prediction most likely
to be defeated by n: 40 departures spread over a decade is roughly four a year, and a histogram of
four events a year has no shape to be bimodal about.

**P6 — retention offers get LESS effective, and that is the change most likely to be resisted.**

Today `retention_modifier` scales the whole composed probability, so a price cut is exactly as
effective against a household leaving because the call centre failed it as against one leaving
over money. Under competing risks a retention offer is a PRICE cut and should reduce the
price-driven risks only. Nothing about a discount addresses dissatisfaction.

*Prediction: measured retention effectiveness falls, and the fall is concentrated in the
service-driven segment.* This makes the world harder for the company — its main retention lever
stops working on part of the book — and it is the correct direction under R13 rather than a cost
to be minimised.

**And it is the first thing in this programme that is genuinely ACTIONABLE by the company**: if a
discount cannot retain a service-driven churner, the right response is a service intervention, and
the company can observe its own service failures. That is inference advantage with a lever
attached, which is more than any of the hidden attitude axes can offer. Recorded here so that when
retention effectiveness drops it is read as the mechanism working rather than as a regression.

*Caveat, from P2b:* with satisfaction effectively one-sided in this world, the service-driven
segment can be identified but barely PROTECTED. So P6's actionability is real in principle and
capped in practice until the satisfaction ceiling is repaired.

## What would make me abandon the approach rather than fix it

If P0 cannot be met — if no calibration of per-cause hazards reproduces the current aggregate
without one hazard being driven to an absurd value — then the multiplicative form is encoding
something the competing-risks form cannot express, and the right response is to find out what
rather than to force the fit. I do not expect this and am recording it because the failure mode of
a calibration exercise is that it always succeeds eventually.

## The shortcut this document exists to refuse

Keeping the composed probability and emitting each factor's marginal contribution as an attributed
"reason" is about a third of the work, produces a plausible reason distribution, and is worthless:
it is a story told after the roll, it cannot produce a departure the composed probability would not
have produced, and the distribution it publishes is a property of the decomposition arithmetic
rather than of the world. If C2 ships in that form, this paragraph is the evidence that it was
considered and rejected before the work started, not discovered afterwards.

## R13

The MECHANISM is mine — real households leave for reasons, and a world where they cannot is less
faithful, not easier. The per-cause hazard VALUES are curriculum. Under §7 of the brief they are
taken from published evidence and cited, and where the evidence is ambiguous the option chosen is
the one that makes the company's advantage harder to demonstrate, with the reason recorded. On the
evidence above that means erring toward MORE service-driven and fewer price-driven departures,
because price is the cause the company's observables can already see.

---

# MARKED, 2026-08-30, beside each prediction

Marked after the first implementation turn, against
`docs/reports/c2_departure_factors.json` (708 renewals, full 2016–2025 run) and
`docs/staging/WORKER_FINDING_THE_P0_CALIBRATION_IS_EITHER_INFEASIBLE_OR_IT_CHOOSES_THE_ANSWER_2026-08-30.md`.
Marks are written here rather than in a separate report so that a wrong prediction sits next to the
result that refuted it. **The competing-risks physics did NOT land in the world this turn** — the
mechanism, its controls and the calibration measurement did — so the predictions that need the new
physics running are marked NOT YET MEASURABLE rather than silently left open.

**P0 — FAILED, and in a more interesting way than "the fit missed".**
Not "the calibration was hard": it is **infeasible at the only evidenced anchor and non-identifying
everywhere it is feasible.** The bill-shock hazard alone is 0.069665 against a 0.060643 target
(+14.9%), and freeing `a_shock` produces a one-parameter family that all hit the target *exactly*
(+0.0000%) with reason mixes from 99.9%/0.0%/0.0% to 56.6%/23.2%/20.1%. Choosing `a_shock` would be
choosing P2's answer.
And the target itself is contaminated: the composed form lets `m_price` scale the BILL-SHOCK term,
and the company is cheaper than the market reference in **74.4%** of renewals, discounting
bill-shock churn by a factor of **0.8705**. Holding that level constant would preserve the defect
C2 exists to remove. *The abandon criterion below was written for exactly this and is honoured.*

**P1 — NOT YET MEASURABLE, and the direction of the tail is already visible.**
It cannot be marked without a P0 that holds, because with the level free the distribution's shift
and its shape are confounded — which is the reason P0 was put first. What the arithmetic already
shows on the captured factors, at an arbitrary feasible scale: p99 falls hard (0.4502 → 0.2787) and
the median rises (0.0334 → 0.0489), which is the predicted direction. **This is NOT scored as a
confirmation**: at a scale I chose, a prediction about shape is not independent of the choice.

**P2 — NOT MEASURED, DELIBERATELY, and §5's instruction was followed.**
The design fixes the order of work and says not to reorder it: do not look at the reason mix before
P0 holds. P0 does not hold, so the mix was not computed as a result. The expected-share column in
the finding's table exists only to *demonstrate the non-identifiability* — it is the evidence that
the mix is unconstrained, and it is explicitly not published as a measurement of the world.
One correction to P2's own arithmetic: with `financial_stress` demoted to a modulator there are
**three** causes, not five, so a decade's ~40 departures give ~13 per cause rather than eight. The
n problem is smaller than filed and is not solved — the mix still gets measured across seeds or not
at all.

**P2b — CONFIRMED, and independently.**
Predicted from a 19,200-combination sweep that the protective satisfaction band (×0.85) is reached
in ~1.60% of cases. Measured on the live 708-renewal run: **8 of 708 = 1.13%**, against 98 at ×1.30
and 602 at ×1.00. Satisfaction is a two-state variable in this world, and the consequence stands as
filed — the decomposition will attribute service-driven departures fairly and show service almost
never *preventing* one. The half that is missing remains the half a supplier can act on.

**P3 — NOT YET MEASURABLE.** Needs the new physics running. The leak it warns about is now guarded
in advance rather than checked afterwards: `tests/architecture/test_the_departure_cause_never_reaches_the_company.py`
refuses any read of a cause label or its decomposition from `company/**`, and was verified to fire
by planting one in `company/analytics/churn_accuracy_report.py`.

**P4 — CONFIRMED, and it was right for the right reason.**
*"A naive rewrite BREAKS it"* — it does, provably and not merely empirically. `m(d)·m(−d) == 1` held
only because price multiplied the whole probability; under competing risks
`p(d)·p(−d) = c² + cb(m + 1/m) + b² ≥ p(0)²`, with equality only when price is the sole risk.
*"If it passes first time, distrust the test"* — this is the line that earned its place. The first
draft of the control asserted the old equality at the total level and would have been **written to
pass** by correcting the bound; the bound runs AGAINST the company (over-pricing punished harder
than under-pricing is rewarded), so correcting it would have been tuning in the direction R13
forbids. The guarantee is re-established as an inequality, which is stronger than the equality where
it matters: a ratio below 1 is now impossible rather than calibrated away. The exact identity
survives at the price hazard itself, for every household. Both legs pinned; both mutation-checked.

**P5 — NOT TESTABLE YET, as filed.** Needs C1b. Unchanged.

**P6 — MECHANISM LANDED, EFFECT NOT YET MEASURED.** The retention offer scales the price risk and
nothing else, pinned by a control that reds when the offer is wired to every risk. The predicted
*fall* in measured retention effectiveness needs the physics running.

**And one prediction that was not filed, which I got wrong by omission.**
The design's §2 risk table was taken as given. It puts `financial_stress` among the RISKS, and its
own stated test — *"a competing-risks model has no negative hazards"* — demotes it: income stress
runs 1.10 / 0.85 / **0.65** and tenure 1.00 / 0.80 / 0.75, so the households the multiplier damps
would have needed negative hazards. I should have applied the design's test to the design's own
table before building to it, and did not; the multiplier table caught it in seconds once printed.
Recorded at design §8. **Both design errors this document has now cost were caught by printing
numbers rather than by more thinking, and neither would have been caught by a test written after
the formula.**
