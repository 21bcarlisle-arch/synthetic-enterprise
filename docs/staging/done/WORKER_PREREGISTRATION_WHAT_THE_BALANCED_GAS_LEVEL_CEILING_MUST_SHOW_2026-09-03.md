**Severity:** RECORDED · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `EP13_adapter_carbon_intensity` · **Claim:** `the-balanced-level-ceiling-decides-whether-daily-gas-level-is-a-build-target`

*Drawn by the dial-weighted self-refill on the maturity map; `W4_the_wall` is the atom's own lane. RECORDED rather than LATENT: nothing here is a defect awaiting repair -- it is a measurement that either promotes the daily gas LEVEL to a build target or retires it, and whichever it does is written into the atom's level-hold note in the same commit.*

# PREREGISTRATION — what the balanced gas-level ceiling must show

**Filed 2026-09-03, BEFORE the instrument was written or run.** Atom:
`EP13_adapter_carbon_intensity`, L2, **twelfth pass**. Written so the run can refute it; a
prediction filed after the answer is not a prediction.

---

## The gap this exists to close

§15 of `docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` retired the fifth candidate — a
publishable proxy for within-day CCGT dispatch, capped at **+0.0485** against a 0.233 gap to the
peer bound — and named the next hypothesis in the same breath:

> **The daily and seasonal LEVEL of gas**, worth +0.116 in 2024 on a rung that is a diagnostic
> rather than a bound. Two things must happen before it is a target: a proper ceiling on it, with
> the residual re-decided so the energy balance holds, and a check that it is *publishable*.

**This pass builds the first of those two.** The +0.116 comes from `ccgt_level`, and §15 is
explicit that it is not a bound, in its own docstring and again in the frame doc:

> `ccgt_level` and `ccgt_full` move the daily gas total **without re-deciding the residual's other
> terms**, so the half hour is met by more or less energy than its demand and part of what they
> report is that disturbance. They point at an axis; they do not bound it.

So the largest number this atom has produced on a live axis is one nobody can attribute, and the
eleventh pass said so and declined to quote it. **A number that cannot be attributed cannot promote
a build target, and it cannot retire one either.** That is the hole.

## What "the residual re-decided" means, stated before the result so it cannot be chosen to fit

The shipped merit order derives a thermal residual from observables and then splits it:

```
thermal_mw   = demand - renewables - imports - must_run          (the energy-balance anchor)
implied_ccgt = min(thermal_mw, CCGT_CAPACITY_MW)                 (30,000 MW)
above_ccgt   = max(0, thermal_mw - CCGT_CAPACITY_MW)
coal         = min(above_ccgt, coal_capacity_for_the_year)
peaker       = above_ccgt - coal, capped at 7,000 MW
```

`ccgt_level` overrides `implied_ccgt` and **leaves `above_ccgt` computed from
`CCGT_CAPACITY_MW`**, so gas + coal + peaker no longer sums to `thermal_mw`. The balanced rung
changes exactly one line — the boundary moves from the fleet's *capacity* to the *imposed gas* —

```
above_ccgt   = max(0, thermal_mw - ccgt_imposed)
```

so **gas + coal + peaker == thermal_mw identically**, and `thermal_mw` itself is untouched because
it is built from observables and is the model's energy balance. The energy a lower gas level does
not serve is served by the next units in the shipped merit order, at their shipped factors, rather
than vanishing.

> ### CORRECTION, 2026-09-03, filed BEFORE the instrument was run and left beside the claim it
> ### replaces rather than rewritten over it
>
> **The paragraph above is wrong, and a four-line smoke test at real inputs refuted it before a
> single rung was scored.** `gas + coal + peaker == thermal_mw` **is not an invariant of the
> SHIPPED model**, so it cannot be the conservation statement. Whenever `thermal_mw` exceeds the
> CCGT fleet (30,000 MW) plus the peaker headroom (7,000 MW), the shipped stack truncates its own
> residual and serves *less* energy than it demanded. Printed at demand 50,000 MW with 3,000 MW of
> renewables and **no override at all**, the baseline is **2,000 MW short of its own residual**.
>
> Keying the control to `thermal_mw` would have reported the **shipped model's truncation** as this
> substitution's imbalance in every high-demand half hour — a control going red for the world
> rather than for the instrument, which is this project's own named failure shape and would have
> been a fresh instance of it, in the very pass whose subject is an unattributable number.
>
> **The anchor is `served_baseline` — what the shipped stack actually dispatches.** The re-decision
> re-splits that fixed total around the imposed gas. The conservation statement becomes *the
> substitution moved WHICH units ran, not HOW MUCH energy ran*, which is what §15's instruction
> means and what the first formulation was reaching for.
>
> **The predictions below are unchanged in substance and P1/P2/P3 are untouched**: they are about
> the size and sign of the balanced rung against the unbalanced one, not about which anchor makes
> the balance hold. **P4's second clause is re-pointed** from "the energy-balance residual is zero"
> to "zero against `served_baseline`". The shipped model's truncation is now counted separately as
> `baseline_could_not_meet_its_own_residual` — an incidental finding about the reconstruction,
> reported and not corrected here.
>
> *This is written down because printing the numbers at real inputs before shipping the formula is
> the rule that caught it, and because a preregistration that quietly acquires the right
> formulation after the fact is not a preregistration.*

