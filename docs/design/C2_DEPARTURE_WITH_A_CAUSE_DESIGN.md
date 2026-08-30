# C2 — a departure with a cause: the design, and the trap the numbers caught

**Date:** 2026-08-30. **Author:** the delivery seat. **Status:** DESIGN, before implementation.
**Pre-registration:** `docs/staging/WORKER_PREREGISTRATION_WHAT_A_DEPARTURE_WITH_A_CAUSE_MUST_SHOW_2026-08-30.md`
— filed first, deliberately, and this document may not weaken a prediction in it.

Brief `DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md` WORK item 5; roadmap step C2.

---

## 1. What is wrong today, in one paragraph

`simulation/customer_events.py` composes a departure from five causes by multiplying them into one
scalar and rolling once:

```
p = p_base                                   # bill shock on their own bill
  · m_market(year)                           # is there anywhere to go
  · m_price(felt differential, their bill)   # our price vs the market reference
  · m_stress(income stress, tenure)          # financial pressure
  · m_satisfaction(score)                    # service
  · (1 − retention_modifier)                 # our offer
```

By the time the die is cast the causes are gone. A departure is not unlabelled; it is **uncaused
by construction**, and any `reason` field added to the emitted record could only hold a story
invented after the roll.

---

## 2. The structure: not everything in that chain is a cause

The first design decision, and the one that makes the rest work: **three of those six terms are
not risks at all.** Treating them as risks is what produced the flat multiply.

### RISKS — each is a reason a household leaves, each gets its own hazard

| risk | driven by | in the world today |
|---|---|---|
| `bill_shock` | a rise in this household's own bill | `renewal_data["churn_probability"]` |
| `price_position` | our rate against the competitor reference, felt in pounds at their bill | `churn_position_multiplier` |
| ~~`financial_stress`~~ | ~~income stress, damped by tenure~~ | **WRONG — see the amendment at §8** |
| `dissatisfaction` | service failures | `adjust_churn_for_satisfaction` |
| *(C1b)* `svt_inertia` | drift off a variable tariff with no term | not yet |
| *(C6)* `home_move` | moving house | not yet |

### MODULATORS — each scales risks and is never a risk itself

| modulator | what it is | scales |
|---|---|---|
| market opportunity | whether there is anywhere to go — 2.17 in 2016, **0.44 in 2022** | the opportunity-seeking risks (`bill_shock`, `price_position`) |
| engagement | whether the household looks at all — Ofgem RMI 45/35/20, already wired | **every** risk; a disengaged household reacts to nothing |
| retention offer | a price cut we make | `price_position` **only** |

**Why market opportunity cannot be a risk.** `market_switching_multiplier(2022) = 0.444`. A
competing-risks model has no negative hazards, and "there was nowhere to go" is not a reason
anyone left. It is a precondition on the reasons that involve going somewhere. Modelling it as a
risk was never possible; modelling it as a multiplier on everything, which is what happens today,
is why 2022 suppresses *dissatisfaction* churn too — a household disgusted with its supplier in
2022 was modelled as 56% less likely to leave because fixed deals were expensive, which is not a
mechanism anyone would defend if it were written down. **It is written down now.**

**Why the retention offer scales only the price risk** is pre-registration P6, and it is the first
genuinely actionable consequence in this programme: a discount cannot retain a service-driven
churner, so the answer to one is a service intervention — and the company can observe its own
service failures.

---

## 3. The trap the numbers caught, which is the reason this document exists

The obvious calibration is: take the published importance weights, normalise them, use them as
hazard shares, and scale globally so the mean matches. It works arithmetically. Driven at the real
mean (n=708, mean realised churn 0.06064):

```
importance weights (Ofgem/BMG, n=3,235):  price 0.40   service 0.32   exit fees 0.22
normalised shares:                              0.426        0.340            0.234
global scale L reproducing the mean:      0.06188
  h_price 0.02633   h_service 0.02106   h_exit 0.01448   ->  composed p = 0.06064  ✓
resulting share of departures:                  0.426        0.340            0.234
```

**The resulting reason mix is the input weights, exactly.** It would satisfy pre-registration P2
by construction, look like a finding, and mean nothing. That is goal-seeking with an extra step,
and it took thirty seconds of printed table to see — which is the whole argument for printing the
table before writing the formula.

### The repair, and it is a real design constraint rather than a caveat

**Hazards must be FUNCTIONS OF EACH HOUSEHOLD'S STATE, never constants.** The published weights
set each function's *sensitivity* — how much a unit of felt price differential, or a unit of
dissatisfaction, converts into hazard — and never the hazard itself.

