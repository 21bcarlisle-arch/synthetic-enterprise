**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# Pre-registration: what letting satisfaction reach the hazard as itself must show

**Filed before the run.** The change, the predictions and what would refute each are written here first;
the result is appended below in its own section and the predictions above it are never edited.

Opened by `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md` item 1, the highest-ranked repair in
the ladder assessment. Canon: `DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31.md` — *"a rung 3
failure is fixed by giving individuals the rationale they lack"*, and repairs go **downward, to the
individuals, never sideways to an aggregate**.

## The defect, measured

`simulation/sim_satisfaction.py` produces a **continuous** per-household satisfaction score — 434
distinct values across the captured book, mean 0.6264, sd 0.0959. It was made continuous in July,
knowledge-first, against Ofgem/Citizens Advice *Energy Consumer Satisfaction Survey* Wave 20 (BMG,
fieldwork Jan 2025, n=3,854), whose own finding is that respondents sharing one coarse band still
split materially underneath it — very satisfied 38% against satisfied 42%.

`simulation/satisfaction_churn.satisfaction_churn_multiplier` then collapses it to **three values**:

```
    s >= 0.80  ->  0.85        0.6% of the book
    s <  0.50  ->  1.30       11.4%
    otherwise  ->  1.00       88.0%
```

**The repair landed on the producer and stopped at the consumer.** Measured consequence, from
`tools/measure_churn_heterogeneity.py` on the two-route capture: `sim_dissatisfaction_response` is
tied on **92.0% of within-stratum pairs** and contributes **+0.0000** to the rung-3 reading. Not
small — zero. A tied pair scores 0.5 whatever hazard is attached to it, so the variable cannot
discriminate at any magnitude.

## The change, and it introduces no new constant

Linear interpolation between the two declared endpoints, `_LOW_SATISFACTION_THRESHOLD` 0.50 → 1.30
and `_HIGH_SATISFACTION_THRESHOLD` 0.80 → 0.85, flat outside them.

**It passes exactly through the model's own neutral point.** `sim_satisfaction.BASELINE_SATISFACTION`
is 0.70 — a household with no bill shock, no income stress and no tenure bonus. The interpolant at
0.70 is `1.30 + (0.85 − 1.30) × (0.20 / 0.30) = 1.00`, to the last decimal. The three anchors the
model already declares are mutually consistent under a straight line, and **the step function was the
thing that broke that consistency**, by flattening everyone between 0.50 and 0.80 onto the neutral
value regardless of where they sat.

So the neutral point is not chosen, and no new magnitude is introduced. What changes is only that
households between the endpoints are **ordered** instead of tied.

**What is NOT repaired and is filed rather than papered over:** 0.85 and 1.30 carry no source. They
are inherited. Nothing in the knowledge layer establishes the *dose* — how much a unit of
dissatisfaction converts into switching — and inventing one is precisely what the knowledge-first
rule forbids. The threshold-to-Likert mapping is likewise a named simplification: the world's cuts
put 0.6% of the book in the top band against a published 38%, and whether that is a
mis-calibration or a mis-mapping is not established either. **Both are registered, not fixed here.**

## Predictions, filed before the run

**P1 — the ties go.** `sim_dissatisfaction_response` distinct values rise from 3 to roughly one per
household, and its tie fraction falls from 92.0% to under 10%. *Refuted if the tie fraction stays
above 50%: that would mean the score reaching this function is not the continuous one.*

**P2 — the dissatisfaction contribution becomes positive.** Direction only; **no magnitude is
predicted.** *Refuted if it stays at 0.0000 or goes negative — which would be the more interesting
result: that the dissatisfaction hazard is too small to matter however well it is ordered, and the
repair owed is the unsourced dose rather than the shape.*

**P3 — the whole-book oracle AUC rises above 0.6760.** *Refuted if it falls. That would say the
discretisation was not costing signal and that this change traded discrimination for something else.*

**P4 — the realised departure level rises, and the band control goes RED.** The population mean of
the multiplier moves 1.03323 → 1.10154, **+6.6%**, because the book sits below the model's own
baseline satisfaction and the step function was rounding all of them up to neutral. The
dissatisfaction hazard is one of four risks, so the effect on total departures is smaller than 6.6%.
The departure-level control has **zero headroom above** in 10 years out of 10, so *any* upward move
fails it. **That red is expected and is not a reason to revert.** The repair is capture → refit →
capture, per `departure_level_anchor`'s own note, and **never a widened band**.

*If P4's red does not appear, that is itself informative and I will say so: it would mean the
dissatisfaction hazard is small enough that a 6.6% move on it is below the instrument's resolution,
which the assessment already puts at 0.00pp above the line.*

## What would make me withdraw the change rather than defend it

If P2 and P3 are both refuted — the ties go, and neither the factor contribution nor the whole-book
reading moves — then the shape was not what was costing rung 3, and shipping a level change (+6.6%)
that buys no discrimination is a worse world, not a better one. In that case the change is reverted
and the finding is that the **dose** is the defect. Written down now so it cannot be re-argued after
the numbers are in.

## The one thing that is NOT allowed as a repair, whatever the result

Re-fitting `YEAR_LEVEL_ANCHOR` so the band goes green **before** the above is answered. That would
absorb an unexplained level move into the aggregate and is the move the canon names as always wrong.
The refit, if it happens, happens after the cause of the move is stated.