**That is one variable, not two.** The substituted quantity is the gas level; the coal/peaker
re-decision is not a second intervention but the arithmetic that makes the first one conserve
energy. The unbalanced rung is kept in the artefact beside it precisely so the difference between
them is *measured* rather than asserted.

## The predictions

> **P1 — the disturbance is material, so the eleventh pass was right to refuse the +0.116.**
> **Predicted:** `|balanced − unbalanced|` ≥ **0.01** in 2024.
> **Refuted if:** the two agree within 0.01 in **every** year — which would mean the disturbance
> was immaterial all along, `ccgt_level` was a usable bound, and §15's refusal to quote it was
> over-cautious. That is a real possible answer and it is recorded here as one.

> **P2 — the unbalanced rung is FLATTERED by the disturbance.**
> **Predicted:** balanced < unbalanced in 2024.
> **Reasoning, so the direction is falsifiable rather than hedged:** §15 measured the model
> running **6% HIGH** on gas in 2024 (8,846 MW modelled against 8,339 true), so imposing truth's
> level moves gas *down*, and in the balanced rung that energy reappears in the **peaker band at
> OCGT efficiency (0.35)** — dirtier per MWh than the CCGT it replaces. The unbalanced rung simply
> deletes it. I am not confident in this one: the shape is normalised to a demand-weighted mean of
> 1.0 per year, so a uniform level shift cancels and only the *pattern* of the modelled-vs-true gap
> survives. The sign is genuinely open and this is the prediction most likely to be refuted.

> **P3 — the balanced ceiling still clears the material bar, or the candidate is RETIRED.**
> **Predicted:** the balanced level gain in 2024 is ≥ **0.01** (`MIN_MATERIAL_GAIN`).
> **If refuted**, the daily and seasonal gas level becomes this atom's **SIXTH** retired candidate,
> the publishability check §15 also owed is **moot and will not be run**, and L3 needs a candidate
> nobody has named yet. Measuring the ceiling before building the approximation is the method that
> retired four of the previous five; it is allowed to retire this one too.

> **P4 — the identity control holds.** Imposing the model's **own** day mean through the balanced
> path changes nothing: `|gain| < 0.001` in every year, and the energy-balance residual is zero to
> floating point. **Refuted if** the instrument reports a gain when handed the model's own level —
> which would mean the rungs measure the act of substituting.

> **P5 — the null does not flatter.** Truth's day means dealt to the **wrong days** must not gain
> (< 0.01), and the correct day means must clear the scrambled ones by ≥ 0.05.
> **Stated as "may not flatter", NOT as "collapses to zero", deliberately:** §15's first draft
> keyed its null to `abs(gain) < 0.01` and went **RED against a sound instrument**, because
> scrambled input is not absent input — it is *wrong* input, and wrong input must hurt. That was a
> control pinned to a guessed answer, red because the world behaved correctly. The repair is
> carried forward here rather than re-learned.

## The constraint that must NOT be violated