```
h_price(household)   = a_price   · f(felt differential in £)  · m_market · engagement · offer
h_service(household) = a_service · g(satisfaction shortfall)  · engagement
h_stress(household)  = a_stress  · s(income stress, tenure)   · engagement
h_shock(household)   = a_shock   · (their own bill's rise)    · m_market · engagement
```

Only the `a_k` come from published evidence. The realised mix then emerges from the population's
actual states and **can differ from the weights** — which is what makes P2 a prediction rather
than a restatement. If the mix comes out equal to the weights, that is now a finding about the
population being uniform, not a tautology.

---

## 4. Two things the published weights cannot carry, stated rather than smoothed

**Exit fees are 22% of the published decision and the world does not model them at all.** The
weight set above therefore has a term with nowhere to go. It is not silently redistributed across
the other two — that would inflate price and service by a third between them and bury the gap.
The honest treatment is that the world models a decision missing its third-largest published
factor, and the roadmap already carries exit fees as a named item ahead of S3.

**Importance weights and stated reasons are different quantities and are not averaged.** Ofgem/BMG
gives IMPORTANCE (price 35–44%, service 32%, exit fees 22%, n=3,235). The Consumer Impacts survey
gives STATED REASONS among movers (cheaper tariff 44%, reputation 19%, issues 16%, poor service
16%, good service 15%, base 174, multi-code). They are different instruments answering different
questions, and the coincidence that price is ~44% in both is a coincidence.

The importance weights set the `a_k` because they are about the decision. The stated reasons are
the **check** on the output, per P2, and are never an input. Combining them into one weight vector
would be two true numbers whose ratio is not a quantity.

---

## 5. The order of work, and what must not be looked at first

1. **P0 calibration.** Fit the `a_k` so the population-mean realised churn matches today within
   ±0.5% relative. Until this holds, nothing else in the pre-registration is readable, because the
   level and the decomposition would both have moved.
2. **P4, the anti-goal-seek guarantee.** Re-establish `m(d)·m(−d) == 1` at the population mean.
   The prediction is that a naive rewrite BREAKS it; if it passes first time, distrust the test.
3. **Only then** the distribution shape (P1), the company's error (P3), retention effectiveness
   (P6) and the reason mix (P2 — across seeds, never off one run: there are **40 departures in a
   decade**, eight per cause).

**Do not look at the reason mix first.** It is the most interesting output and the least
trustworthy, and looking at it before P0 holds is how a calibration gets nudged toward a
recognisable answer without anyone deciding to nudge it.

---

## 6. R13

The MECHANISM — that households leave for reasons, and that a world which cannot express that is
less faithful — is mine, and is decided blind to what it does to company P&L. The measured
consequences point *against* the company: the retention lever gets weaker (P6), the company's
churn estimate gets worse (P3), and dissatisfaction stops being suppressed in crisis years.

The per-cause SENSITIVITIES are curriculum. Under §7 of the brief they are taken from published
evidence and cited, and where the evidence is ambiguous the option chosen is the one that makes
the company's advantage harder to demonstrate, with the reason recorded on the page.

---

## 8. AMENDMENT, 2026-08-30, at implementation: §2 put one term on the wrong side of its own line

Written beside the claim rather than as a quiet edit to the table, because a design corrected in
place is indistinguishable from one that was right the first time.

**§2 defines the test for a modulator and then fails to apply it to its own third row.** The test
is stated there in full: *"a competing-risks model has no negative hazards, and 'there was nowhere
to go' is not a reason anyone left."* It is applied to market opportunity, which is correctly
demoted. Applied to `financial_stress` it demotes that too, and the design did not notice.

The numbers, printed before a line of the hazard code was written:

```
STRESS_SWITCHING_MULTIPLIER    low 1.10    moderate 0.85    high 0.65
TENURE_SWITCHING_MULTIPLIER    owner 1.00  private_renter 0.80  social_renter 0.75
```

A household under HIGH income stress is modelled as **35% less likely to leave**, and a social
renter 25% less. *"I was too financially stressed to switch"* is not a reason anyone left; it is a
precondition damping whether they act at all — the same shape as *"there was nowhere to go"*, and
the same disqualification. Modelling it as a risk would have required a negative hazard for exactly
the households the multiplier damps.

**So there are THREE risks here, not four,** and income stress × tenure is a single ACTION
PROPENSITY modulator scaling every risk. `dissatisfaction` was tested the same way and survives:
it runs 1.30 / 1.00 / 0.85, and the protective 0.85 branch is a *smaller* dissatisfaction hazard
bounded below by zero, not a negative one.

