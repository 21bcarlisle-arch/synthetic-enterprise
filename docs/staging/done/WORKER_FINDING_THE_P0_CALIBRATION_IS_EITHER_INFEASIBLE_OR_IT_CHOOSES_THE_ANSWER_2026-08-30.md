**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# C2's P0 calibration is either infeasible or it chooses the answer, and the target is contaminated by the defect

**Measured 2026-08-30 on the real 708-renewal factor table** (`docs/reports/c2_departure_factors.json`,
captured from a full 2016–2025 run by `tools/capture_departure_factors.py`).
Design `docs/design/C2_DEPARTURE_WITH_A_CAUSE_DESIGN.md`; pre-registration
`docs/staging/WORKER_PREREGISTRATION_WHAT_A_DEPARTURE_WITH_A_CAUSE_MUST_SHOW_2026-08-30.md`.

**Disposition: the competing-risks MECHANISM landed and the world's PHYSICS did not.** The
pre-registration's own abandon criterion and the delivery direction both say the same thing — *"if
P0 will not calibrate, that is a result: say so, keep the prediction, and leave the composed form
standing rather than shipping a half-rewrite"* — and that is what was done.

---

## 1. What P0 asked for, and the two ways it fails

P0 fixes the per-cause sensitivities so population-mean realised churn does not move, making the
LEVEL a control and the DECOMPOSITION the only thing that changed. Baseline: **0.060643** over 708
renewals.

The bill-shock hazard is the one risk that already arrives as a probability, so the natural anchor
is to keep the churn model's own calibrated base rate unscaled (`a_shock = 1.0`) and fit a single
global scale for the published price and service sensitivities. **That is infeasible.** The
bill-shock hazard *alone* has mean **0.069665** — already **14.9% above** the target, before price
or service contribute anything at all. No non-negative scale can reach it.

Freeing `a_shock` makes P0 feasible, and immediately non-identifying:

| `a_shock` | fitted scale | mean | rel. error | expected mix — shock / price / service |
|---|---|---|---|---|
| 1.00 | *infeasible* | 0.069665 | +14.9% | — |
| 0.95 | *infeasible* | 0.066182 | +9.1% | — |
| 0.90 | *infeasible* | 0.062699 | +3.4% | — |
| 0.87 | 0.000053 | 0.060643 | **+0.0000%** | **99.9% / 0.0% / 0.0%** |
| 0.80 | 0.007649 | 0.060643 | **+0.0000%** | **91.7% / 4.5% / 3.9%** |
| 0.70 | 0.018395 | 0.060643 | **+0.0000%** | **79.9% / 10.8% / 9.3%** |
| 0.60 | 0.029018 | 0.060643 | **+0.0000%** | **68.2% / 17.0% / 14.8%** |
| 0.50 | 0.039520 | 0.060643 | **+0.0000%** | **56.6% / 23.2% / 20.1%** |

**Every row from 0.87 down hits P0 exactly, and the reason mix ranges from 99.9% to 56.6%.** P0
cannot distinguish them. `a_shock` has no published evidence behind it — the Ofgem/BMG importances
(price 0.40, service 0.32) fix the price:service ratio and say nothing about how the price family
splits between "my own bill rose" and "someone else is cheaper".

**So choosing `a_shock` IS choosing P2's answer.** It would then be reported as a measurement of the
world. This is design §3's trap one level up: §3 caught constant hazards reproducing the input
weights as the output mix; this catches a free calibration parameter doing the same job through a
constraint that cannot see it.

## 2. And the P0 target itself is contaminated by the defect C2 exists to remove

This is the part worth more than the fit would have been. Why is the bill-shock hazard *above* the
composed total it is supposed to reproduce? Because the composed form lets the price and
satisfaction multipliers scale the **bill-shock** term:

```
p = p_base · m_market · m_price · m_stress · m_satisfaction
```

Measured on the same 708 renewals:

| factor | mean | median |
|---|---|---|
| `sim_price_response` | 0.9475 | **0.7617** |
| `sim_dissatisfaction_response` | 1.0398 | 1.0000 |

**In 527 of 708 renewals (74.4%) the company is CHEAPER than the market reference.** Under the
composed form that multiplies a household's churn *down* — so being cheaper than average is
modelled as making a household less likely to notice that its own bill doubled. Across the
population it discounts bill-shock churn by a factor of **0.8705**.

A competing-risks model cannot express that, and should not: *"we are cheaper than average"* is not
a reason to fail to notice your own bill. It reduces the **price** hazard toward zero, which is all
it should ever have done.

**Therefore matching the old mean exactly would mean preserving the discount.** P0 is written as
"the one number that must NOT be interesting", and it turns out to be interesting for a reason P0
was not designed to detect: it holds the level of a quantity that is partly an artefact. Holding a
contaminated target constant is not a control, it is a way of carrying the contamination forward
under the name of a calibration.

## 3. What landed anyway, and what it is worth