**The balanced rung's energy balance is an identity, not a tolerance.** `gas + coal + peaker −
thermal_mw` must be **0.0 to floating point** on every scored half hour where no cap binds, and
every half hour where a cap *does* bind must be **counted and published**, not averaged away. Two
caps can bind: gas imposed above `thermal_mw` (clamped down), and a shortfall exceeding coal
capacity plus the 7,000 MW peaker headroom (unservable). If the bound share is large the rung is
partly measuring the caps and its reading is **refused rather than footnoted** — the discipline
§15 already applies to its own clamp.

## What this pass may NOT do

- **It may not move the level.** LAW A: a plan said 2→3 and a plan is a diagnostic, never a target.
- **It may not publish any number from the metered gas series.** `sim/elexon_fuel_outturn.py` draws
  that line and an AST walk keeps it: a module that reaches half-hourly metered gas is one edit from
  being NESO's arithmetic with a different cache. The instrument's value is as a **bound**.
- **It may not run the publishability check if P3 is refuted.** A negative ceiling retires the
  candidate outright and a publishability finding on a retired candidate is work nobody asked for.

## Grading

Graded in this document, beside these claims, against the artefact
`docs/observability/ep13_ccgt_level_ceiling.json`. Every clause of every prediction gets a verdict;
a heading that claims more than its evidence covers is reported **SPLIT** rather than confirmed.

---

# SCORECARD — graded 2026-09-03 against the artefact

| year | baseline | balanced | unbalanced | difference | identity | shuffled | cap share | discrim. |
|---|---|---|---|---|---|---|---|---|
| 2019 | 0.8819 | −0.0025 | −0.0635 | +0.0610 | +0.0000 | −0.1144 | **0.831** | pass |
| 2020 | 0.8737 | +0.0056 | −0.0781 | +0.0837 | +0.0000 | −0.0425 | **0.813** | FAIL |
| 2021 | 0.9078 | −0.0046 | −0.0394 | +0.0348 | +0.0000 | −0.0886 | **0.837** | pass |
| 2022 | 0.8697 | −0.0228 | +0.0071 | −0.0299 | +0.0000 | −0.0494 | **0.852** | FAIL |
| 2023 | 0.7973 | −0.1070 | +0.0646 | −0.1716 | +0.0000 | −0.0171 | **0.726** | FAIL |
| 2024 | 0.7425 | −0.1523 | +0.1151 | −0.2674 | +0.0000 | −0.0258 | **0.531** | FAIL |

## THE HEADLINE, AND IT IS NOT ANY OF THE PREDICTIONS

**`the_caps_are_not_carrying_the_rung` is RED in all six years, so NO YEAR HAS A READABLE
CEILING.** The cap binds on **53%–85%** of scored half hours. Conserving energy means gas can only
be raised as far as coal and the peakers were actually running, and where the residual sits below
the CCGT fleet that headroom is exactly **zero** — so the rung is pinned to the baseline on every
half hour of every day whose true gas level runs above the model's, which is roughly half of them by
construction and 83% in 2019 where §15 measured the model running 13% LOW.

**A proper ceiling on the daily gas level cannot be built inside the shipped merit order.** That is
a finding about the METHOD §15 specified, not about the world, and it is the result of this pass.

**THE NEGATIVE NUMBERS ABOVE ARE NOT THAT CEILING AND ARE NOT QUOTED AS ONE.** A rung pinned to its
own baseline on most of its population is measuring the pin.

### The control that says so was FAIL-OPEN in this instrument's first draft

`control_bound_share` counted only the fleet clamps and a non-zero balance. It read **0.000–0.050**
and passed every year. It did not count `capped_to_served` — which binds **117,510** times run-wide
against the clamps' **1,293** — and it could not, because *the cap restores the balance*, so a
balance-derived share is blind to it by construction. Corrected, the share is 0.531–0.852 and the
control is red everywhere. **Uncorrected, this pass would have published a confident sixth
retirement with six negative numbers behind it.** Mutation-proven at
`test_the_bound_share_COUNTS_the_cap_that_actually_binds`.

## The predictions, one verdict per clause

**P1 — the disturbance is material. CONFIRMED AS WRITTEN, INTERPRETATION CORRECTED.**
`|balanced − unbalanced|` is 0.0299–0.2674, over the 0.01 bar in every year, so the literal clause
holds and §15 was right to refuse to quote the +0.116. **But the difference is not cleanly "the
disturbance".** On the cap-bound half hours — the majority — the balanced rung sits at the baseline
while the unbalanced one still moves, so the gap is the disturbance *plus the cap*. The refusal §15
made is vindicated; the decomposition it was reaching for is not delivered.

**P2 — the unbalanced rung is flattered. CONFIRMED on the clause as written, SPLIT across years.**
2024 was the stated subject and balanced (−0.1523) < unbalanced (+0.1151). But the sign reverses in
2019, 2020 and 2021, where balanced runs *above* unbalanced by 0.0348–0.0837. The prediction's own
hedge — *"the sign is genuinely open and this is the prediction most likely to be refuted"* — was
the right instinct applied to the wrong half: it survives where it was stated and fails where it was
generalised.

**P3 — the balanced ceiling clears the bar, or the candidate is retired. NOT GRADED. NEITHER
PROMOTED NOR RETIRED.** P3 assumed the ceiling would be readable and it is not. **The daily and
seasonal gas level is NOT this atom's sixth retired candidate** — that would be a claim this
evidence cannot carry, and the tempting reading (five of six years negative, retire it) is exactly
what the fail-open control would have licensed. The publishability check §15 also owed stays
un-run, now for a different reason than P3 anticipated: not "moot because retired", but "premature
because undecided".

**P4 — the identity control holds. CONFIRMED, both clauses.** `level_identity` is +0.0000 in all
six years, and the balanced rung's maximum absolute balance is 0.00e+00 to 3.64e−12 against the
1e−6 bar. Re-implementation drift against `gci.build_shape` is **exactly 0.0**.

**P5 — the null does not flatter. SPLIT.** The null does not gain in any year (−0.0171 to −0.1144,
all hurting, as a scrambled input must). **The discrimination leg fails in four years of six** —
correct day levels clear scrambled ones by the required 0.05 only in 2019 and 2021. In 2022–2024
scrambled levels score *better* than correct ones. By control 6's own logic a bare negative in those
years is unreadable, which is the second independent reason not to call this a retirement.

## The constraint that must NOT be violated — HELD

The balanced rung's energy balance is an identity: max absolute residual 3.64e−12 against a 1e−6
bar, zero in four years of six. Both caps are counted and published per year. The one failure was in
which caps reached the *control*, corrected above and recorded rather than quietly fixed.