This is the **second** time on this design that printing a table first caught a term facing the
wrong way — §3 caught the first, and both were caught in seconds by numbers rather than by more
thinking about the prose. The §3 argument for printing before writing is now evidenced twice.

**It does not weaken any pre-registered prediction.** P2's reason mix now has three causes to
split rather than four, which makes its n-per-cause problem *less* severe (~13 per cause in a
decade rather than eight) and leaves the prediction — price modal, service double-digit —
unchanged. P6 is untouched. P4 is untouched.

### And P4's guarantee changes shape, exactly as P4 said a naive rewrite would

`m(d)·m(−d) == 1` held on the composed form because price multiplied the WHOLE probability. Under
competing risks price scales one hazard among several and the equality does not survive it. Writing
`p(d) = c + b·m(d)` with `c = 1 − Π_{k≠price}(1−h_k)` and `b = Π_{k≠price}(1−h_k)·h_price(0)`:

```
p(d)·p(−d) = c² + c·b·(m + 1/m) + b²   ≥   c² + 2cb + b²  =  p(0)²
```

since `m + 1/m ≥ 2` for all `m > 0`. **The break is provably in the company-unfavourable
direction** and equals 1 exactly when price is the only risk. So the guarantee is re-established as
an inequality that is *stronger* than the old equality where it matters: a ratio below 1 would be
the goal-seeking hole R12 exists to close — price up one year, down the next, and finish with less
churn than parity — and that is now impossible rather than merely calibrated away. Restoring the
exact equality would mean correcting a bound that runs against us, which R13 forbids.

The exact identity survives where it is a property rather than an artefact: at the price hazard
itself, `h_price(d)·h_price(−d) == h_price(0)²` for every household. Both legs are pinned by
`tests/simulation/test_departure_risks.py`, and both were mutation-checked.

---

## 9. AMENDMENT, 2026-08-30, at wiring: §5's step 1 no longer exists, and that is a result

§5 puts **P0 first** — fit the sensitivities so population-mean realised churn does not move, "until
this holds, nothing else in the pre-registration is readable". That order was right for the question
it was written against and the question changed underneath it. Both halves of the change are
recorded here rather than quietly reordered.

**P0 was non-identifying, and then it was discharged.** The fit came back with every `a_shock` from
0.87 down reproducing the population mean *exactly* while the reason mix ran from 99.9% to 56.6%
bill-shock (`WORKER_FINDING_THE_P0_CALIBRATION_IS_EITHER_INFEASIBLE_OR_IT_CHOOSES_THE_ANSWER_2026-08-30.md`).
Choosing a point in that family would have been choosing P2's answer and reporting it as a
measurement. Then the level anchor removed the equation altogether: `simulation/departure_level_anchor.py`
sets each year's departure level from the **published GB domestic switching record**, so there is no
population mean left for a scale to hit. P0 as an invariance is not merely unidentified now, it is
unaskable.

**And holding the level constant would have been the wrong target anyway.** §5's step 1 assumes
today's level is the thing to preserve. It is not: the world ran **3.45× below** the published record
for the whole of this project's history, and the composed form's mean was additionally contaminated
by letting the price multiplier discount the bill-shock term for the 74.4% of renewals where the
company is cheaper than the market. Preserving that mean would have preserved both. So P0 is
restated as a predicted **move** — the level rises to the record's — pre-registered at
`docs/market_research/gb_switching_rate_denominators.md` §8 and §11 before the run that tests it.

**What replaces the ordering rule.** §5's real content is *do not look at the reason mix first*, and
that survives intact and is obeyed: the level is set by an anchor derived from an external
publication, the anchor scales every hazard by the same factor so it cannot move the mix at all, and
the mix is published as an **interval** across the free parameter rather than as a point. The
protection §5 wanted — that the mix cannot be nudged toward a recognisable answer — is now
structural rather than procedural.

**What the mechanism change and the level change landing together cost, and what buys it back.** The
intent was to land them separately so a churn series would carry one moving part at a time. Measured,
they are not separable: no single scale on the market term reaches the band, and the per-year
divisors that would fix each year have an empty intersection, so the level correction requires the
per-year anchor and the anchor lives inside the competing-risks form. Attribution is bought instead
by the band being an **external** anchor this tree does not generate, by the predictions being filed
before the run, and by the free parameter being published as an interval. None of those depends on
the two changes being in different commits.
