**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*RECORDED, not LATENT: a pre-registration refutes nothing on its own. It exists so the measurement
filed beside it can be shown to have been designed before its answer was known.*

# Pre-registration: what giving the SVT hazard a market term must MOVE

**Filed 2026-09-01, delivery seat, Lane 0, BEFORE writing the term and BEFORE running the re-fit.**

This is a **predicted MOVE, per year, with a direction and a magnitude** — deliberately not an
invariance. An invariance target measured on the old code embeds the defect being removed, and this
project has paid for that class already
(`feedback_an_invariance_target_measured_on_the_old_code_can_embed_the_defect_being_removed`).

---

## 1. Knowledge first — what the published record says suppressed switching in 2022

Established from the world's own sources **before any term was written**, as the direction requires.

**`docs/market_research/svt_rates_active_passive_2016_2025.md` §3 (Crisis Period 2021–2022):**

> Active renewal **effectively collapsed**. Suppliers withdrew fixed tariffs — wholesale costs
> exceeded the Ofgem price cap ceiling so no viable fixed product could be offered.
> […] **Customers did not voluntarily churn: no competitive fixed alternatives existed.** SVT was
> de facto the "safe" tariff under EPG protection.
> […] 29 energy suppliers failed Jul 2021–May 2022, displacing ~4 million customers into SoLR. All
> placed on SVT. By Apr 2023: ~29 million customers on SVT (~90%), ~3 million on fixed (~10%) —
> complete inversion of normal structure.

**The question the direction asked — were there acquisition tariffs to switch TO — is answered
directly and negatively by the source.** There were not. The suppression is not a preference
parameter and not a household-psychology effect: the *destination product did not exist*. A
household on SVT in 2022 could not drift off SVT onto a competitive fix because no supplier was
selling one above the cap. That is a fact about the market's supply side, and it is exactly the
thing a hazard keyed only to `years_on_svt` and `segment_days` cannot represent.

**The magnitude is in the commons, not invented here.**
`simulation/market_switching_propensity.market_departure_rate` carries the published GB domestic
external-switching record: **4.30% in 2022** against **23.00% in 2020** — a 5.3x swing, and 2022 is
the trough. `market_switching_multiplier` is that same record as a dimensionless ratio.

**The base year is established and it is NOT 2024.**
`svt_rates_active_passive_2016_2025.md` §4 infers `SVT_INERTIA_ANNUAL_RECENT = 0.20` and
`SVT_INERTIA_ANNUAL_LONG_STAYER = 0.10` against a **2019–20** market — its basis column reads
*"DESNZ: ~6M switches / ~28M accounts (2019–20)"*. `market_switching_multiplier` is normalised at
`MULTIPLIER_REFERENCE_YEAR = 2024`. Per
`WORKER_FINDING_THE_SVT_FLOORS_FILED_REPAIR_APPLIES_A_2024_REFERENCED_RATIO_TO_A_2019_20_RATE_2026-08-31.md`
(item 2 of its owed list), the naive `floor × m(year)` filed at `18a09617d` levels a 2019–20 rate up
into the market it was already measured in, by a constant **1.375776** in every year.

So the composition under test **re-references the multiplier to the constants' own inference
window** rather than multiplying by the 2024-referenced one:

```
factor(y) = market_switching_multiplier(y) / mean(market_switching_multiplier(2019),
                                                  market_switching_multiplier(2020))
annual_adjusted = published_annual_rate × factor(y)
hazard          = 1 − (1 − annual_adjusted) ^ (segment_days / 365.25)
```

The factor is applied to the **annual** rate before the segment conversion, because the published
rate is annual and the constant-hazard conversion is what carries it to a cap period. Applying it
after the conversion would re-level a converted quantity and break the recomposition property
`test_the_annual_anchor_recomposes_from_the_segment_hazard` pins.

`factor(2019–20 mean) = 1.0` by construction, so **inside the inference window the world still runs
the published 0.20 / 0.10.** That is the property that makes this a re-levelling and not a new
constant.

### The factors, computed from the record before the run (inputs, not results)

| year | record % | m(y), 2024-ref | **factor(y), 2019–20-ref** |
|---|---|---|---|
| 2016 | 17.60 | 1.0932 | 0.7946 |
| 2017 | 14.00 | 0.8696 | 0.6321 |
| 2018 | 20.00 | 1.2422 | 0.9029 |
| 2019 | 21.30 | 1.3230 | 0.9616 |
| 2020 | 23.00 | 1.4286 | 1.0384 |
| 2021 | 18.40 | 1.1429 | 0.8307 |
| 2022 | **4.30** | 0.2671 | **0.1941** |
| 2023 | 12.50 | 0.7764 | 0.5643 |
| 2024 | 16.10 | 1.0000 | 0.7269 |
| 2025 | 17.90 | 1.1118 | 0.8081 |

---

## 2. What is already observed and is therefore NOT a prediction

Re-run live 2026-09-01 on `docs/reports/ladder_churn_factors.json` — **confirmed by running it, not
inherited from `18a09617d`**, because the tree has moved since 08-31. Output reproduced exactly:

| year | accts | nRen | nSVT | record % | SVT floor % | anchor |
|---|---|---|---|---|---|---|
| 2016 | 3 | 1 | 2 | 17.60 | 0.04 | — partial |
| 2017 | 57 | 20 | 115 | 14.00 | 9.27 | 4.0274 |
| 2018 | 53 | 20 | 139 | 20.00 | 11.36 | 2.5386 |
| 2019 | 39 | 14 | 110 | 21.30 | 11.60 | 4.3482 |
| 2020 | 48 | 17 | 127 | 23.00 | 9.85 | 5.8495 |
| 2021 | 54 | 22 | 148 | 18.40 | 9.62 | 4.0422 |
| 2022 | 55 | 0 | 198 | **4.30** | **12.80** | — unreachable |
| 2023 | 54 | 17 | 196 | 12.50 | 12.43 | **0.0300** |
| 2024 | 54 | 18 | 150 | 16.10 | 9.12 | 2.8005 |
| 2025 | 48 | 15 | 81 | 17.90 | 4.90 | — partial |

Refusal live, `rc=1`. That much is measured. Everything below is forecast.

---

## 3. Predictions, filed before the measurement

**P1 — the per-year MOVE, named per year.** The new SVT floor will land at approximately
`old_floor × factor(y)`, and **slightly BELOW** it. The reason is arithmetic and stated here so the
direction of the miss is pre-committed rather than explained afterwards: with
`h(a) = 1 − (1−a)^t` and `t = segment_days/365.25 < 1`, `h` carries a positive second-order term
(`h ≈ ta + t(1−t)a²/2`), so scaling `a` down by `f < 1` scales `h` down by slightly **more** than
`f`. Predicted new floors, ±0.4pp:

| year | old floor % | × factor | **predicted new floor %** | target % | reachable? |
|---|---|---|---|---|---|
| 2016 | 0.04 | 0.7946 | **0.03** | 17.60 | (partial year) |
| 2017 | 9.27 | 0.6321 | **5.86** | 14.00 | yes |
| 2018 | 11.36 | 0.9029 | **10.26** | 20.00 | yes |
| 2019 | 11.60 | 0.9616 | **11.15** | 21.30 | yes |
| 2020 | 9.85 | 1.0384 | **10.23** | 23.00 | yes |
| 2021 | 9.62 | 0.8307 | **7.99** | 18.40 | yes |
| 2022 | 12.80 | 0.1941 | **2.48** | **4.30** | **yes — this is the claim** |
| 2023 | 12.43 | 0.5643 | **7.01** | 12.50 | yes |
| 2024 | 9.12 | 0.7269 | **6.63** | 16.10 | yes |
| 2025 | 4.90 | 0.8081 | **3.96** | 17.90 | (partial year) |

**P2 — 2022 comes inside its band, and for a mechanical reason.** Predicted floor **2.48%** against
a target of **4.30%**: reachable with headroom, where the published band's own bottom
(0.15/0.05) left it at 8.99%. If 2022 comes out still above 4.30%, the term is insufficient and I
will say so on the surface rather than widen a band or clamp the year.

**P3 — 2023's anchor stops being an extinction.** It is 0.0300 today because the floor consumes
12.43 of 12.50. With the floor at ~7.01 the residual is ~5.5pp, so the renewal anchor will rise to
**above 1.0** (predicted 1.3–2.0). This is the leg that matters for the company: 2023 is a year it
can price against again.

**P4 — the floor starts tracking the record.** Spearman rank correlation between the SVT floor and
the published band midpoint over 2017–2024 will go from **−0.26** to **strongly positive, > 0.7**.
It cannot reach exactly 1.0 because the floor also carries each year's segment mix and tenure
composition, which are not monotone in the record.

**P5 — the floor stops being flat.** The CV ratio (floor CV ÷ record CV over 2017–2024) will rise
from **0.336** to **above 0.7**.

**P6 — the invariance refusal lifts, and a DIFFERENT one fires.** `svt_market_invariance_refusal`
is keyed to the signature, so it returns `None` the moment the parameter exists. But
`svt_composition_refusal` reconstructs each captured row's hazard and compares it to the recorded
probability, and `docs/reports/ladder_churn_factors*.json` was produced by the **old** world. So the
whole-book fit will refuse again, with the honest new cause *"this capture is stale"*, and the
re-fit is not landable until the capture is re-run. **I am predicting the wedge moves rather than
clears.** If it clears instead, the composition check is not reading what I think it reads and that
is a finding about the check.

---

## 4. What each outcome means

- **P2 confirmed** → the SVT route's 2022 problem was the missing market term, exactly as
  `18a09617d` named it, and the repair is a wiring change and not a constant.
- **P2 refuted** → the term is necessary but not sufficient. The finish is then the one the
  direction names as acceptable and better: *"the world departs X% in a year the record says 4.30%,
  and here is what we have not modelled"* — published, not buried.
- **P4 refuted** → the factor reaches the arithmetic but something downstream flattens it, and the
  wiring is not where I think it is.

**Two things do not happen on this turn, under any outcome.**
`tests/architecture/test_switching_rate_commons.py` is not re-pointed off its renewal-only subject,
and `population_anchor._churn_by_year`'s blindness to 2022 is **not** repaired by inserting a
`sim_churn_rate` of 0.0 — that would publish a measured zero-churn crisis year, which is the
`feedback_a_default_zero_parameter_turns_an_unobservable_cause_into_a_published_measured_zero`
class. Its arithmetic consumers fail closed instead.

**And it must not finish with a fitted constant.** The factor above is the record's own ratio,
divided by the record's own value in the constants' stated inference window. Nothing in it is
solved for.