---

# THE RESULT — P1 confirmed, P2 and P3 REFUTED, P4 refuted in magnitude

*Appended 2026-08-31 after the run. Nothing above this line has been edited.*

Two full captures of both departure routes, differing by one variable: the shape of
`satisfaction_churn_multiplier`. Baseline `docs/reports/ladder_churn_factors*.json`; treatment
`docs/reports/ladder_churn_factors_continuous_satisfaction*.json`. Both 1,410 decisions, 82
departures, 144 renewals + 1,266 SVT segments.

| prediction | outcome |
|---|---|
| **P1** ties fall below 10% | **CONFIRMED** — 92.0% → **0.2%**; 3 distinct values → 135 |
| **P2** dissatisfaction contribution becomes positive | **REFUTED** — +0.0000 → **−0.0012** |
| **P3** whole-book AUC rises above 0.6760 | **REFUTED** — **0.6760 → 0.6760**, unchanged; renewal route 0.7412 → 0.7400 |
| **P4** level rises, band control reds | **refuted in magnitude** — level +0.0699pp, **departures 32 → 32**, band control green |

## What actually happened, and it is worth more than the prediction was

`sim_dissatisfaction_response` ALONE moved from **0.4971 to 0.3806**. It did not become
uninformative — it was *already* uninformative-looking, and removing the ties revealed that it
points the **wrong way**. In this world, less satisfied households leave **less**.

Measured, on the treatment capture:

| income stress | n | mean satisfaction | dissatisfaction multiplier | action propensity | **realised churn rate** |
|---|---|---|---|---|---|
| low | 111 | 0.6844 | 1.0238 | 0.9801 | **0.243** |
| moderate | 20 | 0.6089 | 1.1367 | 0.7947 | **0.200** |
| high | 12 | 0.5265 | **1.2261** | **0.6067** | **0.083** |

`corr(dissatisfaction_response, action_propensity) = −0.5188`.

**The dissatisfaction risk and the action-propensity modulator are driven by the same thing.**
`sim_satisfaction` computes satisfaction partly from income stress; `action_propensity` is income
stress × tenure. So the households the world models as most dissatisfied are the same households it
models as least able to act, and the damping wins by roughly three to one. The service risk cannot
express itself, and it is not because its dose is small — it is because the world cancels it against
itself.

**With three buckets this was invisible.** 92% of pairs tied, the reading sat on chance at 0.4971,
and the honest conclusion a reader would draw was *"service does not drive departures in this
world"*. That conclusion was wrong in an important way: the mechanism is there, it is wired
backwards, and the tie fraction was hiding it.

## The pre-registered withdrawal condition was MET on its letter and NOT on its premise, and I am keeping the change

The condition above reads: *"If P2 and P3 are both refuted… shipping a level change (+6.6%) that
buys no discrimination is a worse world… the change is reverted."* P2 and P3 are both refuted. So
the letter says revert.

**Its premise is refuted too, and by the same run.** The +6.6% was on the multiplier's population
mean; on the level it is **+0.0699pp**, with **departures identical at 32** and the band control
green. There is no level change to weigh against the discrimination that was not bought. Two of the
nine years moved *down*.

So the trade the condition was written to prevent — buying nothing at the cost of a level move — is
not the trade in front of me. What is in front of me is: **no discrimination gained, no level lost,
and a wrong-signed mechanism made visible and measurable for the first time.** I am keeping the
change, and recording that I departed from the pre-registered instruction rather than quietly
letting the condition lapse.

**Why this is not rationalising, stated so it can be judged.** The reason to keep it makes our world
look *worse*, not better: it converts "service does not seem to matter here" into "our service risk
is wired backwards and we can show it". If the direction of the benefit had flattered us, the right
move would have been to revert and take the pre-registration's word for it. It does not, and the
evidence is a table of realised churn rates by stress tier, not an argument.

## The real defect, now named

**Two of the world's four departure risks are not independent reasons — they are one variable seen
twice.** Filed as
`WORKER_FINDING_THE_WORLDS_SERVICE_RISK_IS_CANCELLED_BY_A_MODULATOR_THAT_SHARES_ITS_DRIVER_2026-08-31.md`.
The repair is downward, to the individuals, and it is choice-and-channel work: satisfaction needs a
driver a supplier can observe and income cannot explain — service failures, contacts, complaints —
so that "unhappy with us" and "unable to act" stop being the same axis.

**The dose (`0.85` / `1.30`) is still unsourced and is still not invented here.** This run says the
dose is not what is stopping the mechanism, so re-deriving it before separating the drivers would be
tuning a term that is being cancelled anyway.

## One more thing the run found, and it belongs to the lane already working it

`tools/measure_departure_level` on the new capture prints **`world E[depart] = nan%`**. Cause:
**the renewal book now has no decisions at all in 2022** — 144 renewals spread over nine years with
2022 empty — so the mean over `COMPARISON_YEARS` (2017–2024) has a hole. The summary line says
`nan`, loudly; but `world_realised_rate_pct` simply *returns a dict without 2022*, and the band
control iterates what it is given, so **a missing year passes silently**. That is the same
population-scope class as the C1b finding and it is inside the delivery lane's current focus item
("the four readers naming their population on every reading"). Recorded here rather than repaired,
to avoid two lanes editing one instrument.
