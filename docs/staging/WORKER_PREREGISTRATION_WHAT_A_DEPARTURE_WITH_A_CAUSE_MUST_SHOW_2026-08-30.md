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