- `simulation/departure_risks.py` — the competing-risks form: per-risk hazards, `S = Π(1−h_k)`,
  order-free cause attribution by cumulative hazard, and the risk/modulator split. **Fails closed**
  with no default sensitivity: a default of 0.0 would silently zero the price and service hazards
  and report a 100%/0%/0% mix that looks like a measurement.
- `tests/simulation/test_departure_risks.py` — 12 controls, each naming its defect, **all four
  substantive mutations checked red**: market opportunity suppressing dissatisfaction; the
  retention offer scaling every risk; sequential (order-dependent) cause attribution; and hazards
  becoming constants.
- `tests/architecture/test_the_departure_cause_never_reaches_the_company.py` — the P3 leak guard,
  verified to fire by planting a read in `company/analytics/churn_accuracy_report.py`.
- `tools/capture_departure_factors.py`, `tools/fit_departure_hazards.py` — the factor capture and
  the fit, so the next attempt starts from measurement rather than from a re-derivation.
- The world now emits the five-factor decomposition on every lifecycle event, which is what made
  this measurable at all. It reconstructs the recorded probability to within 5e-5.

## 4. Two design corrections, both caught by printing numbers before writing formulas

**§2's risk table put `financial_stress` on the wrong side of its own line.** The design's test for
a modulator — *"a competing-risks model has no negative hazards"* — demotes it exactly as it demotes
market opportunity: `STRESS_SWITCHING_MULTIPLIER` runs 1.10 / 0.85 / **0.65** and tenure 1.00 / 0.80
/ 0.75, so high income stress makes a household **35% less likely to leave**. Income stress × tenure
is one ACTION PROPENSITY modulator; there are **three** risks, not four. Recorded at design §8.

**P4's guarantee changes shape, exactly as P4 predicted a naive rewrite would.** `m(d)·m(−d) == 1`
held because price multiplied the whole probability. Under competing risks
`p(d)·p(−d) = c² + cb(m + 1/m) + b² ≥ p(0)²` since `m + 1/m ≥ 2` — so the break is **provably in the
company-unfavourable direction**, and a ratio below 1 (the goal-seeking hole R12 exists to close) is
now impossible rather than merely calibrated away. The exact identity survives at the price hazard
itself. Both legs pinned and mutation-checked.

## 5. What would settle it

`a_shock` needs published evidence, or the question needs re-posing so it is not free:

1. **Evidence for the within-price split.** Ofgem's stated-reason instrument separates "cheaper
   tariff elsewhere" from a bill rise; if a published source splits the *importance* the same way,
   `a_shock` stops being free and P0 becomes identifying.
2. **A second constraint from a different quantity.** P0 is one equation. A second observable that
   the decomposition (not the level) predicts — the crisis-year departure rate, say, where the
   modulator split makes the two forms disagree sharply — would identify `a_shock` without anyone
   choosing it.
3. **Accept that the level moves, and pre-register the move instead of the invariance.** If the
   0.8705 discount is a defect, the honest expectation is that mean churn RISES by ~15% when it is
   removed, and P0 should be restated as a predicted move rather than an invariance. This is the
   option I would take, and it needs the director only because it changes what the world does, not
   because it is hard: it makes the world harder for the company, which is the R13-safe direction.

**Recommendation, and it is what I am doing unless overruled:** option 3, pre-registered as a
predicted +15% level move with the decomposition measured across seeds, in the next C2 turn. Option
1 is worth a discovery pass first because it is cheap and would make option 3 unnecessary.

---

## DISPOSITION UPDATE, 2026-08-30 evening: option 3 landed; this stays STAGED

**§5's option 3 — "accept that the level moves, and pre-register the move instead of the
invariance" — is what was done**, and it went further than this finding proposed. The level does not
merely move; it is taken from the published GB domestic switching record, per year, by
`simulation/departure_level_anchor.py`. The world went **4.50% → 16.20%** (2017–24 mean realised
departure probability per renewal) against a published midpoint of 15.50%.

**That DISCHARGES P0 rather than satisfying it.** P0 was one equation — hold the population mean —
and the anchor removes it: there is no mean left for a scale to hit. So the entanglement this
finding measured is gone, and the non-identification it found is not.

**Which is why this stays staged.** `a_shock` is still free, for exactly the reason §1 gives, and
the mix is published as an interval over the feasible family rather than as a point:

| | expected share |
|---|---|
| bill_shock | **55.1% – 99.9%** |
| price_position | **0.0% – 23.0%** |
| dissatisfaction | **0.0% – 21.8%** |

The world runs at the `a_shock = 0.50` end of that family, declared in
`departure_risks.DECLARED_SHOCK_WEIGHT` and argued on FIDELITY under R13 rather than on a tie-break:
it is the only end at which all three risks are materially live, and the other end is a world in
which a supplier's price position and service quality cause no departures at all — the defect
`churn_position_multiplier` was wired in to remove, arriving again through a calibration parameter.

**§5's three routes to settling it are unchanged and all still open.** Route 1 (published evidence
for the within-price split) is still the cheap one and still the one that would end this.
