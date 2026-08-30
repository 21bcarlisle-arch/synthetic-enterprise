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
| `financial_stress` | income stress, damped by tenure | `adjust_churn_probability` |
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
